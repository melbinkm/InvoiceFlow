"""
Company model for InvoiceFlow
Represents client companies
"""

from datetime import datetime


class Company:
    """Company/Client model"""

    def __init__(self, id=None, user_id=None, company_name='', contact_person='',
                 email='', phone='', address='', city='', state='', zip_code='',
                 country='', created_at=None):
        self.id = id
        self.user_id = user_id
        self.company_name = company_name
        self.contact_person = contact_person
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country
        self.created_at = created_at or datetime.now()

    def get_full_address(self):
        """Get formatted full address"""
        parts = [self.address, self.city, self.state, self.zip_code, self.country]
        return ', '.join([p for p in parts if p])

    def to_dict(self):
        """Convert company to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @staticmethod
    def from_db_row(row):
        """Create Company instance from database row"""
        if not row:
            return None
        return Company(
            id=row['id'],
            user_id=row['user_id'],
            company_name=row['company_name'],
            contact_person=row.get('contact_person', ''),
            email=row.get('email', ''),
            phone=row.get('phone', ''),
            address=row.get('address', ''),
            city=row.get('city', ''),
            state=row.get('state', ''),
            zip_code=row.get('zip_code', ''),
            country=row.get('country', ''),
            created_at=row.get('created_at')
        )

    def __repr__(self):
        return f"<Company {self.company_name}>"
