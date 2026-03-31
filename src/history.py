import sqlite3
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "request_history.db"

DDL = """
CREATE TABLE IF NOT EXISTS request_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  user_input TEXT NOT NULL,
  method TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  params TEXT,
  response TEXT,
  explanation TEXT
);
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(DDL)
    conn.commit()
    conn.close()


def log_request(user_input: str, method: str, endpoint: str, params: dict, response: dict, explanation: str = ""):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO request_history
        (timestamp, user_input, method, endpoint, params, response, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat() + "Z",
            user_input,
            method,
            endpoint,
            json.dumps(params or {}),
            json.dumps(response or {}),
            explanation,
        )
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 10):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, timestamp, user_input, method, endpoint, params, response, explanation
        FROM request_history
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,)
    )
    rows = [
        {
            "id": r[0],
            "timestamp": r[1],
            "user_input": r[2],
            "method": r[3],
            "endpoint": r[4],
            "params": json.loads(r[5]),
            "response": json.loads(r[6]),
            "explanation": r[7],
        }
        for r in cur.fetchall()
    ]
    conn.close()
    return rows