"""
InvoiceFlow - Professional Invoice Management System
Main Flask Application

WARNING: This application contains intentional security vulnerabilities
for penetration testing training purposes only. DO NOT deploy to production!
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file
import os
import secrets
from datetime import datetime

# Import configuration
import config

# Import database functions
import database as db

# Initialize Flask app
app = Flask(__name__)

# Vulnerability #12: Debug mode enabled & weak secret key
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Vulnerability #15: Insecure session configuration
app.config['SESSION_COOKIE_SECURE'] = config.SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = config.SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = config.SESSION_COOKIE_SAMESITE
app.config['PERMANENT_SESSION_LIFETIME'] = config.PERMANENT_SESSION_LIFETIME

# Vulnerability #24: Missing security headers
@app.after_request
def add_headers(response):
    """
    Add response headers - MISSING critical security headers:
    - No Content-Security-Policy
    - No X-Frame-Options (clickjacking)
    - No X-Content-Type-Options
    - No Strict-Transport-Security
    """
    # Vulnerability #25: Verbose server header
    response.headers['Server'] = 'Flask/3.0.0 Python/3.11 InvoiceFlow/1.0'

    # Vulnerability #20: CORS wildcard
    if config.CORS_ENABLED:
        response.headers['Access-Control-Allow-Origin'] = config.CORS_ORIGINS
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    return response


# Helper function to check if user is logged in
def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session and 'username' in session


def require_login():
    """Decorator-like function to check login"""
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    return None


def is_admin():
    """Check if current user is admin"""
    return session.get('role') == 'admin'


# Initialize database on first run
@app.before_request
def before_first_request():
    """Initialize database if it doesn't exist"""
    if not os.path.exists(config.DATABASE_PATH):
        db.init_database()


# Home/Landing page
@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


# Import route blueprints
from routes.auth import auth_bp
from routes.invoice import invoice_bp
from routes.admin import admin_bp
from routes.api import api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(invoice_bp, url_prefix='/invoice')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')


# Dashboard route
@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    user_id = session['user_id']

    # Get dashboard statistics
    stats = db.get_dashboard_stats(user_id)

    # Get recent invoices
    recent_invoices = db.get_invoices_by_user(user_id)[:5]

    return render_template('dashboard/index.html',
                          stats=stats,
                          recent_invoices=recent_invoices,
                          user=session)


# Profile/Settings route
@app.route('/profile')
def profile():
    """User profile page"""
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    user = db.get_user_by_id(session['user_id'])
    return render_template('profile/settings.html', user=user)


# Vulnerability #7: CSRF in profile update (no CSRF token validation)
@app.route('/profile/update', methods=['POST'])
def update_profile():
    """Update user profile - VULNERABLE to CSRF"""
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    user_id = session['user_id']

    # Get form data
    email = request.form.get('email')
    full_name = request.form.get('full_name')
    password = request.form.get('password')

    # Update user
    update_data = {}
    if email:
        update_data['email'] = email
    if full_name:
        update_data['full_name'] = full_name
    if password:
        # Vulnerability #8: Plaintext password storage
        update_data['password'] = password

    if update_data:
        db.update_user(user_id, **update_data)

    return redirect(url_for('profile'))


# Error handlers
# Vulnerability #17: Verbose error messages exposing system information
@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    if config.VERBOSE_ERRORS:
        return f"""
        <h1>404 - Page Not Found</h1>
        <p>The requested URL was not found on the server.</p>
        <p>Request path: {request.path}</p>
        <p>Request method: {request.method}</p>
        <p>Server: {config.HOST}:{config.PORT}</p>
        """, 404
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler - exposes stack trace"""
    if config.VERBOSE_ERRORS:
        import traceback
        return f"""
        <h1>500 - Internal Server Error</h1>
        <p>An error occurred while processing your request.</p>
        <pre>{traceback.format_exc()}</pre>
        <p>Database path: {config.DATABASE_PATH}</p>
        """, 500
    return render_template('errors/500.html'), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Generic exception handler - verbose debugging info"""
    if config.VERBOSE_ERRORS:
        import traceback
        return f"""
        <h1>Application Error</h1>
        <p>Error: {str(error)}</p>
        <pre>{traceback.format_exc()}</pre>
        """, 500
    return "An error occurred", 500


# Main entry point
if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

    # Initialize database if needed
    if not os.path.exists(config.DATABASE_PATH):
        db.init_database()
        print("Database initialized with seed data")

    # Vulnerability #12: Debug mode enabled in production
    # Vulnerability #24: Running on 0.0.0.0 exposes to network
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                      InvoiceFlow                          ║
    ║              Streamline Your Billing                      ║
    ╚═══════════════════════════════════════════════════════════╝

    Starting server at http://{config.HOST}:{config.PORT}

    Test Credentials:
    - Admin:  admin / admin123
    - User:   john / password123
    - User:   test / test

    WARNING: This is a deliberately vulnerable application
             for penetration testing training purposes.
             DO NOT use in production!
    """)

    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
