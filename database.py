import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_all_user_ids():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        # Ambil semua user_id tanpa filter is_active
        cur.execute("SELECT user_id FROM users")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Karena user_id adalah varchar, ubah ke int jika perlu (telegram id biasanya int)
        return [int(row[0]) for row in rows]
    except Exception as e:
        print(f"❌ Gagal ambil user dari database: {e}")
        return []

