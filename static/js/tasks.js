document.addEventListener('DOMContentLoaded', () => {
    const taskTable = document.getElementById('task-table');
    const taskList = document.getElementById('task-list');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const emptyState = document.getElementById('empty-state');
    const loading = document.getElementById('loading');
    const searchInput = document.getElementById('search-input');
    const statusFilter = document.getElementById('status-filter');

    let allTasks = []; // store task for filter

    async function fetchTasks() {
        showLoading();

        try {
            const res = await fetch('/api/tasks/');
            if (!res.ok) throw new Error('Failed to fetch tasks');

            const data = await res.json();
            allTasks = data.data || [];

            hideAllFeedback();
            renderTasks(allTasks);
        } catch (err) {
            showError('Error loading tasks. Please try again later.');
            taskTable.classList.add('d-none');
            emptyState.classList.add('d-none');
            console.error(err)
        } finally {
            hideLoading();
        }
    }

    function renderTasks(tasks) {
        taskList.innerHTML = "";

        if (!tasks.length) {
            taskTable.classList.add('d-none');
            emptyState.classList.remove('d-none');
            return;
        }

        taskTable.classList.remove('d-none');
        emptyState.classList.add('d-none');

        tasks.forEach(task => {
            const row = document.createElement('tr');

            const titleTd = document.createElement('td')
            titleTd.textContent = task.title;
            row.appendChild(titleTd);

            const descTd = document.createElement('td');
            descTd.classList.add('d-none', 'd-md-table-cell');
            descTd.textContent = task.description || '-';
            row.appendChild(descTd);

            const statusTd = document.createElement('td');
            statusTd.textContent = task.is_complete ? 'Completed' : 'Pending';
            statusTd.className = task.is_complete ? 'text-success' : 'text-warning';
            row.appendChild(statusTd);

            const createTimeTd = document.createElement('td');
            createTimeTd.classList.add('d-none', 'd-md-table-cell');
            createTimeTd.textContent = task.created_at;
            row.appendChild(createTimeTd);

            const actionsTd = document.createElement('td');
            actionsTd.innerHTML = `
                <div class="d-flex gap-2">
                    <a href="/tasks/${task.id}" class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-eye"></i>
                    </a>
                    <a href="/tasks/${task.id}/edit" class="btn btn-sm btn-outline-warning">
                        <i class="bi bi-pencil"></i>
                    </a>
                    <button class="btn btn-sm btn-outline-danger btn-delete-task" data-id="${task.id}" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `;
            row.appendChild(actionsTd);
            taskList.appendChild(row);
        });

        attachDeleteHandlers();
    }

    function attachDeleteHandlers() {
        const deleteButtons = document.querySelectorAll('.btn-delete-task');
        deleteButtons.forEach(button => {
            button.addEventListener('click', async () => {
                const taskId = button.getAttribute('data-id');
                if (!taskId) return;

                const confirmed = confirm('Are you sure you wish to delete this task?');
                if (!confirmed) return;

                try {
                    const res = await fetch(`/api/tasks/${taskId}`, {
                        method: 'DELETE'
                    });

                    if (!res.ok) {
                        const data = await res.json();
                        throw new Error(data.detail || 'Failed to delete task');
                    }

                    allTasks = allTasks.filter(task => task.id != taskId);
                    applyFilters();
                } catch (err) {
                    console.error('Delete error:', err);
                    alert(err.message || 'Error deleting task');
                }
            });
        });
    }

    function applyFilters() {
        const searchText = searchInput.value.toLowerCase();
        const statusValue = statusFilter.value;

        const filtered = allTasks.filter(task => {
            const matchesText = task.title.toLowerCase().includes(searchText) || (task.description && task.description.toLowerCase().includes(searchText));
            const matchesStatus = statusValue === "" || (statusValue === 'pending' && !task.is_complete) || (statusValue === 'completed' && task.is_complete);
            return matchesText && matchesStatus;
        });
        renderTasks(filtered);
    }

    function showLoading() {
        loading.classList.remove('d-none');
    }

    function hideLoading() {
        loading.classList.add('d-none');
    }

    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('d-none');
    }

    function hideAllFeedback() {
        errorMessage.classList.add('d-none');
        errorText.textContent = '';
        emptyState.classList.add('d-none');
        taskTable.classList.remove('d-none');
    }

    // connect filters
    searchInput.addEventListener('input', applyFilters);
    statusFilter.addEventListener('change', applyFilters);

    // init call
    fetchTasks();
})