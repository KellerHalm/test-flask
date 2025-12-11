import pytest
import httpx
import asyncio
import threading
import time
from app import app

API_URL = "http://127.0.0.1:5001/api"

def run_server():
    app.config['TESTING'] = True
    app.run(port=5001, debug=False, use_reloader=False)

@pytest.fixture(scope="session", autouse=True)
def start_server():
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(1)
    yield

def reset_database():
    async def _reset():
        async with httpx.AsyncClient() as client:
            await client.post(f"{API_URL}/reset")
    asyncio.run(_reset())

@pytest.fixture(autouse=True)
def reset_db():
    reset_database()

@pytest.mark.asyncio
async def test_register():
    data = {
        "username": "testuser",
        "password": "testpass",
        "email": "testuser@example.com"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/register", json=data)
    assert response.status_code == 201
    assert response.json()["message"] == "User registered"

@pytest.mark.asyncio
async def test_login():
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/register", json={
            "username": "testuser",
            "password": "testpass",
            "email": "testuser@example.com"
        })
        response = await client.post(f"{API_URL}/login", json={
            "username": "testuser",
            "password": "testpass"
        })
    assert response.status_code == 200
    assert response.json()["message"] == "Logged in"

@pytest.mark.asyncio
async def test_get_profile():
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/register", json={
            "username": "testuser",
            "password": "testpass",
            "email": "testuser@example.com"
        })
        await client.post(f"{API_URL}/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        response = await client.get(f"{API_URL}/profile")
    assert response.status_code == 200
    assert response.json() == {
        "username": "testuser",
        "email": "testuser@example.com"
    }

@pytest.mark.asyncio
async def test_update_profile():
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/register", json={
            "username": "testuser",
            "password": "testpass",
            "email": "testuser@example.com"
        })
        await client.post(f"{API_URL}/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        response = await client.put(f"{API_URL}/profile", json={
            "email": "testuser2@example.com"
        })
    assert response.status_code == 200
    assert response.json() == {
        "username": "testuser",
        "email": "testuser2@example.com"
    }