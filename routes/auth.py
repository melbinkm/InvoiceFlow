"""
Authentication routes for InvoiceFlow
Contains SQL Injection, Session Fixation, and other auth vulnerabilities
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import secrets
import database as db
import config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route
    Vulnerability #1: SQL Injection in authentication
    Vulnerability #9: Session Fixation (no session regeneration)
    Vulnerability #19: No rate limiting on login attempts
    """
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # Vulnerability #1: SQL Injection via database.authenticate_user()
        # The database function uses string concatenation
        user = db.authenticate_user(username, password)

        if user:
            # Vulnerability #9: Session fixation - no session regeneration
            # Should call session.clear() and regenerate session ID
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            session['full_name'] = user['full_name']

            # Update last login
            db.update_last_login(user['id'])

            # Log activity
            db.log_activity(user['id'], 'login', 'user', user['id'],
                          request.remote_addr, 'Successful login')

            # Create session record (weak session management)
            session_id = secrets.token_hex(16)
            db.create_session(session_id, user['id'], request.remote_addr,
                            request.headers.get('User-Agent', ''))

            return redirect(url_for('dashboard'))
        else:
            # Vulnerability #17: Verbose error message
            error = f"Invalid credentials for user: {username}"
            return render_template('auth/login.html', error=error)

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route
    Vulnerability #3: No input validation on user data
    Vulnerability #8: Plaintext password storage
    """
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '')

        # Vulnerability #3: No input validation
        # Missing: email format validation, password strength check,
        # username sanitization, SQL injection protection

        # Check if user already exists (also vulnerable to SQL injection)
        existing_user = db.get_user_by_username(username)
        if existing_user:
            error = f"Username '{username}' already exists"
            return render_template('auth/register.html', error=error)

        # Vulnerability #8: Create user with plaintext password
        user_id = db.create_user(username, email, password, full_name, role='user')

        if user_id:
            # Auto-login after registration (session fixation here too)
            user = db.get_user_by_id(user_id)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            session['full_name'] = user['full_name']

            db.log_activity(user_id, 'register', 'user', user_id,
                          request.remote_addr, 'New user registration')

            return redirect(url_for('dashboard'))
        else:
            error = "Registration failed. Please try again."
            return render_template('auth/register.html', error=error)

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """Logout route - clears session"""
    if 'user_id' in session:
        db.log_activity(session['user_id'], 'logout', 'user', session['user_id'],
                       request.remote_addr, 'User logout')

        # Could delete session from database here, but we don't
        # Vulnerability: Sessions not properly invalidated server-side

    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot password route
    Vulnerability: User enumeration via different error messages
    """
    if request.method == 'POST':
        email = request.form.get('email', '')

        # Vulnerability: SQL Injection in email lookup
        conn = db.get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE email='{email}'"

        try:
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()

            if user:
                # Vulnerability: User enumeration - different message for existing user
                message = f"Password reset link sent to {email}"
                # In reality, no email is sent (not implemented)
            else:
                # Different error message reveals user doesn't exist
                message = f"No account found with email: {email}"

            return render_template('auth/forgot_password.html', message=message)
        except Exception as e:
            conn.close()
            # Vulnerability #17: Verbose error
            return render_template('auth/forgot_password.html',
                                 error=f"Database error: {str(e)}")

    return render_template('auth/forgot_password.html')


@auth_bp.route('/profile/update', methods=['POST'])
def update_profile():
    """
    Update user profile
    Vulnerability #14: Mass assignment allows role manipulation
    Vulnerability #7: No CSRF protection
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    # Vulnerability #14: Mass assignment vulnerability
    # Accepts ANY field from POST, including 'role'
    update_data = {}

    # Intentionally process all form fields without validation
    for key in request.form:
        if key in ['email', 'full_name', 'password', 'role']:  # role silently accepted!
            update_data[key] = request.form[key]

    if update_data:
        db.update_user(user_id, **update_data)

        # Update session if role changed
        if 'role' in update_data:
            session['role'] = update_data['role']

        db.log_activity(user_id, 'update_profile', 'user', user_id,
                       request.remote_addr, 'Profile updated')
        flash('Profile updated successfully', 'success')

    return redirect(url_for('dashboard'))


@auth_bp.route('/reset-password/<token>')
def reset_password(token):
    """
    Password reset route
    Vulnerability: Weak/predictable reset tokens (not properly implemented)
    """
    # Vulnerability: Token validation not implemented
    # Any token would work here
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/reset-password-submit', methods=['POST'])
def reset_password_submit():
    """
    Submit password reset
    Vulnerability: No token validation
    """
    token = request.form.get('token', '')
    new_password = request.form.get('password', '')
    user_id = request.form.get('user_id', '')  # Vulnerability: user_id from form

    # Vulnerability: No validation of token or user_id
    # Anyone can reset anyone's password if they know the user_id

    if user_id and new_password:
        # Vulnerability #8: Store plaintext password
        db.update_user(int(user_id), password=new_password)
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', error="Invalid request")
