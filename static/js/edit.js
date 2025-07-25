document.addEventListener('DOMContentLoaded', ()=> {
    const form = document.getElementById('edit-form');
    const submitButton = form.querySelector('button[type=submit]');
    const originalButtonText = submitButton.textContent;

    const feedback = document.getElementById('feedback-message');
    const feedbackText = document.getElementById('feedback-text');
    const feedbackIcon = document.getElementById('feedback-icon');

    const taskId = TASK_ID;

    document.getElementById('due_date').min = new Date().toISOString().split('T')[0];

    async function fetchTask() {
        try {
            const res = await apiClient.get(`/tasks/${taskId}`);
            const data = await apiClient.handleResponse(res);
            populateForm(data.data);
        } catch (err) {
            showFeedback('danger', 'Error loading task. Please try again');
            console.error(err);
        }
    }
//    populate the form
    function populateForm(task) {
        document.getElementById('title').value = task.title || '';
        document.getElementById('description').value = task.description || '';
        document.getElementById('due_date').value = task.due_date || '';
        document.getElementById('is_complete').checked = task.is_complete;
    }

    function showLoading() {
        submitButton.disabled = true;
        submitButton.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Updating...
        `;
    }

    function hideLoading() {
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }

    function showFeedback(type, message) {
        feedback.className = `alert alert-${type} mt-3`;
        feedback.classList.remove('d-none');
        feedbackText.textContent = message;
        feedbackIcon.className = type === 'success' ? 'bi bi-check-circle-fill me-2' : 'bi bi-exclamation-triangle-fill me-2';
    }

    function validateForm() {
        const title = document.getElementById('title').value.trim();

        if (!title) {
            showFeedback('danger', 'Title is required.');
            return false;
        }

        if (title.length < 3 || title.length > 200) {
            showFeedback('warning', 'Title must be between 3 and 200 characters');
            return false;
        }

        return true;
    }

    form.addEventListener('submit', async(e) => {
        e.preventDefault();
        feedback.classList.add('d-none');

        if (!validateForm()) return;

        showLoading();

        const payload = {
            title: document.getElementById('title').value.trim(),
            description: document.getElementById('description').value.trim() || null,
            due_date: document.getElementById('due_date').value.trim() || null,
            is_complete: document.getElementById('is_complete').checked
        };

        try {
            const res = await apiClient.put(`/tasks/${taskId}`, payload);
            const data = await apiClient.handleResponse(res);

            showFeedback('success', 'Task updated successfully.');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } catch (err) {
            showFeedback('danger', err.message);
            console.error(err);
        } finally {
            hideLoading();
        }
    });

    fetchTask();
})