import time
import sqlite3
import functools

def with_db_connection(func):
    """Decorator that automatically handles database connections"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Call the original function with the connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection
            conn.close()
    
    return wrapper

query_cache = {}

def cache_query(func):
    """Decorator that caches query results based on the SQL query string"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from args or kwargs to use as cache key
        query = None
        if len(args) > 1 and isinstance(args[1], str):
            query = args[1]
        elif 'query' in kwargs:
            query = kwargs['query']
        
        # If query is found and cached, return cached result
        if query and query in query_cache:
            print(f"Cache hit for query: {query}")
            return query_cache[query]
        
        # If not cached, execute the function
        result = func(*args, **kwargs)
        
        # Cache the result if we have a query
        if query:
            print(f"Caching result for query: {query}")
            query_cache[query] = result
        
        return result
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
