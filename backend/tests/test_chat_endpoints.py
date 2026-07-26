import json

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def stub_network_calls(monkeypatch):
    field_values = {
        "destination": "Tokyo",
        "num_days": 7,
        "travel_month": "October",
        "total_budget": 80000,
    }

    def fake_call_llm(prompt, on_chunk=None):
        for field, value in field_values.items():
            if f"Ask about: {field}" in prompt:
                return json.dumps({
                    "extracted": {field: value},
                    "reply": f"Got it — noted your {field}.",
                })
        return json.dumps({"extracted": {}, "reply": "Tell me more."})

    def fake_gather_price_context(destination, month, on_progress=None):
        if on_progress:
            on_progress(13, 13)
        return {}

    monkeypatch.setattr(main, "call_llm", fake_call_llm)
    monkeypatch.setattr(main, "gather_price_context", fake_gather_price_context)


@pytest.fixture
def client():
    return TestClient(main.app)


def _complete_required_fields(client, session_id):
    client.post(f"/api/chat/{session_id}/message", json={"text": "7 days"})
    client.post(f"/api/chat/{session_id}/message", json={"text": "October"})
    client.post(f"/api/chat/{session_id}/message", json={"text": "80000 INR"})
    client.post(
        f"/api/chat/{session_id}/message",
        json={"structured_field": "interests", "structured_value": [{"interest": "Food", "rating": 5}]},
    )
    client.post(
        f"/api/chat/{session_id}/message",
        json={"structured_field": "companions", "structured_value": "Solo"},
    )
    return client.post(
        f"/api/chat/{session_id}/message",
        json={"structured_field": "pace", "structured_value": "Moderate"},
    )


def test_chat_start_without_seed_text_returns_opening_question(client):
    response = client.post("/api/chat/start", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["field"] == "destination"
    assert body["widget"] == "text"
    assert "session_id" in body


def test_chat_start_with_seed_text_extracts_destination(client):
    response = client.post("/api/chat/start", json={"seed_text": "Tokyo"})
    assert response.json()["state"]["destination"] == "Tokyo"


def test_chat_message_with_structured_field_updates_state(client):
    start = client.post("/api/chat/start", json={"seed_text": "Tokyo"})
    session_id = start.json()["session_id"]

    response = client.post(
        f"/api/chat/{session_id}/message",
        json={"structured_field": "companions", "structured_value": "Solo"},
    )
    assert response.status_code == 200
    assert response.json()["state"]["companions"] == "Solo"


def test_chat_message_unknown_session_returns_404(client):
    response = client.post("/api/chat/unknown-id/message", json={"text": "hello"})
    assert response.status_code == 404


def test_completing_required_fields_moves_to_optional_wrapup(client):
    start = client.post("/api/chat/start", json={"seed_text": "Tokyo"})
    session_id = start.json()["session_id"]

    response = _complete_required_fields(client, session_id)

    assert response.json()["widget"] == "optional_wrapup"
    assert response.json()["pricing_job_id"] is not None


def test_wrapup_submit_triggers_itinerary_job(client):
    start = client.post("/api/chat/start", json={"seed_text": "Tokyo"})
    session_id = start.json()["session_id"]
    _complete_required_fields(client, session_id)

    response = client.post(
        f"/api/chat/{session_id}/message",
        json={"structured_field": "wrapup_submit", "structured_value": {"nationality": "Indian"}},
    )

    assert response.json()["widget"] == "done"
    assert response.json()["itinerary_job_id"] is not None


def test_wrapup_submit_ignores_none_values_instead_of_storing_literal_none(client):
    start = client.post("/api/chat/start", json={"seed_text": "Tokyo"})
    session_id = start.json()["session_id"]
    _complete_required_fields(client, session_id)

    response = client.post(
        f"/api/chat/{session_id}/message",
        json={"structured_field": "wrapup_submit", "structured_value": {"accommodation": None, "nationality": "Indian"}},
    )

    assert response.json()["state"]["accommodation"] == ""
    assert response.json()["state"]["nationality"] == "Indian"


def test_chat_get_rehydrates_session(client):
    start = client.post("/api/chat/start", json={"seed_text": "Tokyo"})
    session_id = start.json()["session_id"]

    response = client.get(f"/api/chat/{session_id}")
    assert response.status_code == 200
    assert response.json()["state"]["destination"] == "Tokyo"


def test_chat_get_unknown_session_returns_404(client):
    response = client.get("/api/chat/unknown-id")
    assert response.status_code == 404


def test_chat_message_falls_back_gracefully_when_llm_call_raises(client, monkeypatch):
    def raising_call_llm(prompt, on_chunk=None):
        raise ConnectionError("simulated network failure")

    monkeypatch.setattr(main, "call_llm", raising_call_llm)
    start = client.post("/api/chat/start", json={})
    session_id = start.json()["session_id"]

    response = client.post(f"/api/chat/{session_id}/message", json={"text": "somewhere warm"})

    assert response.status_code == 200
    assert response.json()["field"] == "destination"
