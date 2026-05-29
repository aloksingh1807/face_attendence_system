from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database.models import get_user_by_email
from utils.logger import log_info, log_warn

# Define the Auth Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Renders the administrator login portal and validates credentials.
    """
    # If already logged in, redirect directly to dashboard
    if session.get('admin_logged'):
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return redirect(url_for('auth.login'))
            
        # Find user by email
        user = get_user_by_email(email)
        
        # Verify credentials and check if role is Administrator
        if user and user['password_hash'] and check_password_hash(user['password_hash'], password):
            if user['role'] == 'Admin':
                # Establish session keys
                session['admin_logged'] = True
                session['admin_id'] = user['id']
                session['admin_name'] = user['name']
                session['admin_email'] = user['email']
                
                log_info(f"Admin login success: {email}")
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('dashboard.index'))
                
        # Handle invalid log in
        log_warn(f"Failed login attempt for: {email}")
        flash("Invalid email or password. Please try again.", "danger")
        return redirect(url_for('auth.login'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """
    Clears administrator session and redirects to login.
    """
    email = session.get('admin_email', 'Unknown')
    session.clear()
    log_info(f"Admin logged out: {email}")
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('auth.login'))
