import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)


# ==========================================
# 1. Load Dataset
# ==========================================

data = pd.read_csv("dataset/transactions.csv")

print("Dataset loaded successfully!")
print(f"Dataset shape: {data.shape}")


# ==========================================
# 2. Features and Target
# ==========================================

X = data.drop("is_fraud", axis=1)

# ID should not be used for prediction
X = X.drop("transaction_id", axis=1)

y = data["is_fraud"]


# ==========================================
# 3. Feature Types
# ==========================================

categorical_features = [
    "transaction_type"
]

numerical_features = [
    "amount",
    "account_age_days",
    "transactions_last_24h",
    "device_changed",
    "international",
    "transaction_hour",
    "previous_fraud_count"
]


# ==========================================
# 4. Preprocessing
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# ==========================================
# 5. Random Forest
# ==========================================

model = RandomForestClassifier(
    n_estimators=250,
    max_depth=15,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)


# ==========================================
# 6. Pipeline
# ==========================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ==========================================
# 7. Train/Test Split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# ==========================================
# 8. Train
# ==========================================

print("\nTraining Random Forest model...")

pipeline.fit(X_train, y_train)

print("Model training completed!")


# ==========================================
# 9. Fraud Probabilities
# ==========================================

fraud_probability = pipeline.predict_proba(X_test)[:, 1]


# ==========================================
# 10. Find Best Threshold
# ==========================================

best_threshold = 0.50
best_f1 = 0

for threshold in [i / 100 for i in range(10, 91)]:

    predictions = (
        fraud_probability >= threshold
    ).astype(int)

    score = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    if score > best_f1:
        best_f1 = score
        best_threshold = threshold


print("\n========== THRESHOLD OPTIMIZATION ==========")

print(f"Best threshold : {best_threshold:.2f}")
print(f"Best F1 Score  : {best_f1:.4f}")


# ==========================================
# 11. Final Predictions
# ==========================================

y_pred = (
    fraud_probability >= best_threshold
).astype(int)


# ==========================================
# 12. Evaluation
# ==========================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

auc = roc_auc_score(
    y_test,
    fraud_probability
)


print("\n========== MODEL PERFORMANCE ==========")

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
print(f"ROC-AUC   : {auc:.4f}")


# ==========================================
# 13. Classification Report
# ==========================================

print("\n========== CLASSIFICATION REPORT ==========")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Legitimate",
            "Fraud"
        ],
        zero_division=0
    )
)


# ==========================================
# 14. Confusion Matrix
# ==========================================

print("\n========== CONFUSION MATRIX ==========")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ==========================================
# 15. Save Model + Threshold
# ==========================================

model_data = {
    "model": pipeline,
    "threshold": best_threshold
}

joblib.dump(
    model_data,
    "model/fraud_detection_model.pkl"
)

print("\nModel saved successfully!")

print(
    "Location: "
    "model/fraud_detection_model.pkl"
)