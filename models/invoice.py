"""
Invoice model for InvoiceFlow
Represents customer invoices
"""

from datetime import datetime


class Invoice:
    """Invoice model - Vulnerability #22: Sequential predictable IDs"""

    def __init__(self, id=None, user_id=None, company_id=None, invoice_number=None,
                 invoice_date=None, due_date=None, status='draft', subtotal=0.0,
                 tax_rate=0.0, tax_amount=0.0, discount=0.0, total=0.0,
                 notes='', terms='', attachment_path=None, created_at=None, updated_at=None):
        self.id = id  # Sequential AUTO_INCREMENT (predictable)
        self.user_id = user_id
        self.company_id = company_id
        self.invoice_number = invoice_number
        self.invoice_date = invoice_date or datetime.now().date()
        self.due_date = due_date
        self.status = status
        self.subtotal = subtotal
        self.tax_rate = tax_rate
        self.tax_amount = tax_amount
        self.discount = discount
        self.total = total
        self.notes = notes  # Vulnerable to XSS
        self.terms = terms
        self.attachment_path = attachment_path
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def calculate_total(self):
        """Calculate invoice total"""
        self.tax_amount = self.subtotal * (self.tax_rate / 100.0)
        self.total = self.subtotal + self.tax_amount - self.discount
        return self.total

    def to_dict(self):
        """Convert invoice to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'invoice_number': self.invoice_number,
            'invoice_date': str(self.invoice_date) if self.invoice_date else None,
            'due_date': str(self.due_date) if self.due_date else None,
            'status': self.status,
            'subtotal': self.subtotal,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'discount': self.discount,
            'total': self.total,
            'notes': self.notes,
            'terms': self.terms,
            'attachment_path': self.attachment_path,
            'created_at': str(self.created_at) if self.created_at else None,
            'updated_at': str(self.updated_at) if self.updated_at else None
        }

    @staticmethod
    def from_db_row(row):
        """Create Invoice instance from database row"""
        if not row:
            return None
        return Invoice(
            id=row['id'],
            user_id=row['user_id'],
            company_id=row.get('company_id'),
            invoice_number=row['invoice_number'],
            invoice_date=row['invoice_date'],
            due_date=row.get('due_date'),
            status=row['status'],
            subtotal=row.get('subtotal', 0.0),
            tax_rate=row.get('tax_rate', 0.0),
            tax_amount=row.get('tax_amount', 0.0),
            discount=row.get('discount', 0.0),
            total=row.get('total', 0.0),
            notes=row.get('notes', ''),
            terms=row.get('terms', ''),
            attachment_path=row.get('attachment_path'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - ${self.total}>"


class InvoiceItem:
    """Invoice line item model"""

    def __init__(self, id=None, invoice_id=None, description='', quantity=1.0,
                 unit_price=0.0, amount=0.0, sort_order=0):
        self.id = id
        self.invoice_id = invoice_id
        self.description = description  # Vulnerable to XSS
        self.quantity = quantity
        self.unit_price = unit_price
        self.amount = amount
        self.sort_order = sort_order

    def calculate_amount(self):
        """Calculate line item amount"""
        self.amount = self.quantity * self.unit_price
        return self.amount

    def to_dict(self):
        """Convert item to dictionary"""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'amount': self.amount,
            'sort_order': self.sort_order
        }

    @staticmethod
    def from_db_row(row):
        """Create InvoiceItem instance from database row"""
        if not row:
            return None
        return InvoiceItem(
            id=row['id'],
            invoice_id=row['invoice_id'],
            description=row['description'],
            quantity=row['quantity'],
            unit_price=row['unit_price'],
            amount=row['amount'],
            sort_order=row.get('sort_order', 0)
        )

    def __repr__(self):
        return f"<InvoiceItem {self.description} - ${self.amount}>"
