from flask import Blueprint, render_template, jsonify, redirect, url_for
from utils.security import login_required
from database.models import get_dashboard_stats

# Define Dashboard Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """
    Renders the primary administrator overview dashboard with today's stats,
    recent scanner events feed, and weekly charts.
    """
    stats = get_dashboard_stats()
    return render_template('dashboard.html', stats=stats, active_page='dashboard')

@dashboard_bp.route('/api/stats')
@login_required
def get_stats():
    """
    Reactive API returning active statistical summaries.
    """
    stats = get_dashboard_stats()
    return jsonify(stats)
