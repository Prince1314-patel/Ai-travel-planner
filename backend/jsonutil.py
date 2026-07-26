"""Shared tolerant JSON parsing for LLM responses that wrap a JSON object in
prose (the model doesn't always respect "respond with only JSON").
"""

import json


def extract_json_object(text: str) -> dict:
    """Finds the first {...} block in `text` and parses it.

    Raises ValueError if no brace pair is found or the slice isn't valid JSON.
    """
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in text.")
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON object: {exc}") from exc
