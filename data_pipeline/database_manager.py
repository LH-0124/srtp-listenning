import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'capd_database.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 创建句子表
    c.execute('''
        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT UNIQUE,
            context_type TEXT,  -- 'HIGH' or 'LOW'
            score REAL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"数据库已初始化: {DB_PATH}")

def insert_sentence(text, context_type, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO sentences (text, context_type, score) VALUES (?, ?, ?)",
                  (text, context_type, score))
        conn.commit()
    except Exception as e:
        print(f"插入失败: {e}")
    finally:
        conn.close()