// Smoke test: minimal load, just confirms the deployed backend is up and
// the chat-session endpoints behave correctly before running anything bigger.
//
//   k6 run k6/tests/smoke.js
//   k6 run -e BASE_URL=https://wandor-backend.onrender.com k6/tests/smoke.js

import { sleep } from 'k6';
import { DEFAULT_THRESHOLDS } from '../lib/config.js';
import { safeChatFlow } from '../lib/chatFlow.js';

export const options = {
  vus: 2,
  duration: '30s',
  thresholds: DEFAULT_THRESHOLDS,
};

export default function () {
  safeChatFlow();
  sleep(1);
}
