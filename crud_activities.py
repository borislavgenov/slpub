import sqlite3
from typing import List, Dict

DB_PATH = "pharmacy.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

#templates

def get_all_activity_templates() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, notes FROM activity_templates ORDER BY name")
    result = [{"id": row[0], "name": row[1], "notes": row[2]} for row in cursor.fetchall()]
    conn.close()
    return result

def create_activity_template(name: str, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO activity_templates (name, notes) VALUES (?, ?)", (name, notes))
    conn.commit()
    conn.close()

def update_activity_template(activity_id: int, name: str, notes: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE activity_templates SET name = ?, notes = ? WHERE id = ?", (name, notes, activity_id))
    conn.commit()
    conn.close()

def delete_activity_template(activity_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activity_templates WHERE id = ?", (activity_id,))
    conn.commit()
    conn.close()

#assigned

def get_assigned_activity_ids(pharmacy_id: int, month: str) -> List[int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT activity_id FROM assigned_activities WHERE pharmacy_id = ? AND month = ?",
        (pharmacy_id, month)
    )
    result = [row[0] for row in cursor.fetchall()]
    conn.close()
    return result

def assign_activities_to_pharmacy(pharmacy_id: int, month: str, activity_ids: List[int]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assigned_activities WHERE pharmacy_id = ? AND month = ?", (pharmacy_id, month))
    for aid in activity_ids:
        cursor.execute(
            "INSERT INTO assigned_activities (pharmacy_id, month, activity_id) VALUES (?, ?, ?)",
            (pharmacy_id, month, aid)
        )
    conn.commit()
    conn.close()