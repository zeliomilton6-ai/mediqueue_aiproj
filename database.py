import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).with_name("hospital.db")

def connect():
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                phone TEXT,
                department TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                arrival_time TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'Normal',
                status TEXT NOT NULL DEFAULT 'Waiting',
                service_minutes REAL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

def add_patient(patient_name, phone, department, appointment_time, priority):
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        cursor = conn.execute("""
            INSERT INTO patients
            (patient_name, phone, department, appointment_time, arrival_time,
             priority, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Waiting', ?)
        """, (
            patient_name.strip(), phone.strip(), department,
            appointment_time.isoformat(timespec="minutes"),
            now, priority, now
        ))
        conn.commit()
        return cursor.lastrowid

def get_patients(status=None, department=None):
    sql = "SELECT * FROM patients WHERE 1=1"
    params = []
    if status:
        sql += " AND status=?"
        params.append(status)
    if department and department != "All":
        sql += " AND department=?"
        params.append(department)
    sql += """
        ORDER BY CASE priority
            WHEN 'Emergency' THEN 0
            WHEN 'Urgent' THEN 1
            ELSE 2 END,
            appointment_time, arrival_time, id
    """
    with connect() as conn:
        return conn.execute(sql, params).fetchall()

def update_status(patient_id, status, service_minutes=None):
    with connect() as conn:
        if status == "Completed":
            conn.execute(
                "UPDATE patients SET status=?, service_minutes=? WHERE id=?",
                (status, service_minutes, patient_id)
            )
        else:
            conn.execute(
                "UPDATE patients SET status=? WHERE id=?",
                (status, patient_id)
            )
        conn.commit()

def get_completed_durations(department):
    with connect() as conn:
        rows = conn.execute("""
            SELECT service_minutes FROM patients
            WHERE department=? AND status='Completed'
              AND service_minutes IS NOT NULL AND service_minutes > 0
            ORDER BY id DESC LIMIT 100
        """, (department,)).fetchall()
    return [float(row["service_minutes"]) for row in rows]

def get_counts():
    with connect() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS total FROM patients GROUP BY status"
        ).fetchall()
    return {row["status"]: row["total"] for row in rows}
