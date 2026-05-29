import json
from datetime import datetime, timedelta
from database.db import get_db

# --- USER MODELS ---

def add_user(name, email, role, face_encoding_list=None, photo_path=None):
    """
    Inserts a new user profile into the database.
    """
    db = get_db()
    cursor = db.cursor()
    
    encoding_json = json.dumps(list(face_encoding_list)) if face_encoding_list else None
    
    try:
        cursor.execute(
            "INSERT INTO users (name, email, role, face_encoding, photo_path) VALUES (?, ?, ?, ?, ?)",
            (name, email, role, encoding_json, photo_path)
        )
        db.commit()
        return cursor.lastrowid, None
    except Exception as e:
        return None, "A user with this email address already exists."

def get_all_users():
    """
    Fetches all registered users, sorted alphabetically.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email, role, photo_path, created_at FROM users ORDER BY name ASC")
    return [dict(row) for row in cursor.fetchall()]

def get_user_by_id(user_id):
    """
    Retrieves a user profile by unique ID.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email, role, photo_path, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def get_user_by_email(email):
    """
    Retrieves a user profile by unique Email. Used during Admin login lookups.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email, role, password_hash, created_at FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    return dict(row) if row else None

def get_user_encodings():
    """
    Retrieves serialized numpy vectors from the database for facial scans matching.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, face_encoding FROM users WHERE face_encoding IS NOT NULL")
    users = []
    for row in cursor.fetchall():
        try:
            encoding = json.loads(row['face_encoding'])
            users.append({
                "id": row["id"],
                "name": row["name"],
                "encoding": encoding
            })
        except:
            pass
    return users

def delete_user(user_id):
    """
    Deletes a user profile from the database.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    return cursor.rowcount > 0

# --- ATTENDANCE MODELS ---

def log_attendance(user_id, name, timestamp, status, photo_path=None):
    """
    Logs an attendance check-in event.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO attendance (user_id, name, timestamp, status, photo_path) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, timestamp, status, photo_path)
    )
    db.commit()
    return cursor.lastrowid

def get_attendance_logs(search_query=None, status_filter=None):
    """
    Fetches history logs, supporting search query (name/email) and status filters.
    """
    db = get_db()
    cursor = db.cursor()
    
    query = """
        SELECT a.id, a.user_id, a.name AS scan_name, a.timestamp, a.status, a.photo_path,
               u.email, u.role
        FROM attendance a
        LEFT JOIN users u ON a.user_id = u.id
        WHERE 1=1
    """
    params = []
    
    if search_query:
        query += " AND (a.name LIKE ? OR u.email LIKE ?)"
        search_val = f"%{search_query}%"
        params.extend([search_val, search_val])
        
    if status_filter:
        query += " AND a.status = ?"
        params.append(status_filter)
        
    query += " ORDER BY a.timestamp DESC"
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

# --- ALERT MODELS ---

def create_alert(timestamp, photo_path, status='Unresolved'):
    """
    Creates an unrecognized intrusion visitor alert.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO alerts (timestamp, photo_path, status) VALUES (?, ?, ?)",
        (timestamp, photo_path, status)
    )
    db.commit()
    return cursor.lastrowid

def get_all_alerts(status_filter=None):
    """
    Fetches intrusion alerts with optional filters.
    """
    db = get_db()
    cursor = db.cursor()
    
    query = """
        SELECT al.id, al.timestamp, al.photo_path, al.status, al.resolved_at,
               u.name AS resolved_by_name
        FROM alerts al
        LEFT JOIN users u ON al.resolved_user_id = u.id
    """
    params = []
    
    if status_filter:
        query += " WHERE al.status = ?"
        params.append(status_filter)
        
    query += " ORDER BY al.timestamp DESC"
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

def resolve_alert(alert_id, resolved_user_id, status='Resolved'):
    """
    Resolves a security alert.
    """
    db = get_db()
    cursor = db.cursor()
    resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "UPDATE alerts SET status = ?, resolved_user_id = ?, resolved_at = ? WHERE id = ?",
        (status, resolved_user_id, resolved_at, alert_id)
    )
    db.commit()
    return cursor.rowcount > 0

# --- DASHBOARD METRICS ---

def get_dashboard_stats():
    """
    Aggregates statistical figures (today check-ins, active alerts, users count, trends).
    """
    db = get_db()
    cursor = db.cursor()
    
    # 1. Total Registered Employees
    cursor.execute("SELECT COUNT(*) FROM users WHERE role != 'Admin'")
    total_users = cursor.fetchone()[0]
    
    # 2. Checked-in Today count
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT COUNT(DISTINCT user_id) FROM attendance WHERE timestamp LIKE ? AND status = 'Present'",
        (f"{today_str}%",)
    )
    today_present = cursor.fetchone()[0]
    
    # 3. Total Unresolved Intrusion Alerts
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE status = 'Unresolved'")
    active_alerts = cursor.fetchone()[0]
    
    # 4. Weekly Trend (Past 7 Days count)
    weekly_trend = []
    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_label = day.strftime("%a")
        
        # Present count
        cursor.execute(
            "SELECT COUNT(DISTINCT user_id) FROM attendance WHERE timestamp LIKE ? AND status = 'Present'",
            (f"{day_str}%",)
        )
        present_cnt = cursor.fetchone()[0]
        
        # Unrecognized count
        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE timestamp LIKE ? AND status = 'Unknown'",
            (f"{day_str}%",)
        )
        unknown_cnt = cursor.fetchone()[0]
        
        weekly_trend.append({
            "day": day_label,
            "date": day_str,
            "present": present_cnt,
            "unknown": unknown_cnt
        })
        
    # 5. Recent Scan logs (limit 5)
    cursor.execute("""
        SELECT a.id, a.name, a.timestamp, a.status, a.photo_path, u.role
        FROM attendance a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.timestamp DESC LIMIT 5
    """)
    recent_logs = [dict(row) for row in cursor.fetchall()]
    
    return {
        "total_users": total_users,
        "today_present": today_present,
        "active_alerts": active_alerts,
        "weekly_trend": weekly_trend,
        "recent_logs": recent_logs
    }
