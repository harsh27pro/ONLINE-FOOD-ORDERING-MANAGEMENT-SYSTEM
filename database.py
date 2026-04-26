import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1871",
            database="foodorderdb"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
