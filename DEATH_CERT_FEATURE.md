# Death Certificate Review Feature

## Overview
This feature adds realistic death certificate review scenarios to the Life Insurance claims training module. Users review actual death certificate images and identify potential issues.

## How It Works

### Backend
1. **DeathCertificateService** (`backend/death_certificate_service.py`)
   - Randomly selects from your certificate images
   - Generates policy data and error scenarios
   - Validates user reviews and calculates scores

2. **API Endpoints** (added to `backend/app.py`)
   - `POST /api/death-certificate/generate` - Generate new scenario
   - `POST /api/death-certificate/validate` - Validate user's review
   - `GET /api/death-certificate/error-options` - Get checklist options

### Frontend
1. **DeathCertificateReview Component** (`frontend/src/DeathCertificateReview.js`)
   - Displays certificate image
   - Shows policy information
   - Provides error checklist
   - Shows results and feedback

## Certificate Images Used
- `blankdeathcert.jpg` - Blank template
- `FlorDeathCert.jpg` - Florida certificate
- `TexasDeathCert.jpg` - Texas certificate
- `DeathCert1.webp` - Sample 1
- `deathcert2.jpg` - Sample 2

## Error Types Detected
1. **Name Mismatch** (Critical) - Name doesn't match policy holder
2. **Date Inconsistency** (Critical) - Death date before policy date
3. **Missing Signature** (High) - Required physician signature missing
4. **Invalid Cause Code** (Medium) - Cause of death code invalid
5. **Jurisdiction Mismatch** (Medium) - Wrong state/jurisdiction
6. **Expired Certification** (High) - Medical examiner cert expired

## Scoring System
- Base score: 0-100 based on accuracy
- Multipliers: Easy (1x), Medium (1.5x), Hard (2x)
- Penalties for false positives and missed errors
- Perfect score (100) for correctly identifying clean certificates

## Integration with Existing Game

### Option 1: Add to Life Insurance Flow
In `GameScreen.js`, add a button for death certificate review:

```javascript
{claimType === 'life' && (
  <button onClick={() => setShowDeathCertReview(true)}>
    Review Death Certificate
  </button>
)}

{showDeathCertReview && (
  <DeathCertificateReview
    difficulty={difficulty}
    onComplete={(result) => {
      setShowDeathCertReview(false);
      // Handle result
    }}
  />
)}
```

### Option 2: Standalone Mode
Add a new menu option in `StartGame.js`:

```javascript
<button onClick={() => navigate('/death-cert-review')}>
  Death Certificate Training
</button>
```

## Future Enhancements
1. **Annotate Certificates** - Let users click on specific areas to flag issues
2. **More Certificate Types** - Add certificates from different states
3. **Difficulty Variations** - Blur/distort images for harder scenarios
4. **Time Limits** - Add time pressure for advanced training
5. **Comparison Mode** - Show correct vs incorrect certificates side-by-side
6. **Real Data Integration** - Use anonymized real certificates (with compliance approval)

## Testing
1. Start backend: `cd backend && python app.py`
2. Start frontend: `cd frontend && npm start`
3. Navigate to death certificate review
4. Try different difficulty levels
5. Verify scoring and achievements work correctly
