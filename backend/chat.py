"""Deterministic conversation state machine for the chat planning flow.

The LLM's job per turn is narrow (extract fields, phrase a reply) — which
field to ask next, what options it offers, and when the required checklist
is complete are all decided here in plain Python so flow control never
depends on a free-tier model's judgment. Session store and LLM-calling
orchestration live in this same module (added in Task 3) since they're
tightly coupled to this state shape.
"""

from typing import Optional, TypedDict


class Interest(TypedDict):
    interest: str
    rating: int


class TripState(TypedDict):
    destination: str
    num_days: int
    travel_month: str
    total_budget: float
    interests: list[Interest]
    companions: str
    child_ages: str
    pace: str
    accommodation: str
    transportation: str
    dining: str
    special_requests: str
    dietary_restrictions: str
    accessibility_needs: str
    nationality: str


def empty_state() -> TripState:
    return TripState(
        destination="",
        num_days=0,
        travel_month="",
        total_budget=0.0,
        interests=[],
        companions="",
        child_ages="",
        pace="",
        accommodation="",
        transportation="",
        dining="",
        special_requests="",
        dietary_restrictions="",
        accessibility_needs="",
        nationality="",
    )


REQUIRED_FIELDS = [
    "destination",
    "num_days",
    "travel_month",
    "total_budget",
    "interests",
    "companions",
    "pace",
]

QUICK_REPLY_OPTIONS: dict[str, list[str]] = {
    "companions": ["Solo", "Couple", "Family", "Group"],
    "pace": ["Relaxed", "Moderate", "Packed"],
}

FIELD_WIDGET: dict[str, str] = {
    "destination": "text",
    "num_days": "text",
    "travel_month": "text",
    "total_budget": "text",
    "interests": "interest_picker",
    "companions": "choice",
    "child_ages": "text",
    "pace": "choice",
}

CANNED_QUESTIONS: dict[str, str] = {
    "destination": "Where are you thinking of traveling?",
    "num_days": "How many days is the trip?",
    "travel_month": "What month are you planning to travel?",
    "total_budget": "What's your total budget for the trip, in INR?",
    "interests": "What kind of experiences are you most into?",
    "companions": "Who's this trip for?",
    "child_ages": "How old are the kids joining you, so I can tailor things for them?",
    "pace": "What pace do you want — relaxed, moderate, or packed?",
}

CANNED_ACKS: dict[str, str] = {
    "companions": "Got it — {value}.",
    "pace": "{value} pace, noted.",
    "interests": "Great choices — I'll build the days around those.",
}


def _is_filled(state: TripState, field: str) -> bool:
    value = state.get(field)
    if field in ("num_days", "total_budget"):
        return bool(value) and value > 0
    if field == "interests":
        return bool(value)
    return bool(value) and str(value).strip() != ""


def next_missing_field(state: TripState) -> Optional[str]:
    """Returns the next required field to ask about, or None once the
    blocking checklist (including the Family-only child_ages follow-up) is
    complete.
    """
    for field in REQUIRED_FIELDS:
        if not _is_filled(state, field):
            return field
    if state.get("companions") == "Family" and not _is_filled(state, "child_ages"):
        return "child_ages"
    return None


def has_pricing_inputs(state: TripState) -> bool:
    return all(_is_filled(state, f) for f in ("destination", "num_days", "travel_month", "total_budget"))


def canned_ack(field: str, value) -> str:
    template = CANNED_ACKS.get(field, "Got it.")
    return template.format(value=value) if "{value}" in template else template


def canned_question(field: str) -> str:
    return CANNED_QUESTIONS[field]


def apply_extracted_fields(state: TripState, extracted: dict) -> TripState:
    """Merges LLM- or UI-extracted field values into `state`, coercing types
    and dropping anything that doesn't validate. Unknown keys are ignored —
    the LLM's extraction JSON is untrusted input, not a trusted patch.
    """
    updated = dict(state)

    if "destination" in extracted and str(extracted["destination"]).strip():
        updated["destination"] = str(extracted["destination"]).strip()

    if "num_days" in extracted:
        try:
            days = int(extracted["num_days"])
            if days > 0:
                updated["num_days"] = days
        except (TypeError, ValueError):
            pass

    if "travel_month" in extracted and str(extracted["travel_month"]).strip():
        updated["travel_month"] = str(extracted["travel_month"]).strip()

    if "total_budget" in extracted:
        try:
            budget = float(extracted["total_budget"])
            if budget > 0:
                updated["total_budget"] = budget
        except (TypeError, ValueError):
            pass

    if "interests" in extracted and isinstance(extracted["interests"], list):
        interests: list[Interest] = []
        for item in extracted["interests"]:
            if not isinstance(item, dict) or not item.get("interest"):
                continue
            try:
                rating = int(item.get("rating", 3))
            except (TypeError, ValueError):
                rating = 3
            rating = min(5, max(1, rating))
            interests.append({"interest": str(item["interest"]).strip(), "rating": rating})
        if interests:
            updated["interests"] = interests

    if "companions" in extracted:
        value = str(extracted["companions"]).strip().title()
        if value in QUICK_REPLY_OPTIONS["companions"]:
            updated["companions"] = value

    if "pace" in extracted:
        value = str(extracted["pace"]).strip().title()
        if value in QUICK_REPLY_OPTIONS["pace"]:
            updated["pace"] = value

    for field in (
        "child_ages",
        "accommodation",
        "transportation",
        "dining",
        "special_requests",
        "dietary_restrictions",
        "accessibility_needs",
        "nationality",
    ):
        if field in extracted and str(extracted[field]).strip():
            updated[field] = str(extracted[field]).strip()

    return updated  # type: ignore[return-value]
