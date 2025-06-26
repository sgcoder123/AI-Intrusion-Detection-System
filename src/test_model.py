#!/usr/bin/env python3
"""
Test the trained model on unseen test data
This script evaluates model performance on data that was never used during training.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
import joblib
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_test_data():
    """Load the preprocessed test data."""
    print("Loading test data...")
    
    DATA_DIR = '../data/'
    
    # Check what test files we have
    test_files = [
        'kdd_test_processed.csv',  # Processed test data
        'kdd_test.csv'             # Raw test data
    ]
    
    for file in test_files:
        file_path = os.path.join(DATA_DIR, file)
        if os.path.exists(file_path):
            print(f"Found test file: {file}")
    
    # Load processed test data
    test_processed_path = os.path.join(DATA_DIR, 'kdd_test_processed.csv')
    if os.path.exists(test_processed_path):
        print("Loading processed test data...")
        test_data = pd.read_csv(test_processed_path)
        
        # Separate features and labels (assuming last column is the label)
        X_test = test_data.iloc[:, :-1]
        y_test = test_data.iloc[:, -1]
        
        print(f"Test data shape: {X_test.shape}")
        print(f"Test labels shape: {y_test.shape}")
        print(f"Classes in test data: {sorted(y_test.unique())}")
        
        return X_test, y_test
    else:
        raise FileNotFoundError("Processed test data not found. Please run preprocessing first.")

def load_model(model_name):
    """Load a trained model."""
    MODEL_DIR = '../models/'
    model_path = os.path.join(MODEL_DIR, model_name)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    print(f"Loading model: {model_name}")
    model = joblib.load(model_path)
    print(f"✅ Model loaded successfully!")
    
    return model

def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate the model on test data."""
    print(f"\n=== Evaluating {model_name} on Test Data ===")
    
    # Make predictions
    start_time = time.time()
    y_pred = model.predict(X_test)
    prediction_time = time.time() - start_time
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    f1_macro = f1_score(y_test, y_pred, average='macro')
    
    # Print results
    print(f"📊 Test Results for {model_name}:")
    print(f"  🎯 Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  📈 F1-Score (weighted): {f1_weighted:.4f}")
    print(f"  📈 F1-Score (macro): {f1_macro:.4f}")
    print(f"  ⏱️  Prediction time: {prediction_time:.3f} seconds")
    print(f"  🔢 Test samples: {len(y_test):,}")
    
    return {
        'model_name': model_name,
        'accuracy': accuracy,
        'f1_weighted': f1_weighted,
        'f1_macro': f1_macro,
        'prediction_time': prediction_time,
        'predictions': y_pred
    }

def generate_detailed_report(y_test, y_pred, model_name):
    """Generate detailed classification report."""
    print(f"\n=== Detailed Classification Report for {model_name} ===")
    
    # Classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    print("\n📋 Per-Class Performance:")
    print(classification_report(y_test, y_pred))
    
    # Attack detection rates
    print("\n🔍 Attack Detection Analysis:")
    
    # Convert to binary classification (normal vs attack)
    y_test_binary = (y_test != 'normal').astype(int)
    y_pred_binary = (y_pred != 'normal').astype(int)
    
    from sklearn.metrics import precision_recall_fscore_support
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test_binary, y_pred_binary, average='binary'
    )
    
    print(f"  Attack Detection Rate (Recall): {recall:.4f} ({recall*100:.2f}%)")
    print(f"  Attack Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"  Attack F1-Score: {f1:.4f}")
    
    # False positive/negative analysis
    normal_mask = (y_test == 'normal')
    attack_mask = ~normal_mask
    
    true_positives = np.sum((y_pred_binary == 1) & (y_test_binary == 1))
    false_positives = np.sum((y_pred_binary == 1) & (y_test_binary == 0))
    false_negatives = np.sum((y_pred_binary == 0) & (y_test_binary == 1))
    true_negatives = np.sum((y_pred_binary == 0) & (y_test_binary == 0))
    
    print(f"\n📊 Confusion Matrix (Binary):")
    print(f"  True Positives (Attacks detected): {true_positives:,}")
    print(f"  False Positives (Normal flagged as attack): {false_positives:,}")
    print(f"  False Negatives (Attacks missed): {false_negatives:,}")
    print(f"  True Negatives (Normal correctly identified): {true_negatives:,}")
    
    return report

def compare_models():
    """Compare performance of all available models."""
    print("\n=== Comparing All Available Models ===")
    
    # Load test data
    X_test, y_test = load_test_data()
    
    # Available models
    models_to_test = [
        'random_forest_model_quick.joblib',
        'random_forest_model_tuned.joblib',
        'random_forest_model.joblib'
    ]
    
    results = []
    
    for model_file in models_to_test:
        try:
            model = load_model(model_file)
            result = evaluate_model(model, X_test, y_test, model_file.replace('.joblib', ''))
            
            # Generate detailed report for the best performing model
            if model_file == 'random_forest_model_quick.joblib':
                generate_detailed_report(y_test, result['predictions'], result['model_name'])
            
            results.append(result)
            
        except FileNotFoundError:
            print(f"⚠️  Model not found: {model_file}")
            continue
        except Exception as e:
            print(f"❌ Error testing {model_file}: {e}")
            continue
    
    # Summary comparison
    if results:
        print("\n" + "="*80)
        print("🏆 MODEL COMPARISON SUMMARY")
        print("="*80)
        
        best_accuracy = 0
        best_model = None
        
        for result in results:
            print(f"\n📊 {result['model_name']}:")
            print(f"   Accuracy: {result['accuracy']:.4f} ({result['accuracy']*100:.2f}%)")
            print(f"   F1-weighted: {result['f1_weighted']:.4f}")
            print(f"   F1-macro: {result['f1_macro']:.4f}")
            print(f"   Speed: {result['prediction_time']:.3f}s")
            
            if result['accuracy'] > best_accuracy:
                best_accuracy = result['accuracy']
                best_model = result['model_name']
        
        print(f"\n🥇 Best Model: {best_model}")
        print(f"🎯 Best Accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
        
        # Save test results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"../data/test_results_{timestamp}.txt"
        
        with open(results_file, 'w') as f:
            f.write("AI Intrusion Detection System - Test Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Test Samples: {len(y_test):,}\n\n")
            
            for result in results:
                f.write(f"Model: {result['model_name']}\n")
                f.write(f"Accuracy: {result['accuracy']:.4f}\n")
                f.write(f"F1-weighted: {result['f1_weighted']:.4f}\n")
                f.write(f"F1-macro: {result['f1_macro']:.4f}\n")
                f.write(f"Prediction time: {result['prediction_time']:.3f}s\n\n")
            
            f.write(f"Best Model: {best_model}\n")
            f.write(f"Best Accuracy: {best_accuracy:.4f}\n")
        
        print(f"\n💾 Results saved to: {results_file}")

def main():
    """Main testing function."""
    print("🧪 AI INTRUSION DETECTION SYSTEM - TEST EVALUATION")
    print("=" * 60)
    
    try:
        compare_models()
        
        print("\n" + "="*60)
        print("✅ TEST EVALUATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
