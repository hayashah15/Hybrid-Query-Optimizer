"""
Module: Check Database Connection
"""

from db_connection import create_connection


connection = create_connection()

if connection:

    print("Database is ready.")

    connection.close()

else:

    print("Unable to connect to the database.")