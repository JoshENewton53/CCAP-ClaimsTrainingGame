from flask import Flask, jsonify, request, g, session
from flask_cors import CORS
import sqlite3
import os
import json
import hashlib
from ai_service import generate_scenario, classify_claim, generate_feedback, generate_client_profile
from death_certificate_service import DeathCertificateService

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
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Initialize DB on app startup
init_db()

# Initialize death certificate service
death_cert_service = DeathCertificateService()

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
        
        # Classify to get correct answer
        classification = classify_claim(scenario)
        correct_answer = classification['prediction']
        
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
        return jsonify({
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
        })
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
    
    xp_earned = calculate_xp(claim_type, difficulty, is_correct)
    
    feedback = generate_feedback(scenario, user_answer, correct_answer)
    feedback_text = f"{feedback['message']} {feedback['explanation']}"
    
    user_id = session['user_id']
    
    # Update streak
    cur.execute('SELECT current_streak, xp, level FROM users WHERE id = ?', (user_id,))
    user_data = cur.fetchone()
    current_streak = user_data[0]
    current_xp = user_data[1]
    current_level = user_data[2]
    if is_correct:
        new_streak = current_streak + 1 if current_streak >= 0 else 1
    else:
        new_streak = current_streak - 1 if current_streak <= 0 else -1
    
    cur.execute(
        'INSERT INTO attempts (user_id, scenario_id, user_answer, is_correct, feedback_text, points_earned) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, scenario_id, user_answer, 1 if is_correct else 0, feedback_text, points_earned)
    )
    
    new_xp = current_xp + xp_earned
    new_level = calculate_level(new_xp)
    
    cur.execute('UPDATE users SET score = score + ?, current_streak = ?, xp = ?, level = ? WHERE id = ?', 
                (points_earned, new_streak, new_xp, new_level, user_id))
    cur.execute('SELECT score FROM users WHERE id = ?', (user_id,))
    new_score = cur.fetchone()[0]
    
    db.commit()
    
    # Check for new achievements
    new_achievements = check_achievements(user_id, new_score, new_streak, is_correct, difficulty, new_level)
    
    return jsonify({
        'is_correct': is_correct,
        'feedback_text': feedback_text,
        'correct_answer': correct_answer,
        'points_earned': points_earned,
        'xp_earned': xp_earned,
        'total_score': new_score,
        'current_streak': new_streak,
        'level': new_level,
        'xp': new_xp,
        'new_achievements': new_achievements
    })

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
