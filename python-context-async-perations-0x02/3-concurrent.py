import asyncio
import aiosqlite


async def async_fetch_users():
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        list: All users from the users table
    """
    async with aiosqlite.connect('example.db') as conn:
        cursor = await conn.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        return results


async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        list: Users older than 40 from the users table
    """
    async with aiosqlite.connect('example.db') as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE age > ?", (40,))
        results = await cursor.fetchall()
        return results


async def fetch_concurrently():
    """
    Execute both async functions concurrently using asyncio.gather.
    
    Returns:
        tuple: Results from both async functions
    """
    print("Fetching users concurrently...")
    
    # Execute both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print("\nAll Users:")
    print("ID | Name    | Age")
    print("-" * 20)
    for user in all_users:
        print(f"{user[0]:<2} | {user[1]:<7} | {user[2]}")
    
    print("\nUsers older than 40:")
    print("ID | Name    | Age")
    print("-" * 20)
    for user in older_users:
        print(f"{user[0]:<2} | {user[1]:<7} | {user[2]}")
    
    return all_users, older_users


async def create_sample_database():
    """Create a sample database with users table for testing."""
    async with aiosqlite.connect('example.db') as conn:
        # Create users table
        await conn.execute('''
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
            (8, 'Henry', 50),
            (9, 'Ivy', 42),
            (10, 'Jack', 33)
        ]
        
        await conn.executemany('INSERT OR REPLACE INTO users (id, name, age) VALUES (?, ?, ?)', sample_users)
        await conn.commit()


async def main():
    """Main async function to set up database and run concurrent queries."""
    # Create sample database
    await create_sample_database()
    
    # Run concurrent fetch
    await fetch_concurrently()


if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())
