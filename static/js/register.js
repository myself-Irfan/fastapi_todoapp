document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    const alertBox = document.getElementById('alert-placeholder')

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // clear previous alert and validation
        clearValidation();
        alertBox.innerHTML = '';

        const formData = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            password: document.getElementById('password').value.trim()
        };

        // client side validation
        if (!validateForm(formData)) return;

        try {
            const response = await fetch('/api/users/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                showAlert('success', data.message || 'Registration successful');
                setTimeout(() => window.location.href = '/login', 1500)
            } else {
                if (data.detail && typeof data.detail === 'object') {
                    handleServerValidation(data.detail);
                } else {
                    showAlert('danger', data.detail || data.message || 'Registration failed');
                }
            }
        } catch (err) {
            console.error('Registration error: ', err);
            showAlert('danger', 'Network error. Please try again.')
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

        // name validation
        if (!data.name) {
            showFieldError('name', 'Name is required');
            isValid = false;
        } else if (data.name.length < 3) {
            showFieldError('name', 'Name must be at least 3 characters long');
            isValid = false;
        }

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
        ['name', 'email', 'password'].forEach(fieldName => {
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