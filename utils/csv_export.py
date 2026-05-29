def generate_attendance_csv(logs):
    """
    Translates a list of attendance log dictionaries into a standard comma-separated string format.
    Escapes quotes for spreadsheet compliance.
    """
    # 1. Setup headers
    csv_rows = ["Log ID,Name,Email,Access Role,Scan Timestamp,Status"]
    
    # 2. Iterate and append rows
    for log in logs:
        log_id = log.get("id", "")
        name = str(log.get("scan_name", "Unknown")).replace('"', '""')
        email = str(log.get("email") or "N/A").replace('"', '""')
        role = str(log.get("role") or "N/A").replace('"', '""')
        timestamp = log.get("timestamp", "")
        status = log.get("status", "Unknown")
        
        row_str = f'{log_id},"{name}","{email}","{role}",{timestamp},{status}'
        csv_rows.append(row_str)
        
    return "\n".join(csv_rows)
