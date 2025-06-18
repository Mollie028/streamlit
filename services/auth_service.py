def create_user(username, password, role="user"):
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        conn.commit()
        return True
    except Exception as e:
        print("❌ create_user 發生錯誤：", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def test_db_connection():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        print("✅ 成功連接資料庫！查詢結果：", result)
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ 無法連接資料庫：", e)
        return False
