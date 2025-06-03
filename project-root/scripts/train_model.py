# Train a machine learning model on the preprocessed data
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

# Paths
DATA_DIR = 'data'
MODEL_DIR = 'models'
X_TRAIN_FILE = os.path.join(DATA_DIR, 'X_train.csv')
Y_TRAIN_FILE = os.path.join(DATA_DIR, 'y_train.csv')
X_VAL_FILE = os.path.join(DATA_DIR, 'X_val.csv')
Y_VAL_FILE = os.path.join(DATA_DIR, 'y_val.csv')

# Load data
X_train = pd.read_csv(X_TRAIN_FILE)
y_train = pd.read_csv(Y_TRAIN_FILE).values.ravel()
X_val = pd.read_csv(X_VAL_FILE)
y_val = pd.read_csv(Y_VAL_FILE).values.ravel()

# Initialize and train model (Random Forest as example)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate on validation set
y_pred = clf.predict(X_val)
acc = accuracy_score(y_val, y_pred)
print(f"Validation Accuracy: {acc:.4f}")
print("Classification Report:")
print(classification_report(y_val, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_val, y_pred))

# Save the trained model
os.makedirs(MODEL_DIR, exist_ok=True)
model_path = os.path.join(MODEL_DIR, 'random_forest_model.joblib')
joblib.dump(clf, model_path)
print(f"Trained model saved to {model_path}")
