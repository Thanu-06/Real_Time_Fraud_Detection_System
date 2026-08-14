import mysql.connector


def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Venky@123",
        database="fraud_detection",
        port=3306
    )

    return connection