"""
InvoiceFlow Configuration
Centralized configuration for the application
"""

import os

# Application Settings
APP_NAME = "InvoiceFlow"
APP_TAGLINE = "Streamline Your Billing"
SECRET_KEY = "dev-secret-key-12345"  # TODO: Change in production
DEBUG = True  # Vulnerability #12: Debug mode enabled in production

# Database Configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'invoice.db')

# Vulnerability #2: Hardcoded Admin Credentials
# TODO: Remove these temporary credentials before production deployment
DEFAULT_ADMIN_USER = 'admin'
DEFAULT_ADMIN_PASS = 'InvoiceFlow2024!Secure'

# Session Configuration
# Vulnerability #21: Weak session configuration
SESSION_COOKIE_SECURE = False  # Should be True in production
SESSION_COOKIE_HTTPONLY = False  # Should be True to prevent XSS cookie theft
SESSION_COOKIE_SAMESITE = None  # Should be 'Lax' or 'Strict'
PERMANENT_SESSION_LIFETIME = 86400  # 24 hours - too long

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}

# PDF Generation Configuration
WKHTMLTOPDF_PATH = '/usr/bin/wkhtmltopdf'  # Used for command injection vulnerability

# API Configuration
API_RATE_LIMIT_ENABLED = False  # Vulnerability #19: No rate limiting
API_REQUIRE_AUTH = False  # Vulnerability #13: Missing API authentication

# Server Configuration
HOST = '0.0.0.0'
PORT = 5000

# CORS Configuration
CORS_ENABLED = True
CORS_ORIGINS = '*'  # Vulnerability #20: CORS wildcard

# Logging
LOG_LEVEL = 'DEBUG'
VERBOSE_ERRORS = True  # Vulnerability #17: Verbose error messages
