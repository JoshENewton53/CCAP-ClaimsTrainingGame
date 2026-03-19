import sys
sys.path.insert(0, '.')
from ai_service import classify_claim

scenarios = [
    ('Medical - valid codes, all docs',       {'claim_type':'medical','difficulty':'easy','procedure_code':'99213','diagnosis_code':'I10','claim_amount':250.0,'patient_age':45,'document_status':{'missing':[],'submitted':['Patient medical records','Physician notes and diagnosis']},'client_profile':None}),
    ('Medical - code mismatch',               {'claim_type':'medical','difficulty':'hard','procedure_code':'99213','diagnosis_code':'K02.9','claim_amount':8000.0,'patient_age':60,'document_status':{'missing':[],'submitted':['Patient medical records','Physician notes and diagnosis']},'client_profile':None}),
    ('Medical - missing critical docs',       {'claim_type':'medical','difficulty':'medium','procedure_code':'99213','diagnosis_code':'I10','claim_amount':500.0,'patient_age':50,'document_status':{'missing':['Patient medical records'],'submitted':['Physician notes and diagnosis']},'client_profile':None}),
    ('Medical - age mismatch',                {'claim_type':'medical','difficulty':'medium','procedure_code':'99213','diagnosis_code':'I10','claim_amount':500.0,'patient_age':45,'document_status':{'missing':[],'submitted':['Patient medical records','Physician notes and diagnosis']},'client_profile':{'date_of_birth':'1970-01-01','policy_start_date':'2020-01-01','injury_date':'2023-06-01'}}),
    ('Dental - valid',                        {'claim_type':'dental','difficulty':'easy','procedure_code':'D1110','diagnosis_code':'K02.9','claim_amount':120.0,'patient_age':30,'document_status':{'missing':[],'submitted':['X-rays or diagnostic images','Treatment plan with CDT codes']},'client_profile':None}),
    ('Dental - missing xrays',                {'claim_type':'dental','difficulty':'medium','procedure_code':'D2750','diagnosis_code':'K04.5','claim_amount':900.0,'patient_age':38,'document_status':{'missing':['X-rays or diagnostic images'],'submitted':['Treatment plan with CDT codes']},'client_profile':None}),
    ('Life - natural death (unseen code)',     {'claim_type':'life','difficulty':'easy','procedure_code':'death_benefit','diagnosis_code':'natural_death','claim_amount':150000.0,'patient_age':72,'document_status':{'missing':[],'submitted':['Death certificate','Policy documents']},'client_profile':None}),
    ('Life - suspicious death (unseen code)', {'claim_type':'life','difficulty':'hard','procedure_code':'death_benefit','diagnosis_code':'suspicious_death','claim_amount':750000.0,'patient_age':45,'document_status':{'missing':[],'submitted':['Death certificate','Policy documents']},'client_profile':None}),
    ('Life - missing death cert',             {'claim_type':'life','difficulty':'medium','procedure_code':'death_benefit','diagnosis_code':'natural_death','claim_amount':200000.0,'patient_age':68,'document_status':{'missing':['Death certificate'],'submitted':['Policy documents']},'client_profile':None}),
]

passed = 0
failed = 0

print()
for label, s in scenarios:
    r = classify_claim(s)
    p = r['probabilities']
    flat = max(p.values()) - min(p.values()) < 0.05
    status = 'FAIL - flat probs' if flat else 'PASS'
    if flat:
        failed += 1
    else:
        passed += 1
    print(f'[{status}] {label}')
    print(f'       prediction={r["prediction"]}  confidence={r["confidence"]:.1%}')
    print(f'       valid={p.get("valid",0):.1%}  invalid={p.get("invalid",0):.1%}  insufficient={p.get("insufficient",0):.1%}')
    print()

print(f'Results: {passed} passed, {failed} failed out of {len(scenarios)} scenarios')
