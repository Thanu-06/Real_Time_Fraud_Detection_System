# 🛡️ Real-Time Fraud Detection System

A **Machine Learning-powered web application** that analyzes financial transactions in real time and predicts whether a transaction is **Fraudulent** or **Legitimate**.

The system combines **Python, Machine Learning, Flask, HTML, CSS, JavaScript, MySQL, Aiven, and Render** to provide an end-to-end fraud detection solution.

---

## 🚀 Live Demo

🌐 **Live Application:**  
https://real-time-fraud-detection-system-06qw.onrender.com

---

## 📌 Project Overview

Financial fraud is a major challenge in modern digital payment systems. Traditional rule-based approaches may not always identify complex patterns associated with fraudulent transactions.

This project uses a trained **Machine Learning model** to analyze transaction characteristics and estimate the probability of fraud.

The application provides a complete workflow from transaction input to prediction, storage, and visualization.

### The system allows users to:

- 💳 Enter transaction details
- ⚡ Analyze transactions in real time
- 📊 View fraud probability
- 🚨 Detect potentially fraudulent transactions
- ✅ Identify legitimate transactions
- 🆔 Generate unique transaction IDs
- 💾 Store transaction records in MySQL
- 📜 View recent transaction history
- 📈 Monitor fraud and legitimate transaction statistics
- ☁️ Access the application through cloud deployment

---

# 🎯 Objectives

The main objectives of this project are:

- Detect potentially fraudulent transactions using Machine Learning
- Provide real-time transaction analysis
- Calculate fraud probability
- Classify transactions using an optimized threshold
- Store transaction records in a MySQL database
- Maintain transaction history
- Provide dashboard statistics
- Deploy the application on the cloud
- Integrate Machine Learning with a real-world web application

---

# ✨ Features

## 🔍 Real-Time Fraud Detection

The system analyzes transaction details and generates an immediate prediction.

## 🤖 Machine Learning

A trained Machine Learning model is integrated with the Flask backend to calculate the probability of fraud.

## 📊 Fraud Probability

The system displays the estimated probability that a transaction is fraudulent.

## ⚖️ Threshold-Based Classification

The calculated fraud probability is compared with the configured model threshold.

```text
Probability >= Threshold
        ↓
     🚨 FRAUD

Probability < Threshold
        ↓
   ✅ LEGITIMATE
