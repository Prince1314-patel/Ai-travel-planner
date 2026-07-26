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


@app.post("/api/cost-estimate/start")
def start_cost_estimate(payload: CostEstimateRequest):
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
    return {"job_id": job_id}


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


@app.post("/api/itinerary/start")
def start_itinerary(payload: ItineraryRequest):
    job_id = str(uuid.uuid4())
    ITINERARY_JOBS[job_id] = {
        "status": "generating",
        "generated_chars": 0,
        "result": None,
        "error": None,
    }
    threading.Thread(target=_run_itinerary_job, args=(job_id, payload), daemon=True).start()
    return {"job_id": job_id}


@app.get("/api/itinerary/status/{job_id}")
def itinerary_status(job_id: str):
    job = ITINERARY_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


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
