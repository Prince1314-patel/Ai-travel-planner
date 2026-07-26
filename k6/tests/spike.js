// Spike test: sudden burst of traffic (e.g. the app gets shared/goes viral)
// followed by an equally sudden drop, to check the backend survives the jump
// and recovers cleanly afterwards.
//
//   k6 run k6/tests/spike.js
//   k6 run -e BASE_URL=... -e SPIKE_VUS=200 k6/tests/spike.js

import { sleep } from 'k6';
import { safeChatFlow } from '../lib/chatFlow.js';

const spikeVUs = Number(__ENV.SPIKE_VUS || 200);

export const options = {
  stages: [
    { duration: '30s', target: 10 },        // baseline
    { duration: '20s', target: spikeVUs },  // sudden spike
    { duration: '1m', target: spikeVUs },   // hold the spike
    { duration: '20s', target: 10 },        // sudden drop
    { duration: '1m', target: 10 },         // recovery — should look like baseline again
    { duration: '20s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.5'],
  },
};

export default function () {
  safeChatFlow();
  sleep(0.5);
}
