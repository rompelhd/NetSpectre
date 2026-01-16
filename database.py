import sqlite3
from datetime import datetime

DB_NAME = "hosts.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hosts (
            ip TEXT PRIMARY KEY,
            mac TEXT,
            name TEXT,
            last_seen TEXT
        )
    """)
    conn.commit()
    conn.close()

def upsert_host(ip, mac):
    conn = get_db()
    conn.execute("""
        INSERT INTO hosts (ip, mac, last_seen)
        VALUES (?, ?, ?)
        ON CONFLICT(ip) DO UPDATE SET
            mac=excluded.mac,
            last_seen=excluded.last_seen
    """, (ip, mac, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_hosts():
    conn = get_db()
    rows = conn.execute(
        "SELECT ip, mac, name, last_seen FROM hosts ORDER BY ip"
    ).fetchall()
    conn.close()
    return rows

def set_name(ip, name):
    conn = get_db()
    conn.execute(
        "UPDATE hosts SET name=? WHERE ip=?",
        (name, ip)
    )
    conn.commit()
    conn.close()
