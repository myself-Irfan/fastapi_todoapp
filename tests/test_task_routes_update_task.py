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

    def _test_update_task(self, client):
        """
        test to update task
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        payload = {
            "is_complete": True
        }
        response = client.put(self._task_url, headers=auth_headers, json=payload)

        assert response.status == status.HTTP_200_OK
        assert "updated successfully" in response.json().get('message')