from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """
    Decorator that restricts endpoint access to authenticated Administrators.
    Redirects back to login panel if no session is active.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged"):
            flash("Please log in to access this admin panel.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function
