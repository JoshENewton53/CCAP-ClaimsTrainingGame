"""
Test script to verify AI scenario generation is working
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_service import generate_scenario, _generator_model, _generator_tokenizer

def test_ai_generation():
    print("=" * 60)
    print("Testing AI Scenario Generation")
    print("=" * 60)
    
    # Check if models are loaded
    print("\n1. Checking if AI models are loaded...")
    if _generator_model is None or _generator_tokenizer is None:
        print("   ❌ AI models NOT loaded - will use fallback")
        print("   Run the backend server first to load models")
        return False
    else:
        print("   ✓ AI models loaded successfully")
    
    # Generate multiple scenarios to see variety
    print("\n2. Generating scenarios with AI...")
    
    test_cases = [
        ('medical', 'easy'),
        ('medical', 'medium'),
        ('dental', 'easy'),
        ('life', 'hard')
    ]
    
    for claim_type, difficulty in test_cases:
        print(f"\n   Testing: {claim_type.upper()} - {difficulty}")
        print("   " + "-" * 50)
        
        scenario = generate_scenario(claim_type, difficulty)
        
        print(f"   Description: {scenario['description'][:100]}...")
        print(f"   Procedure: {scenario['procedure_code']}")
        print(f"   Diagnosis: {scenario['diagnosis_code']}")
        print(f"   Amount: ${scenario['claim_amount']:.2f}")
    
    print("\n" + "=" * 60)
    print("✓ AI Generation Test Complete!")
    print("=" * 60)
    print("\nIf descriptions vary each run, AI is working.")
    print("If descriptions are identical, fallback is being used.")
    
    return True

if __name__ == "__main__":
    test_ai_generation()
