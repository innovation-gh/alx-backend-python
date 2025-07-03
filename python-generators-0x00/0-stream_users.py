import mysql.connector

def stream_users():
    """Generator that streams rows from user_data table one by one"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # replace with your password
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data")

        for row in cursor:
            yield row

        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
