# Aura Scan - Smart Face Recognition Attendance System

A production-grade, highly structured, **Blueprint-based modular Flask application** utilizing real-time face matching, intrusion alerts, dynamic logs, and administrative controls. 
{Email: admin@admin.com}
{Password: admin}

---

## 🏗️ Folder Architecture

```text
face_attendence_system/
│
├── app.py                  # Main Flask entrypoint & application builder
├── requirements.txt        # Locked PIP dependencies (numpy, OpenCV, dlib)
├── README.md               # User manual & setup guides
├── .gitignore              # Files to ignore in git repository
├── attendance.db           # SQLite database binary (auto-created on run)
│
├── instance/
│   └── config.py           # Configuration values (keys, DB paths)
│
├── database/
│   ├── db.py               # SQLite connection manager & auto-seeding
│   ├── models.py           # Domain SQL queries mapped to python functions
│   └── schema.sql          # Core table definitions
│
├── routes/
│   ├── auth_routes.py      # Session management and password hashing
│   ├── dashboard_routes.py # Stats counts widgets and weekly charts trends
│   ├── user_routes.py      # User registrations and profiles directory CRUD
│   ├── attendance_routes.py# Real-time frame scanning & checking in
│   └── alert_routes.py     # Visitor alerts resolutions & SSE streams
│
├── utils/
│   ├── face_helper.py      # OpenCV / face_recognition wrapper
│   ├── camera.py           # Auxiliary camera helpers
│   ├── csv_export.py       # Streamed CSV generation utility
│   ├── logger.py           # Log events to local instance/app.log file
│   └── security.py         # Login-required decorator guards
│
├── templates/
│   ├── base.html           # Master layout page
│   ├── login.html          # Gateway portal
│   ├── dashboard.html      # Primary statistics panel
│   ├── camera.html         # Live scan viewer
│   ├── users.html          # Profiles directory and registration wizard
│   ├── logs.html           # Interactive table search & CSV logs
│   ├── alerts.html         # Intrusion center with snapshots
│   └── components/
│       ├── sidebar.html    # Reusable sidebar component
│       ├── navbar.html     # Reusable top navigation bar component
│       └── stats_card.html # Reusable stats macro component
│
├── static/
│   ├── css/
│   │   ├── style.css       # Core variables & layout styles
│   │   ├── dashboard.css   # Specialized KPI card designs & widgets
│   │   └── animations.css  # Laser sweeps, heartbeats, glow keyframes
│   └── js/
│       ├── main.js         # SSE broadcasts & general toasts
│       ├── camera.js       # Live mirror canvas drawing & webcam streams
│       ├── users.js        # Snapshot wizard & list loaders
│       └── alerts.js       # Intrusion updates & action resolvers
│
└── tests/
    ├── test_database.py    # Database connection test suite
    ├── test_face_recognition.py # Core recognition test suite
    └── test_routes.py      # Route endpoints validation suite
```

---

## 🚀 Quick Start Guide

### Step 1: Open Terminal in the new project directory
Ensure you open the **`face_attendence_system`** folder in your editor or terminal.
```bash
cd /Users/aloksingh/.gemini/antigravity/scratch/face_attendence_system
```

### Step 2: Set up the Python Virtual Environment
Create and activate the virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
Install the pinned libraries:
```bash
pip install -r requirements.txt
```

### Step 4: Run the Flask Web Server
Launch the application:
```bash
python app.py
```
*The server will spin up on: `http://127.0.0.1:5000`*

### Step 5: Log in to the Admin Portal
Go to `http://127.0.0.1:5000` in your web browser and log in using the default secure seeded admin credentials:
*   **Email**: `admin@admin.com`
*   **Password**: `admin`

---

## 🧪 Running Automated Tests
Validate the database layer, route security session locks, and OpenCV decoding libraries:
```bash
python -m unittest discover -s tests
```
All tests will execute and return successful passes.
