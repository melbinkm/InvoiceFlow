"""
Invoice management routes for InvoiceFlow
Contains IDOR, XSS, Command Injection, Path Traversal, and other vulnerabilities
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, send_file, jsonify, flash
import os
import database as db
import config
from datetime import datetime, timedelta

invoice_bp = Blueprint('invoice', __name__)


def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session


def require_login():
    """Check login and redirect if not authenticated"""
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    return None


@invoice_bp.route('/list')
def list_invoices():
    """List all invoices for current user"""
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    user_id = session['user_id']

    # Vulnerability #16: Reflected XSS in search
    search_term = request.args.get('search', '')

    if search_term:
        # Vulnerability: SQL Injection in search
        invoices = db.search_invoices(user_id, search_term)
    else:
        invoices = db.get_invoices_by_user(user_id)

    # Vulnerability #16: search_term not escaped in template
    return render_template('invoice/list.html', invoices=invoices, search_term=search_term)


@invoice_bp.route('/view', methods=['GET', 'POST'])
def view_invoice():
    """
    View invoice details
    Vulnerability #4: IDOR via POST parameter - No ownership verification
    """
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    # GET request - redirect to form or handle initial request
    if request.method == 'GET':
        invoice_id = request.args.get('id')
        if not invoice_id:
            return redirect(url_for('invoice.list_invoices'))
        # Auto-submit form to convert GET to POST
        return render_template('invoice/view_redirect.html', invoice_id=invoice_id)

    # POST request - process invoice viewing
    # Vulnerability #4: IDOR - invoice_id from POST body, no ownership check
    invoice_id = request.form.get('invoice_id')

    if not invoice_id:
        return "Invoice ID required", 400

    try:
        invoice_id = int(invoice_id)
    except ValueError:
        return "Invalid invoice ID", 400

    invoice = db.get_invoice(invoice_id)

    if not invoice:
        return "Invoice not found", 404

    items = db.get_invoice_items(invoice_id)
    company = None
    if invoice.get('company_id'):
        company = db.get_company(invoice['company_id'])

    # Vulnerability #6: Stored XSS in invoice.notes rendered without escaping
    return render_template('invoice/view.html',
                          invoice=invoice,
                          items=items,
                          company=company)


@invoice_bp.route('/create', methods=['GET', 'POST'])
def create_invoice():
    """
    Create new invoice
    Vulnerability #3: No input validation on amount/numbers
    """
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    user_id = session['user_id']

    if request.method == 'POST':
        # Get form data
        company_id = request.form.get('company_id')
        invoice_date = request.form.get('invoice_date', datetime.now().strftime('%Y-%m-%d'))
        due_date = request.form.get('due_date')
        notes = request.form.get('notes', '')  # XSS payload can be stored here
        terms = request.form.get('terms', '')

        # Vulnerability #3: No input validation on numeric fields
        # Can submit negative values, non-numeric strings, etc.
        try:
            tax_rate = float(request.form.get('tax_rate', 0))
            discount = float(request.form.get('discount', 0))
        except:
            tax_rate = 0
            discount = 0

        # Get line items from form
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')

        # Calculate totals (vulnerability: no validation)
        subtotal = 0
        for i in range(len(descriptions)):
            try:
                qty = float(quantities[i])
                price = float(unit_prices[i])
                subtotal += qty * price
            except:
                pass

        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount - discount

        # Generate invoice number (predictable pattern)
        invoice_number = f"INV-{datetime.now().year}-{db.get_db_connection().execute('SELECT COUNT(*) + 1 FROM invoices').fetchone()[0]:03d}"

        # Create invoice
        invoice_id = db.create_invoice(
            user_id, company_id, invoice_number, invoice_date, due_date,
            'draft', subtotal, tax_rate, tax_amount, discount, total, notes, terms
        )

        # Add line items
        for i, desc in enumerate(descriptions):
            if desc.strip():
                try:
                    qty = float(quantities[i])
                    price = float(unit_prices[i])
                    amount = qty * price
                    db.add_invoice_item(invoice_id, desc, qty, price, amount, i)
                except:
                    pass

        db.log_activity(user_id, 'create', 'invoice', invoice_id,
                       request.remote_addr, f'Created invoice {invoice_number}')

        return redirect(url_for('invoice.view_invoice', invoice_id=invoice_id))

    # GET request - show form
    companies = db.get_companies_by_user(user_id)
    return render_template('invoice/create.html', companies=companies)


@invoice_bp.route('/edit/<int:invoice_id>', methods=['GET', 'POST'])
def edit_invoice(invoice_id):
    """
    Edit invoice
    Vulnerability #4: IDOR - can edit any invoice
    Vulnerability #28: Client-side only validation
    """
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    user_id = session['user_id']

    # Vulnerability #4: IDOR - no ownership check
    invoice = db.get_invoice(invoice_id)
    if not invoice:
        return "Invoice not found", 404

    if request.method == 'POST':
        # Update invoice
        company_id = request.form.get('company_id')
        invoice_date = request.form.get('invoice_date')
        due_date = request.form.get('due_date')
        status = request.form.get('status', 'draft')
        notes = request.form.get('notes', '')
        terms = request.form.get('terms', '')

        # No validation on numeric fields
        try:
            tax_rate = float(request.form.get('tax_rate', 0))
            discount = float(request.form.get('discount', 0))
        except:
            tax_rate = 0
            discount = 0

        # Update line items
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')

        # Calculate new totals
        subtotal = 0
        for i in range(len(descriptions)):
            try:
                qty = float(quantities[i])
                price = float(unit_prices[i])
                subtotal += qty * price
            except:
                pass

        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount - discount

        # Update invoice
        db.update_invoice(invoice_id,
                         company_id=company_id,
                         invoice_date=invoice_date,
                         due_date=due_date,
                         status=status,
                         subtotal=subtotal,
                         tax_rate=tax_rate,
                         tax_amount=tax_amount,
                         discount=discount,
                         total=total,
                         notes=notes,
                         terms=terms)

        # Delete old items and add new ones
        db.delete_invoice_items(invoice_id)
        for i, desc in enumerate(descriptions):
            if desc.strip():
                try:
                    qty = float(quantities[i])
                    price = float(unit_prices[i])
                    amount = qty * price
                    db.add_invoice_item(invoice_id, desc, qty, price, amount, i)
                except:
                    pass

        db.log_activity(user_id, 'update', 'invoice', invoice_id,
                       request.remote_addr, f'Updated invoice {invoice["invoice_number"]}')

        return redirect(url_for('invoice.view_invoice', invoice_id=invoice_id))

    # GET request
    items = db.get_invoice_items(invoice_id)
    companies = db.get_companies_by_user(user_id)
    return render_template('invoice/edit.html',
                          invoice=invoice,
                          items=items,
                          companies=companies)


@invoice_bp.route('/delete/<int:invoice_id>', methods=['POST'])
def delete_invoice(invoice_id):
    """
    Delete invoice
    Vulnerability #4: IDOR - can delete any invoice
    Vulnerability #7: No CSRF protection
    """
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    # Vulnerability #4: IDOR - no ownership check
    # Vulnerability #7: No CSRF token validation

    invoice = db.get_invoice(invoice_id)
    if invoice:
        db.delete_invoice(invoice_id)
        db.log_activity(session['user_id'], 'delete', 'invoice', invoice_id,
                       request.remote_addr, f'Deleted invoice {invoice["invoice_number"]}')

    return redirect(url_for('invoice.list_invoices'))


@invoice_bp.route('/generate-pdf/<int:invoice_id>')
def generate_pdf(invoice_id):
    """
    Generate PDF for invoice
    Vulnerability #5: Command Injection via filename parameter (ADMIN ONLY)
    Vulnerability #14: Requires privilege escalation to exploit
    """
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    # Check if user is admin
    if session.get('role') != 'admin':
        flash('PDF generation is only available for administrator accounts. Please contact support.', 'warning')
        return redirect(url_for('invoice.list_invoices')), 403

    # Vulnerability #4: IDOR - no ownership check (but requires admin)
    invoice = db.get_invoice(invoice_id)
    if not invoice:
        return "Invoice not found", 404

    items = db.get_invoice_items(invoice_id)
    company = db.get_company(invoice['company_id']) if invoice.get('company_id') else None

    # Vulnerability #5: Command Injection via filename parameter
    filename = request.args.get('filename', f"invoice_{invoice_id}")

    # Generate HTML content
    html_content = render_template('invoice/pdf_template.html',
                                   invoice=invoice,
                                   items=items,
                                   company=company)

    # Write HTML to temp file
    html_path = os.path.join(config.UPLOAD_FOLDER, f'temp_{invoice_id}.html')
    with open(html_path, 'w') as f:
        f.write(html_content)

    # Vulnerability #5: Command Injection - unsanitized filename in shell command
    pdf_path = os.path.join(config.UPLOAD_FOLDER, f'{filename}.pdf')

    # Using os.system instead of subprocess (dangerous!)
    command = f'{config.WKHTMLTOPDF_PATH} {html_path} {pdf_path}'
    os.system(command)

    # Clean up temp HTML
    try:
        os.remove(html_path)
    except:
        pass

    if os.path.exists(pdf_path):
        db.log_activity(session['user_id'], 'generate_pdf', 'invoice', invoice_id,
                       request.remote_addr, f'Generated PDF for invoice {invoice["invoice_number"]}')
        return send_file(pdf_path, as_attachment=True, download_name=f'{filename}.pdf')

    return "PDF generation failed", 500


@invoice_bp.route('/upload-attachment/<int:invoice_id>', methods=['POST'])
def upload_attachment(invoice_id):
    """
    Upload attachment for invoice
    Vulnerability #10: Path Traversal via filename
    """
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    # Vulnerability #4: IDOR
    invoice = db.get_invoice(invoice_id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Vulnerability #10: Path Traversal - no sanitization of filename
    # User can upload files like "../../etc/passwd" or "../../../app.py"
    filename = file.filename
    filepath = os.path.join(config.UPLOAD_FOLDER, filename)

    # Save file without validation
    file.save(filepath)

    # Update invoice with attachment path
    db.update_invoice(invoice_id, attachment_path=filename)

    db.log_activity(session['user_id'], 'upload', 'invoice', invoice_id,
                   request.remote_addr, f'Uploaded attachment {filename}')

    return jsonify({'success': True, 'filename': filename})


@invoice_bp.route('/download-attachment/<int:invoice_id>')
def download_attachment(invoice_id):
    """
    Download invoice attachment
    Vulnerability #10: Path Traversal in file download
    """
    redirect_check = require_login()
    if redirect_check:
        return redirect_check

    # Vulnerability #4: IDOR
    invoice = db.get_invoice(invoice_id)
    if not invoice or not invoice.get('attachment_path'):
        return "Attachment not found", 404

    # Vulnerability #10: Path Traversal
    # If attachment_path is "../../../etc/passwd", this would serve it
    filepath = os.path.join(config.UPLOAD_FOLDER, invoice['attachment_path'])

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)

    return "File not found", 404
