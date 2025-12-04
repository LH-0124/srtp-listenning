import sqlite3
import os


'''
数据库初始化函数 init_db() 和句子插入函数insert_sentence(text, context_type, score)
sqlite3 用于操作 SQLite 数据库，涉及sqlite的语法思路。
数据库包含一个表 sentences，字段有 id（自增主键）、text（句子文本）、context_type（语境类型，高或低）、score（语境分数）。
'''

# 文件保存位置是项目根目录下的 capd_database.db
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