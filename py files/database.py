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
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            host TEXT NOT NULL,
            port INTEGER NOT NULL,
            username TEXT,
            group_id INTEGER REFERENCES groups(id)
        )
    """)
    try:
        conn.execute("ALTER TABLE connections ADD COLUMN group_id INTEGER REFERENCES groups(id)")
    except Exception:
        pass
    conn.commit()
    conn.close()

def update_connection(conn_id, name, type_, host, port, username):
    conn = get_db()
    conn.execute(
        "UPDATE connections SET name=?, type=?, host=?, port=?, username=? WHERE id=?",
        (name, type_, host, port, username, conn_id)
    )
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
    return new_id

def delete_connection(conn_id):
    conn = get_db()
    conn.execute("DELETE FROM connections WHERE id=?", (conn_id,))
    conn.commit()
    conn.close()

def get_all_groups():
    conn = get_db()
    rows = conn.execute("SELECT * FROM groups ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_group(name):
    conn = get_db()
    cursor = conn.execute("INSERT INTO groups (name) VALUES (?)", (name,))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_connection_group(conn_id, group_id):
    conn = get_db()
    conn.execute(
        "UPDATE connections SET group_id=? WHERE id=?",
        (group_id, conn_id)
    )
    conn.commit()
    conn.close()

def delete_group(group_id):
    conn = get_db()
    conn.execute("UPDATE connections SET group_id = NULL WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import os
    if DB_PATH.exists():
        os.remove(DB_PATH)


    init_db()
    add_connection("My Linux Server", "ssh", "192.168.1.100", 22, "zac")
    add_connection("Work Desktop", "rdp", "192.168.1.101", 3389, "zac")
    print(get_all_connections())