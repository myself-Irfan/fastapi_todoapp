from fastapi import status


class TestTaskDelete:
    """
    test case for task delete
    """
    _task_url = '/api/tasks'

    def _auth_headers(self, client) -> dict:
        """
        helper func to get auth header
        :param client:
        :return: dict -> Authorization: Bearer Token
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
        """
        helper func to create task
        :param client:
        :param auth_headers:
        :return:
        """
        payload = {
            "title": "Test Task",
            "description": "Test Description",
            "completed": False
        }
        client.post(self._task_url, headers=auth_headers, json=payload)

    def test_delete_task(self, client):
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        response = client.delete(self._task_url + '/1', headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert 'deleted successfully' in response.json().get('message')

    def test_delete_task_notfound(self, client):
        auth_headers = self._auth_headers(client)

        response = client.delete(self._task_url + '/1', headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'not found' in response.json().get('detail')

    def test_delete_task_unauthorized(self, client):
        auth_headers = self._auth_headers(client)
        self._create_task(client, auth_headers)

        response = client.delete(self._task_url + '/1', headers=None)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'Not authenticated' in response.json().get('detail')