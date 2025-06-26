#!/usr/bin/env python3
"""
Simple test script for model evaluation
"""

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report
import joblib
import sys
import os

def main():
    print("🧪 Testing Model on Unseen Data")
    print("=" * 40)
    
    try:
        # Load test data
        print("1. Loading test data...")
        test_data = pd.read_csv('../data/kdd_test_processed.csv')
        
        # Separate features and labels
        X_test = test_data.iloc[:, :-1]  # All columns except last
        y_test = test_data.iloc[:, -1]   # Last column (labels)
        
        print(f"   Test samples: {len(X_test):,}")
        print(f"   Features: {X_test.shape[1]}")
        print(f"   Unique classes: {len(y_test.unique())}")
        
        # Load model
        print("2. Loading trained model...")
        model = joblib.load('../models/random_forest_model_quick.joblib')
        print("   ✅ Model loaded successfully!")
        
        # Make predictions
        print("3. Making predictions...")
        y_pred = model.predict(X_test)
        
        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        
        print("\n📊 TEST RESULTS:")
        print(f"   🎯 Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Show distribution of predictions
        print(f"\n📋 Prediction Summary:")
        pred_counts = pd.Series(y_pred).value_counts()
        for label, count in pred_counts.head(10).items():
            percentage = (count / len(y_pred)) * 100
            print(f"   {label}: {count:,} ({percentage:.1f}%)")
        
        # Binary classification (attack vs normal)
        normal_count = np.sum(y_test == 'normal')
        attack_count = len(y_test) - normal_count
        
        normal_pred = np.sum(y_pred == 'normal')
        attack_pred = len(y_pred) - normal_pred
        
        print(f"\n🔍 Attack Detection:")
        print(f"   Actual Normal: {normal_count:,}")
        print(f"   Actual Attacks: {attack_count:,}")
        print(f"   Predicted Normal: {normal_pred:,}")
        print(f"   Predicted Attacks: {attack_pred:,}")
        
        # Attack detection rate
        y_test_binary = (y_test != 'normal').astype(int)
        y_pred_binary = (y_pred != 'normal').astype(int)
        
        from sklearn.metrics import precision_recall_fscore_support
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test_binary, y_pred_binary, average='binary'
        )
        
        print(f"   Attack Detection Rate: {recall:.4f} ({recall*100:.2f}%)")
        print(f"   Attack Precision: {precision:.4f} ({precision*100:.2f}%)")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
