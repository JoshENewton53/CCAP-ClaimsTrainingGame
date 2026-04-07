import random
from datetime import datetime, timedelta


class ItemizedBillService:
    def __init__(self):
        self.medical_procedures = {
            '99212': {'name': 'Office Visit - Established Patient (Level 2)', 'cost_range': (45,  90)},
            '99213': {'name': 'Office Visit - Established Patient (Level 3)', 'cost_range': (75,  150)},
            '99214': {'name': 'Office Visit - Established Patient (Level 4)', 'cost_range': (150, 250)},
            '99215': {'name': 'Office Visit - Established Patient (Level 5)', 'cost_range': (250, 400)},
            '99285': {'name': 'Emergency Department Visit',                   'cost_range': (300, 600)},
            '70450': {'name': 'CT Scan - Head',                               'cost_range': (500, 1200)},
            '73721': {'name': 'MRI - Lower Extremity',                        'cost_range': (800, 1500)},
            '80053': {'name': 'Comprehensive Metabolic Panel',                'cost_range': (50,  100)},
            '85025': {'name': 'Complete Blood Count',                         'cost_range': (30,  75)},
            '36415': {'name': 'Blood Draw',                                   'cost_range': (15,  35)},
            '97110': {'name': 'Physical Therapy',                             'cost_range': (75,  150)},
            '29881': {'name': 'Knee Arthroscopy',                             'cost_range': (2000, 4000)},
        }

        self.dental_procedures = {
            'D0120': {'name': 'Periodic Oral Evaluation',          'cost_range': (50,  100)},
            'D0220': {'name': 'Intraoral X-ray',                   'cost_range': (25,  60)},
            'D1110': {'name': 'Prophylaxis - Adult',               'cost_range': (75,  150)},
            'D2391': {'name': 'Resin Composite - One Surface',     'cost_range': (150, 250)},
            'D2740': {'name': 'Crown - Porcelain',                 'cost_range': (800, 1500)},
            'D7140': {'name': 'Tooth Extraction',                  'cost_range': (150, 350)},
            'D3310': {'name': 'Root Canal - Anterior',             'cost_range': (600, 1000)},
            'D4341': {'name': 'Periodontal Scaling',               'cost_range': (150, 300)},
        }

        # Upcoding: (legitimate_code, fraudulently_upcoded_code)
        # Bill shows the upcoded code while the scenario/notes document the lower-level one.
        self.upcode_pairs = {
            'medical': [
                ('99212', '99214'),  # Level-2 visit billed as Level-4
                ('99213', '99214'),  # Level-3 billed as Level-4
                ('99213', '99215'),  # Level-3 billed as Level-5
                ('99214', '99215'),  # Level-4 billed as Level-5
            ],
            'dental': [
                ('D2391', 'D2740'),  # Simple composite billed as full crown
                ('D1110', 'D4341'),  # Routine cleaning billed as periodontal scaling
            ],
        }

        # Bundling: if KEY procedure is billed, VALUE codes are ALREADY included
        # and must NOT appear as separate line items.
        self.bundled_inclusions = {
            'medical': {
                '80053': ['36415', '85025'],  # Metabolic panel includes blood draw + CBC
                '85025': ['36415'],            # CBC includes blood draw
                '29881': ['97110'],            # Knee arthroscopy includes immediate post-op PT
            },
            'dental': {
                'D3310': ['D0220'],  # Root canal includes necessary X-rays
                'D2740': ['D0220'],  # Crown prep includes X-ray
                'D4341': ['D0120'],  # Scaling includes evaluation
            },
        }

    def generate_bill(self, claim_type, procedure_code, claim_amount,
                      difficulty, client_profile=None):
        """Generate an itemized bill with potential training errors based on difficulty."""

        if claim_type == 'medical':
            procedures = self.medical_procedures
        elif claim_type == 'dental':
            procedures = self.dental_procedures
        else:
            return None

        # ── Error probabilities by difficulty ────────────────────────────────
        chances = {
            'easy':   dict(amount_mismatch=0.00, upcoding=0.00, unbundling=0.00, date_error=0.00),
            'medium': dict(amount_mismatch=0.20, upcoding=0.22, unbundling=0.18, date_error=0.10),
            'hard':   dict(amount_mismatch=0.30, upcoding=0.32, unbundling=0.25, date_error=0.18),
        }.get(difficulty, {})

        candidates = [k for k, v in chances.items() if random.random() < v]
        if len(candidates) > 2:          # Cap at 2 errors so the bill stays readable
            candidates = random.sample(candidates, 2)

        has_amount_mismatch = 'amount_mismatch' in candidates
        has_upcoding        = 'upcoding'        in candidates
        has_unbundling      = 'unbundling'      in candidates
        has_date_error      = 'date_error'      in candidates
        errors = []

        # ── Upcoding: replace the legitimate code on the bill ─────────────────
        bill_procedure_code = procedure_code
        if has_upcoding:
            pairs   = self.upcode_pairs.get(claim_type, [])
            matches = [(l, u) for l, u in pairs if l == procedure_code]
            if matches:
                _, upcoded = random.choice(matches)
                bill_procedure_code = upcoded
                errors.append(
                    f'Upcoding: {upcoded} billed instead of documented procedure {procedure_code}'
                )
            else:
                has_upcoding = False  # No applicable pair — skip silently

        main_proc = procedures.get(bill_procedure_code) or procedures.get(procedure_code)
        if not main_proc:
            bill_procedure_code = list(procedures.keys())[0]
            main_proc = procedures[bill_procedure_code]

        # ── Amount mismatch: inflate the target total ─────────────────────────
        target_total = claim_amount
        if has_amount_mismatch:
            target_total = claim_amount * random.uniform(1.25, 1.70)
            errors.append(
                f'Bill total (${target_total:,.2f}) does not match submitted '
                f'claim amount (${claim_amount:,.2f})'
            )

        # ── Build line items ──────────────────────────────────────────────────
        cost = target_total * random.uniform(0.40, 0.60)
        items = [{
            'code':        bill_procedure_code,
            'description': main_proc['name'],
            'quantity':    1,
            'unit_cost':   round(cost, 2),
            'total':       round(cost, 2),
        }]

        # ── Unbundling: add a code that is already included in the main proc ──
        unbundled_codes = []
        if has_unbundling:
            included     = self.bundled_inclusions.get(claim_type, {}).get(procedure_code, [])
            valid_extras = [c for c in included if c in procedures]
            if valid_extras:
                code = random.choice(valid_extras)
                proc = procedures[code]
                ub_cost = round(random.uniform(*proc['cost_range']), 2)
                items.append({
                    'code': code, 'description': proc['name'],
                    'quantity': 1, 'unit_cost': ub_cost, 'total': ub_cost,
                })
                unbundled_codes.append(code)
                errors.append(
                    f'Unbundling: {code} ({proc["name"]}) is already included '
                    f'in {procedure_code} and cannot be billed separately'
                )
            else:
                has_unbundling = False

        # ── Filler line items to reach target total ───────────────────────────
        remaining    = target_total - sum(i['total'] for i in items)
        other_codes  = [c for c in procedures
                        if c not in (bill_procedure_code, procedure_code)
                        and c not in unbundled_codes]
        num_extra    = random.randint(1, 3)
        sample_codes = random.sample(other_codes, min(num_extra, len(other_codes)))
        for idx, code in enumerate(sample_codes):
            proc = procedures[code]
            cost = max(10.0, remaining if idx == len(sample_codes) - 1
                       else remaining * random.uniform(0.20, 0.45))
            remaining -= cost
            items.append({
                'code': code, 'description': proc['name'],
                'quantity': 1, 'unit_cost': round(cost, 2), 'total': round(cost, 2),
            })

        # ── Service date (possibly before patient DOB) ────────────────────────
        today        = datetime.now()
        service_date = today - timedelta(days=random.randint(1, 30))
        if has_date_error and client_profile:
            try:
                dob          = datetime.fromisoformat(client_profile['date_of_birth'])
                service_date = dob - timedelta(days=random.randint(30, 365 * 3))
                errors.append(
                    f'Service date ({service_date.strftime("%Y-%m-%d")}) '
                    f'predates patient date of birth ({dob.strftime("%Y-%m-%d")})'
                )
            except Exception:
                has_date_error = False

        # ── Legacy fallback errors when no new errors fired ───────────────────
        if not errors:
            if difficulty == 'medium' and random.random() < 0.35:
                etype = random.choice(['wrong_code', 'math_error'])
                if etype == 'wrong_code' and items:
                    idx   = random.randint(0, len(items) - 1)
                    wrong = random.choice(list(procedures.keys()))
                    items[idx]['code'] = wrong
                    errors.append(f'Incorrect code: {wrong} does not match documented procedure')
                elif items:
                    idx = random.randint(0, len(items) - 1)
                    items[idx]['total'] = round(items[idx]['total'] * random.uniform(1.1, 1.5), 2)
                    errors.append('Math error: line item total does not match unit cost × quantity')

            elif difficulty == 'hard':
                for _ in range(random.randint(1, 2)):
                    etype = random.choice(['wrong_code', 'math_error', 'duplicate'])
                    if etype == 'wrong_code' and items:
                        idx   = random.randint(0, len(items) - 1)
                        wrong = random.choice(list(procedures.keys()))
                        items[idx]['code'] = wrong
                        errors.append(f'Incorrect code: {wrong}')
                    elif etype == 'math_error' and items:
                        idx = random.randint(0, len(items) - 1)
                        items[idx]['total'] = round(items[idx]['total'] * random.uniform(1.2, 1.8), 2)
                        errors.append(f'Math error on line {idx + 1}')
                    elif etype == 'duplicate' and items:
                        dup = random.choice(items).copy()
                        items.append(dup)
                        errors.append(f'Duplicate charge: {dup["code"]}')

        bill_total = sum(i['total'] for i in items)

        return {
            'items':               items,
            'subtotal':            round(bill_total, 2),
            'tax':                 0,
            'total':               round(bill_total, 2),
            'service_date':        service_date.strftime('%Y-%m-%d'),
            'provider':            'Medical Center' if claim_type == 'medical' else 'Dental Clinic',
            'has_errors':          bool(errors),
            'errors':              errors,
            'has_amount_mismatch': has_amount_mismatch,
            'has_upcoding':        has_upcoding,
            'has_unbundling':      has_unbundling,
            'has_date_error':      has_date_error,
            'claimed_amount':      claim_amount,
        }
