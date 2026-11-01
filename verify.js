#!/usr/bin/env node
// Verify a BetsBeats sealed pick. No dependencies. Usage: node verify.js <hash-or-prefix>
const { createHash } = require('node:crypto');

const hash = (process.argv[2] || '').trim().toLowerCase();
const api = process.env.BETSBEATS_API || 'https://api.betsbeats.com';

if (!/^[0-9a-f]{16,64}$/.test(hash)) {
  console.error('usage: node verify.js <sha256 hash, or a prefix of 16+ hex characters>');
  process.exit(2);
}

(async () => {
  const res = await fetch(`${api}/api/v1/public/seal/${hash}`);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    console.error(body.message || `HTTP ${res.status}`);
    process.exit(1);
  }
  const d = body.data;
  console.log(`hash      ${d.commit_hash}`);
  console.log(`sealed at ${d.committed_at}   kickoff ${d.kickoff_at}`);
  if (!d.revealed) {
    console.log('Not revealed yet: the selection stays sealed until the pick settles.');
    return;
  }
  const recomputed = createHash('sha256').update(d.commit_payload).digest('hex');
  console.log(`preimage  ${d.commit_payload}`);
  console.log(`sha256    ${recomputed}`);
  console.log(`result    ${d.status}${d.final_score ? ` (${d.final_score})` : ''}`);
  const ok = recomputed === d.commit_hash;
  console.log(ok ? 'MATCH: the preimage hashes to the sealed hash.' : 'MISMATCH: do not trust this record.');
  process.exit(ok ? 0 : 1);
})().catch((e) => { console.error(e.message); process.exit(1); });
