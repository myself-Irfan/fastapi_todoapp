from io import BytesIO
from fastapi import status


class TestFileUpload:
    _upload_url = "/api/files/upload"
    _task_url = "/api/tasks"

    def _auth_headers(self, client) -> dict:
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
        access_token = login_resp.json()["data"]["access_token"]

        return {"Authorization": f"Bearer {access_token}"}

    def _create_doc_collection(self, client, auth_headers):
        payload = {
            "title": "test document collection",
            "description": "test description"
        }
        response = client.post(self._task_url, headers=auth_headers, json=payload)
        return response.json().get("data", {}).get("id")

    def _upload_file(
        self,
        client,
        auth_headers=None,
        filename="test.txt",
        content=b"test content",
        document_id: int = None
    ):
        files = {
            "file": (filename, BytesIO(content), "text/plain")
        }

        data = {}
        if document_id is not None:
            data["document_id"] = str(document_id)

        return client.post(self._upload_url, headers=auth_headers, files=files, data=data)

    def test_upload_file_success(self, client):
        auth_headers = self._auth_headers(client)
        response = self._upload_file(client, auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        assert "upload successful" in response.json().get("message")

    def test_upload_file_with_document_id(self, client):
        auth_headers = self._auth_headers(client)
        document_id = self._create_doc_collection(client, auth_headers)

        response = self._upload_file(client, auth_headers, document_id=document_id)

        assert response.status_code == status.HTTP_201_CREATED
        assert "upload successful" in response.json().get("message")

    def test_upload_file_unauthorized(self, client):
        response = self._upload_file(client)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json().get("detail")

    def test_upload_file_no_file_provided(self, client):
        auth_headers = self._auth_headers(client)
        response = client.post(self._upload_url, headers=auth_headers, data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_upload_large_file(self, client):
        auth_headers = self._auth_headers(client)
        large_content = b"x" * (1024 * 1024 * 2)
        response = self._upload_file(client, auth_headers, filename="large_file.txt", content=large_content)

        assert response.status_code == status.HTTP_201_CREATED
        assert "upload successful" in response.json().get("message")

    def test_upload_multiple_file_types(self, client):
        auth_headers = self._auth_headers(client)
        file_types = [
            ("document.pdf", "application/pdf"),
            ("image.png", "image/png"),
            ("data.csv", "text/csv"),
            ("archive.zip", "application/zip")
        ]

        for filename, mime_type in file_types:
            files = {"file": (filename, BytesIO(b"test content"), mime_type)}
            response = client.post(self._upload_url, headers=auth_headers, files=files)
            assert response.status_code == status.HTTP_201_CREATED
            assert "upload successful" in response.json().get("message")

    def test_upload_file_invalid_document_id(self, client):
        auth_headers = self._auth_headers(client)
        response = self._upload_file(client, auth_headers, document_id=99)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "does not exist" in response.json().get("detail").lower()

    def test_upload_file_empty_filename(self, client):
        auth_headers = self._auth_headers(client)

        response = self._upload_file(
            client,
            auth_headers,
            filename=""
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Invalid value for file" in response.json().get("errors")