#!/usr/bin/python3
"""
Batch processing module for streaming and processing user data in batches
"""

import seed


def stream_users_in_batches(batch_size):
    """
    Generator function that fetches users from database in batches
    
    Args:
        batch_size (int): Number of users to fetch in each batch
        
    Yields:
        dict: Individual user records from the database
    """
    # Get database connection
    connection = seed.connect_to_prodev()
    
    # Initialize offset for pagination
    offset = 0
    
    # Loop 1: Fetch data in batches using SQL queries
    while True:
        # SQL query to SELECT users FROM user_data table in batches
        query = f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}"
        
        # Execute query and get batch results
        batch_results = connection.execute(query)
        
        # Check if no more results
        if not batch_results:
            return
            
        # Loop 2: Yield each user in the current batch
        for user in batch_results:
            yield user
            
        # Move to next batch
        offset += batch_size


def batch_processing(batch_size):
    """
    Process users in batches and filter those over 25 years old
    
    Args:
        batch_size (int): Size of each batch to process
        
    Prints:
        Filtered users over 25 years old
    """
    # Loop 3: Process each user from the generator
    for user in stream_users_in_batches(batch_size):
        # Filter users over 25 and print them
        if user.get('age', 0) > 25:
            print(user)
