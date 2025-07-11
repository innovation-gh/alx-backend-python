import sqlite3


class ExecuteQuery:
    """
    A reusable class-based context manager for executing database queries.
    Handles both connection management and query execution.
    """
    
    def __init__(self, db_name, query, params=None):
        """
        Initialize the ExecuteQuery context manager.
        
        Args:
            db_name (str): The name of the database file
            query (str): The SQL query to execute
            params (tuple, optional): Parameters for the query
        """
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """
        Enter the context manager by opening connection and executing query.
        
        Returns:
            list: The results of the executed query
        """
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager by closing the database connection.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


def create_sample_database():
    """Create a sample database with users table for testing."""
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    
    # Insert sample data
    sample_users = [
        (1, 'Alice', 30),
        (2, 'Bob', 25),
        (3, 'Charlie', 35),
        (4, 'Diana', 28),
        (5, 'Eve', 45),
        (6, 'Frank', 22),
        (7, 'Grace', 38),
        (8, 'Henry', 50)
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO users (id, name, age) VALUES (?, ?, ?)', sample_users)
    conn.commit()
    conn.close()


def main():
    """Main function to demonstrate the ExecuteQuery context manager."""
    # Create sample database
    create_sample_database()
    
    # Use the ExecuteQuery context manager to query users older than 25
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    
    with ExecuteQuery('example.db', query, params) as results:
        print("Users older than 25:")
        print("ID | Name    | Age")
        print("-" * 20)
        for row in results:
            print(f"{row[0]:<2} | {row[1]:<7} | {row[2]}")


if __name__ == "__main__":
    main()
