import sqlite3
import functools

# Decorator to log SQL queries
def log_queries(func):
    """Decorator that logs SQL queries before executing them"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from args or kwargs
        query = None
        if args and isinstance(args[0], str):
            query = args[0]
        elif 'query' in kwargs:
            query = kwargs['query']
        
        # Log the query
        if query:
            print(f"Executing SQL Query: {query}")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
