import pytest
from fastapi import status
from faker import Faker

from tests.conftest import mock_auth_service

fake = Faker()

@pytest.mark.integration
@pytest.mark.userapp
class TestUserFlowIntegration:
    @pytest.fixture(autouse=True)
    def _setup_urls(self):
        self._register_url = 'api/users/register'
        self._login_url = 'api/users/login'

    def test_register_login_flow(self, client, valid_user_data, disable_rate_limiter, mock_auth_service):
        register_response = client.post(self._register_url, json=valid_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        mock_auth_service.verify_pwd.return_value = (True, False)

        login_data = {
            'email': valid_user_data['email'],
            'password': valid_user_data['password']
        }
        login_response = client.post(self._login_url, json=login_data)

        assert login_response.status_code == status.HTTP_200_OK
        assert 'access_token' in login_response.json().get('data')
        assert 'refresh_token' in login_response.json().get('data')

    def test_multiple_logins_same_user(self, client, make_test_user, mock_auth_service):
        mock_auth_service.verify_pwd.return_value = (True, False)
        login_data = {
            'email': make_test_user.email,
            'password': 'something'
        }

        response_1 = client.post(self._login_url, json=login_data)
        response_2 = client.post(self._login_url, json=login_data)

        assert response_1.status_code == status.HTTP_200_OK
        assert response_2.status_code == status.HTTP_200_OK

        assert response_1.json().get('data').get('access_token') is not None
        assert response_2.json().get('data').get('access_token') is not None