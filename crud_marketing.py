import sqlite3
from typing import List, Optional, Dict

DB_PATH = "pharmacy.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

#all pharmacies
def get_all_pharmacies() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM pharmacies ORDER BY name")
    result = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return result

def create_pharmacy(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pharmacies (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def rename_pharmacy(pharmacy_id: int, new_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pharmacies SET name = ? WHERE id = ?", (new_name, pharmacy_id))
    conn.commit()
    conn.close()

def delete_pharmacy(pharmacy_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pharmacies WHERE id = ?", (pharmacy_id,))
    conn.commit()
    conn.close()

#activities
def create_activity(pharmacy_id: int, month: str, name: str, notes: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO marketing_activities (pharmacy_id, month, name, notes) VALUES (?, ?, ?, ?)",
        (pharmacy_id, month, name, notes)
    )
    conn.commit()
    conn.close()

def update_activity(activity_id: int, name: str, notes: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE marketing_activities SET name = ?, notes = ? WHERE id = ?",
        (name, notes, activity_id)
    )
    conn.commit()
    conn.close()

def delete_activity(activity_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM marketing_activities WHERE id = ?", (activity_id,))
    conn.commit()
    conn.close()

def get_activities_for_month(pharmacy_id: int, month: str) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, notes FROM marketing_activities WHERE pharmacy_id = ? AND month = ? ORDER BY id DESC",
        (pharmacy_id, month)
    )
    result = [{"id": row[0], "name": row[1], "notes": row[2]} for row in cursor.fetchall()]
    conn.close()
    return result