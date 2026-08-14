import pandas as pd
import numpy as np

np.random.seed(42)

N = 20000

data = pd.DataFrame({
    "transaction_id": np.arange(1, N + 1),

    "amount": np.round(
        np.random.lognormal(mean=5.0, sigma=1.0, size=N),
        2
    ),

    "transaction_type": np.random.choice(
        ["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"],
        N,
        p=[0.40, 0.20, 0.20, 0.10, 0.10]
    ),

    "account_age_days": np.random.randint(30, 3000, N),

    "transactions_last_24h": np.random.poisson(3, N),

    "device_changed": np.random.choice(
        [0, 1], N, p=[0.85, 0.15]
    ),

    "international": np.random.choice(
        [0, 1], N, p=[0.90, 0.10]
    ),

    "transaction_hour": np.random.randint(0, 24, N),

    "previous_fraud_count": np.random.poisson(0.3, N)
})


# ------------------------------------------
# Create stronger fraud patterns
# ------------------------------------------

fraud_score = np.zeros(N)

# Very high transaction amount
fraud_score += np.where(
    data["amount"] > 1000, 0.30, 0
)

fraud_score += np.where(
    data["amount"] > 2000, 0.30, 0
)

# New device
fraud_score += np.where(
    data["device_changed"] == 1, 0.25, 0
)

# International transaction
fraud_score += np.where(
    data["international"] == 1, 0.20, 0
)

# Too many transactions
fraud_score += np.where(
    data["transactions_last_24h"] > 8, 0.30, 0
)

fraud_score += np.where(
    data["transactions_last_24h"] > 12, 0.20, 0
)

# Previous fraud history
fraud_score += np.where(
    data["previous_fraud_count"] > 0, 0.30, 0
)

# Unusual transaction time
fraud_score += np.where(
    (data["transaction_hour"] <= 4) |
    (data["transaction_hour"] >= 23),
    0.20,
    0
)

# Suspicious transaction type
fraud_score += np.where(
    data["transaction_type"].isin(["TRANSFER", "CASH_OUT"]),
    0.15,
    0
)

# Very new account
fraud_score += np.where(
    data["account_age_days"] < 180,
    0.20,
    0
)


# ------------------------------------------
# Convert score to probability
# ------------------------------------------

fraud_probability = 1 / (
    1 + np.exp(-4 * (fraud_score - 0.7))
)

data["is_fraud"] = (
    np.random.random(N) < fraud_probability
).astype(int)


# ------------------------------------------
# Save dataset
# ------------------------------------------

data.to_csv(
    "dataset/transactions.csv",
    index=False
)

print("New fraud dataset generated successfully!")

print(f"Total transactions: {len(data)}")

print(
    f"Fraudulent transactions: "
    f"{data['is_fraud'].sum()}"
)

print(
    f"Legitimate transactions: "
    f"{(data['is_fraud'] == 0).sum()}"
)

print("\nFraud percentage:")
print(
    f"{data['is_fraud'].mean() * 100:.2f}%"
)

print("\nFirst 5 records:")
print(data.head())