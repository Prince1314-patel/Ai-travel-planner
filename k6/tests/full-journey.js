// Full-journey test: walks the *entire* real user path — chat → pricing job
// (OpenRouter + Tavily) → itinerary job (OpenRouter) → PDF export (wkhtmltopdf)
// — the same way the frontend does it.
//
// Unlike the other scripts, this one is NOT free to run: it makes real calls
// to OpenRouter and Tavily against whatever backend BASE_URL points at, so it
// costs API quota/money and is subject to those providers' rate limits. It is
// meant to answer "does the whole flow hold up end-to-end?", not "how many
// requests/sec can we serve?" — keep VUS/ITERATIONS low.
//
// Requires explicit opt-in so it's never run by accident:
//
//   k6 run -e CONFIRM_LLM_COST=1 k6/tests/full-journey.js
//   k6 run -e CONFIRM_LLM_COST=1 -e BASE_URL=... -e VUS=3 -e ITERATIONS=3 k6/tests/full-journey.js

import http from 'k6/http';
import { check, sleep, fail } from 'k6';
import { BASE_URL, jsonHeaders } from '../lib/config.js';
import { startSession, setField, getSession } from '../lib/chatFlow.js';

const vus = Number(__ENV.VUS || 1);
const iterations = Number(__ENV.ITERATIONS || 2);

export const options = {
  scenarios: {
    full_journey: {
      executor: 'per-vu-iterations',
      vus,
      iterations,
      maxDuration: '15m', // LLM + search + PDF generation per iteration is slow
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.2'],
  },
};

export function setup() {
  if (__ENV.CONFIRM_LLM_COST !== '1') {
    fail(
      'full-journey.js makes real OpenRouter/Tavily calls and costs API quota. ' +
        'Re-run with -e CONFIRM_LLM_COST=1 to confirm you mean to do that.',
    );
  }
}

function pollUntilDone(url, label, maxAttempts, intervalSeconds) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const res = http.get(url);
    check(res, { [`${label} status 200`]: (r) => r.status === 200 });
    const status = res.json('status');
    if (status === 'done' || status === 'error') {
      return res;
    }
    sleep(intervalSeconds);
  }
  console.warn(`${label} did not finish within ${maxAttempts * intervalSeconds}s`);
  return null;
}

export default function () {
  const sessionId = startSession();

  // Required fields, in an order that avoids "Family" (which would add a
  // child_ages follow-up) and stops short of pricing inputs until the last
  // of the four is set.
  setField(sessionId, 'destination', 'Goa');
  setField(sessionId, 'num_days', 5);
  setField(sessionId, 'travel_month', 'December');
  setField(sessionId, 'total_budget', 50000); // completes pricing inputs -> kicks off cost-estimate job
  setField(sessionId, 'interests', [
    { interest: 'Beaches', rating: 5 },
    { interest: 'Food', rating: 4 },
  ]);
  setField(sessionId, 'companions', 'Solo');
  const paceRes = setField(sessionId, 'pace', 'Moderate'); // completes checklist -> phase becomes optional_wrapup

  check(paceRes, {
    'reached optional_wrapup phase': (r) => r.json('phase') === 'optional_wrapup',
  });

  const wrapupRes = setField(sessionId, 'wrapup_submit', {});
  const itineraryJobId = wrapupRes.json('itinerary_job_id');
  check(wrapupRes, { 'itinerary job started': () => !!itineraryJobId });

  const session = getSession(sessionId);
  const pricingJobId = session.json('pricing_job_id');

  if (pricingJobId) {
    pollUntilDone(`${BASE_URL}/api/cost-estimate/status/${pricingJobId}`, 'pricing job', 30, 3);
  }

  if (!itineraryJobId) {
    return;
  }

  const itineraryStatus = pollUntilDone(
    `${BASE_URL}/api/itinerary/status/${itineraryJobId}`,
    'itinerary job',
    60,
    5,
  );

  const itineraryMarkdown = itineraryStatus && itineraryStatus.json('result.itinerary');
  if (!itineraryMarkdown) {
    console.warn('itinerary job did not produce a result; skipping PDF export');
    return;
  }

  const pdfRes = http.post(
    `${BASE_URL}/api/itinerary/pdf`,
    JSON.stringify({ itinerary_markdown: itineraryMarkdown }),
    jsonHeaders(),
  );
  check(pdfRes, {
    'pdf export status 200': (r) => r.status === 200,
    'pdf export returned bytes': (r) => r.body && r.body.length > 0,
  });
}
