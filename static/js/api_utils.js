class ApiClient {
    constructor() {
        this.baseUrl = '/api';
        this.tokens = this.getStoredTokens();
    }

    // token management
    getStoredTokens() {
        return {
            access: localStorage.getItem('access_token'),
            refresh: localStorage.getItem('refresh_token')
        };
    }

    setTokens(accessToken, refreshToken) {
        if (accessToken) {
            localStorage.setItem('access_token', accessToken);
            this.tokens.access = accessToken;
        }

        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
            this.tokens.refresh = refreshToken;
        }
    }

    clearTokens() {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')

        this.tokens = { access: null, refresh: null };
    }

    // get auth headers
    getAuthHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        if (this.tokens.access) {
            headers['Authorization'] = `Bearer ${this.tokens.access}`;
        }
        return headers;
    }

    // generic request method with token refresh logic
    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;

        const config = {
            ...options,
            headers: {
                ...this.getAuthHeaders(),
                ...options.headers
            }
        };

        try {
            let response = await fetch(url, config);

            if (response.status === 401 && this.tokens.refresh && !options._isRetry) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    config.headers['Authorization'] = `Bearer ${this.tokens.access}`
                    config._isRetry = true;
                    response = await fetch(url, config);
                }
            }

            // if still 401 after refresh attempt or no refresh token, redirect to login
            if (response.status === 401) {
                this.clearTokens();

                const curPath = window.location.pathname;
                if (curPath !== '/login') {
                    window.location.href = '/login';
                    throw new Error('Unauthorized. Please log in again.');
                }
                else {
                    throw new Error('Invalid email or password.');
                }
            }

            return response
        } catch (err) {
            console.error('Request failed:', err);
            throw err;
        }
    }

    // refresh access token
    async refreshAccessToken() {
        if (!this.tokens.refresh) return false;

        try {
            const response = await fetch(`${this.baseUrl}/auth/refresh-token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.tokens.refresh}`
                }
            });

            if (response.ok) {
                const { data } = await response.json();
                this.setTokens(data.access_token);
                return true;
            } else {
                this.clearTokens();

                const curPath = window.location.pathname;
                if (curPath !== '/login') {
                    window.location.href = '/login';
                }

                return false;
            }
        } catch (err) {
            console.error('Token refresh failed', err);
            this.clearTokens();

            const curPath = window.location.pathname;
            if (curPath !== '/login') {
                window.location.href = '/login';
            }

            return false;
        }
    }

    async get(endpoint) {
        return this.request(endpoint);
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        })
    }

    async handleResponse(response) {
        if (!response.ok) {
            let errorMessage = 'Request failed';

            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (err) {
                errorMessage = this.getStatusMessage(response.status);
            }
            throw new Error(errorMessage);
        }
        return response.json();
    }

    getStatusMessage(status) {
        const message = {
            400: 'Invalid data provided',
            401: 'Unauthorized. Please log in again.',
            403: 'Not permitted to perform this action.',
            404: 'Resource not found.',
            422: 'Data validation failed',
            500: 'Server error. Please try again later.'
        };
        return message[status] || `Error ${status}`;
    }
}

const apiClient = new ApiClient();
window.apiClient = apiClient;