import cv2

class CameraUtility:
    """
    Utility helper mapping frame dimensions, resolutions, and video transformations.
    Supports aspect-ratio scaling and cropping.
    """
    
    @staticmethod
    def get_resolutions():
        """
        Returns supported scanning resolutions.
        """
        return {
            "low": (320, 240),
            "standard": (640, 480),
            "high": (1280, 720)
        }
        
    @staticmethod
    def resize_frame(frame, target_width=640):
        """
        Resizes an OpenCV frame maintaining aspect ratio.
        """
        if frame is None:
            return None
            
        h, w = frame.shape[:2]
        if w == target_width:
            return frame
            
        aspect = h / w
        target_height = int(target_width * aspect)
        return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)
        
    @staticmethod
    def crop_face(frame, box, padding_percent=0.2):
        """
        Crops a face out of a BGR frame based on box coordinates [top, right, bottom, left].
        Pads the crop area by the specified percentage for better visual context.
        """
        if frame is None or not box:
            return None
            
        try:
            h, w = frame.shape[:2]
            top, right, bottom, left = box
            
            box_h = bottom - top
            box_w = right - left
            
            pad_h = int(box_h * padding_percent)
            pad_w = int(box_w * padding_percent)
            
            y1 = max(0, top - pad_h)
            y2 = min(h, bottom + pad_h)
            x1 = max(0, left - pad_w)
            x2 = min(w, right + pad_w)
            
            return frame[y1:y2, x1:x2]
        except Exception as e:
            print(f"[CAMERA_UTILITY] Failed to crop face: {e}")
            return frame # Fallback to returning full frame
