import sqlite3
import os
from flask import g, current_app
from werkzeug.security import generate_password_hash

def get_db():
    """
    Returns a unique thread-safe SQLite connection for the current Flask request context.
    Enables row-dict access and enforces foreign keys constraint.
    """
    if 'db' not in g:
        # Pull database path from Flask global application configuration
        db_path = current_app.config['DATABASE']
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
        
    return g.db

def close_db(e=None):
    """
    Closes the SQLite database connection at the end of the Flask context lifecycle.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """
    Binds database teardown hooks and initializes SQLite tables from schema.sql.
    Seeds a default Admin user if none exists.
    """
    app.teardown_appcontext(close_db)
    
    with app.app_context():
        db = get_db()
        
        # 1. Read and execute table schemas
        schema_path = os.path.join(app.root_path, "database", "schema.sql")
        with open(schema_path, "r") as f:
            db.executescript(f.read())
            
        # 2. Check and seed default administrator credentials
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            default_admin_name = "System Admin"
            default_admin_email = "admin@admin.com"
            default_admin_pass = "admin"
            
            # Salt and hash password using Werkzeug's default recommended scrypt method
            pass_hash = generate_password_hash(default_admin_pass, method="scrypt")
            
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (default_admin_name, default_admin_email, pass_hash, 'Admin')
            )
            db.commit()
            print("[DB] Default administrator profile seeded successfully.")
