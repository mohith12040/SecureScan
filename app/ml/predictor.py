import os
import joblib
import numpy as np

class SeverityPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.classes = ['Low', 'Medium', 'High', 'Critical']
        
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.model_path = os.path.join(self.base_dir, 'trained_models', 'model.joblib')
        self.scaler_path = os.path.join(self.base_dir, 'trained_models', 'scaler.joblib')
        
        self.load_model()
        
    def load_model(self):
        """Loads model and scaler, training them if they do not exist."""
        if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
            print("Model files missing. Launching automatic online model training...")
            try:
                from app.ml.train_model import train_severity_model
                train_severity_model()
            except Exception as e:
                print(f"Error training model: {e}")
                return
                
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            print("Successfully loaded ML model and Standard Scaler into application memory.")
        except Exception as e:
            print(f"Failed to load joblib files: {e}")
            self.model = None
            self.scaler = None

    def predict(self, open_ports_count, dangerous_ports_count, exposed_services_count, risk_score, has_critical_port, outdated_services_count):
        """
        Runs random forest prediction.
        Returns:
            predicted_severity (str): 'Low', 'Medium', 'High', or 'Critical'
            confidence (float): Probability score between 0.0 and 1.0
        """
        # Return fallback heuristic if model load failed
        if self.model is None or self.scaler is None:
            print("ML model unavailable. Applying emergency security heuristics...")
            # Fallback heuristics
            if risk_score >= 70 or has_critical_port:
                return 'Critical', 0.95
            elif risk_score >= 45:
                return 'High', 0.85
            elif risk_score >= 20:
                return 'Medium', 0.75
            else:
                return 'Low', 0.90
                
        # Format the features array exactly as trained
        features = np.array([[
            open_ports_count,
            dangerous_ports_count,
            exposed_services_count,
            risk_score,
            has_critical_port,
            outdated_services_count
        ]])
        
        try:
            # Scale features
            scaled_features = self.scaler.transform(features)
            
            # Run prediction and probability
            prediction_idx = self.model.predict(scaled_features)[0]
            probabilities = self.model.predict_proba(scaled_features)[0]
            
            predicted_severity = self.classes[prediction_idx]
            confidence = float(probabilities[prediction_idx])
            
            return predicted_severity, confidence
        except Exception as e:
            print(f"Prediction logic encountered error: {e}. Defaulting to safe indicators.")
            # Safety fallback
            if risk_score >= 70:
                return 'Critical', 0.99
            return 'Low', 0.50

# Global singleton instance for app-wide use
predictor = SeverityPredictor()
