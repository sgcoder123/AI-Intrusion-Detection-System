# AI Intrusion Detection System

An advanced machine learning-based intrusion detection system using Random Forest and Extra Trees classifiers with optimized data preprocessing and class balancing techniques.

## 🚀 Features

- **Advanced Data Preprocessing**: Comprehensive data cleaning and feature engineering
- **Class Balancing**: SMOTE + Tomek Links for handling imbalanced datasets
- **Multiple Models**: Random Forest and Extra Trees classifiers
- **Hyperparameter Optimization**: Automated model selection and tuning
- **Performance Monitoring**: Detailed accuracy metrics and classification reports
- **Production Ready**: Serialized models for deployment

## 📁 Project Structure

```
AI-Intrusion-Detection-System/
├── src/                          # Source code
│   ├── preprocess_data.py        # Data preprocessing pipeline
│   └── train_advanced_rf.py      # Advanced model training
├── notebooks/                    # Jupyter notebooks
│   └── train_model.ipynb         # Model training notebook
├── data/                         # Dataset files
│   ├── kdd_train.csv            # Raw training data
│   ├── kdd_test.csv             # Raw test data
│   ├── kdd_train_processed.csv  # Processed training data
│   ├── kdd_test_processed.csv   # Processed test data
│   ├── X_train.csv              # Training features
│   ├── X_val.csv                # Validation features
│   ├── y_train.csv              # Training labels
│   └── y_val.csv                # Validation labels
├── models/                       # Trained models
│   ├── random_forest_model.joblib      # Base Random Forest model
│   └── random_forest_model_tuned.joblib # Optimized model
├── docs/                         # Documentation
├── tests/                        # Unit tests
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AI-Intrusion-Detection-System
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### 1. Data Preprocessing
```bash
cd src
python preprocess_data.py
```

### 2. Train Advanced Model
```bash
cd src
python train_advanced_rf.py
```

### 3. Using Jupyter Notebook
```bash
jupyter lab notebooks/train_model.ipynb
```

## 📊 Model Performance

The system uses advanced techniques to achieve high accuracy:

- **SMOTE + Tomek Links**: For balanced class distribution
- **Random Forest**: 1000 estimators with optimized parameters
- **Extra Trees**: Alternative ensemble method for comparison
- **Cross-validation**: Robust performance estimation
- **Feature importance**: Automatic feature ranking

### Key Hyperparameters

**Ultra-Optimized Random Forest**:
- `n_estimators`: 1000
- `max_depth`: 25
- `min_samples_split`: 3
- `max_features`: 'log2'
- `class_weight`: 'balanced_subsample'

**Extra Trees Classifier**:
- `n_estimators`: 800
- `max_depth`: 30
- `max_features`: 'sqrt'
- `bootstrap`: False

## 🔧 Advanced Usage

### Custom Model Training

```python
from src.train_advanced_rf import (
    load_data, 
    advanced_class_balancing, 
    create_ultra_optimized_rf
)

# Load and balance data
X_train, y_train, X_val, y_val = load_data()
X_balanced, y_balanced = advanced_class_balancing(X_train, y_train)

# Train model
model = create_ultra_optimized_rf()
model.fit(X_balanced, y_balanced)
```

### Model Evaluation

The system provides comprehensive evaluation metrics:
- **Accuracy Score**: Overall classification accuracy
- **F1-Score**: Weighted and macro averages
- **Classification Report**: Per-class precision, recall, F1
- **Out-of-Bag Score**: Cross-validation estimate
- **Feature Importance**: Top contributing features

## 📈 Dataset

The system is designed for the KDD Cup 1999 dataset:
- **Training**: ~4.9M network connection records
- **Testing**: ~300K network connection records
- **Features**: 41 features including protocol, service, flag, etc.
- **Classes**: Normal vs. various attack types (DoS, Probe, R2L, U2R)

## 🔍 Model Selection

The system automatically:
1. Trains multiple model variants
2. Compares performance metrics
3. Selects the best performing model
4. Saves the optimal model for deployment

## 📝 Requirements

- Python 3.8+
- scikit-learn
- pandas
- numpy
- imbalanced-learn
- matplotlib
- seaborn
- joblib

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 🏆 Performance Highlights

- ✅ Thorough grid search with HyperParameterGridSearchCV
- ✅ Advanced class balancing with SMOTE + Tomek Links
- ✅ Multiple ensemble methods comparison
- ✅ Automated hyperparameter optimization
- ✅ Memory-efficient processing for large datasets
- ✅ Production-ready model serialization
- ✅ Comprehensive performance reporting

## 📞 Support

For questions or issues, please open an issue in the GitHub repository.

---

**Built with ❤️ for cybersecurity and machine learning**
