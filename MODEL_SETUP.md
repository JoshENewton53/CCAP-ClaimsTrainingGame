# AI Model Setup

## Why Models Are Not Included

The trained AI models are **not included in this repository** because they exceed GitHub's file size limits:
- `claim_classifier.pkl` - 88 MB
- `scenario_generator/` models - 1.4 GB

## Option 1: Train Models Yourself (Recommended)

Navigate to the `ai_models/` directory and train the models:

```bash
cd ai_models

# Install dependencies
pip install -r requirements.txt

# Train the claim classifier
python train_classifier.py

# Train the scenario generator (optional, takes longer)
python train_generator.py
```

The trained models will be saved to `ai_models/models/`.

## Option 2: Use Pre-trained Models

If you have access to the pre-trained models:

1. Create the models directory:
   ```bash
   mkdir -p ai_models/models/scenario_generator
   ```

2. Place the model files:
   - `claim_classifier.pkl` → `ai_models/models/`
   - Scenario generator files → `ai_models/models/scenario_generator/`

## Option 3: Run Without AI Models

The application can run with simplified scenario generation by modifying `backend/ai_service.py` to use rule-based generation instead of ML models.

## Verifying Setup

After setting up models, verify they exist:
```bash
ls ai_models/models/
```

You should see:
- `claim_classifier.pkl`
- `scenario_generator/` (directory)
