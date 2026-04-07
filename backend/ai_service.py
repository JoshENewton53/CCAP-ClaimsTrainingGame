"""
AI Service Module
Provides claim scenario generation, classification, and feedback functions
"""
import pickle
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "ai_models" / "models"
CLASSIFIER_PATH = MODELS_DIR / "claim_classifier.pkl"
GENERATOR_PATH = MODELS_DIR / "scenario_generator"

# Global model storage
_classifier = None
_encoders = None
_embedding_model = None
_generator_model = None
_generator_tokenizer = None
_flan_model = None
_flan_tokenizer = None

FLAN_MODEL_NAME = 'google/flan-t5-base'

def load_flan_t5():
    """Load Flan-T5 model for natural language feedback generation"""
    global _flan_model, _flan_tokenizer
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    print("Loading Flan-T5 model (downloads ~250MB on first run)...")
    _flan_tokenizer = T5Tokenizer.from_pretrained(FLAN_MODEL_NAME)
    _flan_model = T5ForConditionalGeneration.from_pretrained(FLAN_MODEL_NAME)
    print("Flan-T5 loaded successfully!")


def generate_flan_feedback(scenario, user_answer, correct_answer, rule_explanation):
    """Use Flan-T5 to generate natural language feedback for a claim decision"""
    global _flan_model, _flan_tokenizer
    if _flan_model is None or _flan_tokenizer is None:
        try:
            load_flan_t5()
        except Exception as e:
            print(f"[WARN] Flan-T5 lazy load failed: {e}")
            return None
    if _flan_model is None or _flan_tokenizer is None:
        return None

    is_correct = user_answer.lower() == correct_answer.lower()
    claim_type = scenario.get('claim_type', 'medical')
    procedure = scenario.get('procedure_code', '')
    diagnosis = scenario.get('diagnosis_code', '')
    amount = scenario.get('claim_amount', 0)

    prompt = (
        "You are an insurance claims training assistant.\n"
        f"Claim type: {claim_type}\n"
        f"Procedure: {procedure}\n"
        f"Diagnosis: {diagnosis}\n"
        f"Amount: ${amount:.2f}\n"
        f"Trainee answer: {user_answer}\n"
        f"Correct answer: {correct_answer}\n"
        f"Key finding: {rule_explanation}\n\n"
        "Task: Write 2-3 sentences of educational feedback for the trainee.\n"
        "Constraints: Do NOT repeat the prompt or instructions. Return ONLY the feedback text.\n"
        "Feedback:"
    )

    try:
        inputs = _flan_tokenizer(prompt, return_tensors='pt', max_length=300, truncation=True)
        outputs = _flan_model.generate(
            **inputs,
            max_new_tokens=120,
            do_sample=True,
            top_p=0.9,
            temperature=0.7,
            repetition_penalty=1.2,
        )
        text = _flan_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        # Guard: if the model echoes instructions/prompt, don't show it to the user.
        lower = text.lower()
        if (
            "in 2-3 sentences" in lower
            or "do not repeat the prompt" in lower
            or "return only the feedback text" in lower
            or "key finding:" in lower
            or lower.startswith("you are an insurance claims training assistant")
        ):
            return None

        # Keep it short and clean (2-3 sentences max).
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        if len(sentences) > 3:
            text = ". ".join(sentences[:3]).strip() + "."
        elif sentences and not text.endswith("."):
            text = text + "."

        # Too short/empty? Fall back to deterministic rule explanation.
        if len(text) < 20:
            return None

        return text
    except Exception as e:
        print(f"Flan-T5 inference error: {e}")
        return None


def load_models():
    """Load all AI models on startup"""
    global _classifier, _encoders, _embedding_model, _generator_model, _generator_tokenizer
    
    if not CLASSIFIER_PATH.exists():
        raise FileNotFoundError(f"Classifier not found at {CLASSIFIER_PATH}")
    if not GENERATOR_PATH.exists():
        raise FileNotFoundError(f"Generator not found at {GENERATOR_PATH}")
    
    print("Loading classifier model...")
    with open(CLASSIFIER_PATH, 'rb') as f:
        data = pickle.load(f)
        _classifier = data['model']
        _encoders = data['encoders']
        _embedding_model = data.get('embedding_model')
    
    print("Loading generator model...")
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    _generator_model = GPT2LMHeadModel.from_pretrained(str(GENERATOR_PATH))
    _generator_tokenizer = GPT2Tokenizer.from_pretrained(str(GENERATOR_PATH))
    
    print("Models loaded successfully!")

def generate_scenario(claim_type, difficulty):
    """Generate a realistic claim scenario with AI-written description"""
    scenario = generate_fallback_scenario(claim_type, difficulty)
    # Try Flan-T5 for description; Claude story generation happens later in the
    # endpoint AFTER the client profile is attached so it has the real name.
    ai_desc = generate_scenario_description(scenario)
    if ai_desc:
        scenario['description'] = ai_desc
    return scenario


# Procedure/diagnosis human-readable labels for richer prompts
_PROCEDURE_LABELS = {
    # Medical
    '99213': 'office visit (established patient, moderate complexity)',
    '99214': 'office visit (established patient, high complexity)',
    '99215': 'office visit (established patient, comprehensive)',
    '99223': 'initial hospital care (high complexity)',
    '99232': 'subsequent hospital care',
    '45378': 'diagnostic colonoscopy',
    '99291': 'critical care (first hour)',
    '99292': 'critical care (additional 30 min)',
    '33533': 'coronary artery bypass graft',
    # Dental
    'D1110': 'adult prophylaxis (teeth cleaning)',
    'D2140': 'amalgam filling (one surface)',
    'D0120': 'periodic oral evaluation',
    'D2750': 'crown (porcelain fused to metal)',
    'D7210': 'surgical extraction of erupted tooth',
    'D4910': 'periodontal maintenance',
    'D6010': 'endosteal implant',
    'D7953': 'bone replacement graft',
    'D4267': 'guided tissue regeneration',
}

_DIAGNOSIS_LABELS = {
    'Z00.00': 'routine general medical exam',
    'I10': 'essential hypertension',
    'E78.5': 'hyperlipidemia',
    'K92.2': 'gastrointestinal hemorrhage',
    'N39.0': 'urinary tract infection',
    'M17.11': 'primary osteoarthritis of right knee',
    'I46.9': 'cardiac arrest',
    'K85.9': 'acute pancreatitis',
    'S72.001A': 'femur fracture',
    'K02.9': 'dental caries',
    'K05.10': 'chronic gingivitis',
    'K04.7': 'periapical abscess',
    'K04.5': 'chronic apical periodontitis',
    'K08.101': 'complete tooth loss',
    'K07.30': 'jaw deformity',
    'K07.25': 'skeletal malocclusion',
    'K10.21': 'osteitis of jaw',
    'K05.31': 'aggressive periodontitis',
}


def generate_scenario_description(scenario):
    """Use Flan-T5 to write a unique scenario description from structured facts."""
    global _flan_model, _flan_tokenizer
    if _flan_model is None or _flan_tokenizer is None:
        return None

    claim_type = scenario['claim_type']
    difficulty = scenario['difficulty']
    procedure = scenario['procedure_code']
    diagnosis = scenario['diagnosis_code']
    amount = scenario['claim_amount']
    age = scenario['patient_age']

    proc_label = _PROCEDURE_LABELS.get(procedure, procedure)
    diag_label = _DIAGNOSIS_LABELS.get(diagnosis, diagnosis)

    # Life insurance uses a different prompt shape
    if claim_type == 'life':
        complexity = {
            'easy': 'straightforward with clear documentation',
            'medium': 'with a complicating factor such as a pre-existing condition or incomplete records',
            'hard': 'with suspicious circumstances or potential fraud indicators',
        }[difficulty]
        prompt = (
            f"Write a 2-sentence insurance claim note for a life insurance death benefit claim. "
            f"The policyholder was {age} years old. The claim is {complexity}. "
            f"Claim amount: ${amount:,.0f}. "
            f"Write only the claim note, no headings or labels."
        )
    else:
        complexity = {
            'easy': 'routine and straightforward',
            'medium': 'moderately complex',
            'hard': 'complex with potential red flags',
        }[difficulty]
        prompt = (
            f"Write a 2-sentence insurance claim note for a {claim_type} claim. "
            f"Patient age: {age}. Procedure: {proc_label} ({procedure}). "
            f"Diagnosis: {diag_label} ({diagnosis}). "
            f"Claim amount: ${amount:,.2f}. Complexity: {complexity}. "
            f"Write only the claim note, no headings or labels."
        )

    try:
        inputs = _flan_tokenizer(
            prompt, return_tensors='pt', max_length=200, truncation=True
        )
        outputs = _flan_model.generate(
            **inputs,
            max_new_tokens=80,
            num_beams=4,
            no_repeat_ngram_size=3,
            early_stopping=True,
        )
        text = _flan_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        # Reject if too short, echoes the prompt, or contains instruction artifacts
        lower = text.lower()
        if (
            len(text) < 30
            or 'write a' in lower
            or 'claim note' in lower
            or 'no headings' in lower
            or text.startswith('{')
        ):
            return None

        # Trim to 2 sentences max
        sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
        if len(sentences) > 2:
            text = '. '.join(sentences[:2]) + '.'
        elif sentences and not text.endswith('.'):
            text += '.'

        print(f"[Flan-T5] Generated description: {text}")
        return text
    except Exception as e:
        print(f"[Flan-T5] Description generation error: {e}")
        return None

def extract_clean_description(generated_text, original_prompt):
    """Extract and clean the AI-generated description"""
    import re
    
    # Remove the original prompt from the generated text
    description = generated_text.replace(original_prompt, "").strip()
    
    # Remove any training artifacts or repeated patterns
    description = re.sub(r'(Generate|Claim Type|Procedure|Diagnosis|Amount|Age|Status).*', '', description, flags=re.IGNORECASE)
    description = re.sub(r'\$[0-9,]+', '', description)  # Remove dollar amounts
    description = re.sub(r'[A-Z0-9]{3,}', '', description)  # Remove codes
    description = re.sub(r'Age: [0-9]+', '', description)  # Remove age references
    
    # Clean up whitespace and formatting
    description = re.sub(r'\s+', ' ', description).strip()
    description = re.sub(r'^[^A-Za-z]*', '', description)  # Remove leading non-letters
    
    # Split into sentences and take first 1-3
    sentences = [s.strip() for s in description.split('.') if s.strip()]
    if sentences:
        description = '. '.join(sentences[:3]) + '.'
    
    # Fallback if description is too short or empty
    if len(description) < 20:
        fallback_descriptions = {
            'medical': "Patient presented for routine examination with standard vital signs assessment.",
            'dental': "Patient received routine dental cleaning and oral health evaluation.",
            'life': "Policyholder death claim submitted with standard documentation review."
        }
        # Try to determine claim type from context
        if 'dental' in description.lower():
            description = fallback_descriptions['dental']
        elif 'death' in description.lower() or 'policy' in description.lower():
            description = fallback_descriptions['life']
        else:
            description = fallback_descriptions['medical']
    
    return description

def generate_structured_scenario(claim_type, difficulty, ai_description):
    """Generate structured scenario data with AI description"""
    import random
    
    # Realistic defaults based on claim type and difficulty
    defaults = {
        'medical': {
            'easy': {
                'procedures': ['99213', '99214', '99215'],
                'diagnoses': ['Z00.00', 'I10', 'E78.5'],
                'amounts': (150, 800)
            },
            'medium': {
                'procedures': ['99223', '99232', '45378'],
                'diagnoses': ['K92.2', 'N39.0', 'M17.11'],
                'amounts': (800, 3000)
            },
            'hard': {
                'procedures': ['99291', '99292', '33533'],
                'diagnoses': ['I46.9', 'K85.9', 'S72.001A'],
                'amounts': (5000, 25000)
            }
        },
        'dental': {
            'easy': {
                'procedures': ['D1110', 'D2140', 'D0120'],
                'diagnoses': ['K02.9', 'K05.10', 'K04.7'],
                'amounts': (80, 400)
            },
            'medium': {
                'procedures': ['D2750', 'D7210', 'D4910'],
                'diagnoses': ['K04.5', 'K08.101', 'K07.30'],
                'amounts': (400, 1500)
            },
            'hard': {
                'procedures': ['D6010', 'D7953', 'D4267'],
                'diagnoses': ['K07.25', 'K10.21', 'K05.31'],
                'amounts': (1500, 8000)
            }
        },
        'life': {
            'easy': {
                'procedures': ['death_benefit'],
                'diagnoses': ['natural_death'],
                'amounts': (50000, 250000)
            },
            'medium': {
                'procedures': ['death_benefit'],
                'diagnoses': ['undisclosed_condition'],
                'amounts': (100000, 500000)
            },
            'hard': {
                'procedures': ['death_benefit'],
                'diagnoses': ['suspicious_death'],
                'amounts': (250000, 1000000)
            }
        }
    }
    
    template = defaults[claim_type][difficulty]
    
    return {
        "claim_type": claim_type,
        "difficulty": difficulty,
        "procedure_code": random.choice(template['procedures']),
        "diagnosis_code": random.choice(template['diagnoses']),
        "claim_amount": round(random.uniform(*template['amounts']), 2),
        "patient_age": random.randint(25, 75),
        "description": ai_description
    }

def generate_fallback_scenario(claim_type, difficulty):
    """Fallback scenario generation when AI is unavailable"""
    import random
    import json
    import os
    
    # Load valid code mappings
    try:
        reference_file = os.path.join(os.path.dirname(__file__), 'reference_data', 'code_mappings.json')
        with open(reference_file, 'r') as f:
            code_mappings = json.load(f)
    except:
        code_mappings = {}
    
    # Realistic descriptions by type and difficulty
    descriptions = {
        'medical': {
            'easy': [
                "Patient presented for routine annual physical examination. Vital signs stable, no acute concerns noted.",
                "Follow-up visit for hypertension management. Blood pressure well controlled on current medications.",
                "Preventive care visit with routine screening labs and immunization updates."
            ],
            'medium': [
                "Patient admitted for chest pain evaluation. EKG and cardiac enzymes ordered for further assessment.",
                "Colonoscopy performed for routine screening. Multiple small polyps removed and sent for pathology.",
                "MRI of knee shows meniscal tear. Patient reports ongoing pain and limited mobility."
            ],
            'hard': [
                "Emergency surgery for acute appendicitis with complications. Extended operative time required.",
                "Critical care management of septic shock patient. Multiple organ support initiated.",
                "Complex cardiac procedure with unexpected findings requiring additional intervention."
            ]
        },
        'dental': {
            'easy': [
                "Routine dental cleaning and examination performed. No cavities detected, oral hygiene counseling provided.",
                "Single surface composite filling placed on posterior tooth. Local anesthesia administered without complications.",
                "Periodontal maintenance therapy completed. Gum health stable with continued home care."
            ],
            'medium': [
                "Crown preparation and temporary placement following root canal therapy. Permanent crown to be placed in two weeks.",
                "Surgical extraction of impacted wisdom tooth. Post-operative care instructions provided.",
                "Deep scaling and root planing performed under local anesthesia. Follow-up scheduled in three months."
            ],
            'hard': [
                "Full mouth reconstruction with multiple implant placements. Bone grafting required for adequate support.",
                "Complex oral surgery for cyst removal. Biopsy specimen sent for pathological examination.",
                "Advanced periodontal surgery with guided tissue regeneration. Multiple quadrants treated simultaneously."
            ]
        },
        'life': {
            'easy': [
                "Policyholder died of natural causes at age 72. Death certificate indicates heart failure as primary cause.",
                "Accidental death claim following motor vehicle accident. Police report and autopsy results available.",
                "Terminal illness claim for cancer patient. Medical records document diagnosis six months prior to death."
            ],
            'medium': [
                "Death occurred 18 months after policy issuance. Suicide listed as cause, but exclusion period has expired.",
                "Policyholder death with undisclosed pre-existing condition. Medical records show prior cardiac history.",
                "Claim submitted with incomplete beneficiary documentation. Additional verification required."
            ],
            'hard': [
                "Large policy claim with suspicious circumstances. Death occurred during contestable period requiring investigation.",
                "Multiple recent policy changes prior to death. Beneficiary behavior raises concerns about potential fraud.",
                "Death under questionable circumstances. Police investigation ongoing, autopsy results pending."
            ]
        }
    }
    
    # Get appropriate description
    desc_list = descriptions.get(claim_type, {}).get(difficulty, ["Standard claim scenario requiring review."])
    description = random.choice(desc_list)
    
    # Generate codes from reference data
    if claim_type in code_mappings and code_mappings[claim_type]:
        # Select random procedure from reference data
        procedure_mapping = random.choice(code_mappings[claim_type])
        procedure_code = procedure_mapping['procedure_code']
        
        # Randomly decide if this should be valid or invalid based on difficulty
        should_be_invalid = (difficulty == 'easy' and random.random() < 0.2) or \
                           (difficulty == 'medium' and random.random() < 0.4) or \
                           (difficulty == 'hard' and random.random() < 0.6)
        
        if should_be_invalid:
            # Pick a diagnosis code that doesn't match
            all_diagnosis_codes = set()
            for mapping in code_mappings[claim_type]:
                all_diagnosis_codes.update(mapping['valid_diagnosis_codes'])
            invalid_codes = all_diagnosis_codes - set(procedure_mapping['valid_diagnosis_codes'])
            diagnosis_code = random.choice(list(invalid_codes)) if invalid_codes else random.choice(procedure_mapping['valid_diagnosis_codes'])
        else:
            # Pick a valid diagnosis code
            diagnosis_code = random.choice(procedure_mapping['valid_diagnosis_codes'])
    else:
        # Fallback for life insurance or missing data
        defaults = {
            'medical': {'procedures': ['99213'], 'diagnoses': ['I10']},
            'dental': {'procedures': ['D1110'], 'diagnoses': ['K02.9']},
            'life': {'procedures': ['death_benefit'], 'diagnoses': ['natural_death']}
        }
        template = defaults.get(claim_type, defaults['medical'])
        procedure_code = random.choice(template['procedures'])
        diagnosis_code = random.choice(template['diagnoses'])
    
    # Amount ranges by difficulty
    amount_ranges = {
        'medical': {'easy': (150, 800), 'medium': (800, 3000), 'hard': (5000, 25000)},
        'dental': {'easy': (80, 400), 'medium': (400, 1500), 'hard': (1500, 8000)},
        'life': {'easy': (50000, 250000), 'medium': (100000, 500000), 'hard': (250000, 1000000)}
    }
    
    amount_range = amount_ranges.get(claim_type, {}).get(difficulty, (100, 1000))
    
    return {
        "claim_type": claim_type,
        "difficulty": difficulty,
        "procedure_code": procedure_code,
        "diagnosis_code": diagnosis_code,
        "claim_amount": round(random.uniform(*amount_range), 2),
        "patient_age": random.randint(25, 75),
        "description": description
    }

def parse_generated_scenario(text, claim_type, difficulty):
    """Parse generated text into structured scenario"""
    lines = text.split('\n')
    scenario = {
        "claim_type": claim_type,
        "difficulty": difficulty,
        "procedure_code": "99213",
        "diagnosis_code": "E11.9",
        "claim_amount": 1500.00,
        "patient_age": 45,
        "description": text,
        "red_flags": []
    }
    
    # Extract values from generated text
    for line in lines:
        if "Procedure:" in line:
            scenario["procedure_code"] = line.split(":")[-1].strip()
        elif "Diagnosis:" in line:
            scenario["diagnosis_code"] = line.split(":")[-1].strip()
        elif "Amount:" in line:
            amount_str = line.split("$")[-1].strip().replace(",", "")
            try:
                scenario["claim_amount"] = float(amount_str)
            except:
                pass
        elif "Patient Age:" in line or "Age:" in line:
            age_str = line.split(":")[-1].strip().split()[0]
            try:
                scenario["patient_age"] = int(age_str)
            except:
                pass
    
    # Randomly assign outcome (valid, insufficient, invalid)
    import random
    outcome = random.choice(['valid', 'insufficient', 'invalid'])
    
    # Add claim-specific details based on type, difficulty, and outcome
    if claim_type == 'medical':
        if outcome == 'invalid':
            if difficulty == 'easy':
                scenario['prior_authorization'] = 'No'
                scenario['diagnosis_matches'] = False
                scenario['out_of_network'] = 'Yes'
                scenario['missing_docs'] = 'Medical records'
                scenario['red_flags'] = ['Missing prior authorization', 'Diagnosis mismatch', 'Out of network', 'Missing medical records']
            elif difficulty == 'medium':
                scenario['prior_authorization'] = 'No'
                scenario['out_of_network'] = 'Yes'
                scenario['red_flags'] = ['Missing prior authorization', 'Out of network provider']
            else:  # hard
                scenario['diagnosis_matches'] = False
                scenario['red_flags'] = ['Subtle diagnosis mismatch']
        elif outcome == 'insufficient':
            if difficulty == 'easy':
                scenario['missing_docs'] = 'Medical records'
                scenario['prior_authorization'] = 'Pending'
                scenario['red_flags'] = ['Missing medical records', 'Authorization pending']
            elif difficulty == 'medium':
                scenario['missing_docs'] = 'Referral letter'
                scenario['red_flags'] = ['Missing referral letter']
            else:  # hard
                scenario['prior_authorization'] = 'Pending'
                scenario['red_flags'] = ['Authorization pending verification']
        else:  # valid
            scenario['prior_authorization'] = 'Yes'
            scenario['diagnosis_matches'] = True
            scenario['out_of_network'] = 'No'
            scenario['missing_docs'] = 'None'
            scenario['red_flags'] = []
            
    elif claim_type == 'dental':
        if outcome == 'invalid':
            if difficulty == 'easy':
                scenario['xray_attached'] = 'No'
                scenario['treatment_approved'] = 'No'
                scenario['tooth_recently_treated'] = 'Yes'
                scenario['red_flags'] = ['Missing X-rays', 'No treatment approval', 'Recently treated', 'Excessive amount']
            elif difficulty == 'medium':
                scenario['tooth_recently_treated'] = 'Yes'
                scenario['treatment_approved'] = 'No'
                scenario['red_flags'] = ['Recently treated', 'No treatment approval']
            else:  # hard
                scenario['tooth_recently_treated'] = 'Yes'
                scenario['red_flags'] = ['Possible duplicate treatment']
        elif outcome == 'insufficient':
            if difficulty == 'easy':
                scenario['xray_attached'] = 'No'
                scenario['missing_docs'] = 'X-rays'
                scenario['red_flags'] = ['Missing required X-rays', 'Missing documentation']
            elif difficulty == 'medium':
                scenario['missing_docs'] = 'Treatment notes'
                scenario['red_flags'] = ['Missing treatment notes']
            else:  # hard
                scenario['treatment_approved'] = 'Pending'
                scenario['red_flags'] = ['Treatment approval pending']
        else:  # valid
            scenario['xray_attached'] = 'Yes'
            scenario['treatment_approved'] = 'Yes'
            scenario['tooth_recently_treated'] = 'No'
            scenario['red_flags'] = []
            
    elif claim_type == 'life':
        if outcome == 'invalid':
            if difficulty == 'easy':
                scenario['policy_duration'] = 2
                scenario['premium_current'] = 'No'
                scenario['exclusions'] = 'Suicide clause'
                scenario['contestability'] = True
                scenario['red_flags'] = ['Policy only 2 months old', 'Premiums not current', 'Suicide exclusion applies', 'Within contestability']
            elif difficulty == 'medium':
                scenario['policy_duration'] = 18
                scenario['premium_current'] = 'Grace period'
                scenario['exclusions'] = 'Pre-existing condition'
                scenario['red_flags'] = ['Pre-existing condition exclusion', 'Premiums in grace period']
            else:  # hard
                scenario['exclusions'] = 'Pre-existing condition'
                scenario['red_flags'] = ['Subtle pre-existing condition issue']
        elif outcome == 'insufficient':
            if difficulty == 'easy':
                scenario['missing_docs'] = 'Death certificate'
                scenario['premium_current'] = 'Grace period'
                scenario['red_flags'] = ['Missing death certificate', 'Premium status unclear']
            elif difficulty == 'medium':
                scenario['missing_docs'] = 'Medical records'
                scenario['red_flags'] = ['Missing medical records']
            else:  # hard
                scenario['missing_docs'] = 'Police report'
                scenario['red_flags'] = ['Police report needed for verification']
        else:  # valid
            scenario['policy_duration'] = 60
            scenario['premium_current'] = 'Yes'
            scenario['exclusions'] = 'None'
            scenario['contestability'] = False
            scenario['red_flags'] = []
    
    return scenario

def classify_claim(scenario_data):
    """Classify a claim using business rules with AI confidence scoring"""
    # Critical business rules - these ALWAYS determine the outcome
    if not validate_age_matching(scenario_data):
        return {
            "prediction": "invalid",
            "confidence": 1.0,
            "probabilities": {"valid": 0.0, "invalid": 1.0, "insufficient": 0.0},
            "ai_reasoning": "Age mismatch detected by validation rules",
            "source": "rules_only"
        }
    
    if not validate_injury_date(scenario_data):
        return {
            "prediction": "invalid",
            "confidence": 1.0,
            "probabilities": {"valid": 0.0, "invalid": 1.0, "insufficient": 0.0},
            "ai_reasoning": "Pre-existing condition detected",
            "source": "rules_only"
        }
    
    if not validate_code_matching(scenario_data):
        return {
            "prediction": "invalid",
            "confidence": 1.0,
            "probabilities": {"valid": 0.0, "invalid": 1.0, "insufficient": 0.0},
            "ai_reasoning": "Procedure-diagnosis code mismatch",
            "source": "rules_only"
        }
    
    doc_status = scenario_data.get('document_status', {})
    missing_docs = doc_status.get('missing', [])
    if has_missing_critical_documents(scenario_data['claim_type'], missing_docs):
        return {
            "prediction": "insufficient",
            "confidence": 1.0,
            "probabilities": {"valid": 0.0, "invalid": 0.0, "insufficient": 1.0},
            "ai_reasoning": "Critical documents missing",
            "source": "rules_only"
        }
    
    # Use AI classifier for confidence scoring and reasoning
    if _classifier is not None and _encoders is not None:
        try:
            # Check for unseen labels before transforming - LabelEncoder throws on unknown values
            known_claim_types = set(_encoders['claim_type'].classes_)
            known_procedures = set(_encoders['procedure_code'].classes_)
            known_diagnoses = set(_encoders['diagnosis_code'].classes_)

            if (scenario_data['claim_type'] not in known_claim_types or
                    scenario_data['procedure_code'] not in known_procedures or
                    scenario_data['diagnosis_code'] not in known_diagnoses):
                print(f"[AI] Unseen label in scenario, skipping ML classifier")
                return classify_with_rules(scenario_data)

            claim_type_enc = _encoders['claim_type'].transform([scenario_data['claim_type']])[0]
            procedure_code_enc = _encoders['procedure_code'].transform([scenario_data['procedure_code']])[0]
            diagnosis_code_enc = _encoders['diagnosis_code'].transform([scenario_data['diagnosis_code']])[0]

            structured = np.array([[
                scenario_data['claim_amount'],
                scenario_data['patient_age'],
                claim_type_enc,
                procedure_code_enc,
                diagnosis_code_enc
            ]])

            # Build hybrid features matching training: structured + sentence embeddings
            if _embedding_model is not None:
                text = (
                    f"{scenario_data['claim_type']} claim for {scenario_data['procedure_code']} "
                    f"diagnosis {scenario_data['diagnosis_code']} "
                    f"amount ${scenario_data['claim_amount']} age {scenario_data['patient_age']}"
                )
                embedding = _embedding_model.encode([text])
                features = np.hstack([structured, embedding])
            else:
                features = structured
            
            # Get AI prediction and confidence
            prediction = _classifier.predict(features)[0]
            probabilities = _classifier.predict_proba(features)[0]
            predicted_label = _encoders['label'].inverse_transform([prediction])[0]
            
            class_probs = {
                label: float(prob) 
                for label, prob in zip(_encoders['label'].classes_, probabilities)
            }
            
            # Generate AI reasoning
            ai_reasoning = generate_ai_reasoning(scenario_data, predicted_label, class_probs)
            
            print(f"[AI] Classification: {predicted_label} (confidence: {max(probabilities):.2%})")
            
            return {
                "prediction": predicted_label,
                "confidence": float(max(probabilities)),
                "probabilities": class_probs,
                "ai_reasoning": ai_reasoning,
                "source": "ml_with_rules_audit"
            }
        except Exception as e:
            print(f"AI classification error: {e}")
    
    # Fallback to rule-based
    return classify_with_rules(scenario_data)

def validate_code_matching(scenario_data):
    """Validate procedure code matches diagnosis code"""
    import json
    import os
    
    claim_type = scenario_data['claim_type']
    procedure_code = scenario_data['procedure_code']
    diagnosis_code = scenario_data['diagnosis_code']
    
    # Skip validation for life insurance
    if claim_type == 'life':
        return True
    
    try:
        reference_file = os.path.join(os.path.dirname(__file__), 'reference_data', 'code_mappings.json')
        with open(reference_file, 'r') as f:
            code_mappings = json.load(f)
        
        codes = code_mappings.get(claim_type, [])
        for mapping in codes:
            if mapping['procedure_code'] == procedure_code:
                return diagnosis_code in mapping['valid_diagnosis_codes']
        
        return False
    except Exception as e:
        print(f"Code validation error: {e}")
        return True

def validate_injury_date(scenario_data):
    """Validate injury date is after policy start date"""
    from datetime import datetime
    
    client_profile = scenario_data.get('client_profile')
    if not client_profile or 'injury_date' not in client_profile:
        return True
    
    try:
        injury_date = datetime.fromisoformat(client_profile['injury_date'])
        policy_start = datetime.fromisoformat(client_profile['policy_start_date'])
        
        return injury_date >= policy_start
    except Exception as e:
        print(f"Injury date validation error: {e}")
        return True

def has_missing_critical_documents(claim_type, missing_docs):
    """Check if any critical documents are missing"""
    critical_docs = {
        'medical': ['Patient medical records', 'Physician notes and diagnosis'],
        'dental': ['X-rays or diagnostic images', 'Treatment plan with CDT codes'],
        'life': ['Death certificate', 'Policy documents']
    }
    
    required = critical_docs.get(claim_type, [])
    for doc in required:
        if doc in missing_docs:
            return True
    return False

def validate_age_matching(scenario_data):
    """Validate patient age matches client profile age"""
    from datetime import datetime
    
    client_profile = scenario_data.get('client_profile')
    if not client_profile:
        return True
    
    claim_age = scenario_data.get('patient_age')
    if not claim_age:
        return True
    
    try:
        dob = datetime.fromisoformat(client_profile['date_of_birth'])
        today = datetime.now()
        profile_age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            profile_age -= 1
        
        return abs(claim_age - profile_age) <= 1
    except Exception as e:
        print(f"Age validation error: {e}")
        return True

def validate_ai_prediction(ai_prediction, scenario_data):
    """Validate AI prediction against business rules"""
    claim_type = scenario_data['claim_type']
    amount = scenario_data['claim_amount']
    age = scenario_data['patient_age']
    description = scenario_data.get('description', '')
    
    # Business rule overrides for obvious cases
    if "fraud" in description.lower() or "suspicious" in description.lower():
        return 'invalid'
    
    if "missing" in description.lower() or "incomplete" in description.lower():
        return 'insufficient'
    
    # High-value claims need investigation
    if claim_type == 'life' and amount > 500000:
        return 'insufficient'
    
    if claim_type == 'medical' and amount > 20000:
        return 'insufficient'
    
    # Return AI prediction if no business rule override
    return ai_prediction

def classify_with_rules(scenario_data):
    """Fallback classification using business rules when AI is unavailable"""
    import random

    difficulty = scenario_data['difficulty']
    description = scenario_data.get('description', '')

    if difficulty == 'easy':
        if "Issues" in description:
            prediction = random.choice(['valid', 'insufficient'])
        else:
            prediction = 'valid'
    elif difficulty == 'medium':
        if "Missing" in description or "Pre-authorization" in description:
            prediction = 'insufficient'
        elif "doesn't match" in description or "exceeds" in description:
            prediction = 'invalid'
        else:
            prediction = random.choice(['valid', 'insufficient'])
    else:  # hard
        if "fraud" in description.lower() or "lapsed" in description.lower():
            prediction = 'invalid'
        elif "Investigation" in description or "Duplicate" in description:
            prediction = 'insufficient'
        else:
            prediction = random.choice(['invalid', 'insufficient'])

    confidence = random.uniform(0.55, 0.75)

    # Build probabilities that reflect the prediction rather than flat 33/33/34
    remaining = 1.0 - confidence
    other_two = [k for k in ['valid', 'invalid', 'insufficient'] if k != prediction]
    split = round(remaining / 2, 4)
    probs = {prediction: round(confidence, 4), other_two[0]: split, other_two[1]: round(remaining - split, 4)}

    return {
        "prediction": prediction,
        "confidence": confidence,
        "probabilities": probs,
        "source": "rules_only_fallback"
    }

def generate_feedback(scenario, user_answer, correct_answer):
    """Generate AI-powered feedback based on user's answer"""
    is_correct = user_answer.lower() == correct_answer.lower()

    # Rule-based explanation is always computed as the authoritative fallback
    rule_explanation = generate_explanation(scenario, correct_answer)

    # Try Claude for richer, confidence-aware feedback
    claude_feedback = None
    try:
        from claude_service import generate_claim_feedback
        claude_feedback = generate_claim_feedback(scenario, user_answer, correct_answer, rule_explanation)
    except Exception as e:
        print(f"[Claude] Feedback skipped: {e}")

    if is_correct:
        message = "Correct! Well done!"
    else:
        message = "Incorrect."

    return {
        "is_correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "message": message,
        "explanation": claude_feedback if claude_feedback else rule_explanation,
    }

def generate_client_profile(scenario_data):
    """Generate client profile data with potential mismatches for training"""
    import random
    from datetime import datetime, timedelta
    
    # Generate realistic names
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Emily', 'James', 'Ashley']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    policy_number = f"POL-{random.randint(10000, 99999)}"
    
    # Calculate dates based on patient age
    patient_age = scenario_data['patient_age']
    today = datetime.now()
    
    # Determine if this should be a mismatch scenario
    should_mismatch = scenario_data['difficulty'] in ['medium', 'hard'] and random.random() < 0.4
    
    if should_mismatch:
        # Create age mismatch (5-10 years difference)
        age_difference = random.randint(5, 10)
        profile_age = patient_age + age_difference if random.random() < 0.5 else patient_age - age_difference
        profile_age = max(18, min(85, profile_age))  # Keep within reasonable bounds
    else:
        profile_age = patient_age
    
    # Calculate date of birth
    birth_year = today.year - profile_age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)  # Safe day for all months
    date_of_birth = datetime(birth_year, birth_month, birth_day)
    
    # Policy start date (1-5 years ago)
    years_ago = random.randint(1, 5)
    policy_start = today - timedelta(days=years_ago * 365 + random.randint(0, 365))
    
    # Generate injury/service date for medical and dental claims
    injury_date = None
    injury_date_mismatch = False
    if scenario_data['claim_type'] in ['medical', 'dental']:
        # Decide if injury date should be before policy start (fraud scenario)
        if scenario_data['difficulty'] in ['medium', 'hard'] and random.random() < 0.3:
            # Injury occurred BEFORE policy started
            days_before = random.randint(30, 365)
            injury_date = policy_start - timedelta(days=days_before)
            injury_date_mismatch = True
        else:
            # Normal: injury after policy start
            days_after = random.randint(30, 365)
            injury_date = policy_start + timedelta(days=days_after)
    
    # Coverage limits based on claim type
    coverage_limits = {
        'medical': [
            '$5,000 annual deductible',
            '$50,000 annual maximum',
            '$1M lifetime maximum',
            '$2,500 out-of-pocket max'
        ],
        'dental': [
            '$1,500 annual maximum',
            '$50 deductible per service',
            '$2,000 orthodontic lifetime',
            '$1,000 annual preventive'
        ],
        'life': [
            f'${scenario_data["claim_amount"]:,.0f} death benefit',
            '$50,000 accidental death',
            '2-year suicide clause',
            '2-year contestable period'
        ]
    }
    
    # Generate dependents for some profiles
    dependents = []
    if random.random() < 0.3:  # 30% chance of having dependents
        num_dependents = random.randint(1, 3)
        has_spouse = False
        for i in range(num_dependents):
            # Determine relationship (only one spouse allowed)
            if not has_spouse and random.random() < 0.3:
                relationship = 'Spouse'
                has_spouse = True
                # Spouse must be 18+ and within 5-10 years of client age
                age_diff = random.randint(-10, 10)
                dep_age = max(18, profile_age + age_diff)
            else:
                relationship = 'Child'
                dep_age = random.randint(5, 25)
            
            dep_birth_year = today.year - dep_age
            dep_name = f"{random.choice(first_names)} {last_names[-1]}"
            
            dependents.append({
                'name': dep_name,
                'relationship': relationship,
                'date_of_birth': datetime(dep_birth_year, random.randint(1, 12), random.randint(1, 28)).isoformat()
            })
    
    profile = {
        'name': name,
        'policy_number': policy_number,
        'date_of_birth': date_of_birth.isoformat(),
        'policy_start_date': policy_start.isoformat(),
        'coverage_type': scenario_data['claim_type'].title(),
        'coverage_limits': random.choice(coverage_limits[scenario_data['claim_type']]),
        'dependents': dependents,
        'has_mismatch': should_mismatch,
        'mismatch_type': 'age_mismatch' if should_mismatch else None
    }
    
    if injury_date:
        profile['injury_date'] = injury_date.isoformat()
        profile['injury_date_mismatch'] = injury_date_mismatch
    
    return profile

def generate_explanation(scenario, correct_answer):
    """Generate explanation for the correct answer"""
    import json
    import os
    from datetime import datetime
    
    # Check age mismatch first
    client_profile = scenario.get('client_profile')
    if client_profile:
        try:
            dob = datetime.fromisoformat(client_profile['date_of_birth'])
            today = datetime.now()
            profile_age = today.year - dob.year
            if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
                profile_age -= 1
            
            claim_age = scenario.get('patient_age')
            if claim_age and abs(claim_age - profile_age) > 1:
                return f"This claim is INVALID due to age mismatch. The claim lists patient age as {claim_age}, but the client profile shows age {profile_age} (DOB: {client_profile['date_of_birth'][:10]}). Age discrepancies over 1 year indicate potential fraud or data entry errors. Always verify patient age in the claim matches the calculated age from the Client Profile DOB."
        except:
            pass
    
    # Check injury date vs policy start (pre-existing condition)
    if client_profile and 'injury_date' in client_profile:
        try:
            injury_date = datetime.fromisoformat(client_profile['injury_date'])
            policy_start = datetime.fromisoformat(client_profile['policy_start_date'])
            
            if injury_date < policy_start:
                return f"This claim is INVALID due to pre-existing condition. The injury/service date ({injury_date.strftime('%Y-%m-%d')}) occurred BEFORE the policy start date ({policy_start.strftime('%Y-%m-%d')}). This indicates the patient was injured before obtaining coverage, which is not covered. Always compare the Date of Injury/Service in the Client Profile against the Policy Start Date."
        except:
            pass
    
    # Check code mismatch
    if scenario['claim_type'] in ['medical', 'dental']:
        try:
            reference_file = os.path.join(os.path.dirname(__file__), 'reference_data', 'code_mappings.json')
            with open(reference_file, 'r') as f:
                code_mappings = json.load(f)
            
            codes = code_mappings.get(scenario['claim_type'], [])
            for mapping in codes:
                if mapping['procedure_code'] == scenario['procedure_code']:
                    if scenario['diagnosis_code'] not in mapping['valid_diagnosis_codes']:
                        valid_codes = ', '.join(mapping['valid_diagnosis_codes'])
                        return f"This claim is INVALID due to procedure-diagnosis code mismatch. Procedure {scenario['procedure_code']} requires diagnosis codes: {valid_codes}. The claim shows {scenario['diagnosis_code']}, which is not valid. Use the 'View Code Reference' button to verify valid pairings before approving claims."
                    break
        except:
            pass
    
    # Check missing documents
    doc_status = scenario.get('document_status', {})
    missing_docs = doc_status.get('missing', [])
    
    # Check for missing critical documents
    critical_docs = {
        'medical': ['Patient medical records', 'Physician notes and diagnosis'],
        'dental': ['X-rays or diagnostic images', 'Treatment plan with CDT codes'],
        'life': ['Death certificate', 'Policy documents']
    }
    
    required = critical_docs.get(scenario['claim_type'], [])
    missing_critical = [doc for doc in required if doc in missing_docs]
    
    if correct_answer == 'insufficient' and missing_critical:
        missing_list = ', '.join(missing_critical)
        return f"This claim has INSUFFICIENT information. Missing CRITICAL documents: {missing_list}. These documents are mandatory and the claim cannot be processed without them. Check the Company Claims Policy (Acceptance tab) for critical document requirements by claim type."
    
    if correct_answer == 'insufficient' and missing_docs:
        missing_list = ', '.join(missing_docs)
        return f"This claim has INSUFFICIENT information. Missing documents: {missing_list}. Review the Document Status section and Company Claims Policy to identify what's needed."
    
    if correct_answer == 'valid':
        return f"This claim is VALID. Procedure {scenario['procedure_code']} correctly pairs with diagnosis {scenario['diagnosis_code']}, all CRITICAL documents are present, patient age matches the profile, and the amount ${scenario['claim_amount']:.2f} is reasonable. All validation checks passed."
    
    if correct_answer == 'invalid':
        return f"This claim is INVALID. Check: 1) Code Reference for valid procedure-diagnosis pairings, 2) Client Profile age vs claim age, 3) Policy exclusions and authorization requirements."

    if correct_answer == 'insufficient':
        return "This claim has INSUFFICIENT information. Review the Document Status section and ensure all required documents are present before processing."

    return f"This claim is {correct_answer.upper()}."

# Initialize models when module is imported
try:
    if CLASSIFIER_PATH.exists() and GENERATOR_PATH.exists():
        load_models()
        print("[OK] AI models loaded successfully")
    else:
        print("[WARN] AI models not found - using fallback mode")
        print(f"  Classifier path: {CLASSIFIER_PATH}")
        print(f"  Generator path: {GENERATOR_PATH}")
except Exception as e:
    print(f"[WARN] Warning: Could not load models: {e}")
    print("  Application will use fallback scenario generation")

try:
    load_flan_t5()
    print("[OK] Flan-T5 feedback model loaded successfully")
except Exception as e:
    print(f"[WARN] Could not load Flan-T5: {e}")
    print("  Feedback will use rule-based explanations")


def generate_ai_reasoning(scenario_data, prediction, probabilities):
    """Generate AI reasoning for classification decision"""
    claim_type = scenario_data['claim_type']
    amount = scenario_data['claim_amount']
    
    reasoning_parts = []
    
    # Analyze confidence levels
    confidence = probabilities.get(prediction, 0)
    if confidence > 0.8:
        reasoning_parts.append(f"High confidence ({confidence:.1%}) in {prediction} classification.")
    elif confidence > 0.6:
        reasoning_parts.append(f"Moderate confidence ({confidence:.1%}) in {prediction} classification.")
    else:
        reasoning_parts.append(f"Low confidence ({confidence:.1%}) - borderline case.")
    
    # Analyze amount
    if claim_type == 'medical' and amount > 10000:
        reasoning_parts.append("High claim amount detected.")
    elif claim_type == 'dental' and amount > 3000:
        reasoning_parts.append("Above-average dental claim amount.")
    elif claim_type == 'life' and amount > 500000:
        reasoning_parts.append("Large life insurance claim.")
    
    # Compare probabilities
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_probs) > 1:
        diff = sorted_probs[0][1] - sorted_probs[1][1]
        if diff < 0.2:
            reasoning_parts.append(f"Close call between {sorted_probs[0][0]} and {sorted_probs[1][0]}.")
    
    return " ".join(reasoning_parts)

def generate_ai_hint(scenario_data, user_attempts=0):
    """Generate scenario-specific hints without revealing the answer"""
    from datetime import datetime
    import json, os

    claim_type = scenario_data.get('claim_type', 'medical')
    client_profile = scenario_data.get('client_profile', {})
    doc_status = scenario_data.get('document_status', {})
    missing_docs = doc_status.get('missing', [])
    procedure_code = scenario_data.get('procedure_code', '')
    diagnosis_code = scenario_data.get('diagnosis_code', '')
    claim_age = scenario_data.get('patient_age')

    # Detect actual issues in the scenario
    issues = []

    # 1. Age mismatch
    if client_profile and claim_age:
        try:
            dob = datetime.fromisoformat(client_profile['date_of_birth'])
            today = datetime.now()
            profile_age = today.year - dob.year
            if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
                profile_age -= 1
            if abs(claim_age - profile_age) > 1:
                issues.append(('age', f"The claim lists the patient as {claim_age} years old. Compare that carefully with the date of birth in the Client Profile."))
        except Exception:
            pass

    # 2. Injury date before policy start
    if client_profile and 'injury_date' in client_profile:
        try:
            injury_date = datetime.fromisoformat(client_profile['injury_date'])
            policy_start = datetime.fromisoformat(client_profile['policy_start_date'])
            if injury_date < policy_start:
                issues.append(('date', f"Look at the Date of Injury/Service ({injury_date.strftime('%Y-%m-%d')}) and compare it to when the policy became active."))
        except Exception:
            pass

    # 3. Code mismatch
    if claim_type in ('medical', 'dental') and procedure_code and diagnosis_code:
        try:
            reference_file = os.path.join(os.path.dirname(__file__), 'reference_data', 'code_mappings.json')
            with open(reference_file, 'r') as f:
                code_mappings = json.load(f)
            for mapping in code_mappings.get(claim_type, []):
                if mapping['procedure_code'] == procedure_code:
                    if diagnosis_code not in mapping['valid_diagnosis_codes']:
                        issues.append(('codes', f"Procedure {procedure_code} is on the claim. Use the Code Reference to check which diagnosis codes are valid for that procedure."))
                    break
        except Exception:
            pass

    # 4. Missing critical documents
    critical_docs = {
        'medical': ['Patient medical records', 'Physician notes and diagnosis'],
        'dental': ['X-rays or diagnostic images', 'Treatment plan with CDT codes'],
        'life': ['Death certificate', 'Policy documents']
    }
    missing_critical = [d for d in critical_docs.get(claim_type, []) if d in missing_docs]
    if missing_critical:
        issues.append(('docs', f"Check the Document Status section — some items listed as missing may be required before this claim can move forward."))
    elif missing_docs:
        issues.append(('docs', f"There are {len(missing_docs)} document(s) listed as missing. Review whether any of them are required for this claim type."))

    # Return hints progressively based on attempts, cycling through detected issues
    if not issues:
        # No specific issues found — give generic progressive guidance
        generic = [
            "Start by reviewing the Client Profile and comparing it against the claim details.",
            "Check the Document Status — are all required documents present for this claim type?",
            "Use the Code Reference to verify the procedure and diagnosis codes are a valid pairing.",
            "Review the policy start date, patient age, and claim amount together for consistency."
        ]
        return [generic[min(user_attempts, len(generic) - 1)]]

    # On first attempt: give a directional hint toward the first issue area
    # On subsequent attempts: reveal more specific detail about each issue
    hint_index = min(user_attempts, len(issues) - 1)
    issue_type, specific_hint = issues[hint_index]

    area_intro = {
        'age': "Take a close look at the Client Profile.",
        'date': "Pay attention to the timeline of this claim.",
        'codes': "The procedure and diagnosis codes are worth a second look.",
        'docs': "The documentation for this claim needs attention."
    }

    if user_attempts == 0:
        return [area_intro.get(issue_type, "Review the claim details carefully.")]
    else:
        return [specific_hint]

def analyze_user_performance(user_history):
    """Use AI to analyze user performance and identify weak areas"""
    if not user_history or len(user_history) < 5:
        return {
            "overall_accuracy": 0.0,
            "weak_areas": [],
            "strong_areas": [],
            "recommendation": "Complete more scenarios for analysis"
        }
    
    # Calculate accuracy by claim type
    by_type = {}
    for attempt in user_history:
        claim_type = attempt.get('claim_type', 'unknown')
        is_correct = attempt.get('is_correct', False)
        
        if claim_type not in by_type:
            by_type[claim_type] = {'correct': 0, 'total': 0}
        
        by_type[claim_type]['total'] += 1
        if is_correct:
            by_type[claim_type]['correct'] += 1
    
    # Identify weak and strong areas
    weak_areas = []
    strong_areas = []
    
    for claim_type, stats in by_type.items():
        accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        if accuracy < 0.6:
            weak_areas.append(f"{claim_type} ({accuracy:.0%})")
        elif accuracy > 0.8:
            strong_areas.append(f"{claim_type} ({accuracy:.0%})")
    
    total_correct = sum(h.get('is_correct', False) for h in user_history)
    overall_accuracy = total_correct / len(user_history)
    
    # AI-generated recommendation
    if overall_accuracy < 0.5:
        recommendation = "Focus on understanding the Code Reference and Document Requirements."
    elif overall_accuracy < 0.7:
        recommendation = "Good progress! Pay attention to age verification and pre-existing conditions."
    else:
        recommendation = "Excellent work! Try harder difficulty levels to challenge yourself."
    
    return {
        "overall_accuracy": overall_accuracy,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas,
        "recommendation": recommendation,
        "total_attempts": len(user_history)
    }


def summarize_performance_with_flan(perf_result):
    """Use Flan-T5 to generate a natural-language study plan from performance stats."""
    global _flan_model, _flan_tokenizer
    if _flan_model is None or _flan_tokenizer is None:
        try:
            load_flan_t5()
        except Exception as e:
            print(f"[WARN] Flan-T5 load failed in summarize_performance_with_flan: {e}")
            return None
    if _flan_model is None or _flan_tokenizer is None:
        return None

    try:
        overall = perf_result.get("overall_accuracy", 0.0)
        weak = ", ".join(perf_result.get("weak_areas", [])) or "none"
        strong = ", ".join(perf_result.get("strong_areas", [])) or "none"
        recommendation = perf_result.get("recommendation", "")
        total = perf_result.get("total_attempts", 0)

        prompt = (
            "You are coaching a trainee insurance claims adjuster.\n"
            f"Total scenarios completed: {total}.\n"
            f"Overall accuracy: {overall:.0%}.\n"
            f"Weak areas: {weak}.\n"
            f"Strong areas: {strong}.\n"
            f"High-level recommendation: {recommendation}\n"
            "In 3-4 sentences, give a friendly, concrete study plan. "
            "Be specific about which claim types and concepts they should practice next, "
            "and keep the tone encouraging."
        )

        inputs = _flan_tokenizer(prompt, return_tensors='pt', max_length=300, truncation=True)
        outputs = _flan_model.generate(
            **inputs,
            max_new_tokens=160,
            num_beams=4,
            temperature=0.7,
            repetition_penalty=1.2,
        )
        return _flan_tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print(f"[WARN] Flan-T5 performance summary error: {e}")
        return None
