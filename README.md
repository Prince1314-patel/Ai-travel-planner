# Wandor — AI Travel Planner

An AI-powered trip planner: describe (or fill in) a destination, days, month, and
budget, and Wandor estimates costs, then generates a personalized day-by-day
itinerary — downloadable as a PDF.

Two services:

- **`frontend/`** — React + TypeScript + Vite + Tailwind CSS. The Wandor landing
  page and the trip-planning flow (details → preferences → itinerary).
- **`backend/`** — FastAPI. Proxies the two LLM calls (cost estimate, itinerary) to
  OpenRouter so the API key never reaches the browser, and generates the downloadable PDF.

See [`PRODUCT.md`](PRODUCT.md) for product context and [`DESIGN.md`](DESIGN.md) for
the visual system.

## Running locally

You need both services running at once.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # on Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `OPENROUTER_API_KEY`. PDF export additionally
requires [`wkhtmltopdf`](https://wkhtmltopdf.org/) installed on this machine.

```bash
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`, calling the backend at `http://localhost:8000`
by default (override with `VITE_API_BASE_URL`, see `.env.example`).

## Project structure

```
frontend/
  src/
    components/
      Hero.tsx              # landing hero
      planner/               # trip-details / preferences / results steps
      ui/                     # shared pill buttons, glass cards, fields
    pages/                    # Landing, Plan
    lib/                      # api client, plan state
backend/
  main.py                     # FastAPI app + endpoints
  prompts.py                  # Groq prompt templates
```

## Contributing

Contributions are welcome — fork the repository and open a pull request. For
larger changes, open an issue first to discuss the approach.
