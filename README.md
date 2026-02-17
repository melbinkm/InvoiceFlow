# InvoiceFlow

> ⚠️ **WARNING: This is a deliberately vulnerable web application for educational and security testing purposes only. DO NOT deploy to production or expose to the internet.**

A vulnerable invoice management system built with Flask, designed to demonstrate common web security vulnerabilities for penetration testing practice and security awareness training.

## 🎯 Purpose

InvoiceFlow is an intentionally insecure web application that helps security professionals, students, and developers:
- Practice identifying and exploiting common web vulnerabilities
- Understand real-world attack scenarios
- Learn secure coding practices by seeing what NOT to do
- Test security tools and scanning techniques

## 🚨 Security Vulnerabilities Included

This application contains the following intentional vulnerabilities:

### SQL Injection (SQLi)
- **Login bypass**: Authentication can be bypassed using SQL injection
- **Data extraction**: User credentials and sensitive data can be extracted
- **Admin panel**: SQL console with direct database access
- **Search functionality**: Invoice search vulnerable to SQLi

### Server-Side Template Injection (SSTI)
- **Invoice templates**: Template rendering vulnerable to code injection
- **Custom fields**: User input directly embedded in templates
- **Remote code execution**: Possible through template injection

### Insecure Authentication
- **Weak password policies**: No password complexity requirements
- **Password reset flaws**: Predictable reset tokens
- **Session management**: Insecure session handling
- **No account lockout**: Unlimited login attempts allowed

### Broken Access Control
- **IDOR vulnerabilities**: Direct object reference in invoice IDs
- **Privilege escalation**: Regular users can access admin functions
- **Missing authorization**: Endpoints lack proper access control

### File Upload Vulnerabilities
- **Unrestricted file types**: No validation on uploaded files
- **Path traversal**: Potential directory traversal in uploads
- **Executable uploads**: Can upload and execute malicious files

### Information Disclosure
- **Verbose error messages**: Stack traces exposed to users
- **Debug mode**: Application runs with debug enabled
- **Sensitive data exposure**: Database backup files accessible
- **robots.txt**: Reveals hidden admin paths

### Other Vulnerabilities
- **XSS (Cross-Site Scripting)**: Multiple reflected and stored XSS points
- **CSRF**: No CSRF protection on forms
- **Hardcoded credentials**: Admin credentials in source code
- **Insecure deserialization**: Session data handling vulnerabilities

## 🛠️ Technology Stack

- **Framework**: Flask (Python)
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Jinja2 Templates
- **PDF Generation**: WeasyPrint
- **Authentication**: Flask sessions (insecure implementation)

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/melbinkm/InvoiceFlow.git
   cd InvoiceFlow
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python database.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

## 👤 Default Credentials

The application comes with pre-seeded user accounts:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| john.doe | password123 | Regular User |
| jane.smith | pass456 | Regular User |
| sarah.wilson | test789 | Regular User |

## 🎮 Features

- **User Management**: Registration, login, profile management
- **Invoice Creation**: Create, edit, and manage invoices
- **PDF Export**: Generate PDF versions of invoices
- **Company Management**: Manage company information
- **Admin Panel**: Administrative functions (SQL console, user management, logs)
- **Dashboard**: Overview of invoices and activities
- **Search & Filter**: Find invoices by various criteria

## 🔍 Testing Guide

### Quick Vulnerability Tests

1. **SQL Injection (Login)**
   ```
   Username: admin' OR '1'='1
   Password: anything
   ```

2. **SSTI (Invoice Description)**
   ```
   Description: {{7*7}}
   ```

3. **IDOR (Invoice Access)**
   ```
   URL: /invoice/view?id=<other_user_invoice_id>
   ```

4. **Admin Access**
   ```
   Navigate to: /admin/panel
   ```

## 📁 Project Structure

```
vulnerable_invoice_app/
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── database.py             # Database initialization
├── requirements.txt        # Python dependencies
├── models/                 # Data models
│   ├── user.py
│   ├── invoice.py
│   └── company.py
├── routes/                 # Route handlers
│   ├── auth.py            # Authentication routes
│   ├── invoice.py         # Invoice management
│   ├── admin.py           # Admin panel
│   └── api.py             # API endpoints
├── templates/             # Jinja2 templates
│   ├── auth/
│   ├── invoice/
│   ├── admin/
│   └── dashboard/
├── static/                # Static files (CSS, JS)
└── database/              # Database files and schemas
```

## ⚠️ Legal Disclaimer

**IMPORTANT**: This application is for **educational purposes only**.

- Only use this application in controlled, isolated environments
- Never deploy to production or public-facing servers
- Always obtain proper authorization before testing
- The authors are not responsible for any misuse
- Use at your own risk

## 🎓 Educational Use

This project is ideal for:
- Security training workshops
- CTF (Capture The Flag) competitions
- Penetration testing practice
- Web application security courses
- Security tool development and testing

## 🤝 Contributing

Contributions are welcome! If you'd like to add new vulnerabilities or improve existing ones:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-vulnerability`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📚 Learning Resources

To learn more about the vulnerabilities in this application:

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [HackTheBox](https://www.hackthebox.com/)
- [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)

## 📝 License

This project is provided as-is for educational purposes. Feel free to use, modify, and distribute for learning and training purposes.

## 🙏 Acknowledgments

Built for security education and awareness. Special thanks to the security community for sharing knowledge and best practices.

---

**Remember**: The best way to learn security is to understand both how attacks work and how to prevent them. Use this knowledge responsibly!
