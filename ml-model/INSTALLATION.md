# 🚀 INSTALLATION GUIDE - Elite Phishing Detection ML Model

## Prerequisites

- **Python 3.11+** (recommended)
- **8GB RAM minimum** (16GB recommended for training)
- **10GB disk space** for data and models
- **Internet connection** for downloading training data

## Step-by-Step Installation

### 1. Navigate to ML Model Directory

```bash
cd "c:\Users\Sri Vishnu\Extension\ml-model"
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activate (Git Bash)
source venv/Scripts/activate
```

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Install Dependencies

```bash
# Install all required packages (this will take 5-10 minutes)
pip install -r requirements.txt
```

#### If you encounter errors, install in stages:

```bash
# Stage 1: Core ML libraries
pip install numpy pandas scipy scikit-learn

# Stage 2: ML frameworks
pip install tensorflow torch xgboost lightgbm

# Stage 3: Feature extraction
pip install tldextract dnspython python-whois beautifulsoup4 requests

# Stage 4: SSL & Security
pip install cryptography pyOpenSSL

# Stage 5: Image processing
pip install Pillow opencv-python imagehash

# Stage 6: NLP (optional)
pip install transformers spacy nltk

# Stage 7: Remaining packages
pip install -r requirements.txt
```

### 5. Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 6. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 7. Set Environment Variables (Optional - for API access)

Create a `.env` file in the `ml-model` directory:

```bash
# Windows
echo VIRUSTOTAL_API_KEY=your_key_here > .env
echo GOOGLE_SAFE_BROWSING_API_KEY=your_key_here >> .env

# Or manually create .env file with:
VIRUSTOTAL_API_KEY=your_virustotal_api_key
GOOGLE_SAFE_BROWSING_API_KEY=your_google_safe_browsing_key
SHODAN_API_KEY=your_shodan_key
```

## 🎯 Quick Start Training

### Option A: Automated Training (Recommended)

```bash
python quick_start.py
```

This will automatically:

1. Collect training data from PhishTank & OpenPhish
2. Extract 150+ features from each URL
3. Train all ensemble models
4. Save models ready for deployment

### Option B: Manual Step-by-Step

```bash
# Step 1: Collect training data
python utils/data_collector.py

# Step 2: Extract features
python features/master_extractor.py

# Step 3: Train models
python training/train_ensemble.py
```

## 📊 Training Configuration

Edit `utils/config.py` to customize:

```python
# Data collection
PHISHING_COUNT = 25000      # Number of phishing URLs
LEGITIMATE_COUNT = 25000    # Number of legitimate URLs

# Model parameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 500,
    'max_depth': 20,
    # ... more params
}
```

## ⚡ Performance Optimization

### For Faster Training:

1. **Reduce dataset size** (for testing):

   ```python
   # In quick_start.py
   PHISHING_COUNT = 100
   LEGITIMATE_COUNT = 100
   ```

2. **Use fewer workers**:

   ```python
   extractor = MasterFeatureExtractor(parallel=True, max_workers=3)
   ```

3. **Reduce model complexity**:
   ```python
   RANDOM_FOREST_PARAMS['n_estimators'] = 100  # Instead of 500
   ```

### For Better Accuracy:

1. **Increase dataset size**:

   ```python
   PHISHING_COUNT = 50000
   LEGITIMATE_COUNT = 50000
   ```

2. **Enable hyperparameter tuning**:
   ```bash
   python training/hyperparameter_tuning.py
   ```

## 🧪 Testing Installation

Test each component individually:

```bash
# Test URL feature extraction
python features/url_features.py

# Test SSL feature extraction
python features/ssl_features.py

# Test master extractor
python features/master_extractor.py

# Test data collector
python utils/data_collector.py
```

## 🐛 Troubleshooting

### Issue: SSL Certificate Errors

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue: DNS Resolution Errors

Install additional DNS libraries:

```bash
pip install dnspython3
```

### Issue: Memory Error During Training

Reduce batch size or dataset:

```python
# In config.py
TRAIN_CONFIG['batch_size'] = 32  # Reduce from 64
```

### Issue: "Module not found" errors

Ensure virtual environment is activated:

```bash
# Check which python
python --version
which python  # Should point to venv/Scripts/python
```

### Issue: WHOIS Lookup Fails

Some domains may have WHOIS protection. This is expected and handled gracefully.

### Issue: Slow Feature Extraction

Expected! Feature extraction takes time:

- 100 URLs: ~5-10 minutes
- 1000 URLs: ~30-60 minutes
- 10000 URLs: ~3-5 hours

Use parallel processing (enabled by default).

## 📁 Expected Directory Structure After Installation

```
ml-model/
├── venv/                     # Virtual environment
├── data/
│   ├── raw/
│   │   ├── phishtank_raw.csv
│   │   ├── openphish_raw.txt
│   │   └── combined_dataset.csv
│   ├── processed/
│   │   └── features.csv
│   └── external/
├── models/
│   ├── random_forest/
│   │   └── model.joblib
│   ├── xgboost/
│   │   └── model.joblib
│   ├── lightgbm/
│   │   └── model.joblib
│   ├── scaler.joblib
│   └── training_metrics.json
├── logs/
│   └── ml_model.log
└── [all source files]
```

## ✅ Verification

After installation, verify everything works:

```bash
# Quick verification
python -c "import tensorflow, xgboost, lightgbm, sklearn; print('✅ All libraries installed')"

# Full test
python quick_start.py
```

## 🚀 Next Steps

After successful installation:

1. **Run quick_start.py** to train models
2. **Test the model** with evaluation scripts
3. **Export to TensorFlow.js** for browser use
4. **Integrate with Chrome extension**

## 💡 Tips

- **Use Git Bash** on Windows for better terminal experience
- **Monitor RAM usage** during training (Task Manager)
- **Keep terminal open** during long-running processes
- **Check logs** in `logs/ml_model.log` for detailed output

## 📞 Need Help?

Check:

- `README.md` - Project overview
- `utils/config.py` - Configuration options
- Individual feature modules for examples

---

**Estimated Installation Time**: 15-30 minutes
**Estimated Training Time**: 1-3 hours (depending on dataset size)
