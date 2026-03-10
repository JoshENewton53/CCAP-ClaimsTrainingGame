import random
from datetime import datetime, timedelta

class ItemizedBillService:
    def __init__(self):
        self.medical_procedures = {
            '99213': {'name': 'Office Visit - Established Patient', 'cost_range': (75, 150)},
            '99214': {'name': 'Office Visit - Complex', 'cost_range': (150, 250)},
            '99285': {'name': 'Emergency Department Visit', 'cost_range': (300, 600)},
            '70450': {'name': 'CT Scan - Head', 'cost_range': (500, 1200)},
            '73721': {'name': 'MRI - Lower Extremity', 'cost_range': (800, 1500)},
            '80053': {'name': 'Comprehensive Metabolic Panel', 'cost_range': (50, 100)},
            '85025': {'name': 'Complete Blood Count', 'cost_range': (30, 75)},
            '36415': {'name': 'Blood Draw', 'cost_range': (15, 35)},
            '97110': {'name': 'Physical Therapy', 'cost_range': (75, 150)},
            '29881': {'name': 'Knee Arthroscopy', 'cost_range': (2000, 4000)}
        }
        
        self.dental_procedures = {
            'D0120': {'name': 'Periodic Oral Evaluation', 'cost_range': (50, 100)},
            'D0220': {'name': 'Intraoral X-ray', 'cost_range': (25, 60)},
            'D1110': {'name': 'Prophylaxis - Adult', 'cost_range': (75, 150)},
            'D2391': {'name': 'Resin Composite - One Surface', 'cost_range': (150, 250)},
            'D2740': {'name': 'Crown - Porcelain', 'cost_range': (800, 1500)},
            'D7140': {'name': 'Tooth Extraction', 'cost_range': (150, 350)},
            'D3310': {'name': 'Root Canal - Anterior', 'cost_range': (600, 1000)},
            'D4341': {'name': 'Periodontal Scaling', 'cost_range': (150, 300)}
        }
    
    def generate_bill(self, claim_type, procedure_code, claim_amount, difficulty, correct_answer):
        """Generate an itemized bill with potential errors based on difficulty"""
        
        if claim_type == 'medical':
            procedures = self.medical_procedures
        elif claim_type == 'dental':
            procedures = self.dental_procedures
        else:
            return None
        
        # Determine if bill should match claim amount
        # For invalid claims, occasionally mismatch (5% chance)
        should_mismatch = correct_answer == 'invalid' and random.random() < 0.05
        
        # Generate bill items
        items = []
        
        if should_mismatch:
            # Generate bill with different total than claim amount
            target_total = claim_amount * random.uniform(1.3, 2.0)
        else:
            # Match claim amount
            target_total = claim_amount
        
        # Add main procedure - ensure it exists
        main_proc = procedures.get(procedure_code)
        if not main_proc:
            # Fallback to first procedure if code not found
            procedure_code = list(procedures.keys())[0]
            main_proc = procedures[procedure_code]
        
        cost = target_total * random.uniform(0.4, 0.6)
        items.append({
            'code': procedure_code,
            'description': main_proc['name'],
            'quantity': 1,
            'unit_cost': round(cost, 2),
            'total': round(cost, 2)
        })
        
        # Add additional procedures to reach target total
        remaining = target_total - sum(item['total'] for item in items)
        other_codes = [code for code in procedures.keys() if code != procedure_code]
        num_additional = random.randint(1, 3)
        
        for i, code in enumerate(random.sample(other_codes, min(num_additional, len(other_codes)))):
            proc = procedures[code]
            if i == num_additional - 1:
                # Last item gets remaining amount
                cost = max(10, remaining)
            else:
                cost = remaining * random.uniform(0.2, 0.4)
            remaining -= cost
            items.append({
                'code': code,
                'description': proc['name'],
                'quantity': 1,
                'unit_cost': round(cost, 2),
                'total': round(cost, 2)
            })
        
        # Introduce errors based on difficulty
        errors = []
        has_error = False
        
        if difficulty == 'medium' and random.random() < 0.5:
            has_error = True
            error_type = random.choice(['wrong_code', 'math_error'])
            if error_type == 'wrong_code':
                # Change one code to incorrect
                idx = random.randint(0, len(items) - 1)
                wrong_code = random.choice(list(procedures.keys()))
                items[idx]['code'] = wrong_code
                errors.append(f"Incorrect CPT code: {wrong_code} does not match procedure")
            else:
                # Math error in total
                idx = random.randint(0, len(items) - 1)
                items[idx]['total'] = round(items[idx]['total'] * random.uniform(1.1, 1.5), 2)
                errors.append(f"Math error: Line item total does not match unit cost × quantity")
        
        elif difficulty == 'hard':
            has_error = True
            # Multiple errors
            num_errors = random.randint(1, 2)
            for _ in range(num_errors):
                error_type = random.choice(['wrong_code', 'math_error', 'duplicate'])
                if error_type == 'wrong_code':
                    idx = random.randint(0, len(items) - 1)
                    wrong_code = random.choice(list(procedures.keys()))
                    items[idx]['code'] = wrong_code
                    errors.append(f"Incorrect CPT code: {wrong_code}")
                elif error_type == 'math_error':
                    idx = random.randint(0, len(items) - 1)
                    items[idx]['total'] = round(items[idx]['total'] * random.uniform(1.2, 1.8), 2)
                    errors.append(f"Math error on line {idx + 1}")
                else:
                    # Duplicate charge
                    duplicate_item = random.choice(items).copy()
                    items.append(duplicate_item)
                    errors.append(f"Duplicate charge: {duplicate_item['code']}")
        
        # Calculate final total
        bill_total = sum(item['total'] for item in items)
        
        # Generate bill metadata
        service_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        return {
            'items': items,
            'subtotal': round(bill_total, 2),
            'tax': 0,
            'total': round(bill_total, 2),
            'service_date': service_date.strftime('%Y-%m-%d'),
            'provider': 'Medical Center' if claim_type == 'medical' else 'Dental Clinic',
            'has_errors': has_error,
            'errors': errors
        }
