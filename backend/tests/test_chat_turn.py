import json

from chat import ChatSession, create_session, get_session, run_chat_turn


def test_create_session_returns_unique_ids():
    id_a, session_a = create_session()
    id_b, session_b = create_session()
    assert id_a != id_b
    assert get_session(id_a) is session_a
    assert get_session(id_b) is session_b


def test_get_session_returns_none_for_unknown_id():
    assert get_session("does-not-exist") is None


def test_run_chat_turn_merges_extracted_fields_and_returns_reply():
    session = ChatSession()
    session.messages.append({"role": "user", "content": "7 days in Tokyo"})

    def fake_call_llm(prompt):
        return json.dumps({
            "extracted": {"destination": "Tokyo", "num_days": 7},
            "reply": "Tokyo for 7 days — great! What month works for you?",
        })

    reply = run_chat_turn(session, fake_call_llm)

    assert reply == "Tokyo for 7 days — great! What month works for you?"
    assert session.state["destination"] == "Tokyo"
    assert session.state["num_days"] == 7


def test_run_chat_turn_retries_once_on_malformed_json_then_falls_back():
    session = ChatSession()
    session.messages.append({"role": "user", "content": "somewhere warm"})
    calls = []

    def fake_call_llm(prompt):
        calls.append(prompt)
        return "not json at all"

    reply = run_chat_turn(session, fake_call_llm)

    assert len(calls) == 2
    assert reply == "Where are you thinking of traveling?"
    assert session.state["destination"] == ""


def test_run_chat_turn_recovers_after_one_bad_response():
    session = ChatSession()
    session.messages.append({"role": "user", "content": "Tokyo"})
    responses = iter([
        "not json",
        json.dumps({"extracted": {"destination": "Tokyo"}, "reply": "Got it, Tokyo!"}),
    ])

    def fake_call_llm(prompt):
        return next(responses)

    reply = run_chat_turn(session, fake_call_llm)

    assert reply == "Got it, Tokyo!"
    assert session.state["destination"] == "Tokyo"


def test_run_chat_turn_prompt_names_the_next_missing_field():
    session = ChatSession()
    session.state["destination"] = "Tokyo"
    session.messages.append({"role": "user", "content": "Tokyo"})
    seen_prompts = []

    def fake_call_llm(prompt):
        seen_prompts.append(prompt)
        return json.dumps({"extracted": {}, "reply": "How many days?"})

    run_chat_turn(session, fake_call_llm)

    assert "Ask about: num_days" in seen_prompts[0]
