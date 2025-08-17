from fastapi import status
from unittest.mock import patch


class TestUserRefreshToken:
    """
    test cases for /api/users/refresh-token
    """

    @staticmethod
    def _initial_registration(client):
        reg_payload = {
            "name": "irfan",
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        client.post("/api/users/register", json=reg_payload)

    def test_refresh_token_success(self, client):
        self._initial_registration(client)

        login_payload = {
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }

        login_response = client.post("/api/users/login", json=login_payload)
        refresh_token = login_response.json().get('data').get('refresh_token')

        headers = {"Authorization": f'Bearer {refresh_token}'}
        response = client.post('/api/auth/refresh-token', headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert "Access token refreshed" in response.json().get('message')
        assert 'access_token' in response.json().get('data')

    def test_refresh_token_invalid_fmt(self, client):
        self._initial_registration(client)

        headers = {'Authorization': 'invalid_fmt_token'}
        response = client.post('/api/auth/refresh-token', headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'Invalid Authorization header format' in response.json().get('detail')

    def test_refresh_token_missing_header(self, client):
        self._initial_registration(client)

        response = client.post('/api/auth/refresh-token')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Field required' in response.json().get('detail')

    def test_refresh_token_invalid_token(self, client):
        self._initial_registration(client)

        headers = {'Authorization': 'Bearer invalid-token'}

        response = client.post('/api/auth/refresh-token', headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'Invalid refresh token' in response.json().get('detail')

    # TODO: Need to understand
    @patch('app.userapp.user_routes.verify_pwd')
    def test_user_login_password_rehash(self, mock_verify_pwd, client):
        self._initial_registration(client)

        mock_verify_pwd.return_value = (True, True)

        login_payload = {
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        response = client.post("/api/users/login", json=login_payload)

        assert response.status_code == status.HTTP_200_OK
        mock_verify_pwd.assert_called_once()
