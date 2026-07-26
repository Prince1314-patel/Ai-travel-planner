// Stress test: pushes well past expected normal load to find where the
// backend starts erroring or degrading. Thresholds are intentionally looser
// than load.js — the goal here is to *observe* the breaking point, not pass
// cleanly, so aborting early on a strict threshold would defeat the point.
//
//   k6 run k6/tests/stress.js
//   k6 run -e BASE_URL=... -e PEAK_VUS=300 k6/tests/stress.js

import { sleep } from 'k6';
import { safeChatFlow } from '../lib/chatFlow.js';

const peakVUs = Number(__ENV.PEAK_VUS || 150);

export const options = {
  stages: [
    { duration: '2m', target: Math.round(peakVUs * 0.33) },
    { duration: '2m', target: Math.round(peakVUs * 0.66) },
    { duration: '2m', target: peakVUs },
    { duration: '3m', target: peakVUs }, // hold at peak to see sustained behavior
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    // Loose ceiling — flags a genuine collapse (near-total failure) without
    // failing the run just because degradation started, which is expected.
    http_req_failed: ['rate<0.5'],
  },
};

export default function () {
  safeChatFlow();
  sleep(0.5);
}
