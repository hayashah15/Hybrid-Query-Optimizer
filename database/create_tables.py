from db_connection import get_connection

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    with open("database/schema.sql", "r") as f:
        sql_script = f.read()
    cur.execute(sql_script)
    conn.commit()
    cur.close()
    conn.close()
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()