# Insurance Claims Datasets

This directory contains processed insurance claims datasets for training the CCAP Claims Training Game AI models.

## Data Sources

### 1. Medical Claims (medical_claims.csv)
- **Source**: CMS Medicare Synthetic Data (DE-SynPUF)
- **URL**: https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs
- **Description**: Synthetic Medicare claims with CPT procedure codes
- **Records**: ~1,000 claims

**Schema**:
- `claim_id`: Unique claim identifier
- `patient_id`: Patient identifier
- `cpt_code`: Current Procedural Terminology code (e.g., 99213, 99214)
- `diagnosis_code`: ICD-10 diagnosis code
- `claim_amount`: Claim amount in USD
- `provider_id`: Healthcare provider identifier
- `service_date`: Date of service (YYYY-MM-DD)
- `claim_status`: APPROVED, DENIED, or PENDING

**Common CPT Codes**:
- 99213-99215: Office visits
- 99385-99386: Preventive care
- 80053: Comprehensive metabolic panel
- 85025: Complete blood count
- 36415: Blood draw

### 2. Dental Claims (dental_claims.csv)
- **Source**: Synthetic dental claims data
- **Description**: Dental procedure claims with CDT codes
- **Records**: ~500 claims

**Schema**:
- `claim_id`: Unique claim identifier
- `patient_id`: Patient identifier
- `cdt_code`: Current Dental Terminology code
- `tooth_number`: Tooth number (1-32)
- `claim_amount`: Claim amount in USD
- `provider_id`: Dental provider identifier
- `service_date`: Date of service (YYYY-MM-DD)
- `claim_status`: APPROVED, DENIED, or PENDING

**Common CDT Codes**:
- D0120: Periodic oral evaluation
- D0150: Comprehensive oral evaluation
- D1110: Prophylaxis (cleaning)
- D2391: Resin-based composite filling
- D2740: Crown - porcelain/ceramic
- D7140: Tooth extraction
- D4341: Periodontal scaling

### 3. Life Insurance Claims (life_insurance_claims.csv)
- **Source**: Synthetic life insurance claims data
- **Description**: Life insurance death benefit and related claims
- **Records**: ~300 claims

**Schema**:
- `claim_id`: Unique claim identifier
- `policy_id`: Life insurance policy identifier
- `claim_type`: death_benefit, accidental_death, or terminal_illness
- `policy_amount`: Face value of policy in USD
- `claim_amount`: Actual claim payout amount in USD
- `beneficiary_id`: Beneficiary identifier
- `claim_date`: Date claim was filed (YYYY-MM-DD)
- `age_at_death`: Age of insured at time of death
- `claim_status`: APPROVED, DENIED, or PENDING

## Data Collection

Run the collection script to download and process datasets:

```bash
cd ai_models
python collect_datasets.py
```

## Data Quality

All datasets have been:
- Cleaned (removed duplicates and null values)
- Standardized (consistent status values and date formats)
- Validated (proper code formats and value ranges)

## Usage Notes

- All data is synthetic/de-identified for training purposes
- Claim amounts are in USD
- Status values are standardized: APPROVED, DENIED, PENDING
- Date format: YYYY-MM-DD

## Additional Resources

- **CPT Codes**: https://www.ama-assn.org/practice-management/cpt
- **CDT Codes**: https://www.ada.org/publications/cdt
- **ICD-10 Codes**: https://www.cms.gov/medicare/coding-billing/icd-10-codes
- **CMS Data**: https://www.cms.gov/data-research
