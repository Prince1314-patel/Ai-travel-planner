// Load test: ramps to an expected-normal-traffic level and holds it, to see
// how the backend behaves under realistic concurrent usage.
//
//   k6 run k6/tests/load.js
//   k6 run -e BASE_URL=... -e TARGET_VUS=50 k6/tests/load.js

import { sleep } from 'k6';
import { DEFAULT_THRESHOLDS } from '../lib/config.js';
import { safeChatFlow } from '../lib/chatFlow.js';

const targetVUs = Number(__ENV.TARGET_VUS || 20);

export const options = {
  stages: [
    { duration: '1m', target: targetVUs }, // ramp up
    { duration: '3m', target: targetVUs }, // hold
    { duration: '1m', target: 0 },          // ramp down
  ],
  thresholds: DEFAULT_THRESHOLDS,
};

export default function () {
  safeChatFlow();
  sleep(1);
}
