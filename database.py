import mysql.connector


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="YOUR_MYSQL_PASSWORD",
            database="it_support"
        )

        return connection

    except mysql.connector.Error as e:
        print("Database connection error:", e)
        return None
