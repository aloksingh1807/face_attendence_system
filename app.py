from flask import Flask
import os

def create_app(test_config=None):
    """
    Application Factory Pattern for Flask.
    Creates and configures the Face Recognition Attendance System workspace.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # 1. Load Configurations
    if test_config is None:
        # Load from config.py in the instance/ folder
        config_path = os.path.join(app.instance_path, 'config.py')
        if os.path.exists(config_path):
            app.config.from_pyfile('config.py')
        else:
            # Set default values if file is missing
            app.config.from_mapping(
                SECRET_KEY="fallback_secure_key",
                DATABASE=os.path.join(app.root_path, "attendance.db"),
                UPLOAD_PROFILES_DIR=os.path.join(app.root_path, "static", "uploads", "profiles"),
                UPLOAD_ALERTS_DIR=os.path.join(app.root_path, "static", "uploads", "alerts")
            )
    else:
        # Load test configs if running tests
        app.config.from_mapping(test_config)
        
    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_PROFILES_DIR'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_ALERTS_DIR'], exist_ok=True)
    
    # 2. Initialize Database Setup
    from database import db
    db.init_db(app)
    
    # 3. Register Blueprints (Dynamic Routing Panels)
    from routes import auth_bp, dashboard_bp, user_bp, attendance_bp, alert_bp
    
    # Bind blueprints to the app factory context
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(alert_bp)
    
    return app

# Instantiate application for standard terminal execution
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
