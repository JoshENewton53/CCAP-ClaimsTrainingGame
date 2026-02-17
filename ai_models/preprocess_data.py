"""
Claims Data Preprocessing Script
Loads raw datasets, extracts features, labels claims, and creates training splits
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

DATASETS_DIR = Path(__file__).parent.parent / "datasets"
OUTPUT_FILE = DATASETS_DIR / "claims_training_data.csv"

def load_datasets():
    """Load all three claim datasets"""
    medical = pd.read_csv(DATASETS_DIR / "medical_claims.csv")
    dental = pd.read_csv(DATASETS_DIR / "dental_claims.csv")
    life = pd.read_csv(DATASETS_DIR / "life_insurance_claims.csv")
    return medical, dental, life

def extract_medical_features(df):
    """Extract features from medical claims"""
    features = pd.DataFrame({
        'claim_id': df['claim_id'],
        'claim_type': 'medical',
        'procedure_code': df['cpt_code'],
        'diagnosis_code': df['diagnosis_code'],
        'claim_amount': df['claim_amount'],
        'patient_age': np.random.randint(18, 85, len(df)),
        'service_date': df['service_date'],
        'claim_status': df['claim_status'].str.upper()
    })
    
    # Add new fields if they exist
    if 'prior_authorization' in df.columns:
        features['prior_authorization'] = df['prior_authorization']
    if 'diagnosis_matches_procedure' in df.columns:
        features['diagnosis_matches'] = df['diagnosis_matches_procedure']
    if 'days_to_file' in df.columns:
        features['days_to_file'] = df['days_to_file']
    if 'out_of_network' in df.columns:
        features['out_of_network'] = df['out_of_network']
    if 'amount_vs_typical_percent' in df.columns:
        features['amount_vs_typical'] = df['amount_vs_typical_percent']
    if 'missing_documentation' in df.columns:
        features['missing_docs'] = df['missing_documentation']
    if 'provider_fraud_history' in df.columns:
        features['provider_fraud'] = df['provider_fraud_history']
    
    return features

def extract_dental_features(df):
    """Extract features from dental claims"""
    features = pd.DataFrame({
        'claim_id': df['claim_id'],
        'claim_type': 'dental',
        'procedure_code': df['cdt_code'],
        'diagnosis_code': 'D' + df['tooth_number'].astype(str),
        'claim_amount': df['claim_amount'],
        'patient_age': df['patient_age'] if 'patient_age' in df.columns else np.random.randint(5, 80, len(df)),
        'service_date': df['service_date'],
        'claim_status': df['claim_status'].str.upper()
    })
    
    # Add new fields if they exist
    if 'xray_attached' in df.columns:
        features['xray_attached'] = df['xray_attached']
    if 'tooth_recently_treated' in df.columns:
        features['tooth_recently_treated'] = df['tooth_recently_treated']
    if 'age_appropriate_procedure' in df.columns:
        features['age_appropriate'] = df['age_appropriate_procedure']
    if 'treatment_plan_approved' in df.columns:
        features['treatment_approved'] = df['treatment_plan_approved']
    if 'amount_vs_typical_percent' in df.columns:
        features['amount_vs_typical'] = df['amount_vs_typical_percent']
    if 'missing_documentation' in df.columns:
        features['missing_docs'] = df['missing_documentation']
    
    return features

def extract_life_features(df):
    """Extract features from life insurance claims"""
    features = pd.DataFrame({
        'claim_id': df['claim_id'],
        'claim_type': 'life',
        'procedure_code': df['claim_type'],
        'diagnosis_code': 'N/A',
        'claim_amount': df['claim_amount'],
        'patient_age': df['age_at_death'],
        'service_date': df['claim_date'],
        'claim_status': df['claim_status'].str.upper().replace('UNDER_REVIEW', 'PENDING')
    })
    
    # Add new fields if they exist
    if 'policy_active_months' in df.columns:
        features['policy_duration'] = df['policy_active_months']
    if 'cause_of_death' in df.columns:
        features['cause_of_death'] = df['cause_of_death']
    if 'beneficiary_relationship' in df.columns:
        features['beneficiary_relation'] = df['beneficiary_relationship']
    if 'premium_payments_current' in df.columns:
        features['premium_current'] = df['premium_payments_current']
    if 'in_contestability_period' in df.columns:
        features['contestability'] = df['in_contestability_period']
    if 'exclusions_apply' in df.columns:
        features['exclusions'] = df['exclusions_apply']
    if 'amount_vs_expected_percent' in df.columns:
        features['amount_vs_expected'] = df['amount_vs_expected_percent']
    if 'missing_documentation' in df.columns:
        features['missing_docs'] = df['missing_documentation']
    
    return features

def label_claims(df):
    """Label claims as valid/invalid/insufficient"""
    labels = []
    for _, row in df.iterrows():
        if row['claim_status'] == 'APPROVED':
            labels.append('valid')
        elif row['claim_status'] == 'DENIED':
            labels.append('invalid')
        else:  # PENDING
            labels.append('insufficient')
    df['label'] = labels
    return df

def create_unified_dataset(medical, dental, life):
    """Create unified dataset from all claim types"""
    medical_features = extract_medical_features(medical)
    dental_features = extract_dental_features(dental)
    life_features = extract_life_features(life)
    
    unified = pd.concat([medical_features, dental_features, life_features], ignore_index=True)
    unified = label_claims(unified)
    
    return unified

def split_data(df):
    """Split data into train/validation/test sets (80/10/10)"""
    train, temp = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])
    val, test = train_test_split(temp, test_size=0.5, random_state=42, stratify=temp['label'])
    
    train['split'] = 'train'
    val['split'] = 'validation'
    test['split'] = 'test'
    
    return pd.concat([train, val, test], ignore_index=True)

def main():
    """Main preprocessing pipeline"""
    print("Loading datasets...")
    medical, dental, life = load_datasets()
    
    print(f"Loaded {len(medical)} medical, {len(dental)} dental, {len(life)} life claims")
    
    print("\nCreating unified dataset...")
    unified = create_unified_dataset(medical, dental, life)
    
    print(f"Total claims: {len(unified)}")
    print(f"Label distribution:\n{unified['label'].value_counts()}")
    
    print("\nSplitting data (80/10/10)...")
    final_data = split_data(unified)
    
    print(f"Train: {len(final_data[final_data['split']=='train'])}")
    print(f"Validation: {len(final_data[final_data['split']=='validation'])}")
    print(f"Test: {len(final_data[final_data['split']=='test'])}")
    
    print(f"\nSaving to {OUTPUT_FILE}...")
    final_data.to_csv(OUTPUT_FILE, index=False)
    
    print("Preprocessing complete!")

if __name__ == "__main__":
    main()
