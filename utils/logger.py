import logging
import os

# Base directory for logs
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance"))

def setup_logger():
    """
    Initializes application log handlers.
    Writes standard system events, errors, and check-ins to instance/app.log.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, "app.log")
    
    logger = logging.getLogger("AuraScan")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if already configured
    if not logger.handlers:
        # File Handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        
        # Console Handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
    return logger

# Initialize standard global logger
app_logger = setup_logger()

def log_info(message):
    """Logs system check-ins or audit trails."""
    app_logger.info(message)

def log_warn(message):
    """Logs security intrusion warnings or alerts."""
    app_logger.warning(message)

def log_error(message):
    """Logs database failures or C++ compiler exceptions."""
    app_logger.error(message)
