import cv2
import numpy as np
import face_recognition
import base64
import os

def decode_base64_image(base64_str):
    """
    Decodes a base64-encoded JPEG/PNG image string into an OpenCV BGR image matrix.
    Handles MIME headers correctly.
    """
    if not base64_str:
        return None
        
    try:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
            
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"[FACE_HELPER] Error decoding base64 image: {e}")
        return None

def encode_face_from_image_path(image_path):
    """
    Loads an image from disk and extracts the 128-dimensional face encoding vector.
    Returns the vector as a Python list of floats, or None if no face is detected.
    """
    if not os.path.exists(image_path):
        return None
        
    try:
        # Load image file
        img = face_recognition.load_image_file(image_path)
        
        # Detect and extract encodings
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:
            # Return standard float array
            return list(encodings[0])
        return None
    except Exception as e:
        print(f"[FACE_HELPER] Failed extracting encoding from {image_path}: {e}")
        return None

def process_frame(cv2_img, enrolled_users, tolerance=0.6):
    """
    Detects all faces in a BGR frame, extracts their vectors, and matches them against enrolled users.
    Returns a list of detected face dictionaries:
    {
        "box": [top, right, bottom, left],
        "user_id": int or None,
        "name": str,
        "matched": bool
    }
    """
    if cv2_img is None or len(cv2_img) == 0:
        return []
        
    try:
        # Convert BGR (OpenCV) to RGB (face_recognition)
        rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        
        # 1. Find all face locations and encodings in the frame
        face_locations = face_recognition.face_locations(rgb_img)
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        detected_faces = []
        
        # Extract enrolled encodings and matching metadata
        known_encodings = [user["encoding"] for user in enrolled_users]
        known_ids = [user["id"] for user in enrolled_users]
        known_names = [user["name"] for user in enrolled_users]
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            user_id = None
            name = "Unknown Visage"
            matched = False
            
            if len(known_encodings) > 0:
                # Calculate Euclidean distances between the current face and all enrolled faces
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_idx = np.argmin(face_distances)
                
                if face_distances[best_match_idx] <= tolerance:
                    user_id = known_ids[best_match_idx]
                    name = known_names[best_match_idx]
                    matched = True
                    
            detected_faces.append({
                "box": [top, right, bottom, left],
                "user_id": user_id,
                "name": name,
                "matched": matched
            })
            
        return detected_faces
    except Exception as e:
        print(f"[FACE_HELPER] Error processing frame: {e}")
        return []
