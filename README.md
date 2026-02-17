# InvoiceFlow

> ⚠️ **EDUCATIONAL USE ONLY**: This application is designed for security testing and educational purposes. It contains security weaknesses and should NOT be deployed in production environments or used for actual business operations.

A modern invoice management system built with Flask to help businesses streamline their billing and invoicing processes.

## 🎯 About

InvoiceFlow is a web-based invoice management application that simplifies the process of creating, managing, and tracking invoices. Designed for small to medium-sized businesses, it provides an intuitive interface for handling all your invoicing needs.

## 🛠️ Technology Stack

- **Framework**: Flask (Python)
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Jinja2 Templates
- **PDF Generation**: WeasyPrint
- **Authentication**: Flask sessions

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

## 🎮 Features

- **User Management**: Registration, login, and profile management
- **Invoice Creation**: Create, edit, and manage invoices with ease
- **PDF Export**: Generate professional PDF versions of invoices
- **Company Management**: Manage your company information and branding
- **Admin Panel**: Administrative functions for user management and system logs
- **Dashboard**: Overview of invoices and recent activities
- **Search & Filter**: Find invoices quickly by various criteria

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

## 🤝 Contributing

Contributions are welcome! If you'd like to improve InvoiceFlow:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## ⚠️ Disclaimer

**This application is intended for educational and security testing purposes only.**

- This software contains intentional security weaknesses for training purposes
- Do NOT use this application to handle real business data
- Do NOT deploy this application on public-facing servers or production environments
- Only use in isolated, controlled environments (local machines, private test networks)
- The authors assume no liability for misuse or damages resulting from deployment

**Use responsibly and only in authorized testing scenarios.**

## 📝 License

This project is provided as-is for business and educational purposes. Feel free to use, modify, and distribute.

## 🙏 Acknowledgments

Built to help businesses manage their invoicing efficiently. Thank you to all contributors and users of InvoiceFlow.

---

**InvoiceFlow** - Streamline your billing process today!
