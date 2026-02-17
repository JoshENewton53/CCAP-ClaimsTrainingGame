"""
Claim Scenario Generator Training
Fine-tunes GPT-2 to generate claim scenarios from real claims data
"""
import pandas as pd
import torch
from pathlib import Path
from transformers import GPT2LMHeadModel, GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments

DATASETS_DIR = Path(__file__).parent.parent / "datasets"
MODELS_DIR = Path(__file__).parent / "models"
INPUT_FILE = DATASETS_DIR / "claims_training_data.csv"
OUTPUT_DIR = MODELS_DIR / "scenario_generator"
TRAINING_FILE = DATASETS_DIR / "training_prompts.txt"

def create_training_data():
    """Create training prompts from claims data"""
    df = pd.read_csv(INPUT_FILE)
    train_df = df[df['split'] == 'train']
    
    prompts = []
    for _, row in train_df.iterrows():
        difficulty = 'easy' if row['label'] == 'valid' else ('hard' if row['label'] == 'invalid' else 'medium')
        
        prompt = f"Generate a {difficulty} {row['claim_type']} claim scenario:\n"
        prompt += f"Claim Type: {row['claim_type']}\n"
        prompt += f"Procedure: {row['procedure_code']}\n"
        prompt += f"Diagnosis: {row['diagnosis_code']}\n"
        prompt += f"Amount: ${row['claim_amount']:.2f}\n"
        prompt += f"Patient Age: {row['patient_age']}\n"
        prompt += f"Status: {row['label']}\n"
        prompt += "<|endoftext|>\n"
        
        prompts.append(prompt)
    
    with open(TRAINING_FILE, 'w') as f:
        f.writelines(prompts)
    
    print(f"Created {len(prompts)} training prompts")
    return TRAINING_FILE

def load_dataset(file_path, tokenizer):
    """Load dataset for training"""
    return TextDataset(
        tokenizer=tokenizer,
        file_path=str(file_path),
        block_size=128
    )

def train_model():
    """Fine-tune GPT-2 on claim scenarios"""
    print("Loading GPT-2 model and tokenizer...")
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token
    
    print("Creating training data...")
    training_file = create_training_data()
    
    print("Loading dataset...")
    train_dataset = load_dataset(training_file, tokenizer)
    
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    print("Setting up training...")
    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        save_steps=500,
        save_total_limit=2,
        logging_steps=100,
        learning_rate=5e-5,
        warmup_steps=100,
        weight_decay=0.01,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )
    
    print("\nTraining model...")
    trainer.train()
    
    print(f"\nSaving model to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print("Training complete!")

def test_generation():
    """Test the trained model"""
    print("\n=== Testing Generation ===")
    model = GPT2LMHeadModel.from_pretrained(OUTPUT_DIR)
    tokenizer = GPT2Tokenizer.from_pretrained(OUTPUT_DIR)
    
    prompts = [
        "Generate a easy medical claim scenario:",
        "Generate a hard dental claim scenario:",
        "Generate a medium life claim scenario:"
    ]
    
    for prompt in prompts:
        inputs = tokenizer.encode(prompt, return_tensors='pt')
        outputs = model.generate(
            inputs,
            max_length=150,
            num_return_sequences=1,
            temperature=0.8,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"\nPrompt: {prompt}")
        print(f"Generated:\n{generated}\n")

def main():
    """Main training pipeline"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    train_model()
    test_generation()

if __name__ == "__main__":
    main()
