import json
import logging
import os
import threading
import time
import uuid
from typing import Callable, Optional

from dotenv import load_dotenv

load_dotenv()  # must run before any local import that reads env vars at module load

import markdown2
import pdfkit
import requests
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from prompts import get_prompt_cost, get_prompt_preference
from search import gather_price_context
from jsonutil import extract_json_object
from chat import (
    FIELD_WIDGET,
    QUICK_REPLY_OPTIONS,
    apply_extracted_fields,
    canned_ack,
    canned_question,
    create_session,
    get_session,
    has_pricing_inputs,
    next_missing_field,
    run_chat_turn,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wandor.main")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "inclusionai/ling-3.0-flash:free")

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app = FastAPI(title="Wandor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def call_llm(prompt: str, on_chunk: Optional[Callable[[str], None]] = None) -> str:
    """Calls OpenRouter. When `on_chunk` is given, streams the response (SSE,
    same format OpenAI-compatible APIs use) and fires `on_chunk(accumulated_text)`
    as each piece arrives — real generation progress, not a guess, since an LLM
    can't report a percentage for a response whose final length it doesn't know
    yet. Without `on_chunk`, behaves exactly as before (one blocking call).
    """
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="Server is missing OPENROUTER_API_KEY.")

    streaming = on_chunk is not None
    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "X-Title": "Wandor",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 1.0,
            "stream": streaming,
        },
        stream=streaming,
    )
    if response.status_code != 200:
        detail = response.text
        try:
            detail = response.json().get("error", detail)
        except ValueError:
            pass
        raise HTTPException(status_code=response.status_code, detail=str(detail))

    if not streaming:
        return response.json()["choices"][0]["message"]["content"]

    full_text = ""
    for raw_line in response.iter_lines():
        # Decode bytes ourselves as UTF-8 — `decode_unicode=True` relies on
        # `response.encoding`, which requests can't infer from an SSE stream
        # (no charset in `text/event-stream`) and falls back to guessing,
        # corrupting multi-byte characters like ₹ and °.
        line = raw_line.decode("utf-8") if raw_line else ""
        if not line or not line.startswith("data: "):
            continue
        data = line[len("data: "):]
        if data.strip() == "[DONE]":
            break
        try:
            chunk = json.loads(data)
        except json.JSONDecodeError:
            continue
        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
        if delta:
            full_text += delta
            on_chunk(full_text)
    return full_text


class CostEstimateRequest(BaseModel):
    destination: str
    num_days: int
    travel_month: str
    total_budget: float


# In-memory job store. Fine for this app's single-process scale; would need a
# shared store (e.g. Redis) behind multiple workers or processes.
COST_ESTIMATE_JOBS: dict[str, dict] = {}


def _run_cost_estimate_job(job_id: str, payload: CostEstimateRequest) -> None:
    job = COST_ESTIMATE_JOBS[job_id]
    try:

        def on_progress(resolved: int, total: int) -> None:
            job["resolved"] = resolved
            job["total"] = total

        price_context = gather_price_context(
            payload.destination, payload.travel_month, on_progress=on_progress
        )
        job["status"] = "generating"

        def on_chunk(accumulated_text: str) -> None:
            job["generated_chars"] = len(accumulated_text)

        prompt = get_prompt_cost(
            destination=payload.destination,
            num_days=payload.num_days,
            travel_month=payload.travel_month,
            total_budget=payload.total_budget,
            price_context=price_context,
        )
        raw_response = call_llm(prompt, on_chunk=on_chunk)

        job["result"] = extract_json_object(raw_response)
        job["status"] = "done"
    except HTTPException as exc:
        job["status"] = "error"
        job["error"] = str(exc.detail)
    except (ValueError, json.JSONDecodeError):
        job["status"] = "error"
        job["error"] = "Failed to parse cost estimates from the model response."
    except Exception as exc:  # last-resort guard so a bug never leaves a job hung
        job["status"] = "error"
        job["error"] = f"Unexpected error: {exc}"


def start_cost_estimate_job(payload: CostEstimateRequest) -> str:
    job_id = str(uuid.uuid4())
    COST_ESTIMATE_JOBS[job_id] = {
        "status": "searching",
        "resolved": 0,
        "total": 13,
        "generated_chars": 0,
        "result": None,
        "error": None,
    }
    threading.Thread(target=_run_cost_estimate_job, args=(job_id, payload), daemon=True).start()
    return job_id


@app.post("/api/cost-estimate/start")
def start_cost_estimate(payload: CostEstimateRequest):
    return {"job_id": start_cost_estimate_job(payload)}


@app.get("/api/cost-estimate/status/{job_id}")
def cost_estimate_status(job_id: str):
    job = COST_ESTIMATE_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


class ItineraryRequest(BaseModel):
    destination: str
    num_days: int
    total_budget: float
    travel_month: str
    companions: str
    child_ages: Optional[str] = None
    interests_str: str
    accommodation: str
    transportation: str
    dining: str
    pace: str
    special_requests: str = ""
    dietary_restrictions: str = ""
    accessibility_needs: str = ""
    nationality: str = ""


# In-memory job store, same pattern as COST_ESTIMATE_JOBS above.
ITINERARY_JOBS: dict[str, dict] = {}


def _run_itinerary_job(job_id: str, payload: ItineraryRequest) -> None:
    job = ITINERARY_JOBS[job_id]
    try:
        prompt = get_prompt_preference(
            num_days=payload.num_days,
            destination=payload.destination,
            total_budget=payload.total_budget,
            companions=payload.companions,
            interests_str=payload.interests_str,
            child_ages=payload.child_ages,
            accommodation=payload.accommodation,
            transportation=payload.transportation,
            dining=payload.dining,
            pace=payload.pace,
            special_requests=payload.special_requests,
            dietary_restrictions=payload.dietary_restrictions,
            accessibility_needs=payload.accessibility_needs,
            nationality=payload.nationality,
            travel_month=payload.travel_month,
        )

        def on_chunk(accumulated_text: str) -> None:
            job["generated_chars"] = len(accumulated_text)

        itinerary_text = call_llm(prompt, on_chunk=on_chunk)
        job["result"] = {"itinerary": itinerary_text}
        job["status"] = "done"
    except HTTPException as exc:
        job["status"] = "error"
        job["error"] = str(exc.detail)
    except Exception as exc:  # last-resort guard so a bug never leaves a job hung
        job["status"] = "error"
        job["error"] = f"Unexpected error: {exc}"


def start_itinerary_job(payload: ItineraryRequest) -> str:
    job_id = str(uuid.uuid4())
    ITINERARY_JOBS[job_id] = {
        "status": "generating",
        "generated_chars": 0,
        "result": None,
        "error": None,
    }
    threading.Thread(target=_run_itinerary_job, args=(job_id, payload), daemon=True).start()
    return job_id


@app.post("/api/itinerary/start")
def start_itinerary(payload: ItineraryRequest):
    return {"job_id": start_itinerary_job(payload)}


@app.get("/api/itinerary/status/{job_id}")
def itinerary_status(job_id: str):
    job = ITINERARY_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


class ChatStartRequest(BaseModel):
    seed_text: Optional[str] = None


class ChatMessageRequest(BaseModel):
    text: Optional[str] = None
    structured_field: Optional[str] = None
    structured_value: Optional[object] = None


class ChatTurnResponse(BaseModel):
    session_id: str
    message: str
    field: Optional[str]
    widget: str
    options: Optional[list[str]] = None
    pricing_job_id: Optional[str] = None
    itinerary_job_id: Optional[str] = None
    state: dict
    phase: str


def _run_chat_turn_safely(session) -> str:
    try:
        return run_chat_turn(session, call_llm)
    except Exception:
        logger.exception("Chat turn LLM call failed; falling back to a canned question.")
        fallback_field = next_missing_field(session.state)
        return canned_question(fallback_field) if fallback_field else "Sorry, something went wrong — could you try again?"


def _maybe_start_pricing(session) -> None:
    if session.pricing_job_id is None and has_pricing_inputs(session.state):
        session.pricing_job_id = start_cost_estimate_job(
            CostEstimateRequest(
                destination=session.state["destination"],
                num_days=session.state["num_days"],
                travel_month=session.state["travel_month"],
                total_budget=session.state["total_budget"],
            )
        )


def _build_chat_response(session_id: str, session, message: str) -> ChatTurnResponse:
    next_field = next_missing_field(session.state)
    if next_field is not None:
        session.phase = "collecting"
        widget = FIELD_WIDGET[next_field]
        options = QUICK_REPLY_OPTIONS.get(next_field)
    elif session.itinerary_job_id is not None:
        session.phase = "generating"
        widget = "done"
        options = None
    else:
        session.phase = "optional_wrapup"
        widget = "optional_wrapup"
        options = None

    return ChatTurnResponse(
        session_id=session_id,
        message=message,
        field=next_field,
        widget=widget,
        options=options,
        pricing_job_id=session.pricing_job_id,
        itinerary_job_id=session.itinerary_job_id,
        state=dict(session.state),
        phase=session.phase,
    )


def _start_itinerary_from_state(session) -> str:
    return start_itinerary_job(
        ItineraryRequest(
            destination=session.state["destination"],
            num_days=session.state["num_days"],
            total_budget=session.state["total_budget"],
            travel_month=session.state["travel_month"],
            companions=session.state["companions"],
            child_ages=session.state.get("child_ages") or None,
            interests_str=", ".join(
                f"{i['interest']} (rated {i['rating']}/5)" for i in session.state["interests"]
            ),
            accommodation=session.state.get("accommodation") or "No preference",
            transportation=session.state.get("transportation") or "No preference",
            dining=session.state.get("dining") or "No preference",
            pace=session.state["pace"],
            special_requests=session.state.get("special_requests", ""),
            dietary_restrictions=session.state.get("dietary_restrictions", ""),
            accessibility_needs=session.state.get("accessibility_needs", ""),
            nationality=session.state.get("nationality", ""),
        )
    )


@app.post("/api/chat/start", response_model=ChatTurnResponse)
def chat_start(payload: ChatStartRequest):
    session_id, session = create_session()

    if payload.seed_text and payload.seed_text.strip():
        session.messages.append({"role": "user", "content": payload.seed_text.strip()})
        reply = _run_chat_turn_safely(session)
        session.messages.append({"role": "assistant", "content": reply})
        _maybe_start_pricing(session)
        return _build_chat_response(session_id, session, reply)

    opening = canned_question("destination")
    session.messages.append({"role": "assistant", "content": opening})
    return _build_chat_response(session_id, session, opening)


@app.post("/api/chat/{session_id}/message", response_model=ChatTurnResponse)
def chat_message(session_id: str, payload: ChatMessageRequest):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    if payload.structured_field:
        field = payload.structured_field
        value = payload.structured_value
        session.messages.append(
            {"role": "user", "content": value if isinstance(value, str) else json.dumps(value)}
        )
        if field == "wrapup_submit":
            cleaned = {k: v for k, v in value.items() if v is not None} if isinstance(value, dict) else {}
            session.state = apply_extracted_fields(session.state, cleaned)
            message = "Perfect — let me put your itinerary together."
        else:
            session.state = apply_extracted_fields(session.state, {field: value})
            message = canned_ack(field, value)
    elif payload.text and payload.text.strip():
        session.messages.append({"role": "user", "content": payload.text.strip()})
        message = _run_chat_turn_safely(session)
    else:
        raise HTTPException(
            status_code=400, detail="Provide either text or a structured_field/structured_value."
        )

    session.messages.append({"role": "assistant", "content": message})
    _maybe_start_pricing(session)

    # `session.phase` here reflects the value `_build_chat_response` left it at
    # on the *previous* turn — the frontend only ever sends "wrapup_submit"
    # after it already received widget == "optional_wrapup", so this check
    # is reading last turn's outcome, not this turn's (not yet computed).
    if session.phase == "optional_wrapup" and payload.structured_field == "wrapup_submit":
        session.itinerary_job_id = _start_itinerary_from_state(session)

    return _build_chat_response(session_id, session, message)


@app.get("/api/chat/{session_id}", response_model=ChatTurnResponse)
def chat_get(session_id: str):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    last_message = session.messages[-1]["content"] if session.messages else ""
    return _build_chat_response(session_id, session, last_message)


class ItineraryPdfRequest(BaseModel):
    itinerary_markdown: str


@app.post("/api/itinerary/pdf")
def itinerary_pdf(payload: ItineraryPdfRequest):
    start = time.monotonic()
    html_body = markdown2.markdown(
        payload.itinerary_markdown, extras=["fenced-code-blocks", "tables"]
    )
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Open Sans', sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    try:
        pdf_bytes = pdfkit.from_string(html_content, False, options={"encoding": "UTF-8"})
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="PDF generation failed — is wkhtmltopdf installed on this host?",
        ) from exc

    elapsed = time.monotonic() - start
    logger.info(
        "PDF generated in %.2fs (%d chars of markdown in, %d bytes out)",
        elapsed, len(payload.itinerary_markdown), len(pdf_bytes),
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=itinerary.pdf"},
    )
