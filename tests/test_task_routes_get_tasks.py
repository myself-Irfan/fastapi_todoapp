from fastapi import status


class TestTaskGet:
    """
    test cases for task-related endpoints
    """
    task_url = '/api/tasks'

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

        client.post(self.task_url, headers=auth_headers, json=payload)

    def test_get_all_tasks_empty(self, client):
        """
        test getting all tasks when no task exist
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)

        response = client.get(self.task_url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert 'No tasks found' in response.json().get('message')

    def test_get_all_tasks(self, client):
        """
        test get all task
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        response = client.get(self.task_url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "Tasks retrieved successfully" in response.json().get('message')
        assert len(response.json().get('data')) > 0

    def test_all_tasks_unauthorized(self, client):
        """
        test all task with no auth
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        response = client.get(self.task_url, headers=None)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'Not authenticated' in response.json().get('detail')

    def test_get_single_task(self, client):
        """
        test get single task
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        response = client.get(self.task_url + '/1', headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "Task retrieved successfully" in response.json().get('message')
        assert "data" in response.json()

    def test_get_single_task_notfound(self, client):
        """
        test get single task not found
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)

        response = client.get(self.task_url + '/1', headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'not found' in response.json().get('detail')

    def test_get_single_task_unauthorized(self, client):
        """
        test get single task with no auth
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        response = client.get(self.task_url + '/1')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json().get('detail')