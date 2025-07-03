import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator that yields batches of user rows."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # your password here
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)
        offset = 0
        while True:
            cursor.execute(
                "SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s",
                (batch_size, offset)
            )
            batch = cursor.fetchall()
            if not batch:
                break
            yield batch
            offset += batch_size

        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def batch_processing(batch_size):
    """Generator that filters and yields users over age 25 from batches."""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                yield user
