# k6 load/stress tests

Tests the `backend/` FastAPI service (`wandor-backend`). Two kinds of scripts:

- **`tests/smoke.js`, `tests/load.js`, `tests/stress.js`, `tests/spike.js`** — hit only the
  chat-session endpoints (`/api/chat/start`, `/api/chat/{id}/message`, `/api/chat/{id}`) using
  `structured_field` values and deliberately stop short of `total_budget`, so they never trigger
  a pricing/itinerary job and never call OpenRouter or Tavily. Free to run as often as you like —
  these measure the app's own request handling, not a third-party LLM's latency.
- **`tests/full-journey.js`** — walks the entire real flow (chat → pricing job → itinerary job →
  PDF), including real OpenRouter and Tavily calls. Costs API quota and is rate-limited by those
  providers, so it's opt-in and meant to be run with very few VUs/iterations.

## Install k6

```bash
# macOS
brew install k6

# Linux (Debian/Ubuntu)
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6

# or download a static binary: https://k6.io/docs/get-started/installation/
```

## Run against local backend

```bash
cd backend && uvicorn main:app --port 8000   # in one terminal

k6 run k6/tests/smoke.js
k6 run k6/tests/load.js
k6 run k6/tests/stress.js
k6 run k6/tests/spike.js
```

## Run against a deployed backend

```bash
k6 run -e BASE_URL=https://wandor-backend.onrender.com k6/tests/load.js
```

Tune the shape of each test with env vars: `TARGET_VUS` (load.js), `PEAK_VUS` (stress.js),
`SPIKE_VUS` (spike.js).

## Full-journey (real LLM calls — costs quota)

```bash
k6 run -e CONFIRM_LLM_COST=1 -e VUS=2 -e ITERATIONS=2 k6/tests/full-journey.js
```

It refuses to run without `CONFIRM_LLM_COST=1`. Keep `VUS`/`ITERATIONS` small — each iteration
makes 2+ sequential LLM calls plus a web search and a PDF render, so it's slow and not meant to
generate volume.

## What to look at

k6's summary reports `http_req_duration` (p95/p99), `http_req_failed` rate, and iteration
throughput. Compare these across runs to answer the scaling questions from before: at what VU
count does p95 latency blow up or the error rate climb, and does that number change after you
change something on the backend?

## Known bottlenecks in this codebase worth stress-testing for

- **In-memory job/session stores** — `COST_ESTIMATE_JOBS`, `ITINERARY_JOBS`, and `CHAT_SESSIONS`
  in `backend/main.py`/`backend/chat.py` live in plain Python dicts in one process. They work
  fine for one `uvicorn` worker but break (404s on jobs/sessions created by a different worker)
  the moment you scale horizontally with multiple processes or workers, since nothing shares that
  state — a real backing store (Redis, etc.) is needed first.
- **Single uvicorn worker** — `backend/Dockerfile` starts `uvicorn` with no `--workers` flag, so
  the whole service runs on one process. `stress.js`/`spike.js` should surface this as latency
  climbing sharply well before CPU/memory limits are hit.
- **Background jobs are raw `threading.Thread`s** — no pool/queue/concurrency cap
  (`_run_cost_estimate_job`/`_run_itinerary_job`), so a burst of pricing/itinerary requests spawns
  a thread per request with no backpressure.
- **External dependencies on the critical path** — every pricing/itinerary request blocks on
  OpenRouter (and Tavily for pricing context), so under load the app's own capacity is often not
  the bottleneck — those providers' latency and rate limits are. `full-journey.js` is the one
  script that will actually exercise this.
- **PDF export shells out to `wkhtmltopdf`** — a subprocess per request; worth checking it doesn't
  become a bottleneck under concurrent PDF exports.
