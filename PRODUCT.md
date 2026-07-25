# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

General global leisure travelers planning a personal trip — solo, as a couple, with family (including children), or in a group. They arrive with a destination and rough trip window already in mind and want a day-by-day plan that actually fits their budget and taste, without doing the manual research themselves. Budget is entered and displayed in INR; a full itinerary is priced end-to-end (accommodation, transport, dining) regardless of the traveler's home currency or nationality, which is captured only for visa-consideration context (defaults to "Indian" but is editable).

## Product Purpose

Generates a personalized, day-by-day travel itinerary from a destination, trip length, travel month, and total budget, then lets the traveler download it as a PDF. Success is a plan the traveler finds specific and usable enough to act on (or adjust) rather than a generic template — it should read as built for their trip, not a form-letter itinerary.

## Positioning

Its edge is personalization depth, not just budget math. It takes a wide, structured set of preference inputs — per-interest importance ratings (not just tag selection), travel pace, companion type (with child ages for families), accommodation/transport/dining style, dietary restrictions, accessibility needs, nationality (for visa awareness), and freeform special requests — and folds all of it into the itinerary prompt. A generic "AI itinerary generator" clone that just takes destination + dates + one interest tag would miss this: the itinerary is meant to feel shaped by the specific traveler, not swapped-in city facts on a fixed template.

## Operating Context

Two-step flow in a single Streamlit page:

1. **Trip Details + Budget** — destination, number of days, travel month, total budget (INR). Once all four are filled, the app automatically calls the Groq API to generate structured cost estimates (accommodation/transportation/dining, each with a min–max range and unit) and stores them in session state.
2. **Preferences** — interests (multi-select with a 1–5 importance slider per interest), travel companions (Solo/Couple/Family/Group, with child ages for Family), accommodation/transportation/dining preference (populated dynamically from the Step 1 cost estimates when available, else static fallback options), pace of travel, special requests, dietary restrictions, accessibility needs, and nationality. Submitting calls the Groq API again to generate the full itinerary.

The itinerary renders as Markdown with a collapsible expander per day, and can be downloaded as a PDF (via `pdfkit`/`wkhtmltopdf`, styled with the Open Sans Google Font). A visible disclaimer warns the AI output may not reflect real-time availability or pricing.

## Capabilities and Constraints

- The app was rebuilt (2026) from a single Streamlit script into two services: a React/TypeScript/Vite frontend (`frontend/`) and a FastAPI backend (`backend/`). See `DESIGN.md` for the visual system.
- Backend LLM provider is OpenRouter, model `inclusionai/ling-3.0-flash:free` — two calls per session (cost estimate, itinerary), both driven by prompt templates in `backend/prompts.py`. This is a free-tier model; if generation quality or reliability (especially strict-JSON cost estimates) becomes a problem, revisit the model choice.
- The cost-estimate call is grounded with live web search (Tavily, `backend/search.py`) — 13 queries, one per accommodation/dining/transportation sub-type (Hotel, Hostel, Vacation rental... Taxi, Public transit, Car rental), all fired concurrently. The model is instructed to use each real result directly rather than extrapolate from a single category anchor. Fails open per sub-type: any individual search failure (or a missing key) just means that one line item falls back to LLM reasoning instead of breaking the whole estimate. The itinerary call (day-by-day activities) is not grounded — that would need per-activity search, a larger scope than the cost estimate.
- Real grounding is genuinely slow and highly variable (observed 18s–130s+ for the same call, depending on Tavily's response time) — user explicitly chose full accuracy over speed. To keep that honest, the cost-estimate flow runs as a backend job (`POST /api/cost-estimate/start` + `GET /api/cost-estimate/status/{job_id}` polling) instead of one blocking call, and the LLM response itself streams (SSE) so the frontend can show real "N of 13 sources checked" and real generated-character progress rather than a spinner or any simulated animation — see DESIGN.md's Loading/Progress component and its Real-Progress Rule.
- Currency is INR-only; no multi-currency support exists today.
- PDF export depends on `wkhtmltopdf` (see `backend/requirements.txt`) via `pdfkit`.
- No user accounts, saved trips, or history — each planning session is one-shot with no persistence across visits.
- No real-time booking or availability data (can't reserve anything) — cost estimates are now web-grounded, but the itinerary's day-by-day suggestions remain AI-generated only, and the app explicitly warns of this.
- **Known issue, not yet resolved by the user:** the old `.streamlit/secrets.toml`, which contained a live Groq API key, was untracked from git during the rebuild — but it's still in this repo's git history on the public GitHub repo (`Prince1314-patel/Ai-travel-planner`) until that key is rotated and/or history is rewritten. Noted here so it isn't lost.

## Evidence on Hand

None. No testimonials, usage data, case studies, or press exist for this project — it is a solo/small project, not a funded product with proof points. Future design and copy work must not fabricate any of this (no invented reviews, user counts, partner logos, or "trusted by" claims).

## Product Principles

1. **Budget is a first-class input, not an afterthought** — cost estimation happens before itinerary generation and grounds every subsequent recommendation.
2. **Personalization comes from breadth of real inputs, not surface theming** — ratings, companions, pace, dietary/accessibility needs, and freeform requests all feed the prompt; the interface should keep making this depth easy to provide, not hide it behind generic tag pickers.
3. **Never imply certainty the AI can't back** — the app is upfront that output is AI-estimated, not live/bookable data; design should preserve that honesty rather than dress up estimates as guarantees.
4. **No fabricated proof or content** — every claim, number, and testimonial-shaped element in the UI must trace to something real; absence of evidence is stated, never papered over.
5. **One-shot, low-friction flow** — no accounts or saved state today; the two-step form should stay fast to complete rather than assume a returning, logged-in user.

## Accessibility & Inclusion

The form itself already asks travelers for accessibility needs (e.g. wheelchair access) as an itinerary input. No formal accessibility standard has been confirmed as a requirement for the UI itself yet — treat as an open decision for future work rather than an established constraint.
