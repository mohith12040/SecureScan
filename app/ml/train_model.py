import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from app.ml.dataset_generator import generate_vulnerability_dataset

def train_severity_model():
    # Setup directories
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dataset_path = os.path.join(base_dir, 'dataset', 'vulnerability_dataset.csv')
    model_path = os.path.join(base_dir, 'trained_models', 'model.joblib')
    scaler_path = os.path.join(base_dir, 'trained_models', 'scaler.joblib')
    metrics_path = os.path.join(base_dir, 'trained_models', 'metrics.txt')
    
    # Generate dataset if missing
    if not os.path.exists(dataset_path):
        generate_vulnerability_dataset(dataset_path)
        
    # Load dataset
    df = pd.read_csv(dataset_path)
    
    # Split features and target
    X = df.drop(columns=['severity'])
    y = df['severity']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Initialize Random Forest Classifier
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_split=5,
        class_weight='balanced',
        random_state=42
    )
    
    # Train the model
    print("Training Random Forest Classifier on vulnerability dataset...")
    model.fit(X_train_scaled, y_train)
    
    # Evaluation
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    class_report = classification_report(
        y_test, 
        y_pred, 
        target_names=['Low', 'Medium', 'High', 'Critical']
    )
    
    print("\nModel Training Complete!")
    print(f"Test Accuracy Score: {accuracy:.4f}")
    print("\nConfusion Matrix:")
    print(conf_matrix)
    print("\nClassification Report:")
    print(class_report)
    
    # Save the model artifacts
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\nTrained model saved to: {model_path}")
    print(f"StandardScaler saved to: {scaler_path}")
    
    # Write metrics log
    with open(metrics_path, 'w') as f:
        f.write("SECURESCAN MODEL TRAINING METRICS\n")
        f.write("=================================\n\n")
        f.write(f"Overall Accuracy: {accuracy:.5%}\n\n")
        f.write("Confusion Matrix:\n")
        f.write(np.array2string(conf_matrix) + "\n\n")
        f.write("Classification Report:\n")
        f.write(class_report + "\n")
        
    print(f"Metrics logs generated at: {metrics_path}")

if __name__ == '__main__':
    train_severity_model()
