import json

import pytest

from app.api import events_crud


def test_create_event(test_app, monkeypatch):
    test_request_payload = {
        "title": "something",
        "city": "somewhere",
        "price_usd": 25.0,
        "seats_left": 100,
    }
    test_response_payload = {
        "id": 1,
        "title": "something",
        "city": "somewhere",
        "price_usd": 25.0,
        "seats_left": 100,
    }

    async def mock_post(payload):
        return 1

    monkeypatch.setattr(events_crud, "post", mock_post)

    response = test_app.post("/events/", content=json.dumps(test_request_payload),)

    assert response.status_code == 201
    assert response.json() == test_response_payload


def test_create_event_invalid_json(test_app):
    response = test_app.post("/events/", content=json.dumps({"title": "something"}))
    assert response.status_code == 422

    response = test_app.post(
        "/events/",
        content=json.dumps(
            {
                "title": "1",
                "city": "1",
                "price_usd": -1,
                "seats_left": -1,
            }
        ),
    )
    assert response.status_code == 422


def test_read_event(test_app, monkeypatch):
    test_data = {
        "id": 1,
        "title": "something",
        "city": "somewhere",
        "price_usd": 25.0,
        "seats_left": 100,
    }

    async def mock_get(id):
        return test_data

    monkeypatch.setattr(events_crud, "get", mock_get)

    response = test_app.get("/events/1")
    assert response.status_code == 200
    assert response.json() == test_data


def test_read_event_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(events_crud, "get", mock_get)

    response = test_app.get("/events/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

    response = test_app.get("/events/0")
    assert response.status_code == 422


def test_read_all_events(test_app, monkeypatch):
    test_data = [
        {
            "id": 1,
            "title": "something",
            "city": "somewhere",
            "price_usd": 25.0,
            "seats_left": 100,
        },
        {
            "id": 2,
            "title": "someone",
            "city": "anywhere",
            "price_usd": 10.5,
            "seats_left": 50,
        },
    ]

    async def mock_get_all():
        return test_data

    monkeypatch.setattr(events_crud, "get_all", mock_get_all)

    response = test_app.get("/events/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_update_event(test_app, monkeypatch):
    test_update_data = {
        "id": 1,
        "title": "someone",
        "city": "anywhere",
        "price_usd": 10.5,
        "seats_left": 50,
    }

    async def mock_get(id):
        return True

    monkeypatch.setattr(events_crud, "get", mock_get)

    async def mock_put(id, payload):
        return 1

    monkeypatch.setattr(events_crud, "put", mock_put)

    response = test_app.put("/events/1/", content=json.dumps(test_update_data))
    assert response.status_code == 200
    assert response.json() == test_update_data


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"city": "bar", "price_usd": 1.0, "seats_left": 1}, 422],
        [
            999,
            {
                "title": "foo",
                "city": "bar",
                "price_usd": 1.0,
                "seats_left": 1,
            },
            404,
        ],
        [
            1,
            {
                "title": "1",
                "city": "bar",
                "price_usd": 1.0,
                "seats_left": 1,
            },
            422,
        ],
        [
            1,
            {
                "title": "foo",
                "city": "b",
                "price_usd": 1.0,
                "seats_left": 1,
            },
            422,
        ],
        [
            1,
            {
                "title": "foo",
                "city": "bar",
                "price_usd": -1.0,
                "seats_left": 1,
            },
            422,
        ],
        [
            1,
            {
                "title": "foo",
                "city": "bar",
                "price_usd": 1.0,
                "seats_left": -1,
            },
            422,
        ],
        [
            0,
            {
                "title": "foo",
                "city": "bar",
                "price_usd": 1.0,
                "seats_left": 1,
            },
            422,
        ],
    ],
)
def test_update_event_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get(id):
        return None

    monkeypatch.setattr(events_crud, "get", mock_get)

    response = test_app.put(f"/events/{id}/", content=json.dumps(payload),)
    assert response.status_code == status_code


def test_remove_event(test_app, monkeypatch):
    test_data = {
        "id": 1,
        "title": "something",
        "city": "somewhere",
        "price_usd": 25.0,
        "seats_left": 100,
    }

    async def mock_get(id):
        return test_data

    monkeypatch.setattr(events_crud, "get", mock_get)

    async def mock_delete(id):
        return id

    monkeypatch.setattr(events_crud, "delete", mock_delete)

    response = test_app.delete("/events/1/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_remove_event_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(events_crud, "get", mock_get)

    response = test_app.delete("/events/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

    response = test_app.delete("/events/0/")
    assert response.status_code == 422
