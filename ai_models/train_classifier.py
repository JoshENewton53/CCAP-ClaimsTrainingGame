"""
Hybrid Claims Classification Model Training
Combines XGBoost with sentence embeddings for superior accuracy
"""
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sentence_transformers import SentenceTransformer

DATASETS_DIR = Path(__file__).parent.parent / "datasets"
MODELS_DIR = Path(__file__).parent / "models"
INPUT_FILE = DATASETS_DIR / "claims_training_data.csv"
MODEL_FILE = MODELS_DIR / "claim_classifier.pkl"

def load_data():
    """Load preprocessed training data"""
    df = pd.read_csv(INPUT_FILE)
    train = df[df['split'] == 'train']
    val = df[df['split'] == 'validation']
    test = df[df['split'] == 'test']
    return train, val, test

def encode_features(train, val, test):
    """Encode categorical features"""
    encoders = {}
    
    encoders['claim_type'] = LabelEncoder()
    train['claim_type_enc'] = encoders['claim_type'].fit_transform(train['claim_type'])
    val['claim_type_enc'] = encoders['claim_type'].transform(val['claim_type'])
    test['claim_type_enc'] = encoders['claim_type'].transform(test['claim_type'])
    
    encoders['procedure_code'] = LabelEncoder()
    train['procedure_code_enc'] = encoders['procedure_code'].fit_transform(train['procedure_code'])
    val['procedure_code_enc'] = encoders['procedure_code'].transform(val['procedure_code'])
    test['procedure_code_enc'] = encoders['procedure_code'].transform(test['procedure_code'])
    
    encoders['diagnosis_code'] = LabelEncoder()
    train['diagnosis_code_enc'] = encoders['diagnosis_code'].fit_transform(train['diagnosis_code'])
    val['diagnosis_code_enc'] = encoders['diagnosis_code'].transform(val['diagnosis_code'])
    test['diagnosis_code_enc'] = encoders['diagnosis_code'].transform(test['diagnosis_code'])
    
    encoders['label'] = LabelEncoder()
    train['label_enc'] = encoders['label'].fit_transform(train['label'])
    val['label_enc'] = encoders['label'].transform(val['label'])
    test['label_enc'] = encoders['label'].transform(test['label'])
    
    return train, val, test, encoders

def generate_text_embeddings(train, val, test):
    """Generate embeddings from text descriptions using sentence transformers"""
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Create text descriptions from claim data
    def create_description(row):
        return f"{row['claim_type']} claim for {row['procedure_code']} diagnosis {row['diagnosis_code']} amount ${row['claim_amount']} age {row['patient_age']}"
    
    train_texts = train.apply(create_description, axis=1).tolist()
    val_texts = val.apply(create_description, axis=1).tolist()
    test_texts = test.apply(create_description, axis=1).tolist()
    
    print("Generating embeddings...")
    train_embeddings = model.encode(train_texts, show_progress_bar=True)
    val_embeddings = model.encode(val_texts, show_progress_bar=True)
    test_embeddings = model.encode(test_texts, show_progress_bar=True)
    
    return train_embeddings, val_embeddings, test_embeddings, model

def prepare_features(df, embeddings):
    """Combine structured features with text embeddings"""
    structured = df[['claim_amount', 'patient_age', 'claim_type_enc', 'procedure_code_enc', 'diagnosis_code_enc']].values
    return np.hstack([structured, embeddings])

def train_model(X_train, y_train, X_val, y_val):
    """Train XGBoost classifier"""
    print("Training XGBoost classifier...")
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        use_label_encoder=False,
        eval_metric='mlogloss'
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X, y, split_name, label_encoder):
    """Evaluate model performance"""
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    
    print(f"\n{split_name} Results:")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y, y_pred, target_names=label_encoder.classes_))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y, y_pred))
    
    return accuracy

def save_model(model, encoders, embedding_model):
    """Save trained model, encoders, and embedding model"""
    MODELS_DIR.mkdir(exist_ok=True)
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump({'model': model, 'encoders': encoders, 'embedding_model': embedding_model}, f)
    print(f"\nModel saved to {MODEL_FILE}")

def main():
    """Main training pipeline"""
    print("Loading data...")
    train, val, test = load_data()
    print(f"Train: {len(train)}, Validation: {len(val)}, Test: {len(test)}")
    
    print("\nEncoding features...")
    train, val, test, encoders = encode_features(train, val, test)
    
    print("\nGenerating text embeddings...")
    train_emb, val_emb, test_emb, embedding_model = generate_text_embeddings(train, val, test)
    
    print("\nPreparing hybrid features...")
    X_train = prepare_features(train, train_emb)
    y_train = train['label_enc'].values
    X_val = prepare_features(val, val_emb)
    y_val = val['label_enc'].values
    X_test = prepare_features(test, test_emb)
    y_test = test['label_enc'].values
    
    print(f"Feature shape: {X_train.shape} (structured + embeddings)")
    
    model = train_model(X_train, y_train, X_val, y_val)
    
    train_acc = evaluate_model(model, X_train, y_train, "Training", encoders['label'])
    val_acc = evaluate_model(model, X_val, y_val, "Validation", encoders['label'])
    test_acc = evaluate_model(model, X_test, y_test, "Test", encoders['label'])
    
    save_model(model, encoders, embedding_model)
    
    print("\n=== Summary ===")
    print(f"Train Accuracy: {train_acc:.4f}")
    print(f"Validation Accuracy: {val_acc:.4f}")
    print(f"Test Accuracy: {test_acc:.4f}")
    print("\nHybrid model (XGBoost + Sentence Embeddings) trained successfully!")

if __name__ == "__main__":
    main()
