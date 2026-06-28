# Intelligent Cyberattack Detection for Networked Systems

## Overview

This project is an AI-powered cyberattack detection system that analyzes network traffic and classifies malicious activities using Deep Learning. The system is trained on the MSCAD dataset and provides an interactive web-based interface for predicting cyberattacks from network traffic features.

## Repository Structure

```
Intelligent-Cyberattack-Detection-for-Networked-Systems/
│
├── README.md
├── Untitled2.ipynb
│
├── models/
│   ├── attack_detector.keras
│   ├── best_attack_detector.keras
│   ├── embedding_classifier.keras
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   └── test_embedding_df.csv
│
└── UI/
    ├── app.py
    ├── requirements.txt
    ├── package.json
    ├── index.html
    ├── src/
    └── dist/
```

## Features

* AI-powered cyberattack detection
* Deep Learning-based attack classification
* Network traffic preprocessing
* Feature scaling using StandardScaler
* Label encoding for attack categories
* Trained Keras models
* Interactive web interface
* Multi-class cyberattack prediction

## Technologies Used

### Backend

* Python
* TensorFlow / Keras
* Scikit-learn
* Pandas
* NumPy

### Frontend

* React (Vite)
* HTML
* CSS
* JavaScript

## Workflow

1. Load the MSCAD dataset.
2. Preprocess network traffic data.
3. Normalize input features.
4. Encode attack labels.
5. Train the Deep Learning model.
6. Save trained models.
7. Load models in the application.
8. Predict attack categories through the web interface.

## Models Included

* Attack Detection Model
* Best Attack Detection Model
* Embedding Classifier
* Feature Scaler
* Label Encoder

## Dataset

MSCAD (Microsoft Cyber Security Attack Dataset)

## Future Improvements

* Real-time packet capture
* Explainable AI (XAI)
* Cloud deployment
* API integration
* Dashboard analytics
---

## Authors

- S Tharun Kumar 
- Shaurya
- Siddharth S
- Kamalnath A
