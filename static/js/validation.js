/**
 * InvoiceFlow Client-Side Validation
 * Vulnerability #28: Client-side only validation (easily bypassed)
 */

// Password strength validation (client-side only - can be bypassed!)
document.addEventListener('DOMContentLoaded', function() {
    // Register form validation
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');

            // Vulnerability #28: Client-side only validation
            // Attacker can bypass by disabling JavaScript or modifying DOM
            if (password && password.value.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long!');
                return false;
            }

            if (confirmPassword && password.value !== confirmPassword.value) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
        });
    }

    // Invoice form validation (client-side only)
    const invoiceForms = document.querySelectorAll('form[action*="invoice"]');
    invoiceForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const quantities = form.querySelectorAll('input[name="quantity[]"]');
            const prices = form.querySelectorAll('input[name="unit_price[]"]');

            // Vulnerability #28: No server-side validation
            // Can submit negative values, strings, or arbitrary data via API/direct POST
            let hasError = false;

            quantities.forEach(qty => {
                if (parseFloat(qty.value) < 0) {
                    hasError = true;
                }
            });

            prices.forEach(price => {
                if (parseFloat(price.value) < 0) {
                    hasError = true;
                }
            });

            if (hasError) {
                e.preventDefault();
                alert('Quantities and prices cannot be negative!');
                return false;
            }
        });
    });

    // Email validation (client-side only)
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            // Vulnerability: Weak email validation, easily bypassed
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                this.setCustomValidity('Please enter a valid email address');
            } else {
                this.setCustomValidity('');
            }
        });
    });
});

// XSS Demonstration Function (intentionally vulnerable)
// Vulnerability #6: Shows how XSS can be executed
function executeUserContent(content) {
    // DANGEROUS: Never use innerHTML with user content in real applications!
    document.getElementById('user-content').innerHTML = content;
}

// Simulated CSRF Token (not actually validated on server)
// Vulnerability #7: CSRF tokens are generated but not validated
function generateCSRFToken() {
    // This looks secure but the server doesn't actually validate it
    return 'csrf_' + Math.random().toString(36).substring(2);
}

// Add CSRF token to forms (fake security)
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[method="POST"]');
    forms.forEach(form => {
        // Vulnerability #7: Token added but not validated server-side
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = generateCSRFToken();
        // Commented out - not actually adding it
        // form.appendChild(csrfInput);
    });
});

// Console warning for developers (informational)
console.log('%cInvoiceFlow Security Warning', 'color: red; font-size: 20px; font-weight: bold;');
console.log('%cThis is a deliberately vulnerable application for pentesting training.', 'color: orange; font-size: 14px;');
console.log('%cDO NOT use in production!', 'color: red; font-size: 14px; font-weight: bold;');
console.log('%cKnown vulnerabilities: SQLi, XSS, CSRF, IDOR, Command Injection, and more.', 'color: yellow; font-size: 12px;');
