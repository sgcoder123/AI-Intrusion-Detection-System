# Project Structure

```
AI-Intrusion-Detection-System/
├── 📁 src/                           # Source code
│   ├── 🐍 __init__.py               # Package initialization
│   ├── 🔧 preprocess_data.py        # Data preprocessing pipeline
│   ├── 🚀 train_quick_rf.py         # Quick Random Forest training
│   ├── 🎯 train_advanced_rf.py      # Advanced Random Forest training
│   ├── 🧪 test_model.py             # Model testing on unseen data
│   ├── 📊 simple_test.py            # Simple model evaluation
│   └── 🚀 deploy_model.py           # Production deployment script
│
├── 📁 notebooks/                    # Jupyter notebooks
│   └── 📓 train_model.ipynb         # Interactive model training
│
├── 📁 data/                         # Dataset files (Git LFS)
│   ├── 📊 kdd_train.csv            # Raw training data
│   ├── 📊 kdd_test.csv             # Raw test data
│   ├── 🔧 kdd_train_processed.csv  # Processed training data
│   ├── 🔧 kdd_test_processed.csv   # Processed test data
│   ├── 📈 X_train.csv              # Training features
│   ├── 📈 X_val.csv                # Validation features
│   ├── 🎯 y_train.csv              # Training labels
│   └── 🎯 y_val.csv                # Validation labels
│
├── 📁 models/                       # Trained models (Git LFS)
│   ├── 🤖 random_forest_model.joblib       # Base model
│   ├── ⚡ random_forest_model_quick.joblib  # Quick trained model
│   └── 🎯 random_forest_model_tuned.joblib # Optimized model
│
├── 📁 tests/                        # Unit tests
│   └── 🧪 test_basic.py            # Basic functionality tests
│
├── 📄 README.md                     # Project documentation
├── 📄 requirements.txt              # Python dependencies
├── 📄 setup.py                      # Package setup configuration
├── 📄 Makefile                      # Development automation
├── 📄 .gitignore                    # Git ignore rules
├── 📄 .gitattributes                # Git LFS configuration
└── 📄 CLEANUP_SUMMARY.md           # Project cleanup documentation
```

## 📋 File Descriptions

### 🔧 Core Scripts
- **preprocess_data.py**: Converts raw KDD data into ML-ready format
- **train_quick_rf.py**: Fast training with good performance (11 seconds)
- **train_advanced_rf.py**: Comprehensive training with optimization (1+ hours)
- **deploy_model.py**: Production-ready inference script

### 🧪 Testing & Evaluation
- **test_model.py**: Comprehensive evaluation on test dataset
- **simple_test.py**: Quick performance check
- **test_basic.py**: Unit tests for basic functionality

### 📊 Data Pipeline
1. Raw data → `preprocess_data.py` → Processed data
2. Processed data → `train_*.py` → Trained models
3. Models → `test_model.py` → Performance metrics
4. Models → `deploy_model.py` → Production inference

### 🎯 Model Performance Summary
- **Quick Model**: 99.5% validation, 92% test accuracy (11 seconds training)
- **Tuned Model**: 99.5% validation accuracy (longer training)
- **Attack Detection**: 86.72% detection rate, 98.89% precision

### 🚀 Usage Commands
```bash
# Development setup
make install

# Data preprocessing
make preprocess

# Quick training
cd src && python train_quick_rf.py

# Testing
make test

# Deployment
cd src && python deploy_model.py
```
