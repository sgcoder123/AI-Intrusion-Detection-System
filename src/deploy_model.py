#!/usr/bin/env python3
"""
Model Deployment Script for AI Intrusion Detection System
"""

import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime

class IntrusionDetector:
    """Production-ready intrusion detection classifier"""
    
    def __init__(self, model_path=None):
        """Initialize the detector with a trained model"""
        if model_path is None:
            # Use the tuned model by default
            model_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'models', 
                'random_forest_model_tuned.joblib'
            )
        
        self.model = self._load_model(model_path)
        self.feature_names = None
        
    def _load_model(self, model_path):
        """Load the trained model"""
        try:
            model = joblib.load(model_path)
            print(f"✅ Model loaded successfully from {model_path}")
            return model
        except Exception as e:
            raise Exception(f"❌ Failed to load model: {e}")
    
    def predict(self, X):
        """Make predictions on new data"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X) if hasattr(self.model, 'predict_proba') else None
        
        return predictions, probabilities
    
    def predict_single(self, connection_data):
        """Predict a single network connection"""
        if isinstance(connection_data, (list, tuple)):
            connection_data = np.array(connection_data).reshape(1, -1)
        elif isinstance(connection_data, pd.Series):
            connection_data = connection_data.values.reshape(1, -1)
        
        prediction, probability = self.predict(connection_data)
        
        result = {
            'prediction': prediction[0],
            'is_attack': prediction[0] != 'normal',
            'confidence': np.max(probability[0]) if probability is not None else None,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def get_model_info(self):
        """Get information about the loaded model"""
        info = {
            'model_type': type(self.model).__name__,
            'n_estimators': getattr(self.model, 'n_estimators', 'N/A'),
            'max_depth': getattr(self.model, 'max_depth', 'N/A'),
            'n_features': getattr(self.model, 'n_features_in_', 'N/A'),
            'classes': getattr(self.model, 'classes_', 'N/A')
        }
        return info

def main():
    """Demo usage of the intrusion detector"""
    print("🚀 AI Intrusion Detection System - Deployment Demo")
    print("=" * 50)
    
    try:
        # Initialize detector
        detector = IntrusionDetector()
        
        # Show model info
        info = detector.get_model_info()
        print(f"📊 Model Type: {info['model_type']}")
        print(f"🌳 Estimators: {info['n_estimators']}")
        print(f"📏 Max Depth: {info['max_depth']}")
        print(f"🔢 Features: {info['n_features']}")
        print(f"🏷️  Classes: {len(info['classes']) if hasattr(info['classes'], '__len__') else 'N/A'}")
        
        # Test with validation data if available
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        val_file = os.path.join(data_dir, 'X_val.csv')
        
        if os.path.exists(val_file):
            print(f"\n🧪 Testing with validation data...")
            X_val = pd.read_csv(val_file)
            
            # Test on first 5 samples
            test_samples = X_val.head(5)
            predictions, probabilities = detector.predict(test_samples)
            
            print("📋 Sample Predictions:")
            for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                max_prob = np.max(prob) if prob is not None else 'N/A'
                print(f"  Sample {i+1}: {pred} (confidence: {max_prob:.3f})")
        
        print("\n✅ Deployment test completed successfully!")
        
    except Exception as e:
        print(f"❌ Deployment test failed: {e}")

if __name__ == "__main__":
    main()
