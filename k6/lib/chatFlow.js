import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, jsonHeaders } from './config.js';

// Drives the chat state machine via `structured_field`/`structured_value`,
// the same path the frontend uses for quick-reply fields. This bypasses the
// LLM extraction call entirely (see backend/main.py chat_message: a
// structured_field skips `_run_chat_turn_safely`), so it's safe to hammer
// with many VUs without burning OpenRouter quota.

export function startSession() {
  const res = http.post(`${BASE_URL}/api/chat/start`, JSON.stringify({}), jsonHeaders());
  check(res, {
    'chat/start status 200': (r) => r.status === 200,
    'chat/start has session_id': (r) => !!r.json('session_id'),
  });
  return res.json('session_id');
}

export function setField(sessionId, field, value) {
  const res = http.post(
    `${BASE_URL}/api/chat/${sessionId}/message`,
    JSON.stringify({ structured_field: field, structured_value: value }),
    jsonHeaders(),
  );
  check(res, { [`set ${field} status 200`]: (r) => r.status === 200 });
  return res;
}

export function getSession(sessionId) {
  const res = http.get(`${BASE_URL}/api/chat/${sessionId}`);
  check(res, { 'chat get status 200': (r) => r.status === 200 });
  return res;
}

// Fills the first three required fields only — deliberately stops short of
// `total_budget` so `has_pricing_inputs` never trips and no pricing job (and
// therefore no OpenRouter/Tavily call) gets kicked off. Good enough to
// exercise session creation and the in-memory store under concurrency.
export function safeChatFlow() {
  const sessionId = startSession();
  setField(sessionId, 'destination', 'Goa');
  setField(sessionId, 'num_days', 5);
  setField(sessionId, 'travel_month', 'December');
  getSession(sessionId);
  return sessionId;
}
