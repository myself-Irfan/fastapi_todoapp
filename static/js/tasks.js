document.addEventListener('DOMContentLoaded', () => {
    const taskTable = document.getElementById('task-table');
    const taskList = document.getElementById('task-list');
    const searchInput = document.getElementById('search-input');
    const statusFilter = document.getElementById('status-filter');

    let allTasks = []; // store task for filter

    class TaskManager {
        async fetchTasks() {
            UIUtils.showLoading();

            try {
                const response = await apiClient.get('/tasks');
                const data = await apiClient.handleResponse(response);

                allTasks = data.data || [];
                this.hideAllFeedback();
                this.renderTasks(allTasks);
            } catch (err) {
                this.showError('Error loading tasks. Please try again later.');
                UIUtils.hideElement('task-table');
                UIUtils.hideElement('empty-state');
                console.error('Fetch tasks error: ', err);
            } finally {
                UIUtils.hideLoading();
            }
        }

        renderTasks(tasks) {
            taskList.innerHTML = "";

            if (!tasks.length) {
                taskTable.classList.add('d-none');

                const emptyState = document.getElementById('empty-state');
                if (emptyState) {
                    emptyState.classList.remove('d-none');
                }
                return;
            }

            UIUtils.showElement('task-table');
            UIUtils.hideElement('empty-state');

            tasks.forEach(task => {
                const row = this.createTaskRow(task);
                taskList.appendChild(row);
            });

            this.attachDeleteHandlers();
        }

        createTaskRow(task) {
            const row = document.createElement('tr');

            // title col
            const titleTd = document.createElement('td');
            titleTd.textContent = task.title;
            row.appendChild(titleTd);

            // description
            const descTd = document.createElement('td');
            descTd.classList.add('d-none', 'd-md-table-cell');
            descTd.textContent = task.description || '-';
            row.appendChild(descTd);

            // status
            const statusTd = document.createElement('td');
            statusTd.textContent = task.is_complete ? 'Completed' : 'Pending';
            statusTd.className = task.is_complete ? 'text-success' : 'text-warning';
            row.appendChild(statusTd);

            // due date
            const dueDateTd = document.createElement('td');
            dueDateTd.classList.add('d-none', 'd-md-table-cell');
            dueDateTd.textContent = UIUtils.formatDateWithOrdinal(task.due_date);
            row.appendChild(dueDateTd);

            // created at
            const createTimeTd = document.createElement('td');
            createTimeTd.classList.add('d-none', 'd-md-table-cell');
            createTimeTd.textContent = task.created_at;
            row.appendChild(createTimeTd);

            // action col
            const actionsTd = document.createElement('td');
            actionsTd.innerHTML = this.getActionButtons(task.id);
            row.appendChild(actionsTd);

            return row;
        }

        getActionButtons(taskId) {
            return `
                <div class="d-flex gap-2">
                    <a href="/${taskId}" class="btn btn-sm btn-outline-primary" title="View">
                        <i class="bi bi-eye"></i>
                    </a>
                    <a href="/edit/${taskId}" class="btn btn-sm btn-outline-warning" title="Edit">
                        <i class="bi bi-pencil"></i>
                    </a>
                    <button class="btn btn-sm btn-outline-danger btn-delete-task"
                            data-id="${taskId}" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `;
        }

        attachDeleteHandlers() {
            const deleteButtons = document.querySelectorAll('.btn-delete-task');
            deleteButtons.forEach(button => {
                button.addEventListener('click', async () => {
                    const taskId = button.getAttribute('data-id');
                    if (!taskId) return;

                    const confirmed = await UIUtils.confirmAction('Are you sure you wish to delete this task?');
                    if (!confirmed) return;

                    await this.deleteTask(taskId, button);
                });
            });
        }

        async deleteTask(taskId, button) {
            const originalHTML = button.innerHTML;

            try {
                button.disabled = true;
                button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';

                const response = await apiClient.delete(`/tasks/${taskId}`);
                await apiClient.handleResponse(response);

                allTasks = allTasks.filter( task => task.id != taskId)
                this.applyFilters();
            } catch (error) {
                console.error('Delete error:', error);
                alert(error.message || 'Error deleting task');

                button.disabled = false;
                button.innerHTML = originalHTML;
            }
        }

        applyFilters() {
            const searchText = searchInput.value.toLowerCase();
            const statusValue = statusFilter.value;

            const filtered = allTasks.filter(task => {
                const matchesText = task.title.toLowerCase().includes(searchText) || (task.description && task.description.toLowerCase().includes(searchText));
                const matchesStatus = statusValue === "" || (statusValue === 'pending' && !task.is_complete) || (statusValue === 'completed' && task.is_complete);
                return matchesText && matchesStatus;
            });
            this.renderTasks(filtered);
        }

        showError(message) {
            const errorText = document.getElementById('error-text');
            const errorMessage = document.getElementById('error-message');

            if (errorText) errorText.textContent = message;
            if (errorMessage) errorMessage.classList.remove('d-none');
        }

        hideAllFeedback() {
            UIUtils.hideElement('error-message');
            const errorText = document.getElementById('error-text');

            if (errorText) errorText.textContent = '';

            UIUtils.hideElement('empty-state');
            UIUtils.showElement('task-state');
        }
    }

    // init task manager
    const taskManager = new TaskManager();

    // set up event listeners
    searchInput.addEventListener('input', () => taskManager.applyFilters());
    statusFilter.addEventListener('change', () => taskManager.applyFilters())

    taskManager.fetchTasks();
});