document.addEventListener('DOMContentLoaded', async () => {
    const taskId = TASK_ID;

    class TaskDetail {
        constructor(taskId) {
            this.taskId = taskId;
            this.deleteBtn = document.getElementById('delete-button');
            this.editBtn = document.getElementById('edit-button');

            this.loadTask();
            this.setupEventListener();
        }

        async loadTask() {
            UIUtils.showLoading();

            try {
                const response = await apiClient.get(`/tasks/${this.taskId}`);
                const data = await apiClient.handleResponse(response);

                this.populateTaskDetails(data.data);
                this.setupActionButtons();
                UIUtils.showElement('task-container');
            } catch (error) {
                console.error('Failed to load task: ', error);
                this.showError(error.message || 'Failed to load task');
            } finally {
                UIUtils.hideLoading();
            }
        }

        populateTaskDetails(task) {
            const elements = {
                'task-title': task.title,
                'task-description': task.description || 'No description provided',
                'task-status': task.is_complete ? 'Complete' : 'Pending',
                'task-due-date': UIUtils.formatDateWithOrdinal(task.due_date),
                'task-created-at': task.created_at
            };

            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) element.textContent = value;
            });

            // set status color
            const statusElement = document.getElementById('task-status');
            if (statusElement) {
                statusElement.className = task.is_complete ? 'text-success' : 'text-warning';
            }
        }

        setupActionButtons() {
            if (this.editBtn) {
                this.editBtn.href = `/edit/${this.taskId}`;
            }
        }

        setupEventListener() {
            if (this.deleteBtn) {
                this.deleteBtn.addEventListener('click', () => this.handleDelete());
            }
        }

        async handleDelete() {
            if (!confirm('Are you sure you want to delete this task?')) return;

            UIUtils.showLoading();

            try {
                const response = await apiClient.delete(`/tasks/${this.taskId}`);
                await apiClient.handleResponse(response);
                UIUtils.showAlert(
                    alertContainer,
                    'success',
                    'Task delete operation successful'
                );
                window.location.href = '/'
            } catch (error) {
                console.error('Failed to delete task: ', error);
                this.showError(
                    error.message || 'Failed to delete task'
                );
            } finally {
                UIUtils.hideLoading();
            }
        }

        showError(message) {
            const errorBox = document.getElementById('error-message');
            if (errorBox) {
                errorBox.textContent = message;
                UIUtils.showElement(errorBox);
            } else {
                alert(message);
            }
        }
    }

    new TaskDetail(taskId);
});