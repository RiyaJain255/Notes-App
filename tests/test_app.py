import os
import sys

import pytest

# Allow "from app import create_app" when running pytest from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def add_note(client, title="Test title", content="Test content"):
    return client.post(
        "/add",
        data={"title": title, "content": content},
        follow_redirects=True,
    )


def test_app_starts(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "start.db")})
    assert app is not None
    assert os.path.exists(str(tmp_path / "start.db"))


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Notes App" in response.data


def test_create_note(client):
    response = add_note(client)
    assert response.status_code == 200
    assert b"Test title" in response.data


def test_display_notes(client):
    add_note(client, "First", "Content one")
    add_note(client, "Second", "Content two")
    response = client.get("/")
    assert b"First" in response.data
    assert b"Second" in response.data
    assert b"Created:" in response.data


def test_empty_note_rejected(client):
    response = client.post("/add", data={"title": "", "content": ""})
    assert response.status_code == 400


def test_edit_note(client):
    add_note(client, "Old title", "Old content")
    response = client.post(
        "/edit/1",
        data={"title": "New title", "content": "New content"},
        follow_redirects=True,
    )
    assert b"New title" in response.data
    assert b"Old title" not in response.data


def test_delete_note(client):
    add_note(client, "To delete", "Bye")
    response = client.post("/delete/1", follow_redirects=True)
    assert b"To delete" not in response.data


def test_missing_note_returns_404(client):
    assert client.get("/edit/999").status_code == 404
