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
        assert response.json()['detail'] == 'User not registered'

