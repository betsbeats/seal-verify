# seal-verify

Check a [BetsBeats](https://betsbeats.com) pick yourself. No dependencies, no account, no trust required.

BetsBeats publishes a SHA-256 hash of each pick before kick-off (the seal). After the pick settles it publishes the exact string that was hashed. If `sha256(string) == hash`, the pick could not have been changed after the seal. Win or lose, the record is the same one.

**21+ only. Entertainment and analysis; no wins are promised. BetsBeats does not take bets.**

## Use

```bash
node verify.js <hash>          # Node 18+
python3 verify.py <hash>       # Python 3, standard library only
```

`<hash>` is the full 64-character hash or a unique prefix of 16 or more characters. Both scripts call `GET https://api.betsbeats.com/api/v1/public/seal/{hash}`, then recompute SHA-256 locally. Exit code 0 means match.

Before a pick settles the endpoint returns only the hash, `committed_at` and `kickoff_at`. The selection and salt are revealed after settlement. That is the point: the salt stops anyone guessing the pick from the hash.

## Exact preimage format

Fields are joined with `|` and hashed as UTF-8:

**commit_version 2** (current)
```
date | teams | market | selection | line | odds | min_odds | kickoff | salt
```

**commit_version 1** (older picks; no selection or line)
```
date | teams | market | odds | min_odds | kickoff | salt
```

- `date`: the pick day, `YYYY-MM-DD`.
- `teams`: as published, with an em dash between clubs (`Home — Away`).
- `selection`: the side, including the line (`Northwestern Wildcats +5.5`).
- `line`: two decimals (`5.50`), or empty when the market has no line.
- `odds`, `min_odds`: two decimals in the format the pick was published in (`-129.00`, `1.90`).
- `kickoff`: ISO 8601 with offset (`2026-10-31T19:30:00+00:00`).
- `salt`: 64 random characters, secret until reveal.

The API also returns the finished string as `commit_payload`, so verification is one line in any language: `sha256(commit_payload) == commit_hash`. Rebuilding it yourself from the separate fields is a good second check.

## Worked example

A real settled pick from https://betsbeats.com/results (a loss, shown on purpose):

```
hash     93c087c1418ff2cf86be7b503e04786c10811971e5bcb169659b2933483e369a
preimage 2026-10-31|Northwestern Wildcats — Oregon Ducks|spread|Northwestern Wildcats +5.5|5.50|-129.00|-129.00|2026-10-31T19:30:00+00:00|LxlEkc0mgt3FBEbmba6ZerObF5sgK1E0I6Pa6BwRJIV0vssAKXiG2TRbhyM9Lzgt
```

```bash
printf '%s' '2026-10-31|Northwestern Wildcats — Oregon Ducks|spread|Northwestern Wildcats +5.5|5.50|-129.00|-129.00|2026-10-31T19:30:00+00:00|LxlEkc0mgt3FBEbmba6ZerObF5sgK1E0I6Pa6BwRJIV0vssAKXiG2TRbhyM9Lzgt' | shasum -a 256
# 93c087c1418ff2cf86be7b503e04786c10811971e5bcb169659b2933483e369a
```

Or `node verify.js 93c087c1418ff2cf86be7b503e04786c10811971e5bcb169659b2933483e369a`.

## What a match proves, and what it does not

It proves the pick existed in this exact form at seal time and was not edited afterwards. It does not prove the pick was good, and a single hash cannot show the archive is complete; compare against the full list at https://betsbeats.com/results. Each hash is also timestamped by an independent authority (RFC 3161), linked from the seal response.

An AI assistant can do the same check through the [BetsBeats MCP server](https://github.com/betsbeats/betsbeats-mcp).

MIT licensed.
