from fastapi import status


class TestTaskUpdate:
    """
    test case for task update
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

    def _create_task(self, client, auth_headers):
        payload = {
            "title": "Test Task",
            "description": "Test Description",
            "completed": False
        }

        client.post(self._task_url, headers=auth_headers, json=payload)

    def test_update_task(self, client):
        """
        test to update task
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        payload = {
            "title": "Test Task take 2",
            "description": "Test Description",
            "is_complete": True,
            "due_date": "2025-07-28"
        }
        response = client.put(self._task_url + '/1', headers=auth_headers, json=payload)

        assert response.status_code == status.HTTP_200_OK
        assert "updated successfully" in response.json().get('message')

    def test_update_task_partial(self, client):
        """
        test to update task
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        payload = {
            "is_complete": True,
            "due_date": "2025-07-28"
        }
        response = client.put(self._task_url + '/1', headers=auth_headers, json=payload)

        assert response.status_code == status.HTTP_200_OK
        assert "updated successfully" in response.json().get('message')

    def test_update_task_notfound(self, client):
        """
        test to update task
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)

        payload = {
            "is_complete": True,
            "due_date": "2025-07-28"
        }
        response = client.put(self._task_url + '/1', headers=auth_headers, json=payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json().get('detail')

    def test_update_task_unauthorized(self, client):
        """
        test to update task
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        payload = {
            "is_complete": True,
            "due_date": "2025-07-28"
        }
        response = client.put(self._task_url + '/1', headers=None, json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json().get('detail')