document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    const alertContainer = 'alert-placeholder'

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // clear previous alert and validation
        UIUtils.clearValidation();
        document.getElementById(alertContainer).innerHTML = '';

        const formData = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            password: document.getElementById('password').value.trim()
        };

        // client side validation
        if (!validateForm(formData)) return;

        try {
            const response = await apiClient.post('/users/register', formData);
            const data = await apiClient.handleResponse(response);

            UIUtils.showAlert(
                alertContainer,
                'success',
                data.message || 'Registration successful'
            )
            UIUtils.redirectAfterDelay('/login')
        } catch (err) {
            if (err.message.includes('detail')) {
                try {
                    const errorData = = JSON.parse(err.message);
                    if (errorData.detail && typeof errorData.detail === 'object') {
                        UIUtils.handleServerValidation(errorData.detail);
                        return;
                    }
                } catch {}
            }

            UIUtils.showAlert(
                alertContainer,
                'danger',
                error.message || 'Registration failed'
            );
        }
    });

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
});