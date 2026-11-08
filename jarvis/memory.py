import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, List

class JarvisMemory:
    """Долговременная память Джарвиса на SQLite"""
    def __init__(self, db_path: str = None):
        if not db_path:
            db_dir = Path.home() / ".jarvis_prime"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "memory.db")
        
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Таблица фактов и предпочтений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            # Таблица истории разговоров
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def set_fact(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def get_fact(self, key: str, default: str = "") -> str:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else default

    def get_all_facts(self) -> Dict[str, str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM user_profile")
            return dict(cur.fetchall())

    def log_interaction(self, role: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
            conn.commit()

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
