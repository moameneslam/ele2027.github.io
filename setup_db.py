import csv
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

# Read CSV file and insert data into users table
with open('users.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        cursor.execute('''INSERT INTO users (user, username, password) VALUES (?, ?, ?)''', (row['user'], row['username'], row['password']))

# Commit and close connection
conn.commit()
conn.close()