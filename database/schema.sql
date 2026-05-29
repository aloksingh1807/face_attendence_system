-- Core Database DDL Schema for Aura Scan

-- 1. Users table (enrolled employees and password-hashed administrators)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,             -- For Admin logins (nullable)
    role TEXT DEFAULT 'Employee',   -- 'Employee', 'Admin', 'Visitor', etc.
    face_encoding TEXT,             -- JSON serialized 128-d vector (nullable)
    photo_path TEXT,                -- File path reference for enrolled profiles
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 2. Attendance history logs
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,             -- Name snapshot at scan time (e.g. 'Unknown Visage')
    timestamp TEXT NOT NULL,        -- YYYY-MM-DD HH:MM:SS
    status TEXT NOT NULL,           -- 'Present' or 'Unknown'
    photo_path TEXT,                -- Matching camera capture snapshot path
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 3. Unrecognized visitor security alerts
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,        -- YYYY-MM-DD HH:MM:SS
    photo_path TEXT NOT NULL,       -- Visitor snapshot crop path
    status TEXT DEFAULT 'Unresolved', -- 'Unresolved', 'Resolved', 'Dismissed'
    resolved_user_id INTEGER,
    resolved_at TEXT,
    FOREIGN KEY (resolved_user_id) REFERENCES users(id) ON DELETE SET NULL
);
