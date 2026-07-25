"""Real-time web grounding for cost estimates, via Tavily's search API.

The LLM alone has no live pricing — only training-data intuition, which is
frequently wrong or stale for less-represented cities. Tavily's `answer` field
is a pre-synthesized, current answer to a targeted query; we hand that to the
LLM as a grounding fact instead of asking it to guess from memory.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional

import requests
from dotenv import load_dotenv

load_dotenv()  # self-sufficient regardless of import order elsewhere

logger = logging.getLogger("wandor.search")

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
TAVILY_URL = "https://api.tavily.com/search"


def tavily_search(query: str) -> str:
    """Returns Tavily's synthesized answer for a query, or "" on any failure.

    Fails open: a missing key, timeout, or API error should degrade the cost
    estimate back to LLM-only reasoning, not break the endpoint.
    """
    if not TAVILY_API_KEY:
        return ""
    try:
        response = requests.post(
            TAVILY_URL,
            headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
            json={
                "query": query,
                "include_answer": True,
                "search_depth": "basic",
                "max_results": 3,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return ""

    answer = data.get("answer")
    if answer:
        return answer

    # Fall back to the top result's content when Tavily has no synthesized answer.
    results = data.get("results") or []
    if results and results[0].get("content"):
        return results[0]["content"][:300]
    return ""


SUBCATEGORY_QUERIES = {
    "accommodation": {
        "hotel": "average hotel price per night in {destination} in {month}",
        "hostel": "average hostel price per night in {destination}",
        "vacation rental": "average vacation rental or Airbnb price per night in {destination}",
        "boutique hotel": "average boutique hotel price per night in {destination}",
        "eco-lodge": "average eco-lodge price per night in {destination}",
    },
    "dining": {
        "street food": "average street food meal price in {destination}",
        "casual dining": "average casual dining restaurant meal price in {destination}",
        "fine dining": "average fine dining restaurant meal price in {destination}",
        "local cuisine": "average local cuisine restaurant meal price in {destination}",
        "international cuisine": "average international cuisine restaurant meal price in {destination}",
    },
    "transportation": {
        "taxi": "average taxi price per km in {destination}",
        "public transit": "average public transit ticket price in {destination}",
        "car rental": "average car rental price per day in {destination}",
    },
}


def gather_price_context(
    destination: str,
    travel_month: str,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> dict[str, dict[str, str]]:
    """Runs every sub-category search concurrently — one real Tavily answer per
    accommodation/dining/transportation sub-type (13 queries total), all fired
    at once so wall-clock latency stays close to the slowest single call, not
    the sum.

    `on_progress(resolved, total)` fires after each query lands (success or
    fail-open empty), in completion order via `as_completed` — this is what
    lets the frontend show real "N of 13 prices found" progress instead of a
    bare spinner, since Tavily latency here is too variable (seconds to
    minutes) for a client-side simulated progress bar to stay honest.
    """
    flat_queries: dict[tuple[str, str], str] = {
        (category, subcategory): template.format(destination=destination, month=travel_month)
        for category, subcategories in SUBCATEGORY_QUERIES.items()
        for subcategory, template in subcategories.items()
    }
    total = len(flat_queries)

    context: dict[str, dict[str, str]] = {category: {} for category in SUBCATEGORY_QUERIES}
    resolved = 0
    with ThreadPoolExecutor(max_workers=total) as executor:
        future_to_key = {
            executor.submit(tavily_search, query): key for key, query in flat_queries.items()
        }
        for future in as_completed(future_to_key):
            category, subcategory = future_to_key[future]
            answer = future.result()
            if answer:
                context[category][subcategory] = answer
            resolved += 1
            if on_progress:
                on_progress(resolved, total)

    hits = sum(len(v) for v in context.values())
    logger.info(
        "price grounding for %s (%s): %d/%d sub-categories resolved",
        destination, travel_month, hits, total,
    )
    return context
