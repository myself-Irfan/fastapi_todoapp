document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const alertBox = document.getElementById('alert-placeholder');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // clear previous alert and validation
        clearValidation();
        alertBox.innerHTML = '';

        const formData = {
            email: document.getElementById('email').value.trim(),
            password: document.getElementById('password').value.trim()
        };

        // client side validation
        if (!validateForm(formData)) return;

        try {
            const response = await fetch('/api/users/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

             if (!response.ok) {
                if (data.detail && Array.isArray(data.detail)) {
                    handleServerValidation(data.detail);
                } else {
                    showAlert('danger', data.detail || 'Login failed');
                }
            } else {
                const tokens = data.data || {};

                localStorage.setItem('access_token', tokens.access_token);
                localStorage.setItem('refresh_token', tokens.refresh_token);

                showAlert('success', 'Login successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            }
        } catch (err) {
            console.error('Login error:', err);
            showAlert('danger', 'Something went wrong. Please try again later.');
        }
    });

    function showFieldError(fieldName, message) {
        const field = document.getElementById(fieldName);
        const feedback = field.nextElementSibling;

        field.classList.add('is-invalid');
        feedback.textContent = message;
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function validateForm(data) {
        let isValid = true;

        // email validation
        if (!data.email) {
            showFieldError('email', 'Email is required');
            isValid = false;
        } else if (!isValidEmail(data.email)) {
            showFieldError('email', 'Please enter a valid email');
            isValid = false;
        }

        // password validation
        if (!data.password) {
            showFieldError('password', 'Password is required');
            isValid = false;
        } else if (data.password.length < 5) {
            showFieldError('password', 'Password must be at least 5 characters long');
            isValid = false
        }

        return isValid;
    }

    function clearValidation() {
        ['email', 'password'].forEach(fieldName => {
            const field = document.getElementById(fieldName);
            const feedback = field.nextElementSibling;

            field.classList.remove('is-invalid');
            feedback.textContent = '';
        });
    }

    function handleServerValidation(errors) {
        if (Array.isArray(errors)) {
            errors.forEach(error => {
                const field = error.loc[1];
                if (document.getElementById(field)) {
                    showFieldError(field, error.msg);
                }
            });
        } else {
            Object.keys(errors).forEach(field => {
                if (document.getElementById(field)) {
                    showFieldError(field, errors[field]);
                }
            });
        }
    }

    function showAlert(type, message) {
        alertBox.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }
})