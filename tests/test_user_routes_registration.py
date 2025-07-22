from fastapi import status


class TestUserRegistration:
    """
    Test cases for /api/users/register endpoint
    """

    def test_user_registration(self, client):
        payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            "password": 'securepass123'
        }
        response = client.post("/api/users/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert "message" in response_data
        assert "User-" in response_data.get("message")
        assert "registered successfully" in response_data.get("message")


    def test_duplicate_user_registration(self, client):
        payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            "password": 'securepass123'
        }
        client.post("/api/users/register", json=payload)
        response = client.post("/api/users/register", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['detail'] == 'Email already in use'


    def test_registration_missing_fields(self, client):
        payload = {

        }
        response = client.post("/api/users/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        payload = {
            "email": "john.doe@example.com",
            "password": "securePassword123"
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing email
        payload = {
            "name": "John Doe",
            "password": "securePassword123"
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing password
        payload = {
            "name": "John Doe",
            "email": "john.doe@example.com"
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY