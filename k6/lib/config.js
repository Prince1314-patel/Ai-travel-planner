// Shared config for all k6 scripts. Override via `-e KEY=value` or env vars.
export const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Cheap, deterministic thresholds shared by the traffic-shape scenarios
// (smoke/load/stress/spike). The full-journey test overrides these itself
// since LLM calls run on a completely different latency budget.
export const DEFAULT_THRESHOLDS = {
  http_req_failed: ['rate<0.01'],
  http_req_duration: ['p(95)<800'],
};

export function jsonHeaders() {
  return { headers: { 'Content-Type': 'application/json' } };
}
