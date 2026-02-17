"""
API routes for InvoiceFlow
Contains XXE, Missing Authentication, and other API vulnerabilities
"""

from flask import Blueprint, request, jsonify, session
import xml.etree.ElementTree as ET
import json
import database as db
import config

api_bp = Blueprint('api', __name__)


def require_api_auth():
    """
    Check API authentication
    Vulnerability #13: Missing API authentication
    """
    if not config.API_REQUIRE_AUTH:
        # Vulnerability: API auth disabled
        return None

    # Check for API key in header
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API key required'}), 401

    # Validate API key (not implemented properly)
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_keys WHERE api_key=? AND is_active=1", (api_key,))
    key_record = cursor.fetchone()
    conn.close()

    if not key_record:
        return jsonify({'error': 'Invalid API key'}), 401

    return None


@api_bp.route('/invoices/list', methods=['GET'])
def api_list_invoices():
    """
    List invoices via API
    Vulnerability #13: Missing authentication
    Vulnerability #19: No rate limiting
    """
    # Vulnerability #13: No authentication check when API_REQUIRE_AUTH is False
    auth_check = require_api_auth()
    if auth_check:
        return auth_check

    # Vulnerability: No user isolation - can see all invoices
    all_invoices = db.get_all_invoices()

    return jsonify({
        'success': True,
        'count': len(all_invoices),
        'invoices': all_invoices
    })


@api_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
def api_get_invoice(invoice_id):
    """
    Get invoice by ID via API
    Vulnerability #4: IDOR via API
    Vulnerability #13: Missing authentication
    """
    # Vulnerability #13: No authentication
    auth_check = require_api_auth()
    if auth_check:
        return auth_check

    # Vulnerability #4: IDOR - no ownership check
    invoice = db.get_invoice(invoice_id)

    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    items = db.get_invoice_items(invoice_id)

    return jsonify({
        'success': True,
        'invoice': invoice,
        'items': items
    })


@api_bp.route('/invoices/create', methods=['POST'])
def api_create_invoice():
    """
    Create invoice via API
    Vulnerability #13: Missing authentication
    Vulnerability #3: No input validation
    """
    auth_check = require_api_auth()
    if auth_check:
        return auth_check

    data = request.get_json()

    # Vulnerability #3: No validation of input data
    try:
        invoice_id = db.create_invoice(
            data.get('user_id'),
            data.get('company_id'),
            data.get('invoice_number'),
            data.get('invoice_date'),
            data.get('due_date'),
            data.get('status', 'draft'),
            data.get('subtotal', 0),
            data.get('tax_rate', 0),
            data.get('tax_amount', 0),
            data.get('discount', 0),
            data.get('total', 0),
            data.get('notes', ''),
            data.get('terms', '')
        )

        # Add items
        for item in data.get('items', []):
            db.add_invoice_item(
                invoice_id,
                item.get('description', ''),
                item.get('quantity', 1),
                item.get('unit_price', 0),
                item.get('amount', 0),
                item.get('sort_order', 0)
            )

        return jsonify({
            'success': True,
            'invoice_id': invoice_id
        })
    except Exception as e:
        # Vulnerability #17: Verbose error
        return jsonify({'error': str(e)}), 500


@api_bp.route('/invoices/import-xml', methods=['POST'])
def api_import_xml():
    """
    Import invoices from XML
    Vulnerability #11: XXE (XML External Entity) Injection
    """
    auth_check = require_api_auth()
    if auth_check:
        return auth_check

    xml_data = request.data.decode('utf-8')

    try:
        # Vulnerability #11: XXE - XML parser without entity expansion disabled
        # This allows attackers to read local files, perform SSRF, etc.
        parser = ET.XMLParser()  # Default parser is vulnerable
        root = ET.fromstring(xml_data, parser=parser)

        invoices_imported = 0

        # Parse XML and create invoices
        for invoice_elem in root.findall('invoice'):
            user_id = invoice_elem.find('user_id').text if invoice_elem.find('user_id') is not None else None
            invoice_number = invoice_elem.find('invoice_number').text if invoice_elem.find('invoice_number') is not None else ''
            invoice_date = invoice_elem.find('invoice_date').text if invoice_elem.find('invoice_date') is not None else ''
            total = float(invoice_elem.find('total').text) if invoice_elem.find('total') is not None else 0

            if user_id and invoice_number:
                invoice_id = db.create_invoice(
                    int(user_id), None, invoice_number, invoice_date, None,
                    'draft', total, 0, 0, 0, total, '', ''
                )
                invoices_imported += 1

        return jsonify({
            'success': True,
            'imported': invoices_imported
        })

    except Exception as e:
        # Vulnerability #17: Verbose error
        return jsonify({'error': f'XML parsing error: {str(e)}'}), 400


@api_bp.route('/users/list', methods=['GET'])
def api_list_users():
    """
    List all users via API
    Vulnerability #13: Missing authentication
    Vulnerability #25: Exposes passwords in API response
    """
    auth_check = require_api_auth()
    if auth_check:
        return auth_check

    users = db.get_all_users()

    # Vulnerability #25: Returns plaintext passwords
    return jsonify({
        'success': True,
        'count': len(users),
        'users': users  # Includes plaintext passwords!
    })


@api_bp.route('/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    """
    Get user by ID via API
    Vulnerability #13: Missing authentication
    Vulnerability #25: Exposes password
    """
    auth_check = require_api_auth()
    if auth_check:
        return auth_check

    user = db.get_user_by_id(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Vulnerability #25: Returns plaintext password
    return jsonify({
        'success': True,
        'user': user
    })


@api_bp.route('/search', methods=['GET'])
def api_search():
    """
    Search API endpoint
    Vulnerability #1: SQL Injection in search parameter
    """
    auth_check = require_api_auth()
    if auth_check:
        return auth_check

    search_term = request.args.get('q', '')
    search_type = request.args.get('type', 'invoices')

    # Vulnerability #1: SQL Injection
    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        if search_type == 'invoices':
            query = f"SELECT * FROM invoices WHERE invoice_number LIKE '%{search_term}%' OR notes LIKE '%{search_term}%'"
            cursor.execute(query)
        elif search_type == 'users':
            query = f"SELECT * FROM users WHERE username LIKE '%{search_term}%' OR email LIKE '%{search_term}%'"
            cursor.execute(query)
        else:
            return jsonify({'error': 'Invalid search type'}), 400

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        conn.close()
        # Vulnerability #17: Verbose error
        return jsonify({'error': f'Search error: {str(e)}'}), 500


@api_bp.route('/stats', methods=['GET'])
def api_stats():
    """
    System statistics API
    Vulnerability #13: Missing authentication
    Vulnerability #23: Information disclosure
    """
    auth_check = require_api_auth()
    if auth_check:
        return auth_check

    conn = db.get_db_connection()
    cursor = conn.cursor()

    # Get various statistics
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM invoices")
    total_invoices = cursor.fetchone()['count']

    cursor.execute("SELECT SUM(total) as revenue FROM invoices WHERE status='paid'")
    total_revenue = cursor.fetchone()['revenue'] or 0

    conn.close()

    # Vulnerability #23: Exposes internal system information
    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'total_invoices': total_invoices,
            'total_revenue': total_revenue,
            'database_path': config.DATABASE_PATH,  # Sensitive info!
            'debug_mode': config.DEBUG
        }
    })


@api_bp.route('/health', methods=['GET'])
def api_health():
    """
    Health check endpoint
    Vulnerability #23: Information disclosure
    """
    import sys
    import platform

    # Vulnerability: Exposes too much system information
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'python_version': sys.version,
        'platform': platform.platform(),
        'database_path': config.DATABASE_PATH
    })
