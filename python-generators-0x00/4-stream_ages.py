#!/usr/bin/python3
"""
Memory-efficient aggregation module for computing average age using generators
"""

import seed


def stream_user_ages():
    """
    Generator function that yields user ages one by one
    
    Yields:
        int: User age from the database
    """
    # Get database connection
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    
    # Execute query to get all users
    cursor.execute("SELECT age FROM user_data")
    
    # Loop 1: Fetch and yield ages one by one
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row['age']
    
    # Close connection
    connection.close()


def calculate_average_age():
    """
    Calculate average age using the generator without loading all data into memory
    
    Returns:
        float: Average age of all users
    """
    total_age = 0
    user_count = 0
    
    # Loop 2: Process each age from the generator
    for age in stream_user_ages():
        total_age += age
        user_count += 1
    
    # Calculate and return average
    if user_count > 0:
        return total_age / user_count
    else:
        return 0


def main():
    """
    Main function to calculate and print average age
    """
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age}")


if __name__ == "__main__":
    main()
