"""
User model for InvoiceFlow
Represents system users with authentication
"""

from datetime import datetime


class User:
    """User model"""

    def __init__(self, id=None, username=None, email=None, password=None,
                 full_name=None, role='user', created_at=None, last_login=None,
                 is_active=1):
        self.id = id
        self.username = username
        self.email = email
        self.password = password  # Vulnerability #8: Plaintext password
        self.full_name = full_name
        self.role = role
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
        self.is_active = is_active

    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'

    def to_dict(self):
        """Convert user to dictionary (excluding password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'created_at': str(self.created_at) if self.created_at else None,
            'last_login': str(self.last_login) if self.last_login else None,
            'is_active': self.is_active
        }

    def to_dict_with_password(self):
        """
        Convert user to dictionary including password
        Vulnerability #25: Password exposure in API responses
        """
        data = self.to_dict()
        data['password'] = self.password  # Dangerous!
        return data

    @staticmethod
    def from_db_row(row):
        """Create User instance from database row"""
        if not row:
            return None
        return User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            password=row['password'],
            full_name=row['full_name'],
            role=row['role'],
            created_at=row['created_at'],
            last_login=row['last_login'],
            is_active=row['is_active']
        )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
