class UIUtils {
    static showFieldError(fieldName, message) {
        const field = document.getElementById(fieldName);
        const feedback = field?.nextElementSibling;

        if (field && feedback) {
            field.classList.add('is-invalid');
            feedback.textContent = message;
        }
    }

    static clearValidation(fieldNames) {
        fieldNames.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            const feedback = field?.nextElementSibling;

            if (field && feedback) {
                field.classList.remove('is-invalid')
                feedback.textContent = '';
            }
        });
    }

    static isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    static showAlert(containerId, type, message) {
        const container = document.getElementById(containerId);

        if (!container) return;

        container.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }

    static showFeedback(feedbackId, iconId, textId, type, message) {
        const feedback = document.getElementById(feedbackId);
        const icon = document.getElementById(iconId);
        const text = document.getElementById(textId);

        if (!feedback || !text ) return;

        feedback.className = `alert alert-${type} mt-3`;
        feedback.className.remove('d-none');
        text.textContent = message;

        if (icon) {
            icon.className = type === 'success' ? 'bi bi-check-circle-fill me-2' : 'bi bi-exclamation-triangle-fill-md-2';
        }
    }

    static hideFeedback(feedbackId, iconId, textId) {
        const feedback = document.getElementById(feedbackId);
        const icon = document.getElementById(iconId);
        const text = document.getElementById(textId);

        if (feedback) feedback.className.add('d-none');
        if (icon) icon.className = '';
        if (text) text.textContent = ''
    }

    static setLoadingState(buttonId, isLoading, loadingText = 'Loading...') {
        const button = document.getElementById(buttonId)
        if (!button) return;

        if (!button._originalText) {
            button._originalText = button.textContent
        }

        button.disabled = isLoading;

        if (isLoading) {
            button.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                ${loadingText}
            `;
        } else {
            button.innerHTML = button._originalText;
        }
    }

    static showLoading(loadingId = 'loading') {
        const loading = document.getElementById(loadingId);
        if (loading) loading.classList.remove('d-none');
    }

    static hideLoading(loadingId = 'loading') {
        const loading = document.getElementById(loadingId);
        if (loading) loading.classList.add('d-none');
    }

    // date util
    static formatDateWithOrdinal(dateStr) {
        const dateObj = new Date(dateStr);
        if (isNaN(dateObj)) return '-';

        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        let formatted = dateObj.toLocaleDateString('en-us', options)

        const day = dateObj.getDate();
        const suffix = (n) => {
            if (n >= 11 & n <= 13) return 'th';
            switch(n%10) {
                case 1: return 'st';
                case 2: return 'nd';
                case 3: return 'rd';
                default: return 'th';
            }
        };

        formatted = formatted.replace(/\d+/, match => `${match}${suffix(day)}`);
        return formatted;
    }

    static setMinDate(inputId) {
        const input = document.getElementById(inputId);
        if (input) input.min = new Date().toISOString().split('T')[0];
    }

    // server validation error handling
    static handleServerValidation(errors) {
        if (Array.isArray(errors)) {
            errors.forEach(error => {
                const field = error.loc?.[1];
                if (field && document.getElementById(field)) {
                    this.showFieldError(field, error.msg)
                }
            });
        } else if (typeof errors === 'object') {
            Object.keys(errors).forEach(field => {
                if (document.getElementById(field)) {
                    this.showFieldError(field, errors[field]);
                }
            });
        }
    }

    // redirect with delay
    static redirectAfterDelay(url, delay = 1500) {
        setTimeout(() => {
            window.location.href = url
        }, delay)
    }

    // confirm alert dialog
    static async confirmAction(message) {
        return confirm(message);
    }

    // toggle element visibility
    static toggleVisibility(elementId, show) {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.classList.toggle('d-none', !show);
    }

    static hideElement(elementId) {
        this.toggleVisibility(elementId, false);
    }

    static showElement(elementId) {
        this.toggleVisibility(elementId, true);
    }
}

window.UIUtils = UIUtils;