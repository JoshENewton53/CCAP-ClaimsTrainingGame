from flask import Flask, jsonify, request, g, session
from flask_cors import CORS
import sqlite3
import os
import json
import hashlib
from ai_service import (
    generate_scenario,
    classify_claim,
    generate_feedback,
    generate_client_profile,
    generate_ai_hint,
    analyze_user_performance,
)
from death_certificate_service import DeathCertificateService
from itemized_bill_service import ItemizedBillService

BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, 'data.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_type TEXT,
            difficulty TEXT,
            scenario_json TEXT,
            correct_answer TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            scenario_id INTEGER,
            user_answer TEXT,
            is_correct INTEGER,
            feedback_text TEXT,
            points_earned INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            achievement_key TEXT,
            unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, achievement_key)
        )
    ''')
    
    # Create admin account
    admin_hash = hashlib.sha256('Password'.encode()).hexdigest()
    cur.execute('INSERT OR IGNORE INTO users (username, password_hash, score, current_streak, xp, level) VALUES (?, ?, ?, ?, ?, ?)',
                ('Admin1', admin_hash, 0, 0, 0, 1))
    
    # Add xp and level columns if they don't exist (migration)
    try:
        cur.execute('ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0')
        cur.execute('ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1')
        cur.execute('ALTER TABLE users ADD COLUMN bio TEXT')
        cur.execute('ALTER TABLE users ADD COLUMN profile_picture BLOB')
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'changeme-set-FLASK_SECRET_KEY-in-production')
CORS(app, supports_credentials=True)

# Initialize DB on app startup
init_db()

# Initialize death certificate service
death_cert_service = DeathCertificateService()
bill_service = ItemizedBillService()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify(status='ok')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute('INSERT INTO users (username, password_hash, score, current_streak, xp, level) VALUES (?, ?, ?, ?, ?, ?)',
                    (username, password_hash, 0, 0, 0, 1))
        db.commit()
        user_id = cur.lastrowid
        session['user_id'] = user_id
        session['username'] = username
        return jsonify({'username': username, 'score': 0, 'current_streak': 0, 'xp': 0, 'level': 1})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, username, score, current_streak FROM users WHERE username = ? AND password_hash = ?',
                (username, password_hash))
    user = cur.fetchone()
    
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        cur.execute('SELECT xp, level FROM users WHERE id = ?', (user[0],))
        xp_level = cur.fetchone()
        return jsonify({'username': user[1], 'score': user[2], 'current_streak': user[3], 
                       'xp': xp_level[0] if xp_level else 0, 'level': xp_level[1] if xp_level else 1})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT username, score, current_streak, xp, level FROM users WHERE id = ?', (session['user_id'],))
        user = cur.fetchone()
        if user:
            return jsonify({'username': user[0], 'score': user[1], 'current_streak': user[2], 
                          'xp': user[3], 'level': user[4]})
    return jsonify({'error': 'Not authenticated'}), 401

@app.route('/api/scenario/generate', methods=['POST'])
def generate_scenario_endpoint():
    try:
        data = request.get_json()
        claim_type = data.get('claim_type', 'medical')
        difficulty = data.get('difficulty', 'easy')
        
        # Validate inputs
        if claim_type not in ['medical', 'dental', 'life']:
            return jsonify({'error': 'Invalid claim_type'}), 400
        if difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({'error': 'Invalid difficulty'}), 400
        
        # Generate scenario
        scenario = generate_scenario(claim_type, difficulty)

        # Generate client profile with potential mismatches
        client_profile = generate_client_profile(scenario)
        scenario['client_profile'] = client_profile

        # Generate document submission status
        document_status = generate_submitted_documents(claim_type, difficulty)
        scenario['document_status'] = document_status

        # Now that client profile and documents are attached, ask Claude for
        # a richer story using the real name and document details.
        try:
            from claude_service import generate_claim_story
            claude_desc = generate_claim_story(scenario)
            if claude_desc:
                scenario['description'] = claude_desc
        except Exception as e:
            print(f"[Claude] Story generation skipped: {e}")
        
        # Classify to get correct answer
        classification = classify_claim(scenario)
        correct_answer = classification['prediction']
        
        # Determine base actual reasons for invalid/insufficient
        actual_reasons = []
        if correct_answer == 'insufficient':
            actual_reasons = list(document_status.get('missing', []))
        elif correct_answer == 'invalid':
            if scenario.get('has_mismatch'):
                actual_reasons.append('Procedure code does not match diagnosis')
            if scenario.get('out_of_coverage'):
                actual_reasons.append('Service date outside policy coverage period')
            if len(document_status.get('missing', [])) > 0:
                actual_reasons.append('Missing required documentation')

        # Generate additional reviewable documents for medium/hard
        generated_docs = {}
        if difficulty in ['medium', 'hard']:
            generated_docs['insurance_card'] = generate_insurance_card(client_profile, difficulty, correct_answer)
            if claim_type in ['medical', 'dental']:
                generated_docs['prior_auth'] = generate_prior_auth(scenario, difficulty, correct_answer)
            try:
                from claude_service import generate_physician_notes
                notes = generate_physician_notes(scenario, client_profile, difficulty, correct_answer)
                if notes:
                    generated_docs['physician_notes'] = notes
            except Exception as e:
                print(f"[Claude] Physician notes skipped: {e}")
        if difficulty == 'hard':
            try:
                from claude_service import generate_medical_record
                record = generate_medical_record(scenario, client_profile, difficulty, correct_answer)
                if record:
                    generated_docs['medical_record'] = record
            except Exception as e:
                print(f"[Claude] Medical record skipped: {e}")

        # Wire document discrepancies into actual_reasons
        if generated_docs:
            card = generated_docs.get('insurance_card', {})
            auth = generated_docs.get('prior_auth', {})
            if card.get('is_expired'):
                actual_reasons.append('Insurance card expired')
            if card.get('has_name_mismatch'):
                actual_reasons.append('Patient name does not match insurance records')
            if auth.get('is_mismatch'):
                actual_reasons.append('Prior authorization for wrong procedure')
            if auth.get('is_expired'):
                actual_reasons.append('Prior authorization expired')
            if auth.get('status') == 'Pending' and correct_answer == 'insufficient':
                actual_reasons.append('Prior authorization pending')
            scenario['generated_docs'] = generated_docs

        scenario['actual_reasons'] = actual_reasons

        # Generate itemized bill for medical claims
        itemized_bill = None
        if claim_type == 'medical' and 'Itemized bill with CPT codes' in document_status.get('submitted', []):
            try:
                itemized_bill = bill_service.generate_bill(claim_type, scenario['procedure_code'], scenario['claim_amount'], difficulty, correct_answer)
                scenario['itemized_bill'] = itemized_bill
            except Exception as e:
                print(f"Error generating bill: {e}")
                import traceback
                traceback.print_exc()
        
        # Save to database
        db = get_db()
        cur = db.cursor()
        cur.execute(
            'INSERT INTO scenarios (claim_type, difficulty, scenario_json, correct_answer) VALUES (?, ?, ?, ?)',
            (claim_type, difficulty, json.dumps(scenario), correct_answer)
        )
        db.commit()
        scenario_id = cur.lastrowid
        
        # Return response
        response_data = {
            'id': scenario_id,
            'claim_type': claim_type,
            'difficulty': difficulty,
            'procedure_code': scenario['procedure_code'],
            'diagnosis_code': scenario['diagnosis_code'],
            'claim_amount': scenario['claim_amount'],
            'patient_age': scenario['patient_age'],
            'description': scenario['description'],
            'document_status': document_status,
            'client_profile': client_profile,
            'max_points': {'easy': 50, 'medium': 100, 'hard': 200}[difficulty]
        }
        
        if itemized_bill:
            response_data['itemized_bill'] = itemized_bill
        if generated_docs:
            response_data['generated_docs'] = generated_docs

        return jsonify(response_data)
    except Exception as e:
        print(f"Error in generate_scenario: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

ACHIEVEMENTS = {
    'hard_solver': {'name': 'Hard Solver', 'desc': 'Solved a hard question'},
    'score_250': {'name': 'Rising Star', 'desc': 'Reached 250 points'},
    'score_500': {'name': 'Expert', 'desc': 'Reached 500 points'},
    'score_750': {'name': 'Master', 'desc': 'Reached 750 points'},
    'score_1000': {'name': 'The Big 1K', 'desc': 'Reached 1000 points'},
    'score_neg100': {'name': 'Struggling', 'desc': 'Reached -100 points'},
    'score_neg250': {'name': 'In Trouble', 'desc': 'Reached -250 points'},
    'score_neg500': {'name': 'Rock Bottom', 'desc': 'Reached -500 points'},
    'streak_3': {'name': 'On Fire', 'desc': '3 correct answers in a row'},
    'fail_streak_3': {'name': 'Rough Patch', 'desc': '3 wrong answers in a row'},
    'level_5': {'name': 'Apprentice', 'desc': 'Reached level 5'},
    'level_10': {'name': 'Professional', 'desc': 'Reached level 10'},
    'level_15': {'name': 'Specialist', 'desc': 'Reached level 15'},
    'level_20': {'name': 'Expert Adjuster', 'desc': 'Reached level 20'},
    'level_30': {'name': 'Master Adjuster', 'desc': 'Reached level 30'},
    'level_40': {'name': 'Legend', 'desc': 'Reached level 40'},
    'level_50': {'name': 'Mythic', 'desc': 'Reached level 50'}
}

def calculate_xp(claim_type, difficulty, is_correct):
    base_xp = {'easy': 20, 'medium': 50, 'hard': 100}
    xp = base_xp.get(difficulty, 20)
    if claim_type == 'life':
        xp = int(xp * 0.7)
    if not is_correct:
        xp = int(xp * 0.5)
    return xp

def calculate_level(xp):
    return max(1, xp // 100 + 1)

def check_achievements(user_id, score, streak, is_correct, difficulty, level):
    db = get_db()
    cur = db.cursor()
    new_achievements = []
    
    # Check score achievements
    score_checks = [(250, 'score_250'), (500, 'score_500'), (750, 'score_750'), (1000, 'score_1000'),
                    (-100, 'score_neg100'), (-250, 'score_neg250'), (-500, 'score_neg500')]
    for threshold, key in score_checks:
        if (threshold > 0 and score >= threshold) or (threshold < 0 and score <= threshold):
            try:
                cur.execute('INSERT INTO achievements (user_id, achievement_key) VALUES (?, ?)', (user_id, key))
                new_achievements.append(ACHIEVEMENTS[key])
            except sqlite3.IntegrityError:
                pass
    
    # Check streak achievements
    if streak >= 3:
        try:
            cur.execute('INSERT INTO achievements (user_id, achievement_key) VALUES (?, ?)', (user_id, 'streak_3'))
            new_achievements.append(ACHIEVEMENTS['streak_3'])
        except sqlite3.IntegrityError:
            pass
    elif streak <= -3:
        try:
            cur.execute('INSERT INTO achievements (user_id, achievement_key) VALUES (?, ?)', (user_id, 'fail_streak_3'))
            new_achievements.append(ACHIEVEMENTS['fail_streak_3'])
        except sqlite3.IntegrityError:
            pass
    
    # Check hard question achievement
    if is_correct and difficulty == 'hard':
        try:
            cur.execute('INSERT INTO achievements (user_id, achievement_key) VALUES (?, ?)', (user_id, 'hard_solver'))
            new_achievements.append(ACHIEVEMENTS['hard_solver'])
        except sqlite3.IntegrityError:
            pass
    
    # Check level achievements
    level_checks = [(5, 'level_5'), (10, 'level_10'), (15, 'level_15'), (20, 'level_20'), 
                    (30, 'level_30'), (40, 'level_40'), (50, 'level_50')]
    for threshold, key in level_checks:
        if level >= threshold:
            try:
                cur.execute('INSERT INTO achievements (user_id, achievement_key) VALUES (?, ?)', (user_id, key))
                new_achievements.append(ACHIEVEMENTS[key])
            except sqlite3.IntegrityError:
                pass
    
    db.commit()
    return new_achievements

@app.route('/api/scenario/submit', methods=['POST'])
def submit_scenario():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    scenario_id = data.get('scenario_id')
    user_answer = data.get('user_answer')
    
    if not scenario_id:
        return jsonify({'error': 'scenario_id required'}), 400
    if user_answer not in ['valid', 'invalid', 'insufficient']:
        return jsonify({'error': 'Invalid user_answer'}), 400
    
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT scenario_json, correct_answer, difficulty, claim_type FROM scenarios WHERE id = ?', (scenario_id,))
    row = cur.fetchone()
    
    if not row:
        return jsonify({'error': 'Scenario not found'}), 404
    
    scenario = json.loads(row[0])
    correct_answer = row[1]
    difficulty = row[2]
    claim_type = row[3]
    is_correct = user_answer == correct_answer
    
    difficulty_points = {'easy': 50, 'medium': 100, 'hard': 200}
    base_points = difficulty_points.get(difficulty, 50)
    points_earned = base_points if is_correct else -int(base_points / 2)

    # Score reason selection
    reasons = data.get('reasons', [])
    actual_reasons = scenario.get('actual_reasons', [])
    reason_bonus = 0
    reason_score = {}
    if user_answer in ['invalid', 'insufficient'] and actual_reasons:
        correct_picks = [r for r in reasons if r in actual_reasons]
        wrong_picks   = [r for r in reasons if r not in actual_reasons]
        missed        = [r for r in actual_reasons if r not in reasons]
        max_bonus     = int(base_points * 0.25)
        ratio         = max(0.0, (len(correct_picks) - len(wrong_picks) * 0.5) / max(1, len(actual_reasons)))
        reason_bonus  = int(ratio * max_bonus)
        reason_score  = {
            'correct': correct_picks,
            'incorrect': wrong_picks,
            'missed': missed,
            'bonus': reason_bonus,
            'max_bonus': max_bonus,
        }

    xp_earned = calculate_xp(claim_type, difficulty, is_correct)

    feedback = generate_feedback(scenario, user_answer, correct_answer)
    feedback_text = feedback['explanation']

    user_id = session['user_id']

    # Update streak
    cur.execute('SELECT current_streak, xp, level FROM users WHERE id = ?', (user_id,))
    user_data = cur.fetchone()
    current_streak = user_data[0]
    current_xp     = user_data[1]
    current_level  = user_data[2]
    if is_correct:
        new_streak = current_streak + 1 if current_streak >= 0 else 1
    else:
        new_streak = current_streak - 1 if current_streak <= 0 else -1

    total_points = points_earned + reason_bonus

    cur.execute(
        'INSERT INTO attempts (user_id, scenario_id, user_answer, is_correct, feedback_text, points_earned) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, scenario_id, user_answer, 1 if is_correct else 0, feedback_text, total_points)
    )

    new_xp    = current_xp + xp_earned
    new_level = calculate_level(new_xp)

    cur.execute('UPDATE users SET score = score + ?, current_streak = ?, xp = ?, level = ? WHERE id = ?',
                (total_points, new_streak, new_xp, new_level, user_id))
    cur.execute('SELECT score FROM users WHERE id = ?', (user_id,))
    new_score = cur.fetchone()[0]
    
    db.commit()
    
    # Check for new achievements
    new_achievements = check_achievements(user_id, new_score, new_streak, is_correct, difficulty, new_level)

    # AI confidence scoring
    ai_confidence = None
    try:
        classification = classify_claim(scenario)
        ai_confidence = {
            'prediction': classification['prediction'],
            'confidence': classification['confidence'],
            'probabilities': classification['probabilities'],
            'ai_reasoning': classification.get('ai_reasoning', ''),
            'ai_agreed': classification['prediction'] == user_answer,
            'source': classification.get('source', 'unknown')
        }
    except Exception as e:
        print(f"AI confidence scoring failed: {e}")

    return jsonify({
        'is_correct': is_correct,
        'feedback_text': feedback_text,
        'correct_answer': correct_answer,
        'points_earned': points_earned,
        'reason_bonus': reason_bonus,
        'reason_score': reason_score,
        'xp_earned': xp_earned,
        'total_score': new_score,
        'current_streak': new_streak,
        'level': new_level,
        'xp': new_xp,
        'new_achievements': new_achievements,
        'ai_confidence': ai_confidence
    })

def generate_insurance_card(client_profile, difficulty, correct_answer):
    import random
    from datetime import datetime, timedelta

    name         = client_profile.get('name', 'Unknown Patient')
    policy_num   = client_profile.get('policy_number', f'POL-{random.randint(10000,99999)}')
    coverage_type = client_profile.get('coverage_type', 'Medical')

    today          = datetime.now()
    effective_date = today - timedelta(days=random.randint(180, 730))
    expiry_date    = effective_date + timedelta(days=365)
    group_num      = f"GRP-{random.randint(10000, 99999)}"
    copay          = random.choice(['$20', '$25', '$30', '$35', '$40'])
    deductible     = random.choice(['$500', '$750', '$1,000', '$1,500', '$2,000'])

    has_name_mismatch = False
    is_expired        = False
    display_name      = name

    if difficulty == 'hard' and correct_answer == 'invalid' and random.random() < 0.35:
        if random.random() < 0.5:
            has_name_mismatch = True
            parts = name.split()
            if len(parts) >= 2:
                display_name = f"{parts[0][0]}. {parts[-1]}"
        else:
            is_expired    = True
            expiry_date   = today - timedelta(days=random.randint(5, 60))

    return {
        'member_name':    display_name,
        'member_id':      policy_num,
        'group_number':   group_num,
        'plan_name':      f"{coverage_type} PPO Plan",
        'effective_date': effective_date.strftime('%m/%d/%Y'),
        'expiry_date':    expiry_date.strftime('%m/%d/%Y'),
        'copay':          copay,
        'deductible':     deductible,
        'is_expired':     is_expired,
        'has_name_mismatch': has_name_mismatch,
        'has_discrepancy':   has_name_mismatch or is_expired,
    }


def generate_prior_auth(scenario, difficulty, correct_answer):
    import random
    from datetime import datetime, timedelta

    procedure_code = scenario.get('procedure_code', '')
    claim_type     = scenario.get('claim_type', 'medical')

    today       = datetime.now()
    auth_number = f"AUTH-{random.randint(100000, 999999)}"
    auth_date   = today - timedelta(days=random.randint(5, 45))
    auth_expiry = auth_date + timedelta(days=90)

    authorized_procedure = procedure_code
    status          = 'Approved'
    has_discrepancy = False

    if difficulty == 'easy':
        status = 'Approved'
    elif difficulty == 'medium':
        if correct_answer == 'valid':
            status = 'Approved'
        else:
            status = random.choice(['Approved', 'Approved', 'Pending'])
    else:
        if correct_answer == 'invalid' and random.random() < 0.4:
            alt_codes = {
                'medical': ['99213', '99214', '70553', '80053'],
                'dental':  ['D0120', 'D1110', 'D2391'],
                'life':    [],
            }
            alts = [c for c in alt_codes.get(claim_type, []) if c != procedure_code]
            if alts:
                authorized_procedure = random.choice(alts)
                has_discrepancy = True
        elif correct_answer == 'invalid' and random.random() < 0.3:
            auth_expiry     = today - timedelta(days=random.randint(3, 30))
            has_discrepancy = True
        elif correct_answer == 'insufficient':
            status = random.choice(['Pending', 'Pending', 'Approved'])

    return {
        'auth_number':           auth_number,
        'status':                status,
        'authorized_procedure':  authorized_procedure,
        'requested_procedure':   procedure_code,
        'auth_date':             auth_date.strftime('%m/%d/%Y'),
        'expiry_date':           auth_expiry.strftime('%m/%d/%Y'),
        'is_expired':            auth_expiry < today,
        'is_mismatch':           authorized_procedure != procedure_code,
        'has_discrepancy':       has_discrepancy,
    }


def get_required_documents(claim_type):
    """Get list of required documents for claim type"""
    documents = {
        'medical': [
            'Patient medical records',
            'Physician notes and diagnosis',
            'Itemized bill with CPT codes',
            'Insurance card copy',
            'Prior authorization (if required)'
        ],
        'dental': [
            'Dental examination records',
            'X-rays or diagnostic images',
            'Treatment plan with CDT codes',
            'Insurance card copy',
            'Pre-treatment estimate'
        ],
        'life': [
            'Death certificate',
            'Policy documents',
            'Beneficiary identification',
            'Claim form completed',
            'Medical records (if applicable)'
        ]
    }
    return documents.get(claim_type, [])

def generate_submitted_documents(claim_type, difficulty):
    """Generate which documents were submitted vs missing based on difficulty"""
    import random
    
    all_documents = get_required_documents(claim_type)
    
    if difficulty == 'easy':
        # Easy scenarios: most documents submitted (80-100%)
        submission_rate = random.uniform(0.8, 1.0)
    elif difficulty == 'medium':
        # Medium scenarios: some documents missing (60-80%)
        submission_rate = random.uniform(0.6, 0.8)
    else:  # hard
        # Hard scenarios: many documents missing (40-70%)
        submission_rate = random.uniform(0.4, 0.7)
    
    num_to_submit = max(1, int(len(all_documents) * submission_rate))
    
    # For insufficient scenarios, ensure critical documents are missing
    if difficulty in ['medium', 'hard'] and random.random() < 0.6:
        # Identify critical documents
        critical_docs = {
            'medical': ['Patient medical records', 'Physician notes and diagnosis'],
            'dental': ['X-rays or diagnostic images', 'Treatment plan with CDT codes'],
            'life': ['Death certificate', 'Policy documents']
        }
        
        critical = critical_docs.get(claim_type, [])
        non_critical = [doc for doc in all_documents if doc not in critical]
        
        # Ensure at least one critical document is missing
        submitted = random.sample(non_critical, min(len(non_critical), num_to_submit - 1))
        if num_to_submit > len(submitted):
            submitted.extend(random.sample(critical, min(len(critical), num_to_submit - len(submitted))))
    else:
        submitted = random.sample(all_documents, num_to_submit)
    
    missing = [doc for doc in all_documents if doc not in submitted]
    
    return {
        'submitted': submitted,
        'missing': missing,
        'all_required': all_documents
    }

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT username, score, level, profile_picture FROM users ORDER BY score DESC LIMIT 100')
    users = cur.fetchall()
    
    import base64
    leaderboard = []
    for user in users:
        leaderboard.append({
            'username': user[0],
            'score': user[1],
            'level': user[2],
            'profile_picture': base64.b64encode(user[3]).decode('utf-8') if user[3] else None
        })
    
    return jsonify({'leaderboard': leaderboard})

@app.route('/api/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT bio, profile_picture FROM users WHERE id = ?', (session['user_id'],))
    user = cur.fetchone()
    
    if user:
        import base64
        return jsonify({
            'bio': user[0] or '',
            'profile_picture': base64.b64encode(user[1]).decode('utf-8') if user[1] else None
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    bio = request.form.get('bio', '')
    profile_picture = request.files.get('profile_picture')
    
    db = get_db()
    cur = db.cursor()
    
    if profile_picture:
        picture_data = profile_picture.read()
        cur.execute('UPDATE users SET bio = ?, profile_picture = ? WHERE id = ?',
                   (bio, picture_data, session['user_id']))
    else:
        cur.execute('UPDATE users SET bio = ? WHERE id = ?',
                   (bio, session['user_id']))
    
    db.commit()
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT achievement_key, unlocked_at FROM achievements WHERE user_id = ?', (session['user_id'],))
    unlocked = cur.fetchall()
    
    achievements_list = []
    for key, info in ACHIEVEMENTS.items():
        unlocked_entry = next((u for u in unlocked if u[0] == key), None)
        achievements_list.append({
            'key': key,
            'name': info['name'],
            'description': info['desc'],
            'unlocked': unlocked_entry is not None,
            'unlocked_at': unlocked_entry[1] if unlocked_entry else None
        })
    
    return jsonify({'achievements': achievements_list})

@app.route('/api/reference/codes', methods=['GET'])
def get_reference_codes():
    claim_type = request.args.get('type', 'medical')
    
    try:
        import json
        import os
        
        # Load reference data
        reference_file = os.path.join(BASE_DIR, 'reference_data', 'code_mappings.json')
        with open(reference_file, 'r') as f:
            data = json.load(f)
        
        codes = data.get(claim_type, [])
        
        return jsonify({
            'claim_type': claim_type,
            'codes': codes
        })
        
    except Exception as e:
        print(f"Error loading reference codes: {e}")
        return jsonify({'error': 'Failed to load reference codes'}), 500

@app.route('/api/ai/hint', methods=['POST'])
def get_ai_hint():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        scenario_id = data.get('scenario_id')
        attempts = data.get('attempts', 0)
        
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT scenario_json FROM scenarios WHERE id = ?', (scenario_id,))
        row = cur.fetchone()
        
        if not row:
            return jsonify({'error': 'Scenario not found'}), 404
        
        scenario = json.loads(row[0])
        hints = generate_ai_hint(scenario, attempts)
        
        return jsonify({'hints': hints})
    except Exception as e:
        print(f"Error generating hint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/death-certificate/generate', methods=['POST'])
def generate_death_certificate():
    """Generate a death certificate review scenario for life insurance claims"""
    try:
        data = request.get_json()
        difficulty = data.get('difficulty', 'medium')
        client_profile = data.get('client_profile', {})
        
        if difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({'error': 'Invalid difficulty'}), 400
        
        scenario = death_cert_service.generate_scenario(difficulty, client_profile)
        
        return jsonify(scenario)
        
    except Exception as e:
        print(f"Error generating death certificate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/death-certificate/validate', methods=['POST'])
def validate_death_certificate():
    """Validate user's death certificate review"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user_findings = data.get('user_findings', [])
        actual_errors = data.get('actual_errors', [])
        difficulty = data.get('difficulty', 'medium')
        
        # Validate the review
        result = death_cert_service.validate_review(user_findings, actual_errors)
        
        # Award points based on score
        difficulty_multiplier = {'easy': 1, 'medium': 1.5, 'hard': 2}
        base_points = result['score']
        points_earned = int(base_points * difficulty_multiplier.get(difficulty, 1))
        
        # Update user score
        user_id = session['user_id']
        db = get_db()
        cur = db.cursor()
        
        # Update streak
        cur.execute('SELECT current_streak, xp, level FROM users WHERE id = ?', (user_id,))
        user_data = cur.fetchone()
        current_streak = user_data[0]
        current_xp = user_data[1]
        current_level = user_data[2]
        is_correct = result['correct']
        
        if is_correct:
            new_streak = current_streak + 1 if current_streak >= 0 else 1
        else:
            new_streak = current_streak - 1 if current_streak <= 0 else -1
        
        xp_earned = int(result['score'] * difficulty_multiplier.get(difficulty, 1) * 0.5)
        new_xp = current_xp + xp_earned
        new_level = calculate_level(new_xp)
        
        cur.execute('UPDATE users SET score = score + ?, current_streak = ?, xp = ?, level = ? WHERE id = ?', 
                   (points_earned, new_streak, new_xp, new_level, user_id))
        cur.execute('SELECT score FROM users WHERE id = ?', (user_id,))
        new_score = cur.fetchone()[0]
        db.commit()
        
        # Check for achievements
        new_achievements = check_achievements(user_id, new_score, new_streak, is_correct, difficulty, new_level)
        
        return jsonify({
            **result,
            'points_earned': points_earned,
            'xp_earned': xp_earned,
            'total_score': new_score,
            'current_streak': new_streak,
            'level': new_level,
            'xp': new_xp,
            'new_achievements': new_achievements
        })
        
    except Exception as e:
        print(f"Error validating death certificate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/death-certificate/error-options', methods=['GET'])
def get_error_options():
    """Get list of possible errors for death certificate review"""
    try:
        options = death_cert_service.get_error_options()
        return jsonify({'error_options': options})
    except Exception as e:
        print(f"Error getting error options: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],))
    row = cur.fetchone()
    if not row or row[0] != 'Admin1':
        return jsonify({'error': 'Forbidden'}), 403

    # All trainees (exclude admin)
    cur.execute('SELECT id, username, score, current_streak, xp, level FROM users WHERE username != ?', ('Admin1',))
    trainees = cur.fetchall()

    result = []
    for t in trainees:
        user_id, username, score, streak, xp, level = t

        # Total attempts and correct
        cur.execute('SELECT COUNT(*), SUM(is_correct) FROM attempts WHERE user_id = ?', (user_id,))
        totals = cur.fetchone()
        total_attempts = totals[0] or 0
        total_correct = int(totals[1] or 0)
        accuracy = round(total_correct / total_attempts * 100, 1) if total_attempts else 0

        # Per claim type breakdown
        cur.execute('''
            SELECT s.claim_type, COUNT(*) as total, SUM(a.is_correct) as correct
            FROM attempts a
            JOIN scenarios s ON a.scenario_id = s.id
            WHERE a.user_id = ?
            GROUP BY s.claim_type
        ''', (user_id,))
        type_rows = cur.fetchall()
        by_type = {
            r[0]: {'total': r[1], 'correct': int(r[2] or 0),
                   'accuracy': round(int(r[2] or 0) / r[1] * 100, 1) if r[1] else 0}
            for r in type_rows
        }

        # Per difficulty breakdown
        cur.execute('''
            SELECT s.difficulty, COUNT(*) as total, SUM(a.is_correct) as correct
            FROM attempts a
            JOIN scenarios s ON a.scenario_id = s.id
            WHERE a.user_id = ?
            GROUP BY s.difficulty
        ''', (user_id,))
        diff_rows = cur.fetchall()
        by_difficulty = {
            r[0]: {'total': r[1], 'correct': int(r[2] or 0),
                   'accuracy': round(int(r[2] or 0) / r[1] * 100, 1) if r[1] else 0}
            for r in diff_rows
        }

        # Recent activity (last 5 attempts)
        cur.execute('''
            SELECT s.claim_type, s.difficulty, a.is_correct, a.points_earned, a.created_at
            FROM attempts a
            JOIN scenarios s ON a.scenario_id = s.id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
            LIMIT 5
        ''', (user_id,))
        recent = [{'claim_type': r[0], 'difficulty': r[1], 'is_correct': bool(r[2]),
                   'points_earned': r[3], 'created_at': r[4]} for r in cur.fetchall()]

        # Confusion matrix: what they answered vs correct answer
        cur.execute('''
            SELECT a.user_answer, s.correct_answer, COUNT(*) as cnt
            FROM attempts a
            JOIN scenarios s ON a.scenario_id = s.id
            WHERE a.user_id = ?
            GROUP BY a.user_answer, s.correct_answer
        ''', (user_id,))
        confusion_raw = cur.fetchall()
        # Build {actual: {predicted: count}}
        confusion = {}
        for user_ans, correct_ans, cnt in confusion_raw:
            if correct_ans not in confusion:
                confusion[correct_ans] = {}
            confusion[correct_ans][user_ans] = cnt

        # False approval rate: marked valid when actually invalid or insufficient
        false_approvals = sum(
            confusion.get(actual, {}).get('valid', 0)
            for actual in ['invalid', 'insufficient']
        )
        false_approval_rate = round(false_approvals / total_attempts * 100, 1) if total_attempts else 0

        # Weekly accuracy trend: last 8 weeks, each as {week, correct, total}
        cur.execute('''
            SELECT
                strftime('%Y-W%W', a.created_at) as week,
                SUM(a.is_correct) as correct,
                COUNT(*) as total
            FROM attempts a
            WHERE a.user_id = ?
            AND a.created_at >= date('now', '-56 days')
            GROUP BY week
            ORDER BY week ASC
        ''', (user_id,))
        trend_rows = cur.fetchall()
        weekly_trend = [
            {
                'week': r[0],
                'correct': int(r[1] or 0),
                'total': r[2],
                'accuracy': round(int(r[1] or 0) / r[2] * 100, 1) if r[2] else 0
            }
            for r in trend_rows
        ]

        result.append({
            'username': username,
            'score': score,
            'level': level,
            'xp': xp,
            'current_streak': streak,
            'total_attempts': total_attempts,
            'total_correct': total_correct,
            'accuracy': accuracy,
            'by_type': by_type,
            'by_difficulty': by_difficulty,
            'recent_activity': recent,
            'confusion': confusion,
            'false_approval_rate': false_approval_rate,
            'weekly_trend': weekly_trend,
        })

    # Sort by score descending
    result.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({'trainees': result})



@app.route('/api/ai/test-flan', methods=['GET'])
def test_flan():
    from ai_service import generate_flan_feedback
    test_scenario = {'claim_type': 'dental', 'procedure_code': 'D1110', 'diagnosis_code': 'K04.5', 'claim_amount': 320.00}
    result = generate_flan_feedback(test_scenario, 'valid', 'invalid', 'Procedure D1110 requires diagnosis codes K02.9, K05.10, K04.7. The claim shows K04.5, which is not valid.')
    if result:
        return jsonify({'status': 'ok', 'flan_output': result})
    return jsonify({'status': 'fallback', 'message': 'Flan-T5 not loaded'}), 503

@app.route('/api/ai/performance', methods=['GET'])
def get_ai_performance():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db = get_db()
    cur = db.cursor()
    cur.execute('''
        SELECT s.claim_type, a.is_correct
        FROM attempts a
        JOIN scenarios s ON a.scenario_id = s.id
        WHERE a.user_id = ?
        ORDER BY a.created_at DESC
        LIMIT 100
    ''', (session['user_id'],))
    rows = cur.fetchall()

    history = [{'claim_type': r[0], 'is_correct': bool(r[1])} for r in rows]
    result = analyze_user_performance(history)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
