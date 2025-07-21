def test_user_registration(client):
    payload = {
        'name': 'Test User',
        'email': 'test@example.com',
        "password": 'securepass123'
    }
    response = client.post("/api/users/register", json=payload)
    assert response.status_code == 201
    assert response.json()['message'].startswith('User-')