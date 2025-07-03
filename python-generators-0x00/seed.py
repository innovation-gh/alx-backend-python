import mysql.connector
import csv
import uuid

def connect_db():
    """Connect to MySQL server (no database selected)"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""  # add your password here
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def create_database(connection):
    """Create the ALX_prodev database if it doesn't exist"""
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    cursor.close()

def connect_to_prodev():
    """Connect to ALX_prodev database"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # add your password here
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None

def create_table(connection):
    """Create user_data table with required schema"""
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL NOT NULL,
        INDEX (user_id)
    )
    """
    cursor.execute(create_table_query)
    connection.commit()
    print("Table user_data created successfully")
    cursor.close()

def insert_data(connection, csv_file):
    """Insert data from CSV file into user_data table if not exists"""
    cursor = connection.cursor()

    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if user_id exists to avoid duplicates
            cursor.execute("SELECT * FROM user_data WHERE user_id=%s", (row['user_id'],))
            if cursor.fetchone() is None:
                # Insert row
                cursor.execute("""
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                """, (row['user_id'], row['name'], row['email'], row['age']))
        connection.commit()
    cursor.close()
