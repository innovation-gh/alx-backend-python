import sqlite3


class DatabaseConnection:
    """
    A class-based context manager for handling database connections.
    Automatically opens and closes database connections using the with statement.
    """
    
    def __init__(self, db_name):
        """
        Initialize the DatabaseConnection with a database name.
        
        Args:
            db_name (str): The name of the database file
        """
        self.db_name = db_name
        self.connection = None
    
    def __enter__(self):
        """
        Enter the context manager by opening a database connection.
        
        Returns:
            sqlite3.Connection: The database connection object
        """
        self.connection = sqlite3.connect(self.db_name)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager by closing the database connection.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred  
            exc_tb: Exception traceback if an exception occurred
        """
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
        (5, 'Eve', 45)
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO users (id, name, age) VALUES (?, ?, ?)', sample_users)
    conn.commit()
    conn.close()


def main():
    """Main function to demonstrate the DatabaseConnection context manager."""
    # Create sample database
    create_sample_database()
    
    # Use the context manager to query the database
    with DatabaseConnection('example.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        print("Query Results:")
        print("ID | Name    | Age")
        print("-" * 20)
        for row in results:
            print(f"{row[0]:<2} | {row[1]:<7} | {row[2]}")


if __name__ == "__main__":
    main()
