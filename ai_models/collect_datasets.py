"""
Insurance Claims Dataset Collection Script
Downloads and processes medical, dental, and life insurance claims datasets
"""
import os
import pandas as pd
import numpy as np
import requests
from pathlib import Path

DATASETS_DIR = Path(__file__).parent.parent / "datasets"
RAW_DIR = DATASETS_DIR / "raw"
DATASETS_DIR.mkdir(exist_ok=True)
RAW_DIR.mkdir(exist_ok=True)

def download_cms_medicare_claims():
    """Download CMS Medicare claims sample data"""
    print("Downloading CMS Medicare claims data...")
    
    # Try to download real medical insurance data
    try:
        url = "https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/master/insurance.csv"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            raw_path = RAW_DIR / "medical_insurance_raw.csv"
            with open(raw_path, 'wb') as f:
                f.write(response.content)
            
            df = pd.read_csv(raw_path)
            print(f"✓ Downloaded {len(df)} real medical insurance records")
            
            # Extract real statistics
            avg_age = df['age'].mean() if 'age' in df.columns else 45
            avg_charges = df['charges'].mean() if 'charges' in df.columns else 2500
            std_charges = df['charges'].std() if 'charges' in df.columns else 1500
            
            print(f"  Real data stats: avg_age={avg_age:.1f}, avg_charges=${avg_charges:.2f}")
        else:
            print("✗ Download failed, using default values")
            avg_charges = 2500
            std_charges = 1500
    except Exception as e:
        print(f"✗ Error: {e}, using default values")
        avg_charges = 2500
        std_charges = 1500
    
    # Generate synthetic claims using real statistics
    n_samples = 3000
    cpt_codes = np.random.choice(['99213', '99214', '99215', '99385', '99386', '80053', '85025', '36415'], n_samples)
    diagnosis_codes = np.random.choice(['E11.9', 'I10', 'J44.9', 'M79.3', 'Z00.00'], n_samples)
    claim_amounts = np.random.normal(avg_charges, std_charges, n_samples).clip(50, 10000).round(2)
    
    # Typical costs for each CPT code
    typical_costs = {'99213': 150, '99214': 200, '99215': 250, '99385': 180, '99386': 200, '80053': 100, '85025': 50, '36415': 30}
    
    # Generate additional fields
    prior_auth_required = ['99215', '80053']  # Some codes need pre-auth
    prior_authorization = [('Yes' if code in prior_auth_required else 'No') for code in cpt_codes]
    
    # Diagnosis-procedure matching (simplified)
    valid_pairs = [('E11.9', '80053'), ('I10', '99213'), ('J44.9', '99214'), ('M79.3', '99213'), ('Z00.00', '99385')]
    diagnosis_matches = [(diag, code) in valid_pairs or np.random.random() > 0.2 for diag, code in zip(diagnosis_codes, cpt_codes)]
    
    # Claim timing (days between service and filing)
    claim_delays = np.random.choice([1, 2, 3, 5, 7, 14, 30, 60, 90], n_samples, p=[0.1, 0.15, 0.2, 0.15, 0.15, 0.1, 0.08, 0.05, 0.02])
    
    # Out of network status
    out_of_network = np.random.choice(['Yes', 'No'], n_samples, p=[0.15, 0.85])
    
    # Amount vs typical (red flag if >200%)
    amount_vs_typical = [(amt / typical_costs.get(code, 150)) * 100 for amt, code in zip(claim_amounts, cpt_codes)]
    
    # Missing documentation
    doc_options = ['None', 'Medical records', 'Lab results', 'Referral letter']
    missing_docs = np.random.choice(doc_options, n_samples, p=[0.75, 0.10, 0.10, 0.05])
    
    # Provider fraud history
    provider_fraud = np.random.choice(['Clean', 'Minor flags', 'Under investigation'], n_samples, p=[0.90, 0.08, 0.02])
    
    # Balanced difficulty: each level has valid, insufficient, and invalid
    statuses = []
    difficulties = []
    outcomes = []
    
    # Distribute outcomes evenly across difficulties
    for i in range(n_samples):
        difficulty = np.random.choice(['easy', 'medium', 'hard'])
        outcome = np.random.choice(['valid', 'insufficient', 'invalid'])
        
        # Inject red flags based on difficulty and outcome
        if outcome == 'invalid':
            if difficulty == 'easy':
                # 4-6 obvious red flags
                diagnosis_matches[i] = False
                out_of_network[i] = 'Yes'
                missing_docs[i] = 'Medical records'
                provider_fraud[i] = 'Under investigation'
                statuses.append('denied')
            elif difficulty == 'medium':
                # 2-3 moderate red flags
                out_of_network[i] = 'Yes'
                missing_docs[i] = 'Lab results'
                statuses.append('denied')
            else:  # hard
                # 0-1 subtle red flags
                claim_delays[i] = 65
                statuses.append('denied')
        elif outcome == 'insufficient':
            if difficulty == 'easy':
                # Obviously missing info
                missing_docs[i] = 'Medical records'
                prior_authorization[i] = 'Pending'
                statuses.append('pending')
            elif difficulty == 'medium':
                # Some missing info
                missing_docs[i] = 'Referral letter'
                statuses.append('pending')
            else:  # hard
                # Subtle missing info
                prior_authorization[i] = 'Pending'
                statuses.append('pending')
        else:  # valid
            if difficulty == 'easy':
                # Obviously valid
                diagnosis_matches[i] = True
                out_of_network[i] = 'No'
                missing_docs[i] = 'None'
                provider_fraud[i] = 'Clean'
                statuses.append('approved')
            elif difficulty == 'medium':
                # Valid but needs verification
                diagnosis_matches[i] = True
                out_of_network[i] = 'No'
                missing_docs[i] = 'None'
                statuses.append('approved')
            else:  # hard
                # Valid but requires deep analysis
                diagnosis_matches[i] = True
                out_of_network[i] = 'No'
                missing_docs[i] = 'None'
                provider_fraud[i] = 'Clean'
                statuses.append('approved')
        
        difficulties.append(difficulty)
        outcomes.append(outcome)
    
    medical_claims = pd.DataFrame({
        'claim_id': range(1000, 1000 + n_samples),
        'patient_id': [f'P{i:05d}' for i in range(n_samples)],
        'cpt_code': cpt_codes,
        'diagnosis_code': diagnosis_codes,
        'claim_amount': claim_amounts,
        'provider_id': [f'PR{i%50:03d}' for i in range(n_samples)],
        'service_date': pd.date_range('2023-01-01', periods=n_samples, freq='8H').strftime('%Y-%m-%d'),
        'claim_status': statuses,
        'difficulty': difficulties,
        'prior_authorization': prior_authorization,
        'diagnosis_matches_procedure': diagnosis_matches,
        'days_to_file': claim_delays,
        'out_of_network': out_of_network,
        'amount_vs_typical_percent': [round(x, 1) for x in amount_vs_typical],
        'missing_documentation': missing_docs,
        'provider_fraud_history': provider_fraud
    })
    
    output_path = DATASETS_DIR / "medical_claims.csv"
    medical_claims.to_csv(output_path, index=False)
    print(f"Saved {len(medical_claims)} medical claims to {output_path}")
    return medical_claims

def download_dental_claims():
    """Generate dental claims dataset with CDT codes"""
    print("Generating dental claims data...")
    
    n_samples = 1500
    cdt_codes = np.random.choice(['D0120', 'D0150', 'D1110', 'D2391', 'D2740', 'D7140', 'D4341'], n_samples)
    tooth_numbers = np.random.choice([str(i) for i in range(1, 33)], n_samples)
    
    # Cost ranges by procedure
    cost_map = {'D0120': (50, 150), 'D0150': (75, 200), 'D1110': (75, 200), 'D2391': (150, 400), 'D2740': (800, 2000), 'D7140': (150, 500), 'D4341': (500, 1500)}
    claim_amounts = [np.random.uniform(*cost_map[code]) for code in cdt_codes]
    
    # X-ray requirements
    xray_required_codes = ['D2740', 'D7140', 'D4341']
    xray_attached = [('Yes' if code in xray_required_codes else np.random.choice(['Yes', 'No'])) for code in cdt_codes]
    
    # Tooth already treated (red flag)
    tooth_recently_treated = np.random.choice(['Yes', 'No'], n_samples, p=[0.10, 0.90])
    
    # Age appropriate procedures
    patient_ages = np.random.randint(5, 80, n_samples)
    age_appropriate = [(age > 18 or code not in ['D2740', 'D4341']) for age, code in zip(patient_ages, cdt_codes)]
    
    # Treatment plan approved
    treatment_plan_approved = np.random.choice(['Yes', 'No', 'Not required'], n_samples, p=[0.70, 0.10, 0.20])
    
    # Amount vs typical
    typical_costs = {'D0120': 100, 'D0150': 150, 'D1110': 125, 'D2391': 250, 'D2740': 1200, 'D7140': 300, 'D4341': 800}
    amount_vs_typical = [(amt / typical_costs.get(code, 200)) * 100 for amt, code in zip(claim_amounts, cdt_codes)]
    
    # Missing documentation
    missing_docs = np.random.choice(['None', 'X-rays', 'Treatment notes', 'Pre-approval'], n_samples, p=[0.70, 0.15, 0.10, 0.05])
    
    # Balanced difficulty: each level has valid, insufficient, and invalid
    statuses = []
    difficulties = []
    outcomes = []
    
    for i in range(n_samples):
        difficulty = np.random.choice(['easy', 'medium', 'hard'])
        outcome = np.random.choice(['valid', 'insufficient', 'invalid'])
        
        if outcome == 'invalid':
            if difficulty == 'easy':
                # 4-6 obvious red flags
                xray_attached[i] = 'No'
                tooth_recently_treated[i] = 'Yes'
                treatment_plan_approved[i] = 'No'
                missing_docs[i] = 'X-rays'
                statuses.append('denied')
            elif difficulty == 'medium':
                # 2-3 moderate red flags
                tooth_recently_treated[i] = 'Yes'
                treatment_plan_approved[i] = 'No'
                statuses.append('denied')
            else:  # hard
                # 0-1 subtle red flags
                tooth_recently_treated[i] = 'Yes'
                statuses.append('denied')
        elif outcome == 'insufficient':
            if difficulty == 'easy':
                # Obviously missing info
                xray_attached[i] = 'No'
                missing_docs[i] = 'X-rays'
                treatment_plan_approved[i] = 'Not required'
                statuses.append('pending')
            elif difficulty == 'medium':
                # Some missing info
                missing_docs[i] = 'Treatment notes'
                statuses.append('pending')
            else:  # hard
                # Subtle missing info
                treatment_plan_approved[i] = 'Not required'
                statuses.append('pending')
        else:  # valid
            if difficulty == 'easy':
                # Obviously valid
                xray_attached[i] = 'Yes'
                tooth_recently_treated[i] = 'No'
                treatment_plan_approved[i] = 'Yes'
                missing_docs[i] = 'None'
                statuses.append('approved')
            elif difficulty == 'medium':
                # Valid but needs verification
                xray_attached[i] = 'Yes'
                tooth_recently_treated[i] = 'No'
                missing_docs[i] = 'None'
                statuses.append('approved')
            else:  # hard
                # Valid but requires deep analysis
                xray_attached[i] = 'Yes'
                tooth_recently_treated[i] = 'No'
                treatment_plan_approved[i] = 'Yes'
                missing_docs[i] = 'None'
                statuses.append('approved')
        
        difficulties.append(difficulty)
        outcomes.append(outcome)
    
    dental_claims = pd.DataFrame({
        'claim_id': range(2000, 2000 + n_samples),
        'patient_id': [f'P{i:05d}' for i in range(n_samples)],
        'cdt_code': cdt_codes,
        'tooth_number': tooth_numbers,
        'claim_amount': [round(x, 2) for x in claim_amounts],
        'provider_id': [f'DT{i%25:03d}' for i in range(n_samples)],
        'service_date': pd.date_range('2023-01-01', periods=n_samples, freq='17H').strftime('%Y-%m-%d'),
        'claim_status': statuses,
        'difficulty': difficulties,
        'xray_attached': xray_attached,
        'tooth_recently_treated': tooth_recently_treated,
        'patient_age': patient_ages,
        'age_appropriate_procedure': age_appropriate,
        'treatment_plan_approved': treatment_plan_approved,
        'amount_vs_typical_percent': [round(x, 1) for x in amount_vs_typical],
        'missing_documentation': missing_docs
    })
    
    output_path = DATASETS_DIR / "dental_claims.csv"
    dental_claims.to_csv(output_path, index=False)
    print(f"Saved dental claims to {output_path}")
    return dental_claims

def download_life_insurance_claims():
    """Generate life insurance claims dataset"""
    print("Generating life insurance claims data...")
    
    n_samples = 1000
    claim_types = np.random.choice(['death_benefit', 'accidental_death', 'terminal_illness'], n_samples, p=[0.70, 0.20, 0.10])
    policy_amounts = np.random.choice([100000, 250000, 500000, 1000000], n_samples)
    ages_at_death = np.random.randint(35, 90, n_samples)
    
    # Policy active duration (months)
    policy_durations = np.random.choice([3, 6, 12, 24, 36, 60, 120, 240], n_samples, p=[0.05, 0.05, 0.10, 0.15, 0.20, 0.25, 0.15, 0.05])
    
    # Cause of death
    cause_of_death = []
    for claim_type in claim_types:
        if claim_type == 'accidental_death':
            cause_of_death.append(np.random.choice(['Car accident', 'Fall', 'Drowning']))
        elif claim_type == 'terminal_illness':
            cause_of_death.append(np.random.choice(['Cancer', 'Heart disease', 'Kidney failure']))
        else:
            cause_of_death.append(np.random.choice(['Natural causes', 'Heart attack', 'Stroke', 'Cancer']))
    
    # Beneficiary relationship
    beneficiary_relationship = np.random.choice(['Spouse', 'Child', 'Parent', 'Sibling', 'Other'], n_samples, p=[0.60, 0.25, 0.05, 0.05, 0.05])
    
    # Premium payments current
    premium_current = np.random.choice(['Yes', 'No', 'Grace period'], n_samples, p=[0.85, 0.10, 0.05])
    
    # Contestability period (within 2 years)
    in_contestability = [duration <= 24 for duration in policy_durations]
    
    # Exclusions apply
    exclusions = []
    for i, (cause, duration) in enumerate(zip(cause_of_death, policy_durations)):
        if cause == 'Suicide' and duration <= 24:
            exclusions.append('Suicide clause')
        elif in_contestability[i] and np.random.random() < 0.1:
            exclusions.append('Pre-existing condition')
        else:
            exclusions.append('None')
    
    # Claim amounts based on type
    claim_amounts = []
    for policy_amt, claim_type in zip(policy_amounts, claim_types):
        if claim_type == 'accidental_death':
            claim_amounts.append(policy_amt * np.random.uniform(1.8, 2.0))  # Double indemnity
        elif claim_type == 'terminal_illness':
            claim_amounts.append(policy_amt * np.random.uniform(0.5, 0.8))  # Partial payout
        else:
            claim_amounts.append(policy_amt * np.random.uniform(0.98, 1.0))  # Full payout
    
    # Amount vs expected
    amount_vs_expected = [(claim / policy) * 100 for claim, policy in zip(claim_amounts, policy_amounts)]
    
    # Missing documentation
    missing_docs = np.random.choice(['None', 'Death certificate', 'Medical records', 'Police report'], n_samples, p=[0.70, 0.10, 0.10, 0.10])
    
    # Balanced difficulty: each level has valid, insufficient, and invalid
    statuses = []
    difficulties = []
    outcomes = []
    
    for i in range(n_samples):
        difficulty = np.random.choice(['easy', 'medium', 'hard'])
        outcome = np.random.choice(['valid', 'insufficient', 'invalid'])
        
        if outcome == 'invalid':
            if difficulty == 'easy':
                # 4-6 obvious red flags
                policy_durations[i] = 2
                premium_current[i] = 'No'
                exclusions[i] = 'Suicide clause'
                missing_docs[i] = 'Death certificate'
                statuses.append('denied')
            elif difficulty == 'medium':
                # 2-3 moderate red flags
                policy_durations[i] = 18
                premium_current[i] = 'Grace period'
                exclusions[i] = 'Pre-existing condition'
                statuses.append('denied')
            else:  # hard
                # 0-1 subtle red flags
                exclusions[i] = 'Pre-existing condition'
                statuses.append('denied')
        elif outcome == 'insufficient':
            if difficulty == 'easy':
                # Obviously missing info
                missing_docs[i] = 'Death certificate'
                premium_current[i] = 'Grace period'
                statuses.append('under_review')
            elif difficulty == 'medium':
                # Some missing info
                missing_docs[i] = 'Medical records'
                statuses.append('under_review')
            else:  # hard
                # Subtle missing info
                missing_docs[i] = 'Police report'
                statuses.append('under_review')
        else:  # valid
            if difficulty == 'easy':
                # Obviously valid
                policy_durations[i] = 60
                premium_current[i] = 'Yes'
                exclusions[i] = 'None'
                missing_docs[i] = 'None'
                statuses.append('approved')
            elif difficulty == 'medium':
                # Valid but needs verification
                policy_durations[i] = 36
                premium_current[i] = 'Yes'
                exclusions[i] = 'None'
                missing_docs[i] = 'None'
                statuses.append('approved')
            else:  # hard
                # Valid but requires deep analysis
                policy_durations[i] = 30
                premium_current[i] = 'Yes'
                exclusions[i] = 'None'
                missing_docs[i] = 'None'
                statuses.append('approved')
        
        difficulties.append(difficulty)
        outcomes.append(outcome)
    
    life_claims = pd.DataFrame({
        'claim_id': range(3000, 3000 + n_samples),
        'policy_id': [f'LP{i:05d}' for i in range(n_samples)],
        'claim_type': claim_types,
        'policy_amount': policy_amounts,
        'claim_amount': [round(x, 2) for x in claim_amounts],
        'beneficiary_id': [f'B{i:05d}' for i in range(n_samples)],
        'claim_date': pd.date_range('2023-01-01', periods=n_samples, freq='29H').strftime('%Y-%m-%d'),
        'age_at_death': ages_at_death,
        'claim_status': statuses,
        'difficulty': difficulties,
        'policy_active_months': policy_durations,
        'cause_of_death': cause_of_death,
        'beneficiary_relationship': beneficiary_relationship,
        'premium_payments_current': premium_current,
        'in_contestability_period': in_contestability,
        'exclusions_apply': exclusions,
        'amount_vs_expected_percent': [round(x, 1) for x in amount_vs_expected],
        'missing_documentation': missing_docs
    })
    
    output_path = DATASETS_DIR / "life_insurance_claims.csv"
    life_claims.to_csv(output_path, index=False)
    print(f"Saved life insurance claims to {output_path}")
    return life_claims

def clean_and_standardize(df, claim_type):
    """Clean and standardize claims data"""
    df = df.dropna()
    df = df.drop_duplicates(subset=['claim_id'])
    
    # Standardize status values
    status_map = {'approved': 'APPROVED', 'denied': 'DENIED', 'pending': 'PENDING', 'under_review': 'PENDING'}
    if 'claim_status' in df.columns:
        df['claim_status'] = df['claim_status'].map(status_map)
    
    return df

def main():
    """Main execution function"""
    print("Starting dataset collection...\n")
    
    # Download and process datasets
    medical_df = download_cms_medicare_claims()
    medical_df = clean_and_standardize(medical_df, 'medical')
    
    dental_df = download_dental_claims()
    dental_df = clean_and_standardize(dental_df, 'dental')
    
    life_df = download_life_insurance_claims()
    life_df = clean_and_standardize(life_df, 'life')
    
    # Generate summary statistics
    print("\n=== Dataset Summary ===")
    print(f"Medical Claims: {len(medical_df)} records")
    print(f"Dental Claims: {len(dental_df)} records")
    print(f"Life Insurance Claims: {len(life_df)} records")
    print(f"\nAll datasets saved to: {DATASETS_DIR}")

if __name__ == "__main__":
    main()
