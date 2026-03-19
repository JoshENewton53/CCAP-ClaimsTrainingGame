# Death Certificate Review Feature

## Overview
Life insurance claims include a death certificate review scenario. Users review a generated death certificate PDF and identify potential issues using a checklist.

## How It Works

### Backend
- **`backend/death_certificate_service.py`** — Generates policy data and injects errors based on difficulty. Validates user reviews and calculates scores.
- **`backend/pdf_generator.py`** — Generates the death certificate PDF programmatically using ReportLab.

### API Endpoints
- `POST /api/death-certificate/generate` — Generate a new scenario
- `POST /api/death-certificate/validate` — Validate the user's review
- `GET /api/death-certificate/error-options` — Get checklist options

### Frontend
- **`frontend/src/DeathCertificateReview.js`** — Displays the certificate PDF, policy information, error checklist, and results.

## Error Types
1. **Name Mismatch** (Critical) — Name doesn't match policy holder
2. **Date Inconsistency** (Critical) — Death date before policy effective date
3. **Missing Signature** (High) — Required physician signature missing
4. **Invalid Cause Code** (Medium) — ICD-10 cause of death code invalid
5. **Jurisdiction Mismatch** (Medium) — Wrong state/jurisdiction
6. **Age Mismatch** (High) — Age doesn't match policy records
7. **State Mismatch** (Medium) — Residence state doesn't match policy
8. **Expired Certification** (High) — Medical examiner certification expired

## Difficulty
- Easy: 0–1 errors
- Medium: 0–2 errors
- Hard: 0–3 errors

## Scoring
- Base score: 0–100 based on accuracy
- Multipliers: Easy (1x), Medium (1.5x), Hard (2x)
- Penalties for false positives and missed errors
- Score of 100 for correctly identifying a clean certificate
