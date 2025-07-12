document.addEventListener('DOMContentLoaded', () => {
    const dueDateInput = document.getElementById('due_date');
    const today = new Date().toISOString().split('T')[0];
    dueDateInput.min = today;

    const form = document.getElementById('create-form');
    const submitButton = form.querySelector('button[type=submit]');
    const originalButtonText = submitButton.textContent;
    const feedbackDiv = document.getElementById('feedback-message');
    const feedbackIcon = document.getElementById('feedback-icon');
    const feedbackText = document.getElementById('feedback-text');

    function showLoading() {
        submitButton.disabled = true;
        submitButton.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Creating...
        `;
    }

    function hideLoading() {
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }

    function showFeedback(type, message) {
        feedbackDiv.classList.remove('alert-danger', 'alert-success', 'd-none');
        feedbackIcon.className = 'me-2'; // reset icon classes

        if (type === 'success') {
            feedbackDiv.classList.add('alert-success');
            feedbackIcon.classList.add('bi', 'bi-check-circle-fill');
        } else if (type === 'error') {
            feedbackDiv.classList.add('alert-danger');
            feedbackIcon.classList.add('bi', 'bi-exclamation-triangle-fill');
        }

        feedbackText.textContent = message;
    }

    function hideAllMessages() {
        feedbackDiv.classList.add('d-none');
        feedbackIcon.className = '';
        feedbackText.textContent = '';
    }

    function validateForm() {
        const title = document.getElementById('title').value.trim();

        if (!title) {
            showFeedback('error', 'Title is required.');
            return false;
        }

        if (title.length < 3) {
            showFeedback('error', 'Title must be at least 3 characters long.');
            return false;
        }

        if (title.length > 200) {
            showFeedback('error', 'Title must be less than 200 characters.');
            return false;
        }

        return true;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        hideAllMessages();

        if (!validateForm()) {
            return;
        }

        showLoading();

        const title = document.getElementById('title').value.trim();
        const description = document.getElementById('description').value.trim();
        const due_date = document.getElementById('due_date').value;
        const is_complete = document.getElementById('is_complete').checked;

        const payload = {
            title,
            description: description || null,
            due_date: due_date || null,
            is_complete
        };

        try {
            const res = await fetch('/api/tasks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                let errorMessage = 'Failed to create task';
                try {
                    const errorData = await res.json();
                    errorMessage = errorData.message || errorData.error || errorMessage;
                } catch {
                    switch (res.status) {
                        case 400:
                            errorMessage = 'Invalid task data provided';
                            break;
                        case 401:
                            errorMessage = 'Unauthorized. Please log in again.';
                            break;
                        case 403:
                            errorMessage = 'You do not have permission to create tasks';
                            break;
                        case 422:
                            errorMessage = 'Task data validation failed';
                            break;
                        case 500:
                            errorMessage = 'Server error. Please try again later.';
                            break;
                        default:
                            errorMessage = `Error ${res.status}: ${res.statusText}`;
                    }
                }
                throw new Error(errorMessage);
            }

            showFeedback('success', 'Task created successfully! Redirecting...');
            form.reset();

            setTimeout(() => {
                window.location.href = '/';
            }, 1500);

        } catch (err) {
            console.error('Error creating task:', err);
            showFeedback('error', err.message || 'Error creating task. Please try again.');
        } finally {
            hideLoading();
        }
    });

    const titleInput = document.getElementById('title');
    titleInput.addEventListener('blur', () => {
        if (titleInput.value.trim()) {
            validateForm();
        }
    });

    titleInput.addEventListener('input', () => {
        if (!feedbackDiv.classList.contains('d-none')) {
            hideAllMessages();
        }
    });
});
