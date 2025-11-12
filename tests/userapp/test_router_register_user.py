import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.userapp
class TestRegisterRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._register_url = 'api/users/register'

    def test_register_success(self, client, valid_user_data, disable_rate_limiter, mock_auth_service):
        response = client.post(self._register_url, json=valid_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.json()
        assert 'created successfully' in response.json()['message'].lower()

    def test_register_duplicate_email(self, client, valid_user_data, disable_rate_limiter, mock_auth_service):
        client.post(self._register_url, json=valid_user_data)

        duplicate_data = {
            "name": "New User",
            'email': valid_user_data.get('email'),
            'password': "newpwd123"
        }

        response = client.post(self._register_url, json=duplicate_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already exists' in response.json().get('detail').lower()

    def test_register_invalid_email(self, client, invalid_user_data_bad_email, disable_rate_limiter):
        invalid_data = {
            'name': invalid_user_data_bad_email.get('name'),
            'email': invalid_user_data_bad_email.get('email'),
            'password': invalid_user_data_bad_email.get('password')
        }

        response = client.post(self._register_url, json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_name(self, client, invalid_user_data_short_name, disable_rate_limiter):
        response = client.post(self._register_url, json=invalid_user_data_short_name)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_long_name(self, client, invalid_user_data_long_name, disable_rate_limiter):
        response = client.post(self._register_url, json=invalid_user_data_long_name)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_pwd(self, client, invalid_user_data_short_password, disable_rate_limiter):
        response = client.post(self._register_url, json=invalid_user_data_short_password)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_fields(self, client, disable_rate_limiter):
        incomplete_data = {
            'name': "Test User"
        }

        response = client.post(self._register_url, json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_empty_payload(self, client, disable_rate_limiter):
        response = client.post(self._register_url, json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_special_chars_in_name(self, client, disable_rate_limiter, mock_auth_service):
        data = {
            'name': 'Test User @#$',
            'email': 'test@example.com',
            'password': 'password123'
        }

        response = client.post(self._register_url, json=data)

        assert response.status_code == status.HTTP_201_CREATED