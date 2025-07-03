Python Generators Project - 0x00
Project Overview
This project introduces advanced usage of Python generators by working with a MySQL database to efficiently stream and process data.

You will:

Set up a MySQL database named ALX_prodev.

Create a table user_data with fields for user ID, name, email, and age.

Populate the table with sample data from a CSV file.

Implement Python functions to connect to the database, create schema, and insert data.

Prepare for generator-based streaming of database rows for memory-efficient data processing.

Database Schema
Database: ALX_prodev

Table: user_data

Column	Type	Constraints
user_id	VARCHAR(36)	Primary Key, Indexed (UUID)
name	VARCHAR(255)	NOT NULL
email	VARCHAR(255)	NOT NULL
age	DECIMAL	NOT NULL

Files
seed.py: Contains functions to connect to MySQL, create the database and table, and populate the table from user_data.csv.

user_data.csv: CSV file with sample user data to be inserted.

0-main.py: Example script demonstrating the usage of seed.py functions.

Usage Instructions
Setup MySQL Database
Make sure MySQL server is running on your machine.
Adjust MySQL user credentials inside seed.py as necessary.

Run the seed script via 0-main.py
This will:

Connect to MySQL server

Create the ALX_prodev database if not existing

Create the user_data table if not existing

Insert data from user_data.csv into the table

Verify the data
The script prints a sample of inserted rows to confirm.

Dependencies
Python 3.x

mysql-connector-python library
Install via:

bash
Copy
Edit
pip install mysql-connector-python
Example Output
nginx
Copy
Edit
connection successful
Table user_data created successfully
Database ALX_prodev is present 
[('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67),
 ('006bfede-724d-4cdd-a2a6-59700f40d0da', 'Glenda Wisozk', 'Miriam21@gmail.com', 119),
 ('006e1f7f-90c2-45ad-8c1d-1275d594cc88', 'Daniel Fahey IV', 'Delia.Lesch11@hotmail.com', 49),
 ('00af05c9-0a86-419e-8c2d-5fb7e899ae1c', 'Ronnie Bechtelar', 'Sandra19@yahoo.com', 22),
 ('00cc08cc-62f4-4da1-b8e4-f5d9ef5dbbd4', 'Alma Bechtelar', 'Shelly_Balistreri22@hotmail.com', 102)]
