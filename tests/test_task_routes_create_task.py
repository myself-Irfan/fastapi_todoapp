from fastapi import status


class TestTaskCreate:
    """
    test case for create task
    """
    _task_url = '/api/tasks'

    def _auth_headers(self, client) -> dict:
        """
        helper func to get auth headers
        :param client:
        :return:
        """
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
        login_resp = client.post("/api/users/login", json=login_payload)

        access_token = login_resp.json().get('data').get('access_token')

        return {'Authorization': f'Bearer {access_token}'}

    def _create_task(self, client, auth_headers=None):
        payload = {
            "title": "Test Task",
            "description": "Test Description",
            "completed": False
        }

        return client.post(self._task_url, headers=auth_headers, json=payload)

    def test_create_task(self, client):
        """
        test creating task
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)

        response = self._create_task(client, auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'created successfully' in response.json().get('message')

    def test_create_task_missing_field(self, client):
        """
        test create task with missing field
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)

        task_payload = {
            "description": "Only description"
        }
        response = client.post(self._task_url, headers=auth_headers, json=task_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Field required' in response.json().get('detail')

    def test_create_task_empty_title(self, client):
        """
        test create task with empty title
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)

        task_payload = {
            "title": "",
            "description": "Test description",
            "is_complete": True
        }

        response = client.post(self._task_url, headers=auth_headers, json=task_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Field required' in response.json().get('detail')

    def test_create_task_not_bool(self, client):
        """
        test create task with empty title
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)

        task_payload = {
            "title": "",
            "description": "Test description",
            "is_complete": "True"
        }

        response = client.post(self._task_url, headers=auth_headers, json=task_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Field required' in response.json().get('detail')

    def test_create_task_unauthorized(self, client):
        """
        test create task with no auth
        :param client:
        :return:
        """
        response = self._create_task(client)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'Not authenticated' in response.json().get('detail')

    def test_create_task_null_values(self, client):
        """
        test create task with null values
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)

        task_payload = {
            "title": None,
            "description": None,
            "is_complete": None
        }
        response = client.post(self._task_url, headers=auth_headers, json=task_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST