from fastapi import status


class TestUserLogin:
    """
    test cases for /api/users/login endpoint
    """

    def test_user_login(self, client):
        reg_payload = {
            "name": "irfan",
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        client.post("/api/users/register", json=reg_payload)

        login_payload = {
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        response = client.post("/api/users/login", json=login_payload)

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "Login successful" in response_data.get('message')
        assert "data" in response_data

        token_data = response_data.get('data')
        assert "access_token" in token_data
        assert "refresh_token" in token_data

    def test_nonexistent_user_login(self, client):
        payload = {
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        response = client.post("/api/users/login", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()['detail'] == "Invalid credentials"

    def test_user_login_wrong_pwd(self, client):
        reg_payload = {
            "name": "irfan",
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        client.post("/api/users/register", json=reg_payload)

        login_payload = {
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12346789"
        }
        response = client.post("/api/users/login", json=login_payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json().get('detail') == 'Invalid credentials'

    def test_user_login_short_pwd(self, client):
        reg_payload = {
            "name": "irfan",
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        client.post("/api/users/register", json=reg_payload)

        login_payload = {
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "1234"
        }
        response = client.post("/api/users/login", json=login_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json().get('detail') == 'password should have at least 5 characters'

    def test_user_login_missing_cred(self, client):
        reg_payload = {
            "name": "irfan",
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        client.post("/api/users/register", json=reg_payload)

        login_payload = {
            "password": "12345"
        }
        response = client.post("/api/users/login", json=login_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Field required' in response.json().get('detail')

        login_payload = {
            "email": "ahmed.1995.irfan@gmail.com"
        }
        response = client.post("/api/users/login", json=login_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Field required' in response.json().get('detail')

    def test_user_login_invalid_fmt(self, client):
        reg_payload = {
            "name": "irfan",
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        client.post("/api/users/register", json=reg_payload)

        invalid_mail_fmt = {
            "invalid-email",
            "invalid@",
            "@invalid.com",
            "invalid.email.com",
            ""
        }

        for mail in invalid_mail_fmt:
            payload = {
                "email": mail,
                "password": "12345"
            }
            response = client.post("/api/users/login", json=payload)
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_login_db_error(self, broken_db, client):
        reg_payload = {
            "name": "irfan",
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        client.post("/api/users/register", json=reg_payload)

        login_payload = {
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }
        response = client.post("/api/users/login", json=login_payload)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
