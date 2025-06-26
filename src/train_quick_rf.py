#!/usr/bin/env python3
"""
Quick Random Forest Training - Optimized for Speed
This script provides a balance between accuracy and training time.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from imblearn.over_sampling import SMOTE
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
    
    DATA_DIR = '../data/'
    X_train = pd.read_csv(os.path.join(DATA_DIR, 'X_train.csv'))
    y_train = pd.read_csv(os.path.join(DATA_DIR, 'y_train.csv')).values.ravel()
    X_val = pd.read_csv(os.path.join(DATA_DIR, 'X_val.csv'))
    y_val = pd.read_csv(os.path.join(DATA_DIR, 'y_val.csv')).values.ravel()
    
    return X_train, y_train, X_val, y_val

def quick_class_balancing(X_train, y_train, max_samples=50000):
    """Apply fast class balancing with sample limiting."""
    print("\n=== Quick Class Balancing ===")
    
    # First, limit dataset size for speed
    if len(X_train) > max_samples:
        print(f"Limiting to {max_samples} samples for speed...")
        indices = np.random.RandomState(42).choice(len(X_train), max_samples, replace=False)
        X_train = X_train.iloc[indices]
        y_train = y_train[indices]
    
    # Remove classes with very few samples
    unique, counts = np.unique(y_train, return_counts=True)
    classes_to_keep = unique[counts > 2]  # Keep classes with >2 samples
    mask = np.isin(y_train, classes_to_keep)
    X_train_filtered = X_train[mask]
    y_train_filtered = y_train[mask]
    
    print(f"Removed {len(unique) - len(classes_to_keep)} classes with ≤2 samples")
    
    # Use simple SMOTE (no Tomek Links for speed)
    print("Applying SMOTE...")
    smote = SMOTE(random_state=42, k_neighbors=1)
    X_resampled, y_resampled = smote.fit_resample(X_train_filtered, y_train_filtered)
    
    # Limit final samples to prevent memory issues
    max_final = 75000
    if len(X_resampled) > max_final:
        print(f"Limiting final dataset to {max_final} samples...")
        indices = np.random.RandomState(42).choice(len(X_resampled), max_final, replace=False)
        X_resampled = X_resampled.iloc[indices] if hasattr(X_resampled, 'iloc') else X_resampled[indices]
        y_resampled = y_resampled[indices]
    
    print(f"Final dataset: {len(X_resampled)} samples, {len(np.unique(y_resampled))} classes")
    
    return X_resampled, y_resampled

def create_quick_rf():
    """Create a quick Random Forest for fast training."""
    print("\n=== Creating Quick Random Forest ===")
    
    rf = RandomForestClassifier(
        n_estimators=200,           # Reduced from 1000
        max_depth=15,               # Reduced depth
        min_samples_split=5,        # Less splitting
        min_samples_leaf=2,         # Larger leaves
        max_features='sqrt',        # Faster than log2
        bootstrap=True,
        oob_score=True,
        class_weight='balanced',    # Simple balancing
        random_state=42,
        n_jobs=-1,                  # Use all cores
        verbose=1
    )
    
    print("Quick Random Forest parameters:")
    print(f"  n_estimators: {rf.n_estimators}")
    print(f"  max_depth: {rf.max_depth}")
    print(f"  min_samples_split: {rf.min_samples_split}")
    print(f"  min_samples_leaf: {rf.min_samples_leaf}")
    print(f"  max_features: {rf.max_features}")
    
    return rf

def main():
    """Main quick training pipeline."""
    print("=" * 60)
    print("QUICK RANDOM FOREST INTRUSION DETECTION TRAINING")
    print("=" * 60)
    
    start_time = time.time()
    
    # Load data
    X_train, y_train, X_val, y_val = load_data()
    print(f"Original dataset: {len(X_train)} training samples")
    
    # Quick class balancing
    X_train_balanced, y_train_balanced = quick_class_balancing(X_train, y_train)
    
    # Create and train model
    rf = create_quick_rf()
    
    print("\n=== Training Model ===")
    train_start = time.time()
    rf.fit(X_train_balanced, y_train_balanced)
    train_time = time.time() - train_start
    
    print(f"Training completed in {train_time:.2f} seconds")
    print(f"Out-of-bag score: {rf.oob_score_:.4f}")
    
    # Evaluate on validation set
    print("\n=== Evaluating Model ===")
    y_pred = rf.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)
    f1_weighted = f1_score(y_val, y_pred, average='weighted')
    f1_macro = f1_score(y_val, y_pred, average='macro')
    
    print(f"Validation Accuracy: {accuracy:.4f}")
    print(f"F1-weighted: {f1_weighted:.4f}")
    print(f"F1-macro: {f1_macro:.4f}")
    
    # Save model
    MODEL_DIR = '../models/'
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, 'random_forest_model_quick.joblib')
    joblib.dump(rf, model_path)
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("QUICK TRAINING COMPLETED!")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Final Accuracy: {accuracy:.4f}")
    print(f"Model saved to: {model_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
