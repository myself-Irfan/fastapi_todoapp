document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('create-form');
    const titleInput = document.getElementById('title');

    // set minimum date for due date input
    UIUtils.setMinDate('due_date');

    class TaskCreator {
        constructor() {
            this.setupEventListener();
        }

        setupEventListener() {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
            titleInput.addEventListener('blur', () => this.validateOnBlur());
            titleInput.addEventListener('input', () => this.clearMessageOnInput());
        }

        async handleSubmit(event) {
            event.preventDefault();

            this.hideAllMessages();

            if (!this.validateForm()) return;

            UIUtils.setLoadingState(
                'create-form',
                true,
                'Creating...'
            )

            const payload = this.getFormData();

            try {
                const response = await apiClient.post('/tasks', payload);
                await apiClient.handleResponse(response);

                UIUtils.showFeedback(
                    'feedback-message',
                    'feedback-icon',
                    'feedback-text',
                    'success',
                    'Task created successfully! Redirecting...'
                );

                form.reset();
                UIUtils.redirectAfterDelay('/');
            } catch (error) {
                console.error('Error creating task:', error);
                UIUtils.showFeedback(
                    'feedback-message',
                    'feedback-icon',
                    'feedback-text',
                    'danger',
                    error.message || 'Error creating task. Please try again.'
                );
            } finally {
                UIUtils.setLoadingState('create-form', false);
            }
        }

        getFormData() {
            return {
                title: document.getElementById('title').value.trim(),
                description: document.getElementById('description').value.trim() || null,
                due_date: document.getElementById('due_date').value || null,
                is_complete: document.getElementById('is_complete').checked
            };
        }

        validateForm() {
            const title = document.getElementById('title').value.trim();

            if (!title) {
                UIUtils.showFeedback(
                    'feedback-message',
                    'feedback-icon',
                    'feedback-text',
                    'danger',
                    'Title is required'
                );
                return false;
            }

            if (title.length < 3 || title.length > 200) {
                UIUtils.showFeedback(
                    'feedback-message',
                    'feedback-icon',
                    'feedback-text',
                    'danger',
                    'Title must be between 3 to 200 characters'
                );
                return false;
            }

            return true;
        }

        validateOnBlue() {
            if (titleInput.value.trim()) {
                this.validateForm();
            }
        }

        clearMessageOnInput() {
            const feedbackDiv = document.getElementById('feedback-message');
            if (!feedback.classList.contains('d-none')) {
                this.hideAllMessages();
            }
        }

        hideAllMessages() {
            UIUtils.hideFeedback(
                'feedback-message',
                'feedback-icon',
                'feedback-text'
            );
        }
    }

    new TaskCreator();
});
