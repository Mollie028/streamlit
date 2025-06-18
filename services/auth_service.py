import psycopg2
from core.config import DB_URL

# ✅ 自動測試 DB 是否能成功連線
try:
    print("🧪 測試 DB_URL =", DB_URL)
    test_conn = psycopg2.connect(DB_URL)
    print("✅ 成功連線 PostgreSQL")
    test_conn.close()
except Exception as e:
    print("❌ 無法連線 DB：", e)

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
    except Exception as e:
        print("❌ 註冊失敗：", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def check_login(username, password):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT password, role FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and row[0] == password:
            return row[1]
    except Exception as e:
        print("❌ 登入失敗：", e)
    return None
