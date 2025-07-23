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

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        payload = {
            "email": "john.doe@example.com",
            "password": "securePassword123"
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Missing email
        payload = {
            "name": "John Doe",
            "password": "securePassword123"
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Missing password
        payload = {
            "name": "John Doe",
            "email": "john.doe@example.com"
        }
        response = client.post("/api/users/register", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_registration_invalid_mail_fmt(self, client):
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
                "name": "irfan",
                "password": '12345'
            }
            response = client.post("/api/users/register", json=payload)
            assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_registration_db_error(self, broken_db, client):
        """
        Test registration with database error
        """
        payload = {
            'name': 'irfan',
            'email': 'ahmed.1995.irfan@gmail.com',
            'password': '12345'
        }

        response = client.post('/api/users/register', json=payload)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = response.json()

        assert "Database error" in response_data['detail'] or "Operation error" in response_data['detail']


    def test_registration_empty_str(self, client):
        """
        test with empty str fields
        :param client:
        :return:
        """
        payload = {
            "name": "",
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }

        response = client.post('/api/users/register', json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()

        assert 'Field required' in response_data.get('detail')

    def test_registration_long_field(self, client):
        """
        test long field registration
        :param client:
        :return:
        """
        payload = {
            "name": "x" * 1000,
            "email": "ahmed.1995.irfan@gmail.com",
            "password": "12345"
        }

        response = client.post('/api/users/register', json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name should have at most 100 characters' in response.json().get('detail')
