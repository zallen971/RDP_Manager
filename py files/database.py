import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".pyrdm" / "connections.db"

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            host TEXT NOT NULL,
            port INTEGER NOT NULL,
            username TEXT
        )
    """)
    conn.commit()
    conn.close()



def get_all_connections():
    conn = get_db()
    rows = conn.execute("SELECT * FROM connections ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_connection(name, type_, host, port, username):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO connections (name, type, host, port, username) VALUES (?, ?, ?, ?, ?)",
        (name, type_, host, port, username)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

if __name__ == "__main__":
    import os
    if DB_PATH.exists():
        os.remove(DB_PATH)


    init_db()
    add_connection("My Linux Server", "ssh", "192.168.1.100", 22, "zac")
    add_connection("Work Desktop", "rdp", "192.168.1.101", 3389, "zac")
    print(get_all_connections())