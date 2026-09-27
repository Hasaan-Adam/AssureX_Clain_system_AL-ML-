# Teachable Machine Vision Model Card

## Model Overview
- **Model Name:** AssureX Claim Summary Card Vision Classifier
- **Architecture:** MobileNetV2 Transfer Learning (TensorFlow.js / Teachable Machine Vision)
- **Input Size:** 224x224 RGB Claim Summary Card images
- **Output Classes:**
  1. `Valid Claim`
  2. `Invalid Claim`
  3. `Manual Review`

## Training Details
- **Training Source:** `data/train/cards/` (3,150 cards: 1,050 base + 2,100 augmented variations)
- **Validation Source:** `data/validation/cards/` (225 cards)
- **Test Source:** `data/test/cards/` (225 cards)
- **Epochs:** 50
- **Batch Size:** 32
- **Learning Rate:** 0.001

## Performance Metrics
- **Overall Accuracy:** 94.8%
- **Macro Precision:** 0.949
- **Macro Recall:** 0.948
- **Macro F1-Score:** 0.948

## Key Constraints & Fairness
- **Sanitized Visual Representation:** Summary cards strictly exclude target class predictions and confidence values.
- **Ensemble Role:** Serves as the independent second-opinion classifier against tabular XGBoost/RandomForest models.