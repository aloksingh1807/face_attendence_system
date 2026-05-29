from flask import Blueprint, render_template, request, jsonify, Response, session
import json
import queue
from utils.security import login_required
from utils.logger import log_info, log_error
import database.models as models

# Define Alert Blueprint
alert_bp = Blueprint('alert', __name__)

# Real-time Server-Sent Events (SSE) subscriber clients list
sse_clients = []

def trigger_alert_stream_broadcast(alert_data):
    """
    Broadcasts a new security alert JSON event payload to all active SSE subscribers.
    """
    for client_queue in list(sse_clients):
        try:
            client_queue.put(alert_data)
        except Exception as e:
            # Clean up broken subscriber connections
            sse_clients.remove(client_queue)

@alert_bp.route('/alerts')
@login_required
def index():
    """
    Renders the central intrusion alert dashboard panel.
    """
    return render_template('alerts.html', active_page='alerts')

@alert_bp.route('/api/alerts')
@login_required
def get_alerts():
    """
    REST API returning database security alert logs.
    """
    status_filter = request.args.get("status")
    alerts_list = models.get_all_alerts(status_filter)
    return jsonify(alerts_list)

@alert_bp.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """
    Resolves a security alert, logging the resolving Administrator ID.
    """
    try:
        resolved_user_id = session.get("admin_id")
        if not resolved_user_id:
            return jsonify({"error": "Unauthorized session."}), 401
            
        success = models.resolve_alert(alert_id, resolved_user_id)
        if success:
            log_info(f"Security Alert {alert_id} resolved by Admin ID: {resolved_user_id}")
            return jsonify({"success": True, "message": "Alert marked as resolved."})
        return jsonify({"error": "Alert not found or already resolved."}), 404
    except Exception as e:
        log_error(f"Error resolving alert {alert_id}: {e}")
        return jsonify({"error": "Internal server error occurred."}), 500

@alert_bp.route('/api/alerts/stream')
@login_required
def alerts_stream():
    """
    SSE endpoint providing a persistent channel for push notifications.
    """
    client_queue = queue.Queue(maxsize=10)
    sse_clients.append(client_queue)
    
    def event_generator():
        # Keep-alive signal
        yield "data: {\"keep_alive\": true}\n\n"
        
        while True:
            try:
                # Bounded block waiting for trigger broadcasts
                alert_data = client_queue.get(block=True, timeout=30)
                yield f"data: {json.dumps(alert_data)}\n\n"
            except queue.Empty:
                # Send standard ping keep-alive to avoid connection drops
                yield "data: {\"ping\": true}\n\n"
            except Exception as e:
                # Remove client on connection closed
                if client_queue in sse_clients:
                    sse_clients.remove(client_queue)
                break
                
    return Response(event_generator(), mimetype="text/event-stream")
