import sqlite3
import functools

def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Look for query in kwargs first
        query = kwargs.get('query')
        if not query and args:
            # Look for query in positional arguments
            query = args[0] if args and isinstance(args[0], str) else None
        
        if query:
            print(f"Executing SQL Query: {query}")
        
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
