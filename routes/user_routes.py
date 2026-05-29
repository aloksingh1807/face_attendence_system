from flask import Blueprint, render_template, request, jsonify, current_app
import os
import uuid
import cv2
from utils.security import login_required
from utils.logger import log_info, log_error
import utils.face_helper as face_helper
import database.models as models

# Define User Blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/users')
@login_required
def index():
    """
    Renders the employee directory and profile registration workspace.
    """
    return render_template('users.html', active_page='users')

@user_bp.route('/api/users', methods=['GET', 'POST'])
@login_required
def api_users():
    """
    REST API handling user CRUD operations.
    """
    if request.method == 'GET':
        users_list = models.get_all_users()
        return jsonify(users_list)
        
    elif request.method == 'POST':
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")
        role = data.get("role", "Employee")
        image_base64 = data.get("image")
        
        if not name or not email or not image_base64:
            return jsonify({"error": "Missing required fields (name, email, image)."}), 400
            
        try:
            # 1. Decode base64 frame
            cv2_img = face_helper.decode_base64_image(image_base64)
            if cv2_img is None:
                return jsonify({"error": "Failed to decode base64 profile image."}), 400
                
            # 2. Save temporary photo to disk
            upload_dir = current_app.config['UPLOAD_PROFILES_DIR']
            temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
            temp_path = os.path.join(upload_dir, temp_filename)
            cv2.imwrite(temp_path, cv2_img)
            
            # 3. Extract dlib face vector
            face_encoding = face_helper.encode_face_from_image_path(temp_path)
            
            if face_encoding is None:
                # Cleanup temp
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return jsonify({"error": "No face detected in the image. Please try again with better lighting."}), 400
                
            # Rename temp file to final profile image path
            final_filename = f"profile_{uuid.uuid4().hex}.jpg"
            final_path = os.path.join(upload_dir, final_filename)
            os.rename(temp_path, final_path)
            
            # 4. Save to Database
            relative_photo_path = f"static/uploads/profiles/{final_filename}"
            user_id, err = models.add_user(name, email, role, face_encoding, relative_photo_path)
            
            if err:
                # Cleanup file
                if os.path.exists(final_path):
                    os.remove(final_path)
                return jsonify({"error": err}), 400
                
            log_info(f"Successfully registered new user: {name} (ID: {user_id})")
            return jsonify({
                "success": True,
                "message": "User registered successfully!",
                "user": {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "role": role,
                    "photo_path": relative_photo_path
                }
            }), 201
            
        except Exception as e:
            log_error(f"Error enrolling user: {e}")
            return jsonify({"error": "Internal server error occurred."}), 500

@user_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """
    Deletes a registered user and removes their face profile photo from disk.
    """
    try:
        user = models.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404
            
        # Delete photo from disk if it exists
        photo_path = user.get("photo_path")
        if photo_path:
            abs_photo_path = os.path.join(current_app.root_path, photo_path)
            if os.path.exists(abs_photo_path):
                os.remove(abs_photo_path)
                
        # Delete from DB
        success = models.delete_user(user_id)
        if success:
            log_info(f"Deleted user profile ID: {user_id}")
            return jsonify({"success": True, "message": "User profile deleted successfully."})
        return jsonify({"error": "Failed to delete user from database."}), 500
    except Exception as e:
        log_error(f"Error deleting user {user_id}: {e}")
        return jsonify({"error": "Internal server error occurred."}), 500
