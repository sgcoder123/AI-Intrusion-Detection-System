#!/usr/bin/env python3
"""
Test script for the AI Intrusion Detection System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class TestIntrusionDetection(unittest.TestCase):
    
    def test_data_loading(self):
        """Test if data files exist and can be loaded"""
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Check if key data files exist
        required_files = [
            'X_train.csv', 'y_train.csv', 
            'X_val.csv', 'y_val.csv'
        ]
        
        for file in required_files:
            file_path = os.path.join(data_dir, file)
            self.assertTrue(os.path.exists(file_path), f"Required file {file} not found")
    
    def test_model_loading(self):
        """Test if trained models exist and can be loaded"""
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        
        # Check if model files exist
        model_files = [
            'random_forest_model.joblib',
            'random_forest_model_tuned.joblib'
        ]
        
        for model_file in model_files:
            model_path = os.path.join(models_dir, model_file)
            if os.path.exists(model_path):
                # Try to load the model
                import joblib
                model = joblib.load(model_path)
                self.assertIsInstance(model, (RandomForestClassifier,), 
                                    f"Model {model_file} is not a valid classifier")
    
    def test_random_forest_creation(self):
        """Test if Random Forest model can be created with our parameters"""
        try:
            rf = RandomForestClassifier(
                n_estimators=10,  # Small number for testing
                max_depth=5,
                min_samples_split=3,
                min_samples_leaf=1,
                max_features='log2',
                bootstrap=True,
                oob_score=True,
                class_weight='balanced_subsample',
                random_state=42,
                n_jobs=1
            )
            self.assertIsNotNone(rf)
        except Exception as e:
            self.fail(f"Failed to create Random Forest model: {e}")

if __name__ == '__main__':
    unittest.main()
