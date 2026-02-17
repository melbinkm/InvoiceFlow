/**
 * InvoiceFlow Client-Side Validation
 */

// Password strength validation
document.addEventListener('DOMContentLoaded', function() {
    // Register form validation
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');

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

    // Invoice form validation
    const invoiceForms = document.querySelectorAll('form[action*="invoice"]');
    invoiceForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const quantities = form.querySelectorAll('input[name="quantity[]"]');
            const prices = form.querySelectorAll('input[name="unit_price[]"]');

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

    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                this.setCustomValidity('Please enter a valid email address');
            } else {
                this.setCustomValidity('');
            }
        });
    });
});

// User content display
function executeUserContent(content) {
    document.getElementById('user-content').innerHTML = content;
}

// CSRF Token generation
function generateCSRFToken() {
    return 'csrf_' + Math.random().toString(36).substring(2);
}

// Add CSRF token to forms
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[method="POST"]');
    forms.forEach(form => {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = generateCSRFToken();
        // Commented out - not actually adding it
        // form.appendChild(csrfInput);
    });
});
