# Conversational Planning Flow — Design

## Summary

Replace Wandor's two-step form (Trip Details → Preferences → Results) with a
single AI chat flow. The traveler describes their trip in plain language; the
AI asks clarifying questions (with Claude-style quick-reply buttons where a
question has a natural set of choices) until it has enough to generate a
personalized itinerary, which is then delivered inline in the same
conversation thread — no separate results page.

## Goals

- Replace form-filling with natural conversation as the primary input method.
- Ask only what's needed: a small required checklist, everything else optional
  and asked once, skippable.
- Reuse existing backend grounding (live price search) and generation logic
  unchanged — only the *collection* of inputs changes, not how the itinerary
  or cost estimates are produced.
- Keep the free-tier LLM (`inclusionai/ling-3.0-flash:free`) as the default,
  but make the model configurable via `.env` without code changes.
- Preserve the existing visual system (DESIGN.md) — the One Video Rule, the
  Narrow Terracotta Rule, and the Blur-Is-Depth Rule all still apply; the chat
  panel is a flat-white "flow page" surface, not a new visual world.

## Non-goals

- No user accounts, saved trips, or cross-visit history — still one-shot per
  Product Principle 5. A chat session lives only in `sessionStorage` +
  backend memory, not a database.
- No change to how the cost-estimate or itinerary LLM calls are grounded or
  formatted — `prompts.py`'s `get_prompt_cost` and `get_prompt_preference`
  are reused unchanged.
- No multi-turn "edit my itinerary" chat after generation — "Plan another
  trip" still resets to a fresh session, same as today's "Plan another trip"
  button.

## Architecture Overview

The chat is driven by a **deterministic Python state machine**, not by
trusting the LLM to decide when it's "ready." Per turn, the LLM does exactly
one narrow job: extract any fields it can confidently read from the user's
last message, and phrase a warm reply asking about whichever field Python
says is next. This keeps the free-tier model's structured-output burden small
(one flat JSON object: extracted fields + a reply string) and keeps the
question order, required-field gating, and quick-reply option lists
reliable and testable in code.

## Backend Design

### Session state

A new in-memory store (same pattern as `COST_ESTIMATE_JOBS` /
`ITINERARY_JOBS`), keyed by `session_id`:

```python
class ChatSession(TypedDict):
    messages: list[dict]       # [{role, content}, ...] — full turn history for prompt context
    state: TripState           # extracted fields, same shape as today's PlanState
    phase: str                 # "collecting" | "pricing" | "optional_wrapup" | "generating" | "done"
    pricing_job_id: str | None
    itinerary_job_id: str | None
```

`TripState` carries the same fields the old `PlanState` did: destination,
num_days, travel_month, total_budget, interests (list of {interest, rating}),
companions, child_ages, accommodation, transportation, dining, pace,
special_requests, dietary_restrictions, accessibility_needs, nationality.

### Required-field checklist (deterministic, in Python)

**Blocking** (asked one at a time, in order, until filled):
destination → num_days → travel_month → total_budget → interests →
companions (+ child_ages if Family) → pace.

**Optional wrap-up** (asked once, as a single combined message, after the
blocking checklist is complete — never blocks generation):
accommodation / transportation / dining preference (pre-defaulted to the
first price-grounded option if the pricing job has resolved by then, else
today's static fallback list), plus a free-text box covering dietary
restrictions, accessibility needs, special requests, and nationality
together. A "Generate my itinerary" action submits immediately — skipping
is just clicking it without filling the text box.

Quick-reply **option lists for enum fields are hardcoded in Python**
(companions: Solo/Couple/Family/Group; pace: Relaxed/Moderate/Packed;
accommodation/transportation/dining: from the cost-estimate job or the
existing `FALLBACK_*` lists) — the LLM never invents these, it only picks
which field to ask about and phrases the sentence.

### Endpoints

```
POST /api/chat/start        {seed_text?: string}
  → {session_id, message, quick_replies?}

POST /api/chat/{id}/message {text: string}
  → {message, quick_replies?, phase, pricing_job_id?, itinerary_job_id?}

GET  /api/chat/{id}
  → {messages, state, phase, quick_replies?, pricing_job_id?, itinerary_job_id?}
  # rehydrate transcript after a refresh — quick_replies (if the latest
  # assistant message was a question) and any in-flight job ids are included
  # so the UI can resume mid-question or mid-progress-bar, not just replay text

GET  /api/cost-estimate/status/{job_id}   # existing, unchanged, reused
GET  /api/itinerary/status/{job_id}       # existing, unchanged, reused
POST /api/itinerary/pdf                    # existing, unchanged, reused
```

`POST /api/chat/start` seeds the first user message from the hero textarea
(if non-empty) and runs one turn immediately so the AI's first reply already
reacts to whatever the visitor typed.

Once `total_budget` is filled, the backend fires the existing
`gather_price_context` + cost-estimate LLM call as a background job (reusing
`_run_cost_estimate_job`'s pattern) and moves `phase` to `"pricing"` while
continuing to collect `interests` / `companions` / `pace` in parallel — the
chat shows a `PricingProgressBubble` alongside ongoing questions, not a
blocking wait.

Once the blocking checklist and the optional wrap-up are both settled, the
backend fires the existing itinerary job (`_run_itinerary_job`, reusing
`get_prompt_preference` unchanged) and moves `phase` to `"generating"`.

### Turn prompt (new: `get_prompt_chat_turn`)

Input: conversation history, current known `TripState`, the name of the next
field Python wants asked about (or `None` if this is the optional wrap-up or
a free-form follow-up), and that field's hardcoded option list if any.

Output (single JSON object, parsed with the same tolerant brace-scan
`main.py` already uses for the cost-estimate response):

```json
{
  "extracted": { "destination": "Tokyo", "num_days": 7 },
  "reply": "Tokyo for 7 days — love it. What month are you thinking of traveling?"
}
```

The `reply` string becomes the `message` field in the `/api/chat/*` HTTP
responses below — same value, renamed at the API boundary because "message"
is the noun the frontend's `ChatBubble` list already uses.

On parse failure: retry once, then fall back to a canned clarifying
question for the current field without losing any previously extracted
state.

### Model configuration

```python
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "inclusionai/ling-3.0-flash:free")
```

One env var, used uniformly by the chat-turn, cost-estimate, and itinerary
calls — swappable anytime without a code change.

## Frontend Design

### Landing becomes the single entry surface

`/` (`Landing.tsx`) owns both the hero and the chat panel via local state
(`started: boolean`); there is no more `/plan` route as the primary path. A
direct visit to `/plan` redirects to `/` and mounts the chat panel
immediately (no hero, no video, no transition — see below).

The hero's decorative `<p>` becomes a real controlled `<textarea>`. Submitting
(via the "Plan My Trip" pill) calls `POST /api/chat/start` with the typed
text and flips `started` to `true`, triggering the transition below.

### Hero → chat transition (authored focal moment)

On submit, a single ~650ms sequence plays, honoring the One Video Rule and
the Blur-Is-Depth Rule *during* the transition, not just after it:

1. **0–200ms** — headline/subtitle fade + drift up 12px and out; nav links
   fade lightly. Opacity/transform only, no layout-height animation.
2. **0–350ms** (concurrent) — video and its white gradient overlay cross-fade
   to solid white.
3. **150–550ms** (the focal beat) — the glass hero card itself survives the
   cut via a FLIP-style shared-element transform into the first chat bubble's
   position: border `3px white → 1px black/8%`, fill
   `bg-white/[0.06]+blur-20px → solid white`, radius held at 44px, shadow
   value held constant (same value in both systems per DESIGN.md).
   `cubic-bezier(0.16,1,0.3,1)`.
4. **400–650ms** — the landed bubble shows the user's typed text (kept
   terracotta, extending the Narrow Terracotta Rule from hero into chat); the
   AI's first reply fades+rises in underneath; the persistent input dock
   fades in at the bottom.

Edge cases: empty hero textarea → same choreography, placeholder text fades
out instead of "becoming" a message, AI's opening question is the first
bubble. `prefers-reduced-motion` → skip the FLIP/blur-resolve, plain 150ms
cross-fade to the landed state. Entering via the nav pill while scrolled, or
a direct `/plan` visit → no card to morph from, so the chat panel mounts
directly with a simple fade; the full sequence is reserved for the actual
hero-card submit.

The wordmark never moves — pinned top-left throughout — which is what makes
this read as "the same page," not a disguised navigation.

### New components

- `ChatThread` — scrollable message list, auto-scrolls to newest.
- `ChatBubble` — user (terracotta text) vs. assistant (flat white card).
- `QuickReplyGroup` — pill buttons reusing `PillRadioGroup`/`PillButton`
  styling; the text input stays live underneath always, so typing overrides
  the buttons.
- `InterestPickerMessage` — today's `InterestPicker` embedded inline for the
  one genuinely multi-select + rated question.
- `PricingProgressBubble` — reuses `ProgressBar`, polls
  `/api/cost-estimate/status/{job_id}`, updates in place.
- `ItineraryBubble` — reuses `ResultsStep`'s day-accordion cards + PDF
  button + AI disclaimer, rendered inline instead of a standalone page;
  includes the "Plan another trip" reset action.
- Optional wrap-up renders as one combined assistant message: three
  single-select pill groups (pre-defaulted), one free-text box, one
  "Generate my itinerary" button.

### State persistence

`session_id` persists to `sessionStorage`. On mount, if one exists, the page
calls `GET /api/chat/{id}` to rehydrate the transcript, so an accidental
refresh mid-conversation doesn't lose a long chat. This is new versus
today's fully in-memory `planContext` (which had no refresh resilience
either, but also had much less to lose per session).

## Error Handling

- Turn-extraction JSON fails to parse → retry once, then fall back to a
  generic clarifying reply, no state lost.
- Pricing job fails per sub-type → unchanged, fails open exactly as today.
- Itinerary job errors → error bubble with a "Try again" quick-reply that
  re-fires the same job without re-asking any questions.
- Session not found (expired / server restarted — no TTL needed given
  one-shot scope) → frontend clears `sessionStorage` and restarts fresh.

## Migration / Removed Code

- `frontend/src/lib/planContext.tsx` — deleted; field list becomes the
  backend `TripState` schema.
- `frontend/src/pages/Plan.tsx`, `StepIndicator.tsx` — deleted; replaced by
  the chat panel living in `Landing.tsx`.
- `TripDetailsStep.tsx`, `PreferencesStep.tsx` — deleted; fields ported into
  the Python question checklist; their input components (`PillInput`,
  `Select`, `PillRadioGroup`, `InterestPicker`, `ProgressBar`) are reused
  inside chat bubbles/quick-replies.
- `ResultsStep.tsx` — kept, adapted into `ItineraryBubble` (same logic,
  embedded instead of standalone).
- `backend/main.py` — existing cost-estimate/itinerary/pdf endpoints and job
  pattern kept as-is; new `/api/chat/*` endpoints and `ChatSession` store
  added alongside.
- `backend/prompts.py` — `get_prompt_cost`, `get_prompt_preference` unchanged;
  new `get_prompt_chat_turn` added.
- `OPENROUTER_MODEL` becomes env-configurable.

## Open Questions Resolved During Brainstorming

1. Scope: chat replaces the form **and** the results page — itinerary is
   delivered inline in the thread.
2. Cost-estimate grounding auto-fires once trip basics (destination, days,
   month, budget) are known, running in the background while the
   conversation continues.
3. Required fields: destination, days, month, budget, interests, companions
   (+ child ages), pace. Everything else is optional, asked once, defaulted.
4. Quick replies: buttons + always-live text input; typing overrides buttons.
5. Conversation state lives server-side in a session store, not resent by
   the frontend each turn.
6. The hero textarea is a real input and seeds the first chat message.
7. Model reliability: keep the free-tier model, make it env-configurable,
   mitigate with deterministic Python-side flow control instead of trusting
   LLM judgment for "ready to generate."
8. Hero → chat transition: shared-element (FLIP) animation, same page/route,
   per the interaction spec above.
