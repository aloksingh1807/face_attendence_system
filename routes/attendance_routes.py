from flask import Blueprint, render_template, request, jsonify, make_response, current_app
from datetime import datetime, timedelta
import os
import uuid
import cv2
from utils.security import login_required
from utils.logger import log_info, log_warn, log_error
import utils.face_helper as face_helper
import utils.csv_export as csv_export
from utils.camera import CameraUtility
import database.models as models

# Define Attendance Blueprint
attendance_bp = Blueprint('attendance', __name__)

# Simple in-memory cooldown trackers
last_logged_scans = {}  # {user_id: last_timestamp}
last_alert_logged = datetime.min

@attendance_bp.route('/camera')
@login_required
def camera():
    """
    Renders the live webcam recognition scanner viewport.
    """
    return render_template('camera.html', active_page='camera')

@attendance_bp.route('/logs')
@login_required
def index():
    """
    Renders the searchable attendance records logs table.
    """
    return render_template('logs.html', active_page='logs')

@attendance_bp.route('/api/scan', methods=['POST'])
@login_required
def api_scan():
    """
    Processes an incoming webcam base64 frame, matches it with database profiles,
    and logs attendance logs and unrecognized intrusion alerts.
    """
    global last_alert_logged
    
    data = request.get_json() or {}
    image_base64 = data.get("image")
    tolerance = float(data.get("tolerance", 0.6))
    
    if not image_base64:
        return jsonify({"error": "Missing frame image data."}), 400
        
    try:
        # 1. Decode frame
        cv2_img = face_helper.decode_base64_image(image_base64)
        if cv2_img is None:
            return jsonify({"error": "Failed to decode scan frame."}), 400
            
        # 2. Get enrolled employee vectors
        enrolled_users = models.get_user_encodings()
        
        # 3. Match faces
        faces = face_helper.process_frame(cv2_img, enrolled_users, tolerance=tolerance)
        
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        scan_results = []
        
        for face in faces:
            box = face["box"]
            user_id = face["user_id"]
            name = face["name"]
            matched = face["matched"]
            
            if matched:
                # 4. Handle Cooldown for recognized employee
                cooldown_expiry = last_logged_scans.get(user_id)
                if cooldown_expiry and (now - cooldown_expiry) < timedelta(minutes=5):
                    # Skip logging check-in due to 5-minute cooldown
                    scan_results.append({
                        "name": name,
                        "status": "Present (Cooldown Active)",
                        "matched": True
                    })
                    continue
                    
                # Log attendance
                models.log_attendance(user_id, name, timestamp_str, "Present")
                last_logged_scans[user_id] = now
                log_info(f"Check-in logged for: {name} (ID: {user_id})")
                
                scan_results.append({
                    "name": name,
                    "status": "Present",
                    "matched": True
                })
            else:
                # 5. Handle Cooldown and logging for unrecognized intruders
                if (now - last_alert_logged) < timedelta(seconds=15):
                    # Skip logging alert to avoid flooding during scanner streams
                    scan_results.append({
                        "name": "Unknown Visage",
                        "status": "Unknown (Cooldown Active)",
                        "matched": False
                    })
                    continue
                    
                last_alert_logged = now
                
                # Crop intruder face
                face_crop = CameraUtility.crop_face(cv2_img, box)
                relative_alert_path = None
                
                if face_crop is not None and len(face_crop) > 0:
                    alert_dir = current_app.config['UPLOAD_ALERTS_DIR']
                    alert_filename = f"alert_{uuid.uuid4().hex}.jpg"
                    alert_path = os.path.join(alert_dir, alert_filename)
                    cv2.imwrite(alert_path, face_crop)
                    relative_alert_path = f"static/uploads/alerts/{alert_filename}"
                    
                # Log attendance as Unknown
                models.log_attendance(None, "Unknown Visage", timestamp_str, "Unknown", relative_alert_path)
                
                # Log active security intrusion alert
                alert_id = models.create_alert(timestamp_str, relative_alert_path or "")
                log_warn(f"Intrusion Alert generated! Unrecognized visitor (Alert ID: {alert_id})")
                
                # Trigger a live event notification via alert blueprint SSE channel if possible
                from routes.alert_routes import trigger_alert_stream_broadcast
                trigger_alert_stream_broadcast({
                    "id": alert_id,
                    "timestamp": timestamp_str,
                    "photo_path": relative_alert_path or "",
                    "status": "Unresolved"
                })
                
                scan_results.append({
                    "name": "Unknown Visage",
                    "status": "Security Alert Created",
                    "matched": False,
                    "alert_id": alert_id
                })
                
        return jsonify({"success": True, "results": scan_results})
    except Exception as e:
        log_error(f"Error scanning live frame: {e}")
        return jsonify({"error": "Internal server error during frame matching."}), 500

@attendance_bp.route('/api/logs')
@login_required
def api_logs():
    """
    REST API returning history logs supporting filtering parameters.
    """
    search_query = request.args.get("search")
    status_filter = request.args.get("status")
    logs = models.get_attendance_logs(search_query, status_filter)
    return jsonify(logs)

@attendance_bp.route('/logs/export')
@login_required
def export_logs():
    """
    Generates streamed CSV sheet containing complete attendance records logs.
    """
    logs = models.get_attendance_logs()
    csv_content = csv_export.generate_attendance_csv(logs)
    
    response = make_response(csv_content)
    response.headers['Content-Disposition'] = 'attachment; filename=attendance_history.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response
