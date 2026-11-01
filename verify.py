#!/usr/bin/env python3
"""Verify a BetsBeats sealed pick. Standard library only.

Usage: python3 verify.py <sha256 hash, or a prefix of 16+ hex characters>
"""
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

h = (sys.argv[1] if len(sys.argv) > 1 else "").strip().lower()
api = os.environ.get("BETSBEATS_API", "https://api.betsbeats.com")

if not re.fullmatch(r"[0-9a-f]{16,64}", h):
    sys.exit("usage: python3 verify.py <sha256 hash, or a prefix of 16+ hex characters>")

try:
    req = urllib.request.Request(f"{api}/api/v1/public/seal/{h}", headers={"Accept": "application/json", "User-Agent": "seal-verify/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)["data"]
except urllib.error.HTTPError as e:
    msg = json.loads(e.read() or b"{}").get("message", f"HTTP {e.code}")
    sys.exit(msg)

print(f"hash      {d['commit_hash']}")
print(f"sealed at {d['committed_at']}   kickoff {d['kickoff_at']}")
if not d["revealed"]:
    sys.exit("Not revealed yet: the selection stays sealed until the pick settles.")

recomputed = hashlib.sha256(d["commit_payload"].encode("utf-8")).hexdigest()
print(f"preimage  {d['commit_payload']}")
print(f"sha256    {recomputed}")
print(f"result    {d['status']}" + (f" ({d['final_score']})" if d.get("final_score") else ""))
ok = recomputed == d["commit_hash"]
print("MATCH: the preimage hashes to the sealed hash." if ok else "MISMATCH: do not trust this record.")
sys.exit(0 if ok else 1)
