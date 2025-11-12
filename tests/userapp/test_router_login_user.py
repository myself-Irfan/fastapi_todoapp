import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.userapp
class TestLoginRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._login_url = 'api/users/login'

    def test_login_success(self, client, login_payload, mock_auth_service, make_test_user):
        mock_auth_service.verify_pwd.return_value = (True, False)
        response = client.post(self._login_url, json=login_payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'data' in data
        assert 'access_token' in data.get('data')
        assert 'refresh_token' in data.get('data')
        assert data.get('data').get('access_token') == 'mock_access_token'
        assert data.get('data').get('refresh_token') == 'mock_refresh_token'

    def test_login_response_structure(self, client, login_payload, make_test_user, mock_auth_service):
        mock_auth_service.verify_pwd.return_value = (True, False)
        response = client.post(self._login_url, json=login_payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "data" in data
        assert isinstance(data["data"], dict)
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_login_user_not_found(self, client):
        login_data = {
            'email': 'nonexistant@gmail.com',
            'password': 'pwd123'
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_login_wrong_pwd(self, client, mock_auth_service, make_test_user):
        mock_auth_service.verify_pwd.return_value = (False, False)
        login_data = {
            'email': make_test_user.email,
            'password': 'wrongpwd123'
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_email_fmt(self, client, invalid_user_data_bad_email):
        response = client.post(self._login_url, json=invalid_user_data_bad_email)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_pwd(self, client, valid_user_data):
        login_data = {
            "email": valid_user_data.get('email')
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_email(self, client, valid_user_data):
        login_data = {
            'password': valid_user_data.get('password')
        }
        response = client.post(self._login_url, json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_empty_payload(self, client):
        response = client.post(self._login_url, json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY