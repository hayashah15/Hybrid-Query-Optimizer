from db_connection import get_connection

def check_connection():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"Connected successfully: {version[0]}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    check_connection()