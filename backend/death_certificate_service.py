"""
Death Certificate Service for Life Insurance Claims Training
Generates realistic death certificate PDFs with controllable errors
"""
import os
import base64
import random
from pathlib import Path
from datetime import datetime, timedelta
from pdf_generator import DeathCertificateGenerator

class DeathCertificateService:
    def __init__(self):
        self.pdf_generator = DeathCertificateGenerator()
        self.error_scenarios = [
            {
                'type': 'name_mismatch',
                'description': 'Name on certificate does not match policy holder',
                'severity': 'critical'
            },
            {
                'type': 'date_inconsistency',
                'description': 'Death date is before policy effective date',
                'severity': 'critical'
            },
            {
                'type': 'missing_signature',
                'description': 'Required physician signature is missing',
                'severity': 'high'
            },
            {
                'type': 'invalid_cause_code',
                'description': 'Cause of death code is invalid or incomplete',
                'severity': 'medium'
            },
            {
                'type': 'jurisdiction_mismatch',
                'description': 'Certificate issued in wrong state/jurisdiction',
                'severity': 'medium'
            },
            {
                'type': 'age_mismatch',
                'description': 'Age on certificate does not match policy records',
                'severity': 'high'
            },
            {
                'type': 'state_mismatch',
                'description': 'State of residence does not match policy',
                'severity': 'medium'
            },
            {
                'type': 'expired_certification',
                'description': 'Medical examiner certification has expired',
                'severity': 'high'
            }
        ]
    
    def generate_scenario(self, difficulty='medium', client_profile=None):
        """Generate a death certificate review scenario"""
        # Generate policy data from client profile if provided
        if client_profile:
            policy_data = self._generate_policy_from_client(client_profile)
        else:
            policy_data = self._generate_policy_data()
        
        # Determine if scenario has errors
        has_errors = random.choice([True, False])
        
        # Select errors based on difficulty
        errors = []
        error_types = []
        if has_errors:
            num_errors = {'easy': 1, 'medium': 2, 'hard': 3}.get(difficulty, 2)
            errors = random.sample(self.error_scenarios, min(num_errors, len(self.error_scenarios)))
            error_types = [e['type'] for e in errors]
        
        # Generate PDF with errors
        pdf_bytes = self.pdf_generator.generate_certificate(policy_data, error_types)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return {
            'certificate_pdf': pdf_base64,
            'policy_data': policy_data,
            'has_errors': has_errors,
            'errors': error_types,
            'error_details': errors,
            'difficulty': difficulty
        }
    
    def _generate_policy_from_client(self, client_profile):
        """Generate policy data from client profile"""
        # Extract client info
        name = client_profile.get('name', f"{random.choice(['John', 'Mary'])} {random.choice(['Smith', 'Johnson'])}")
        state = client_profile.get('state', random.choice(['Florida', 'Texas', 'California']))
        age = client_profile.get('age', random.randint(50, 80))
        
        # Calculate dates
        birth_date = datetime.now() - timedelta(days=age * 365)
        policy_date = datetime.now() - timedelta(days=random.randint(365, 3650))
        death_date = datetime.now() - timedelta(days=random.randint(1, 180))
        
        return {
            'policy_number': f'LI-{random.randint(100000, 999999)}',
            'policy_holder': name,
            'policy_effective_date': policy_date.strftime('%Y-%m-%d'),
            'death_date': death_date.strftime('%Y-%m-%d'),
            'benefit_amount': random.choice([100000, 250000, 500000, 1000000]),
            'state': state,
            'age': age
        }
    
    def _generate_policy_data(self):
        """Generate realistic policy holder data"""
        first_names = ['John', 'Mary', 'Robert', 'Patricia', 'Michael', 'Jennifer']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia']
        
        policy_date = datetime.now() - timedelta(days=random.randint(365, 3650))
        death_date = datetime.now() - timedelta(days=random.randint(1, 180))
        
        return {
            'policy_number': f'LI-{random.randint(100000, 999999)}',
            'policy_holder': f'{random.choice(first_names)} {random.choice(last_names)}',
            'policy_effective_date': policy_date.strftime('%Y-%m-%d'),
            'death_date': death_date.strftime('%Y-%m-%d'),
            'benefit_amount': random.choice([100000, 250000, 500000, 1000000]),
            'state': random.choice(['Florida', 'Texas', 'California', 'New York'])
        }
    
    def validate_review(self, user_findings, actual_errors):
        """Validate user's certificate review"""
        user_set = set(user_findings)
        actual_set = set(actual_errors)
        
        true_positives = len(user_set & actual_set)
        false_positives = len(user_set - actual_set)
        false_negatives = len(actual_set - user_set)
        
        # Calculate score
        if not actual_errors and not user_findings:
            score = 100  # Correctly identified clean certificate
        elif not actual_errors:
            score = max(0, 100 - (false_positives * 20))  # Penalize false flags
        else:
            base_score = (true_positives / len(actual_errors)) * 100
            penalty = (false_positives * 10) + (false_negatives * 15)
            score = max(0, base_score - penalty)
        
        return {
            'score': round(score),
            'correct': user_set == actual_set,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'missed_errors': list(actual_set - user_set),
            'incorrect_flags': list(user_set - actual_set)
        }
    
    def get_error_options(self):
        """Get list of possible errors for UI checklist"""
        return [
            {'id': e['type'], 'label': e['description'], 'severity': e['severity']}
            for e in self.error_scenarios
        ]
