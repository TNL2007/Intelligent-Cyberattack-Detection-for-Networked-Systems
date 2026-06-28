# Intelligent Cyberattack Detection for Networked Systems

## Overview

This project presents an intelligent intrusion detection system that leverages Artificial Intelligence and Deep Learning to identify cyberattacks in network environments. The model processes network traffic features, learns meaningful representations using neural networks, and classifies different attack types with high accuracy.

---

## Features

- AI-based cyberattack detection
- Deep Neural Network for attack classification
- Network traffic preprocessing and feature scaling
- Learned feature embeddings for improved detection
- Multi-class attack classification
- Model persistence using Keras
- Label encoding and data normalization
- Evaluation using confusion matrix and classification metrics

---

## Technologies Used

- Python
- TensorFlow / Keras
- Scikit-learn
- NumPy
- Pandas
- Matplotlib
- Seaborn

---

## Workflow

1. Load the MSCAD network traffic dataset.
2. Perform preprocessing and exploratory data analysis.
3. Split the dataset into training and testing sets.
4. Normalize features using StandardScaler.
5. Encode attack labels.
6. Train a Deep Neural Network classifier.
7. Extract feature embeddings from the embedding layer.
8. Detect and classify cyberattacks.
9. Evaluate model performance using accuracy, precision, recall, F1-score, and confusion matrix.

---

## Project Structure

```
Intelligent-Cyberattack-Detection/
│
├── models/
│   ├── attack_detector.keras
│   ├── best_attack_detector.keras
│   ├── embedding_classifier.keras
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   └── test_embedding_df.csv
│
├── Untitled2(1).ipynb
├── requirements.txt
└── README.md
```

---

## Dataset

This project uses the **MSCAD (Microsoft Cyber Attack Dataset)** for training and evaluating the intrusion detection model.

---

## Results

The trained Deep Learning model is capable of:

- Detecting malicious network traffic
- Classifying different attack categories
- Learning meaningful feature embeddings
- Improving intrusion detection performance using AI

---

## Future Improvements

- Real-time network traffic monitoring
- Web-based dashboard
- Explainable AI (XAI)
- API deployment using Flask/FastAPI
- Integration with SIEM tools

---

## Authors

- S Tharun Kumar 
- Shaurya
- Siddharth S
- Kamalnath A
