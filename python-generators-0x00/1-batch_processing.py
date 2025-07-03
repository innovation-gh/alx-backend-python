import mysql.connector
from typing import Generator, List, Dict

def stream_users_in_batches(batch_size: int) -> Generator[List[Dict], None, None]:
    """
    Generator that yields batches of users from the database.

    Args:
        batch_size (int): Number of users to fetch per batch.

    Yields:
        List[Dict]: A batch of user rows as dictionaries.
    """
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # update with your password
        database="ALX_prodev"
    )
    try:
        with connection.cursor(dictionary=True) as cursor:
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
    finally:
        connection.close()

def batch_processing(batch_size: int) -> Generator[Dict, None, None]:
    """
    Generator that yields users older than 25 from batches.

    Args:
        batch_size (int): Number of users to fetch per batch.

    Yields:
        Dict: User dictionary where age > 25.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                yield user
