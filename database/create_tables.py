"""
Module: Create Database Tables
"""

from db_connection import create_connection


def create_tables():

    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS documents (

            id SERIAL PRIMARY KEY,
            title TEXT,
            content TEXT

        );

    """)

    connection.commit()

    print("Table 'documents' created successfully.")

    cursor.close()
    connection.close()


if __name__ == "__main__":

    create_tables()