import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.userapp
class TestLoginRoute:
    def __init__(self):
        self._login_url = '/login'

    def test_login_success(self, client, get_default_test_user, mock_auth_service):
        mock_auth_service.verify_pwd.return_value = (True, False)
        login_data = {
            'email': get_default_test_user.email,
            'password': 'testpwd123'
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'data' in data
        assert 'access_token' in data.get('data')
        assert 'refresh_token' in data.get('data')
        assert data.get('data').get('access_token') == 'mock_access_token'
        assert data.get('data').get('refresh_token') == 'mock_refresh_token'

    def test_login_user_not_found(self, client):
        login_data = {
            'email': 'nonexistant@gmail.com',
            'password': 'pwd123'
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_login_wrong_pwd(self, client, get_default_test_user, mock_auth_service):
        mock_auth_service.verify_pwd.return_value = (False, False)
        login_data = {
            'email': get_default_test_user.email,
            'password': 'wrongpwd123'
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_email_fmt(self, client):
        login_data = {
            'email': 'not-an-email',
            'password': 'pwd12345'
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_pwd(self, client):
        login_data = {
            "email": "test@example.com"
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_email(self, client):
        login_data = {
            'password': 'randpwd123'
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY