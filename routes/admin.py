"""
Admin panel routes for InvoiceFlow
Contains weak access control and privilege escalation vulnerabilities
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import database as db

admin_bp = Blueprint('admin', __name__)


def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session


def is_admin():
    """
    Check if user is admin
    Vulnerability #14: Weak access control - only checks session variable
    """
    return session.get('role') == 'admin'


def require_admin():
    """Require admin access"""
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    if not is_admin():
        # Vulnerability #17: Verbose error exposing admin endpoint
        return f"Access denied. Admin role required. Your role: {session.get('role', 'none')}", 403
    return None


@admin_bp.route('/')
@admin_bp.route('/panel')
def panel():
    """
    Admin panel main page
    Vulnerability #14: Weak access control
    Vulnerability #23: Sensitive information in HTML comments
    """
    redirect_check = require_admin()
    if redirect_check:
        return redirect_check

    # Get system statistics
    all_users = db.get_all_users()
    all_invoices = db.get_all_invoices()

    total_revenue = sum([inv['total'] for inv in all_invoices if inv['status'] == 'paid'])
    pending_revenue = sum([inv['total'] for inv in all_invoices if inv['status'] in ['sent', 'draft']])

    stats = {
        'total_users': len(all_users),
        'total_invoices': len(all_invoices),
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue
    }

    # Vulnerability #23: Sensitive information will be in HTML comments
    return render_template('admin/panel.html',
                          stats=stats,
                          users=all_users,
                          recent_invoices=all_invoices[:10])


@admin_bp.route('/users')
def users():
    """
    Admin user management
    Vulnerability #25: Exposes plaintext passwords
    """
    redirect_check = require_admin()
    if redirect_check:
        return redirect_check

    users = db.get_all_users()

    # Vulnerability #25: User list includes plaintext passwords
    return render_template('admin/users.html', users=users)


@admin_bp.route('/user/<int:user_id>')
def view_user(user_id):
    """
    View user details
    Vulnerability #25: Exposes plaintext password
    """
    redirect_check = require_admin()
    if redirect_check:
        return redirect_check

    user = db.get_user_by_id(user_id)
    if not user:
        return "User not found", 404

    # Get user's invoices
    invoices = db.get_invoices_by_user(user_id)

    return render_template('admin/user_details.html',
                          user=user,
                          invoices=invoices)


@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """
    Edit user
    Vulnerability #7: No CSRF protection
    Vulnerability #14: Can manipulate role field
    """
    redirect_check = require_admin()
    if redirect_check:
        return redirect_check

    user = db.get_user_by_id(user_id)
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        # Vulnerability #7: No CSRF token validation
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        role = request.form.get('role')  # Vulnerability: Can escalate privileges
        password = request.form.get('password')
        is_active = request.form.get('is_active', '1')

        update_data = {}
        if email:
            update_data['email'] = email
        if full_name:
            update_data['full_name'] = full_name
        if role:
            update_data['role'] = role  # Privilege escalation possible
        if password:
            update_data['password'] = password  # Plaintext
        if is_active is not None:
            update_data['is_active'] = int(is_active)

        db.update_user(user_id, **update_data)

        db.log_activity(session['user_id'], 'admin_update', 'user', user_id,
                       request.remote_addr, f'Admin updated user {user["username"]}')

        return redirect(url_for('admin.view_user', user_id=user_id))

    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """
    Delete user
    Vulnerability #7: No CSRF protection
    """
    redirect_check = require_admin()
    if redirect_check:
        return redirect_check

    # Vulnerability #7: No CSRF token
    user = db.get_user_by_id(user_id)
    if user:
        # Delete user (dangerous - should soft delete)
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

        db.log_activity(session['user_id'], 'admin_delete', 'user', user_id,
                       request.remote_addr, f'Admin deleted user {user["username"]}')

    return redirect(url_for('admin.users'))


@admin_bp.route('/invoices')
def invoices():
    """Admin view of all invoices"""
    redirect_check = require_admin()
    if redirect_check:
        return redirect_check

    all_invoices = db.get_all_invoices()
    return render_template('admin/invoices.html', invoices=all_invoices)


@admin_bp.route('/logs')
def logs():
    """
    View activity logs
    Vulnerability #23: Exposes system information
    """
    redirect_check = require_admin()
    if redirect_check:
        return redirect_check

    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT al.*, u.username
        FROM activity_log al
        LEFT JOIN users u ON al.user_id = u.id
        ORDER BY al.created_at DESC
        LIMIT 100
    """)
    logs = cursor.fetchall()
    conn.close()

    return render_template('admin/logs.html', logs=[dict(log) for log in logs])


@admin_bp.route('/debug-info')
def debug_info():
    """
    Debug information endpoint
    Vulnerability #12: Debug mode exposing sensitive info
    Vulnerability #23: System information disclosure
    """
    redirect_check = require_admin()
    if redirect_check:
        return redirect_check

    import sys
    import platform
    import config

    debug_data = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'database_path': config.DATABASE_PATH,
        'upload_folder': config.UPLOAD_FOLDER,
        'secret_key': config.SECRET_KEY,  # Vulnerability: Exposes secret key!
        'debug_mode': config.DEBUG,
        'session_config': {
            'secure': config.SESSION_COOKIE_SECURE,
            'httponly': config.SESSION_COOKIE_HTTPONLY,
            'samesite': config.SESSION_COOKIE_SAMESITE
        },
        'current_session': dict(session)  # Vulnerability: Exposes session data
    }

    return jsonify(debug_data)


@admin_bp.route('/sql-console', methods=['GET', 'POST'])
def sql_console():
    """
    SQL Console for admin
    Vulnerability #1: Direct SQL execution without validation
    """
    redirect_check = require_admin()
    if redirect_check:
        return redirect_check

    result = None
    error = None

    if request.method == 'POST':
        sql_query = request.form.get('query', '')

        # Vulnerability: Execute any SQL query directly
        try:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query)

            if sql_query.strip().upper().startswith('SELECT'):
                result = [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                result = f"Query executed. Rows affected: {cursor.rowcount}"

            conn.close()
        except Exception as e:
            error = str(e)

    return render_template('admin/sql_console.html', result=result, error=error)
