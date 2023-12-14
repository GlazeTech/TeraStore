from fastapi.testclient import TestClient


def test_create_already_existing_user(client: TestClient) -> None:
    user_payload = {"email": "admin@admin", "password": "admin"}
    response = client.post("/auth/signup", json=user_payload)
    data = response.json()

    assert response.status_code == 409
    assert data["detail"] == "Email admin@admin already exists."


def test_login_with_wrong_password(client: TestClient) -> None:
    user_payload = {"username": "admin@admin", "password": "wrong_password"}
    response = client.post("/auth/login", data=user_payload)
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Email or password is incorrect."


def test_get_all_users(client: TestClient) -> None:
    user_payload = {"email": "admin2@admin", "password": "admin"}
    response = client.post("/auth/signup", json=user_payload)
    data = response.json()

    assert response.status_code == 200
    assert data == "User created"

    response = client.get("/user/users")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["email"] == "admin@admin"
    assert data[1]["email"] == "admin2@admin"


def test_delete_user(client: TestClient) -> None:
    user_payload = {"email": "admin2@admin", "password": "admin"}
    response = client.post("/auth/signup", json=user_payload)
    data = response.json()

    assert response.status_code == 200
    assert data == "User created"

    delete_payload = {"email": "admin2@admin"}
    response = client.post("/user/delete", json=delete_payload)
    data = response.json()

    assert response.status_code == 200
    assert data == "User deleted"

    response = client.get("/user/users")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["email"] == "admin@admin"


def test_update_auth_level(client: TestClient) -> None:
    user_payload = {"email": "admin2@admin", "password": "admin"}
    response = client.post("/auth/signup", json=user_payload)
    data = response.json()

    assert response.status_code == 200
    assert data == "User created"

    update_payload = {"email": "admin2@admin", "auth_level": 3}
    response = client.post("/user/update", json=update_payload)
    data = response.json()

    assert response.status_code == 200
    assert data == "User updated"

    response = client.get("/user/users")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[1]["email"] == "admin2@admin"
    assert data[1]["auth_level"] == 3


def test_logout(client: TestClient) -> None:
    response = client.post("/user/logout")
    data = response.json()

    assert response.status_code == 200
    assert data == "Logout successful"
