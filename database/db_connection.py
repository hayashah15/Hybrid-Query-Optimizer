"""
Module: Database Connection
Description:
Creates a PostgreSQL database connection.
"""

import psycopg2


def create_connection():

    try:

        connection = psycopg2.connect(
            host="localhost",
            database="hybrid_query",
            user="postgres",
            password="password",
            port="5432"
        )

        print("Database connected successfully.")

        return connection

    except Exception as error:

        print("Database Connection Error:")
        print(error)

        return None