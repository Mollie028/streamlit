from core.config import DB_URL
import psycopg2


from core.config import DB_URL
import psycopg2

def test_db_connection():
    try:
        conn = psycopg2.connect(DB_URL)
        print("✅ 成功連線 DB")
        conn.close()
    except Exception as e:
        print("❌ 無法連線資料庫：", e)


def get_conn():
    return psycopg2.connect(DB_URL)

def create_user(username, password, role="user"):
    conn = cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        conn.commit()
        return True
    except:
        if conn:
            conn.rollback()
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

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
