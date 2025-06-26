import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os

# Paths
DATA_DIR = '../data'
TRAIN_FILE = os.path.join(DATA_DIR, 'kdd_train.csv')
TEST_FILE = os.path.join(DATA_DIR, 'kdd_test.csv')
PROCESSED_DIR = DATA_DIR  # You can change this if you want a separate folder

# Load datasets
train_df = pd.read_csv(TRAIN_FILE)
test_df = pd.read_csv(TEST_FILE)

# Combine for consistent encoding
full_df = pd.concat([train_df, test_df], ignore_index=True)

# Identify categorical columns (adjust as needed for your dataset)
categorical_cols = ['protocol_type', 'service', 'flag']

# Encode categorical columns
for col in categorical_cols:
    le = LabelEncoder()
    full_df[col] = le.fit_transform(full_df[col])

# Split back into train and test
train_df = full_df.iloc[:len(train_df)]
test_df = full_df.iloc[len(train_df):]

# Identify feature columns (exclude label/target columns)
label_col = 'label' if 'label' in train_df.columns else train_df.columns[-1]
feature_cols = [col for col in train_df.columns if col != label_col]

# Scale features
scaler = StandardScaler()
train_df[feature_cols] = scaler.fit_transform(train_df[feature_cols])
test_df[feature_cols] = scaler.transform(test_df[feature_cols])

# Save processed data
train_df.to_csv(os.path.join(PROCESSED_DIR, 'kdd_train_processed.csv'), index=False)
test_df.to_csv(os.path.join(PROCESSED_DIR, 'kdd_test_processed.csv'), index=False)

# Optionally, split train into train/val sets
X = train_df[feature_cols]
y = train_df[label_col]
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

X_train.to_csv(os.path.join(PROCESSED_DIR, 'X_train.csv'), index=False)
X_val.to_csv(os.path.join(PROCESSED_DIR, 'X_val.csv'), index=False)
y_train.to_csv(os.path.join(PROCESSED_DIR, 'y_train.csv'), index=False)
y_val.to_csv(os.path.join(PROCESSED_DIR, 'y_val.csv'), index=False)

print("Preprocessing complete. Processed files saved in the data directory.")