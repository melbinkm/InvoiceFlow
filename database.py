"""
Database operations for InvoiceFlow
Contains intentional SQL injection vulnerabilities for training
"""

import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with schema and seed data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute schema
    schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        cursor.executescript(f.read())

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()['count'] == 0:
        # Execute seed data
        seed_path = os.path.join(os.path.dirname(__file__), 'database', 'seed_data.sql')
        with open(seed_path, 'r') as f:
            cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_PATH}")


# Vulnerability #1 & #8: SQL Injection in authentication
def authenticate_user(username, password):
    """
    Authenticate user with username and password
    VULNERABLE: Time-based blind SQL injection in password check
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # First, get user by username (safe parameterized query)
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return None

    # Vulnerability #1: Time-based blind SQL injection via password verification
    # The password check uses a CASE statement that can be exploited
    query = f"""
        SELECT * FROM users
        WHERE username=?
        AND (
            CASE
                WHEN password='{password}' THEN 1
                ELSE 0
            END
        ) = 1
    """

    try:
        cursor.execute(query, (username,))
        authenticated_user = cursor.fetchone()
        conn.close()
        return dict(authenticated_user) if authenticated_user else None
    except Exception as e:
        conn.close()
        # Vulnerability #17: Verbose error messages (keep for training)
        print(f"Database error: {str(e)}")
        return None


def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_username(username):
    """Get user by username - VULNERABLE to SQL injection"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vulnerability: SQL Injection in user lookup
    query = f"SELECT * FROM users WHERE username='{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def create_user(username, email, password, full_name, role='user'):
    """Create new user - Vulnerability #8: plaintext password storage"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Vulnerability #8: Storing password as plaintext
        cursor.execute("""
            INSERT INTO users (username, email, password, full_name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, password, full_name, role, datetime.now()))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def update_user(user_id, **kwargs):
    """Update user information"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build update query dynamically
    fields = []
    values = []
    for key, value in kwargs.items():
        if key in ['username', 'email', 'password', 'full_name', 'role']:
            fields.append(f"{key}=?")
            values.append(value)

    if not fields:
        conn.close()
        return False

    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE id=?"

    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return True


def update_last_login(user_id):
    """Update user's last login timestamp"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_login=? WHERE id=?", (datetime.now(), user_id))
    conn.commit()
    conn.close()


# Invoice operations
def create_invoice(user_id, company_id, invoice_number, invoice_date, due_date,
                  status, subtotal, tax_rate, tax_amount, discount, total, notes, terms):
    """Create new invoice"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO invoices (user_id, company_id, invoice_number, invoice_date, due_date,
                             status, subtotal, tax_rate, tax_amount, discount, total, notes, terms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, company_id, invoice_number, invoice_date, due_date,
          status, subtotal, tax_rate, tax_amount, discount, total, notes, terms))

    invoice_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return invoice_id


def get_invoice(invoice_id):
    """
    Get invoice by ID
    Used in IDOR vulnerability - no authorization check here
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
    invoice = cursor.fetchone()
    conn.close()
    return dict(invoice) if invoice else None


def get_invoices_by_user(user_id):
    """Get all invoices for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, c.company_name
        FROM invoices i
        LEFT JOIN companies c ON i.company_id = c.id
        WHERE i.user_id=?
        ORDER BY i.created_at DESC
    """, (user_id,))
    invoices = cursor.fetchall()
    conn.close()
    return [dict(inv) for inv in invoices]


def search_invoices(user_id, search_term):
    """
    Search invoices - VULNERABLE to SQL injection
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vulnerability: SQL Injection in search
    query = f"""
        SELECT i.*, c.company_name
        FROM invoices i
        LEFT JOIN companies c ON i.company_id = c.id
        WHERE i.user_id={user_id} AND (
            i.invoice_number LIKE '%{search_term}%' OR
            i.notes LIKE '%{search_term}%' OR
            c.company_name LIKE '%{search_term}%'
        )
        ORDER BY i.created_at DESC
    """

    cursor.execute(query)
    invoices = cursor.fetchall()
    conn.close()
    return [dict(inv) for inv in invoices]


def update_invoice(invoice_id, **kwargs):
    """Update invoice"""
    conn = get_db_connection()
    cursor = conn.cursor()

    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(f"{key}=?")
        values.append(value)

    values.append(datetime.now())
    fields.append("updated_at=?")
    values.append(invoice_id)

    query = f"UPDATE invoices SET {', '.join(fields)} WHERE id=?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()


def delete_invoice(invoice_id):
    """Delete invoice and associated items"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM invoice_items WHERE invoice_id=?", (invoice_id,))
    cursor.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))

    conn.commit()
    conn.close()


# Invoice items operations
def add_invoice_item(invoice_id, description, quantity, unit_price, amount, sort_order=0):
    """Add item to invoice"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, amount, sort_order)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (invoice_id, description, quantity, unit_price, amount, sort_order))

    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id


def get_invoice_items(invoice_id):
    """Get all items for an invoice"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoice_items WHERE invoice_id=? ORDER BY sort_order", (invoice_id,))
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]


def delete_invoice_items(invoice_id):
    """Delete all items for an invoice"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoice_items WHERE invoice_id=?", (invoice_id,))
    conn.commit()
    conn.close()


# Company operations
def create_company(user_id, company_name, contact_person, email, phone,
                   address, city, state, zip_code, country):
    """Create new company"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO companies (user_id, company_name, contact_person, email, phone,
                              address, city, state, zip_code, country)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, company_name, contact_person, email, phone,
          address, city, state, zip_code, country))

    company_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return company_id


def get_companies_by_user(user_id):
    """Get all companies for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE user_id=? ORDER BY company_name", (user_id,))
    companies = cursor.fetchall()
    conn.close()
    return [dict(comp) for comp in companies]


def get_company(company_id):
    """Get company by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE id=?", (company_id,))
    company = cursor.fetchone()
    conn.close()
    return dict(company) if company else None


# Session operations (Vulnerability #9: Weak session management)
def create_session(session_id, user_id, ip_address, user_agent):
    """Create session - vulnerable to session fixation"""
    conn = get_db_connection()
    cursor = conn.cursor()

    from datetime import timedelta
    expires_at = datetime.now() + timedelta(hours=24)

    cursor.execute("""
        INSERT INTO sessions (session_id, user_id, ip_address, user_agent, expires_at)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, user_id, ip_address, user_agent, expires_at))

    conn.commit()
    conn.close()


def get_session(session_id):
    """Get session by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,))
    session = cursor.fetchone()
    conn.close()
    return dict(session) if session else None


def delete_session(session_id):
    """Delete session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_id=?", (session_id,))
    conn.commit()
    conn.close()


# Activity logging
def log_activity(user_id, action, resource_type=None, resource_id=None, ip_address=None, details=None):
    """Log user activity"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO activity_log (user_id, action, resource_type, resource_id, ip_address, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, action, resource_type, resource_id, ip_address, details))

    conn.commit()
    conn.close()


# Admin functions
def get_all_users():
    """Get all users (admin function)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]


def get_all_invoices():
    """Get all invoices (admin function)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, u.username, c.company_name
        FROM invoices i
        LEFT JOIN users u ON i.user_id = u.id
        LEFT JOIN companies c ON i.company_id = c.id
        ORDER BY i.created_at DESC
    """)
    invoices = cursor.fetchall()
    conn.close()
    return [dict(inv) for inv in invoices]


def get_dashboard_stats(user_id):
    """Get dashboard statistics for user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}

    # Total invoices
    cursor.execute("SELECT COUNT(*) as count FROM invoices WHERE user_id=?", (user_id,))
    stats['total_invoices'] = cursor.fetchone()['count']

    # Paid invoices
    cursor.execute("SELECT COUNT(*) as count FROM invoices WHERE user_id=? AND status='paid'", (user_id,))
    stats['paid_invoices'] = cursor.fetchone()['count']

    # Pending invoices
    cursor.execute("SELECT COUNT(*) as count FROM invoices WHERE user_id=? AND status='sent'", (user_id,))
    stats['pending_invoices'] = cursor.fetchone()['count']

    # Overdue invoices
    cursor.execute("SELECT COUNT(*) as count FROM invoices WHERE user_id=? AND status='overdue'", (user_id,))
    stats['overdue_invoices'] = cursor.fetchone()['count']

    # Total revenue
    cursor.execute("SELECT SUM(total) as revenue FROM invoices WHERE user_id=? AND status='paid'", (user_id,))
    result = cursor.fetchone()
    stats['total_revenue'] = result['revenue'] if result['revenue'] else 0

    # Outstanding amount
    cursor.execute("SELECT SUM(total) as outstanding FROM invoices WHERE user_id=? AND status IN ('sent', 'overdue')", (user_id,))
    result = cursor.fetchone()
    stats['outstanding_amount'] = result['outstanding'] if result['outstanding'] else 0

    conn.close()
    return stats
