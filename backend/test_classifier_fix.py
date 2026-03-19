"""
Test script to verify the classifier inference fix (Fix #2).
Checks:
  1. Whether embedding_model was saved in the pickle
  2. Whether classify_claim builds hybrid features correctly
  3. Whether confidence scores look realistic vs the old 5-feature baseline
"""
import sys
import os
import pickle
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

CLASSIFIER_PATH = os.path.join(os.path.dirname(__file__), '..', 'ai_models', 'models', 'claim_classifier.pkl')

def check_pickle():
    print("=" * 60)
    print("1. Inspecting claim_classifier.pkl")
    print("=" * 60)
    with open(CLASSIFIER_PATH, 'rb') as f:
        data = pickle.load(f)

    keys = list(data.keys())
    print(f"   Keys in pickle: {keys}")

    has_embedding = 'embedding_model' in data and data['embedding_model'] is not None
    print(f"   embedding_model present: {'YES' if has_embedding else 'NO - needs retraining'}")

    model = data['model']
    n_features = model.n_features_in_
    print(f"   XGBoost expects {n_features} features")
    print(f"   Expected: 389 (5 structured + 384 embeddings) or 5 (structured only)")

    if n_features == 389:
        print("   PASS: Model was trained with hybrid features")
    elif n_features == 5:
        print("   WARN: Model was trained with structured features only")
        print("     The fix will use 5-feature mode (embedding_model path skipped)")
    else:
        print(f"   UNKNOWN feature count: {n_features}")

    return has_embedding, n_features

def test_classify_claim():
    print("\n" + "=" * 60)
    print("2. Testing classify_claim() with hybrid features")
    print("=" * 60)

    from ai_service import classify_claim, _embedding_model, _classifier

    if _classifier is None:
        print("   ✗ Classifier not loaded - check model paths")
        return

    print(f"   _embedding_model loaded: {'YES' if _embedding_model is not None else 'NO (fallback to 5 features)'}")

    test_scenarios = [
        {
            'claim_type': 'medical',
            'difficulty': 'easy',
            'procedure_code': '99213',
            'diagnosis_code': 'I10',
            'claim_amount': 250.00,
            'patient_age': 45,
            'document_status': {'missing': [], 'submitted': ['Patient medical records', 'Physician notes and diagnosis']},
            'client_profile': None
        },
        {
            'claim_type': 'dental',
            'difficulty': 'medium',
            'procedure_code': 'D2750',
            'diagnosis_code': 'K04.5',
            'claim_amount': 900.00,
            'patient_age': 38,
            'document_status': {'missing': ['X-rays or diagnostic images'], 'submitted': []},
            'client_profile': None
        },
        {
            'claim_type': 'medical',
            'difficulty': 'hard',
            'procedure_code': '99213',
            'diagnosis_code': 'K02.9',  # intentional mismatch
            'claim_amount': 8000.00,
            'patient_age': 60,
            'document_status': {'missing': [], 'submitted': ['Patient medical records', 'Physician notes and diagnosis']},
            'client_profile': None
        },
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        result = classify_claim(scenario)
        print(f"\n   Scenario {i}: {scenario['claim_type']} / {scenario['difficulty']}")
        print(f"   Prediction : {result['prediction']}")
        print(f"   Confidence : {result['confidence']:.1%}")
        print(f"   Probs      : { {k: f'{v:.1%}' for k, v in result['probabilities'].items()} }")
        print(f"   Reasoning  : {result.get('ai_reasoning', 'n/a')}")

        # Flag suspiciously flat probabilities (sign of the old broken path)
        probs = list(result['probabilities'].values())
        if max(probs) - min(probs) < 0.05:
            print("   WARN: Probabilities are nearly flat - may still be using fallback")
        else:
            print("   PASS: Probabilities show clear differentiation")

def main():
    has_embedding, n_features = check_pickle()

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    if has_embedding and n_features == 389:
        print("PASS: Fix is fully active - classifier running with hybrid features")
    elif not has_embedding and n_features == 5:
        print("WARN: Pickle has no embedding_model saved.")
        print("  The fix code is correct but the model needs to be retrained")
        print("  so the embedding_model gets saved into the pickle.")
        print("  Run: cd ai_models && python train_classifier.py")
    elif not has_embedding and n_features == 389:
        print("FAIL: Model expects 389 features but no embedding_model in pickle.")
        print("  This will cause a feature shape mismatch at inference.")
        print("  Retrain: cd ai_models && python train_classifier.py")
    else:
        print(f"UNKNOWN state - embedding: {has_embedding}, features: {n_features}")

    print("\nRunning live classification tests...")
    test_classify_claim()

if __name__ == "__main__":
    main()
