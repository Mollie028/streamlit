import psycopg2
from core.config import DB_URL

def get_conn():
    return psycopg2.connect(DB_URL)

def create_user(username, password, role="user"):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        conn.commit()
        return True
    except:
        return False
    finally:
        cur.close()
        conn.close()

def check_login(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT password, role FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and row[0] == password:
        return row[1]
    return None
