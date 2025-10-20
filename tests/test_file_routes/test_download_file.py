import urllib.parse
from io import BytesIO
from fastapi import status


class TestFileDownload:
    _upload_url = "/api/files/upload"
    _task_url = "/api/tasks"
    _download_url = "/api/files/{file_id}/download"

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

    def _upload_file(
        self,
        client,
        auth_headers=None,
        filename="test.txt",
        content=b"test content",
        mime_type="text/plain",
        document_id: int = None
    ):
        files = {
            "file": (filename, BytesIO(content), mime_type)
        }

        data = {}
        if document_id is not None:
            data["document_id"] = str(document_id)

        return client.post(self._upload_url, headers=auth_headers, files=files, data=data)

    def test_download_file_success(self, client):
        auth_headers = self._auth_headers(client)

        file_content = b"test file content for download"

        upload_response = self._upload_file(
            client,
            auth_headers,
            filename="test_download.txt",
            content=file_content
        )
        assert upload_response.status_code == status.HTTP_201_CREATED

        message = upload_response.json().get("message")
        file_id = int(message.split("file-")[1].split(" ")[0])

        download_url = self._download_url.format(file_id=file_id)
        response = client.get(download_url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.content == file_content
        assert "test_download.txt" in response.headers.get("content-disposition", "")

    def test_download_file_not_found(self, client):
        auth_headers = self._auth_headers(client)
        download_url = self._download_url.format(file_id=99)

        response = client.get(download_url, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json().get("detail").lower()

    def test_download_file_different_user(self, client):
        auth_headers_user1 = self._auth_headers(client)
        upload_response = self._upload_file(
            client,
            auth_headers_user1,
            filename="user1_file.txt",
            content=b"user 1 content"
        )
        message = upload_response.json().get("message")
        file_id = int(message.split("file-")[1].split(" ")[0])

        reg_payload = {
            "name": "user2",
            "email": "user2@example.com",
            "password": "12345"
        }
        client.post("/api/users/register", json=reg_payload)

        login_payload = {
            "email": "user2@example.com",
            "password": "12345"
        }
        login_resp = client.post("/api/users/login", json=login_payload)
        auth_headers_user2 = {
            "Authorization": f"Bearer {login_resp.json()['data']['access_token']}"
        }

        download_url = self._download_url.format(file_id=file_id)
        response = client.get(download_url, headers=auth_headers_user2)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_different_file_types(self, client):
        auth_headers = self._auth_headers(client)

        test_files = [
            ("document.pdf", b"PDF content", "application/pdf"),
            ("image.png", b"PNG content", "image/png"),
            ("data.csv", b"CSV,content", "text/csv"),
        ]

        for filename, content, mime_type in test_files:
            upload_response = self._upload_file(
                client,
                auth_headers,
                filename=filename,
                content=content,
                mime_type=mime_type
            )

            message = upload_response.json().get("message")
            file_id = int(message.split("file-")[1].split(" ")[0])

            # Download file
            download_url = self._download_url.format(file_id=file_id)
            response = client.get(download_url, headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            assert response.content == content
            assert filename in response.headers.get("content-disposition", "")
            assert mime_type in response.headers.get("content-type", "")

    def test_download_large_file(self, client):
        auth_headers = self._auth_headers(client)
        large_content = b"x" * (1024 * 1024 * 10)
        upload_response = self._upload_file(
            client,
            auth_headers,
            filename="large_file.bin",
            content=large_content,
            mime_type="application/octet-stream"
        )

        message = upload_response.json().get("message")
        file_id = int(message.split("file-")[1].split(" ")[0])

        download_url = self._download_url.format(file_id=file_id)
        response = client.get(download_url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.content) == len(large_content)
        assert response.content == large_content

    def test_download_without_auth(self, client):
        download_url =  self._download_url.format(file_id=1)
        response = client.get(download_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_download_with_invalid_token(self, client):
        download_url = self._download_url.format(file_id=1)
        invalid_headers = {
            "Authorization": "Bearer invalid_token"
        }
        response = client.get(download_url, headers=invalid_headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_download_file_special_characters_filename(self, client):
        auth_headers = self._auth_headers(client)

        special_filenames = [
            "file spaces.txt",
            "file-dashes.txt",
            "file_underscores.txt",
            "file(parenthesis).txt",
            "file[brackets].txt"
        ]

        for filename in special_filenames:
            upload_response = self._upload_file(
                client, auth_headers, filename=filename, content=b"test content"
            )

            message = upload_response.json().get("message")
            file_id = int(message.split("file-")[1].split(" ")[0])
            download_url = self._download_url.format(file_id=file_id)
            response = client.get(download_url, headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK

            cd_header = response.headers.get("content-disposition", "")

            if "filename*=" in cd_header:
                encoded_filename = cd_header.split("filename*=utf-8''")[1]
                decoded_filename = urllib.parse.unquote(encoded_filename)
            elif "filename=" in cd_header:
                decoded_filename = cd_header.split("filename=")[1].strip('"')
            else:
                decoded_filename = ""

            assert decoded_filename == filename

    def test_download_empty_file(self, client):
        auth_headers = self._auth_headers(client)

        upload_response = self._upload_file(
            client, auth_headers, "empty.txt", b""
        )

        message = upload_response.json().get("message")
        file_id = int(message.split("file-")[1].split(" ")[0])
        download_url = self._download_url.format(file_id=file_id)
        response = client.get(download_url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.content == b""
        assert len(response.content) == 0

    def test_download_file_with_unicode_filename(self, client):
        auth_headers = self._auth_headers(client)

        unicode_filenames = [
            "文档.txt",
            "файл.txt",
            "αρχείο.txt",
            "ملف.txt",
        ]

        for filename in unicode_filenames:
            upload_response = self._upload_file(
                client, auth_headers, filename, b"unicode test"
            )

            message = upload_response.json().get("message")

            file_id = int(message.split("file-")[1].split(" ")[0])
            download_url = self._download_url.format(file_id=file_id)

            response = client.get(download_url, headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK

    def test_download_multiple_times_same_file(self, client):
        auth_headers = self._auth_headers(client)

        upload_response = self._upload_file(
            client, auth_headers,
            "multi_download.txt",
            b"download multiple times"
        )

        message = upload_response.json().get("message")
        file_id = int(message.split("file-")[1].split(" ")[0])
        download_url = self._download_url.format(file_id=file_id)

        for _ in range(5):
            response = client.get(download_url, headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            assert response.content == b"download multiple times"

    def test_download_file_headers_content_type(self, client):
        auth_headers = self._auth_headers(client)

        test_cases = [
            ("text.txt", "text/plain"),
            ("doc.pdf", "application/pdf"),
            ("img.jpg", "image/jpeg"),
            ("sheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("archive.zip", "application/zip"),
        ]

        for filename, expected_mime in test_cases:
            upload_response = self._upload_file(
                client, auth_headers, filename, b"test", mime_type=expected_mime
            )

            message = upload_response.json().get("message")
            file_id = int(message.split("file-")[1].split(" ")[0])
            download_url = self._download_url.format(file_id=file_id)

            response = client.get(download_url, headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            assert expected_mime in response.headers.get("content-type")

    def test_download_file_content_disposition_attachment(self, client):
        auth_headers = self._auth_headers(client)

        upload_response = self._upload_file(
            client, auth_headers, filename="download_test.txt", content=b"test"
        )

        message = upload_response.json().get("message")
        file_id = int(message.split("file-")[1].split(" ")[0])
        download_url = self._download_url.format(file_id=file_id)

        response = client.get(download_url, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        content_disposition = response.headers.get("content-disposition", "")
        assert "attachment", "download_test.txt" in content_disposition