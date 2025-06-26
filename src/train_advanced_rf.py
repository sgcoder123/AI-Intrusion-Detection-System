#!/usr/bin/env python3
"""
Advanced Random Forest Training with Additional Optimizations
This script implements additional techniques to maximize accuracy beyond the basic optimized model.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.under_sampling import EditedNearestNeighbours, TomekLinks
from imblearn.combine import SMOTEENN, SMOTETomek
import joblib
import os
import time
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(42)

def load_data():
    """Load the preprocessed training and validation data."""
    print("Loading preprocessed data...")
    
    # Try relative path first, then absolute path
    possible_data_dirs = [
        '../data/',  # When running from src/
        'data/',     # When running from project root
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')  # Absolute fallback
    ]
    
    DATA_DIR = None
    for data_dir in possible_data_dirs:
        if os.path.exists(os.path.join(data_dir, 'X_train.csv')):
            DATA_DIR = data_dir
            break
    
    if DATA_DIR is None:
        raise FileNotFoundError("Could not find data directory with required files")
    
    print(f"Using data directory: {DATA_DIR}")
    X_train = pd.read_csv(os.path.join(DATA_DIR, 'X_train.csv'))
    y_train = pd.read_csv(os.path.join(DATA_DIR, 'y_train.csv')).values.ravel()
    X_val = pd.read_csv(os.path.join(DATA_DIR, 'X_val.csv'))
    y_val = pd.read_csv(os.path.join(DATA_DIR, 'y_val.csv')).values.ravel()
    
    return X_train, y_train, X_val, y_val

def advanced_class_balancing(X_train, y_train):
    """Apply advanced class balancing techniques."""
    print("\n=== Advanced Class Balancing ===")
    
    # Remove classes with very few samples
    unique, counts = np.unique(y_train, return_counts=True)
    classes_to_keep = unique[counts > 1]
    mask = np.isin(y_train, classes_to_keep)
    X_train_filtered = X_train[mask]
    y_train_filtered = y_train[mask]
    
    print(f"Removed {len(unique) - len(classes_to_keep)} classes with ≤1 samples")
    
    # Use SMOTE + Tomek Links for better boundary cleaning
    print("Applying SMOTE + Tomek Links...")
    
    smote_tomek = SMOTETomek(
        smote=SMOTE(random_state=42, k_neighbors=1),
        tomek=TomekLinks(),
        random_state=42
    )
    
    X_resampled, y_resampled = smote_tomek.fit_resample(X_train_filtered, y_train_filtered)
    
    print(f"After SMOTE + Tomek Links: {X_resampled.shape[0]} samples")
    
    # Limit total samples to prevent memory issues
    max_samples = 100000
    if len(X_resampled) > max_samples:
        print(f"Limiting to {max_samples} samples for memory efficiency...")
        indices = np.random.RandomState(42).choice(len(X_resampled), max_samples, replace=False)
        X_resampled = X_resampled[indices]
        y_resampled = y_resampled[indices]
    
    final_dist = pd.Series(y_resampled).value_counts().sort_index()
    print(f"Final number of classes: {len(final_dist)}")
    print(f"Total samples: {len(X_resampled)}")
    
    return X_resampled, y_resampled

def create_ultra_optimized_rf():
    """Create an ultra-optimized Random Forest with advanced settings."""
    print("\n=== Creating Ultra-Optimized Random Forest ===")
    
    rf = RandomForestClassifier(
        n_estimators=1000,          # More trees for better performance
        max_depth=25,               # Slightly deeper trees
        min_samples_split=3,        # More strict splitting
        min_samples_leaf=1,         # Allow smaller leaves for better detail
        max_features='log2',        # Use log2 for more randomness
        bootstrap=True,
        oob_score=True,
        class_weight='balanced_subsample',  # Better balancing per tree
        criterion='gini',           # Gini impurity
        max_samples=0.8,           # Use 80% of samples per tree
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    print("Ultra-optimized Random Forest parameters:")
    print(f"  n_estimators: {rf.n_estimators}")
    print(f"  max_depth: {rf.max_depth}")
    print(f"  min_samples_split: {rf.min_samples_split}")
    print(f"  min_samples_leaf: {rf.min_samples_leaf}")
    print(f"  max_features: {rf.max_features}")
    print(f"  class_weight: {rf.class_weight}")
    print(f"  max_samples: {rf.max_samples}")
    
    return rf

def create_extra_trees():
    """Create an Extra Trees classifier as an alternative."""
    print("\n=== Creating Extra Trees Classifier ===")
    
    et = ExtraTreesClassifier(
        n_estimators=800,
        max_depth=30,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features='sqrt',
        bootstrap=False,  # Extra Trees uses all samples
        class_weight='balanced_subsample',
        criterion='gini',
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    return et

def train_and_compare_models(X_train, y_train, X_val, y_val):
    """Train both models and compare performance."""
    print("\n=== Training and Comparing Models ===")
    
    models = {
        'Ultra-Optimized Random Forest': create_ultra_optimized_rf(),
        'Extra Trees': create_extra_trees()
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        start_time = time.time()
        
        model.fit(X_train, y_train)
        training_time = time.time() - start_time
        
        y_pred = model.predict(X_val)
        accuracy = accuracy_score(y_val, y_pred)
        f1_weighted = f1_score(y_val, y_pred, average='weighted')
        f1_macro = f1_score(y_val, y_pred, average='macro')
        
        if hasattr(model, 'oob_score_'):
            oob_score = model.oob_score_
        else:
            oob_score = None
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'f1_weighted': f1_weighted,
            'f1_macro': f1_macro,
            'oob_score': oob_score,
            'training_time': training_time,
            'predictions': y_pred
        }
        
        print(f"Training time: {training_time:.2f} seconds")
        if oob_score:
            print(f"Out-of-bag score: {oob_score:.4f}")
        print(f"Validation accuracy: {accuracy:.4f}")
        print(f"F1-weighted: {f1_weighted:.4f}")
        print(f"F1-macro: {f1_macro:.4f}")
    
    return results

def select_best_model(results):
    """Select the best performing model."""
    print("\n=== Model Comparison ===")
    
    best_name = None
    best_accuracy = 0
    
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Accuracy: {result['accuracy']:.4f}")
        print(f"  F1-weighted: {result['f1_weighted']:.4f}")
        print(f"  F1-macro: {result['f1_macro']:.4f}")
        if result['oob_score']:
            print(f"  OOB Score: {result['oob_score']:.4f}")
        print(f"  Training time: {result['training_time']:.2f}s")
        
        if result['accuracy'] > best_accuracy:
            best_accuracy = result['accuracy']
            best_name = name
    
    print(f"\n🏆 Best Model: {best_name} (Accuracy: {best_accuracy:.4f})")
    
    return best_name, results[best_name]

def save_best_model(best_result, model_name):
    """Save the best performing model."""
    print(f"\n=== Saving Best Model ===")
    
    # Try relative path first, then absolute path
    possible_model_dirs = [
        '../models/',  # When running from src/
        'models/',     # When running from project root
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')  # Absolute fallback
    ]
    
    MODEL_DIR = None
    for model_dir in possible_model_dirs:
        if os.path.exists(os.path.dirname(model_dir)) or model_dir == '../models/':
            MODEL_DIR = model_dir
            break
    
    if MODEL_DIR is None:
        MODEL_DIR = 'models/'  # Default fallback
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, model_name)
    
    joblib.dump(best_result['model'], model_path)
    print(f"Best model saved to: {model_path}")
    
    return model_path

def generate_detailed_report(best_name, best_result, y_val):
    """Generate a detailed performance report."""
    print(f"\n=== Detailed Performance Report for {best_name} ===")
    
    y_pred = best_result['predictions']
    
    print("\nClassification Report:")
    print(classification_report(y_val, y_pred))
    
    # Feature importance (if available)
    if hasattr(best_result['model'], 'feature_importances_'):
        print("\nTop 15 Most Important Features:")
        feature_names = [f"feature_{i}" for i in range(len(best_result['model'].feature_importances_))]
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': best_result['model'].feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.head(15).iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")

def main():
    """Main advanced training pipeline."""
    print("=" * 70)
    print("ADVANCED RANDOM FOREST INTRUSION DETECTION TRAINING")
    print("=" * 70)
    
    # Load data
    X_train, y_train, X_val, y_val = load_data()
    
    # Advanced class balancing
    X_train_balanced, y_train_balanced = advanced_class_balancing(X_train, y_train)
    
    # Train and compare models
    results = train_and_compare_models(X_train_balanced, y_train_balanced, X_val, y_val)
    
    # Select best model
    best_name, best_result = select_best_model(results)
    
    # Save the best model
    model_path = save_best_model(best_result, 'random_forest_model_tuned.joblib')
    
    # Generate detailed report
    generate_detailed_report(best_name, best_result, y_val)
    
    print("\n" + "=" * 70)
    print("ADVANCED TRAINING COMPLETED SUCCESSFULLY!")
    print(f"Best Model: {best_name}")
    print(f"Final Validation Accuracy: {best_result['accuracy']:.4f}")
    print(f"Model saved to: {model_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
