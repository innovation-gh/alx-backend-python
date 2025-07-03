import mysql.connector
from contextlib import contextmanager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # your MySQL password
        database="ALX_prodev"
    )
    try:
        yield connection
    finally:
        connection.close()

def stream_users_in_batches(batch_size):
    """
    Generator that yields batches of users from the database.
    
    Args:
        batch_size (int): Number of records to fetch per batch
        
    Yields:
        list: Batch of user records as dictionaries
    """
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        offset = 0
        
        while True:
            try:
                cursor.execute(
                    "SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s",
                    (batch_size, offset)
                )
                batch = cursor.fetchall()
                
                if not batch:
                    logger.info(f"Processed all records. Total batches: {offset // batch_size}")
                    break
                
                logger.info(f"Processing batch {offset // batch_size + 1} with {len(batch)} records")
                yield batch
                offset += batch_size
                
            except mysql.connector.Error as e:
                logger.error(f"Database error: {e}")
                break
            finally:
                cursor.close()

def batch_processing(batch_size):
    """
    Generator that processes batches and yields filtered users.
    
    Args:
        batch_size (int): Number of records to process per batch
        
    Yields:
        dict: User record for users over 25
    """
    total_processed = 0
    total_filtered = 0
    
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            total_processed += 1
            if user['age'] > 25:
                total_filtered += 1
                yield user
    
    logger.info(f"Total processed: {total_processed}, Total filtered: {total_filtered}")

def process_users_example():
    """Example usage of the batch processing system"""
    batch_size = 1000
    
    # Process users in batches
    for user in batch_processing(batch_size):
        # Process individual user
        print(f"Processing user: {user['name']} (ID: {user['user_id']}, Age: {user['age']})")
        
        # You can add your processing logic here
        # For example: send email, update records, etc.

# Alternative implementation using cursor as iterator
def stream_users_cursor_iterator(batch_size):
    """
    Alternative implementation using cursor as iterator.
    More memory efficient for very large datasets.
    """
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT user_id, name, email, age FROM user_data")
            
            batch = []
            for row in cursor:
                batch.append(row)
                
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            
            # Yield remaining records
            if batch:
                yield batch
                
        except mysql.connector.Error as e:
            logger.error(f"Database error: {e}")
        finally:
            cursor.close()

def advanced_batch_processing(batch_size, age_filter=25):
    """
    More flexible batch processing with configurable filters.
    
    Args:
        batch_size (int): Number of records to process per batch
        age_filter (int): Minimum age for filtering users
        
    Yields:
        dict: Filtered user records
    """
    for batch in stream_users_in_batches(batch_size):
        # Process entire batch at once for better performance
        filtered_batch = [user for user in batch if user['age'] > age_filter]
        
        # Yield individual users or entire filtered batch
        for user in filtered_batch:
            yield user

# Example usage with error handling
def main():
    """Main function demonstrating usage"""
    try:
        batch_size = 500
        processed_count = 0
        
        print("Starting batch processing...")
        
        for user in batch_processing(batch_size):
            processed_count += 1
            print(f"User {processed_count}: {user['name']} (Age: {user['age']})")
            
            # Break after processing a certain number for demo
            if processed_count >= 10:
                break
                
    except Exception as e:
        logger.error(f"Error in main processing: {e}")

if __name__ == "__main__":
    main()
