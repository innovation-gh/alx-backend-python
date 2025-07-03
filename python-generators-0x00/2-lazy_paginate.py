#!/usr/bin/python3
"""
Lazy pagination module for fetching paginated data from users database
"""

import seed


def paginate_users(page_size, offset):
    """
    Fetch users from database with pagination
    
    Args:
        page_size (int): Number of users per page
        offset (int): Starting position for the query
        
    Returns:
        list: List of user dictionaries for the current page
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_paginate(page_size):
    """
    Generator function that lazily loads paginated data
    
    Args:
        page_size (int): Number of users per page
        
    Yields:
        list: Page of users as a list of dictionaries
    """
    offset = 0
    
    # Single loop to fetch pages lazily
    while True:
        # Fetch the next page using paginate_users
        page_data = paginate_users(page_size, offset)
        
        # If no data returned, we've reached the end
        if not page_data:
            return
            
        # Yield the current page
        yield page_data
        
        # Move to the next page
        offset += page_size


# Alias for the function name used in the test
lazy_pagination = lazy_paginate
