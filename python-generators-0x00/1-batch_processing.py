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
    # Get all users from database
    all_users = seed.connect_to_prodev()
    
    # Loop 1: Process users in batches
    for i in range(0, len(all_users), batch_size):
        # Get current batch slice
        batch = all_users[i:i + batch_size]
        
        # Loop 2: Yield each user in the batch
        for user in batch:
            yield user


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
