from httpx import AsyncClient


async def test_register_and_login(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpass",
        "first_name": "Test",
        "last_name": "User",
        "phone": None,
        "skills": None,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["status"] == "successfully registered as volunteer"

    login_response = await client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "strongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


async def test_register_duplicate(client: AsyncClient):
    user = {
        "username": "dup",
        "email": "dup@example.com",
        "password": "pass",
        "first_name": "A",
        "last_name": "B",
        "phone": None,
        "skills": None,
    }
    await client.post("/auth/register", json=user)
    response = await client.post("/auth/register", json=user)
    assert response.status_code == 400


async def test_me_unauthorized(client: AsyncClient):
    response = await client.get("/auth/me")
    assert response.status_code == 401


async def test_me_authorized(client: AsyncClient):
    await client.post("/auth/register", json={
        "username": "me",
        "email": "me@test.com",
        "password": "pass",
        "first_name": "Me",
        "last_name": "User",
        "phone": None,
        "skills": None,
    })
    login = await client.post(
        "/auth/login",
        data={"username": "me@test.com", "password": "pass"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"


async def test_refresh_token(client: AsyncClient):
    await client.post("/auth/register", json={
        "username": "ref",
        "email": "ref@test.com",
        "password": "pass",
        "first_name": "R",
        "last_name": "T",
        "phone": None,
        "skills": None,
    })
    login = await client.post(
        "/auth/login",
        data={"username": "ref@test.com", "password": "pass"},
    )
    refresh = login.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 200
    assert "access_token" in response.json()