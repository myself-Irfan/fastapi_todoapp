document.addEventListener('DOMContentLoaded', async () => {
    const loading = document.getElementById('loading');
    const container = document.getElementById('task-container');
    const errorBox = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const editBtn = document.getElementById('edit-button');
    const deleteBtn = document.getElementById('delete-button');

    const taskId = TASK_ID;

    try {
        const res = await fetch(`/api/tasks/${taskId}`);
        if (!res.ok) throw new Error('Failed to fetch task (${res.status}');

        const data = await res.json();
        const task = data.data;

        document.getElementById('task-title').textContent = task.title;
        document.getElementById('task-description').textContent = task.description;
        document.getElementById('task-status').textContent = task.is_complete ? 'Completed' : 'Pending';
        document.getElementById('task-status').className = task.is_complete ? 'text-success' : 'text-warning';
        document.getElementById('task-due-date').textContent = task.due_date || 'N/A';
        document.getElementById('task-created-at').textContent = task.created_at;

        editBtn.href = `/edit/${taskId}`;

        deleteBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to delete this task?')) return;;

            try {
                deleteBtn.disabled = true;
                deleteBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Deleting...`;

                const deleteRes = await fetch(`/api/tasks/${taskId}`, {
                    method: 'DELETE'
                });

                if (!deleteRes.ok) {
                    const errData = await deleteRes.json();
                    throw new Error(errData.detail || 'Failed to delete task');
                }

                window.location.href = '/';
            } catch (err) {
                console.error(err)
                deleteBtn.disabled = false;
                deleteBtn.innerHTML = `<i class="bi bi-trash me-1"></i> Delete`;
                alert(err.message);
            }
        });

        container.classList.remove('d-none');

    } catch (err) {
        console.error(err);
        errorText.textContent = err.message || 'Failed to load task';
        errorBox.classList.remove('d-none');
    } finally {
        loading.classList.add('d-none');
    }
});