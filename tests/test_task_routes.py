import pytest
from fastapi import status
from unittest.mock import patch


class TestTaskRoutes:
    """
    test cases for task-related endpoints
    """
    task_url = '/api/tasks'

    @staticmethod
    def _auth_headers(client) -> dict:
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


    def test_get_all_tasks_empty(self, client):
        """
        test getting all tasks when no task exist
        :param client:
        :return:
        """
        auth_headers = self._auth_headers(client)

        response = client.get(self.task_url, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'No task found' in response.json().get('detail')