from flask import Flask, render_template, request, jsonify
import joblib
import sys
import os
import pandas as pd
from datetime import datetime

# ==========================================
# Allow importing database.py from app folder
# ==========================================

sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

from database import get_connection


# ==========================================
# Flask Configuration
# ==========================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="../static",
    static_url_path="/static"
)


# ==========================================
# Project Root Directory
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==========================================
# Load Trained ML Model
# ==========================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "fraud_detection_model.pkl"
)

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
threshold = model_data["threshold"]

print("========================================")
print("Fraud Detection Model Loaded")
print("Model:", type(model).__name__)
print("Threshold:", threshold)
print("========================================")


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# PREDICT TRANSACTION
# ==========================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        print("\n========================================")
        print("Incoming Transaction:")
        print(data)
        print("========================================")

        # --------------------------------------
        # Read transaction values
        # --------------------------------------

        amount = float(data["amount"])

        transaction_type = str(
            data["transaction_type"]
        )

        account_age_days = int(
            data["account_age_days"]
        )

        transactions_last_24h = int(
            data["transactions_last_24h"]
        )

        device_changed = int(
            data["device_changed"]
        )

        international = int(
            data["international"]
        )

        transaction_hour = int(
            data["transaction_hour"]
        )

        previous_fraud_count = int(
            data["previous_fraud_count"]
        )

        # --------------------------------------
        # Create DataFrame for ML model
        # --------------------------------------

        transaction_data = pd.DataFrame([{

            "amount": amount,

            "transaction_type":
                transaction_type,

            "account_age_days":
                account_age_days,

            "transactions_last_24h":
                transactions_last_24h,

            "device_changed":
                device_changed,

            "international":
                international,

            "transaction_hour":
                transaction_hour,

            "previous_fraud_count":
                previous_fraud_count

        }])

        print("\nData sent to ML model:")
        print(transaction_data)

        print("\nData shape:")
        print(transaction_data.shape)

        # --------------------------------------
        # Fraud probability
        # --------------------------------------

        fraud_probability = float(
            model.predict_proba(
                transaction_data
            )[0][1]
        )

        print(
            "\nFraud Probability:",
            fraud_probability
        )

        # --------------------------------------
        # Apply optimized threshold
        # --------------------------------------

        prediction = (
            "Fraud"
            if fraud_probability >= threshold
            else "Legitimate"
        )

        print(
            "Prediction:",
            prediction
        )

        # ======================================
        # Generate Transaction ID
        # ======================================

        transaction_id = (
            "TXN"
            + datetime.now().strftime(
                "%Y%m%d%H%M%S%f"
            )
        )

        # ======================================
        # Save Transaction to MySQL
        # ======================================

        connection = get_connection()

        cursor = connection.cursor()

        insert_query = """
            INSERT INTO transactions (
                transaction_id,
                amount,
                transaction_type,
                account_age_days,
                transactions_last_24h,
                device_changed,
                international,
                transaction_hour,
                previous_fraud_count,
                fraud_probability,
                prediction
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """

        values = (
            transaction_id,
            amount,
            transaction_type,
            account_age_days,
            transactions_last_24h,
            device_changed,
            international,
            transaction_hour,
            previous_fraud_count,
            fraud_probability,
            prediction
        )

        cursor.execute(
            insert_query,
            values
        )

        connection.commit()

        cursor.close()
        connection.close()

        print(
            "Transaction saved:",
            transaction_id
        )

        # ======================================
        # Return result to frontend
        # ======================================

        return jsonify({

            "success": True,

            "transaction_id":
                transaction_id,

            "prediction":
                prediction,

            "fraud_probability":
                round(
                    fraud_probability,
                    4
                ),

            "threshold":
                round(
                    threshold,
                    4
                )

        })

    except Exception as e:

        print("\n========================================")
        print("PREDICTION ERROR")
        print("========================================")
        print(str(e))
        print("========================================")

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ==========================================
# GET RECENT TRANSACTIONS
# ==========================================

@app.route("/transactions", methods=["GET"])
def transactions():

    connection = None
    cursor = None

    try:

        print("\n========================================")
        print("Loading Recent Transactions")
        print("========================================")

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                id,
                transaction_id,
                amount,
                transaction_type,
                fraud_probability,
                prediction,
                created_at
            FROM transactions
            ORDER BY id DESC
            LIMIT 50
        """

        cursor.execute(query)

        results = cursor.fetchall()

        print(
            "Transactions found:",
            len(results)
        )

        # --------------------------------------
        # Convert MySQL values to JSON safe data
        # --------------------------------------

        for transaction in results:

            if transaction.get("created_at"):

                transaction["created_at"] = (
                    transaction["created_at"]
                    .strftime("%Y-%m-%d %H:%M:%S")
                )

            if transaction.get("fraud_probability") is not None:

                transaction["fraud_probability"] = float(
                    transaction["fraud_probability"]
                )

            if transaction.get("amount") is not None:

                transaction["amount"] = float(
                    transaction["amount"]
                )

        return jsonify({

            "success": True,

            "transactions": results

        })

    except Exception as e:

        print("\n========================================")
        print("TRANSACTION HISTORY ERROR")
        print("========================================")
        print(str(e))
        print("========================================")

        return jsonify({

            "success": False,

            "error": str(e),

            "transactions": []

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# DASHBOARD STATISTICS
# ==========================================

@app.route("/stats", methods=["GET"])
def stats():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # --------------------------------------
        # Total transactions
        # --------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM transactions
        """)

        total = cursor.fetchone()["total"]

        # --------------------------------------
        # Fraud transactions
        # --------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS fraud
            FROM transactions
            WHERE prediction = 'Fraud'
        """)

        fraud = cursor.fetchone()["fraud"]

        # --------------------------------------
        # Legitimate transactions
        # --------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS legitimate
            FROM transactions
            WHERE prediction = 'Legitimate'
        """)

        legitimate = cursor.fetchone()["legitimate"]

        print("\n========================================")
        print("Dashboard Statistics")
        print("Total:", total)
        print("Fraud:", fraud)
        print("Legitimate:", legitimate)
        print("========================================")

        return jsonify({

            "success": True,

            "total": total,

            "fraud": fraud,

            "legitimate": legitimate

        })

    except Exception as e:

        print("\n========================================")
        print("STATISTICS ERROR")
        print("========================================")
        print(str(e))
        print("========================================")

        return jsonify({

            "success": False,

            "error": str(e),

            "total": 0,

            "fraud": 0,

            "legitimate": 0

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )