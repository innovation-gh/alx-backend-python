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
        list: Batch of users as dictionaries
    """
    # Get total number of users to know when to stop
    total_users = len(seed.connect_to_prodev())
    
    # Loop 1: Iterate through batches
    for start_index in range(0, total_users, batch_size):
        # Calculate end index for current batch
        end_index = min(start_index + batch_size, total_users)
        
        # Fetch batch of users from database
        batch = []
        users_data = seed.connect_to_prodev()
        
        # Loop 2: Build current batch
        for i in range(start_index, end_index):
            batch.append(users_data[i])
        
        # Yield the current batch
        yield batch


def batch_processing(batch_size):
    """
    Process users in batches and filter those over 25 years old
    
    Args:
        batch_size (int): Size of each batch to process
        
    Prints:
        Filtered users over 25 years old
    """
    # Get batches using the generator
    batches = stream_users_in_batches(batch_size)
    
    # Loop 3: Process each batch
    for batch in batches:
        # Filter users over 25 and print them
        for user in batch:
            if user.get('age', 0) > 25:
                print(user)
