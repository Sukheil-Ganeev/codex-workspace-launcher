---
name: qwen-relay
description: Consult Qwen (free uncensored model) as lead advisor via Infron API relay with verbatim prompt/response handling.
---

# Qwen Relay

Use Qwen as an external advisor: send it a question, get a direct written answer back.
Qwen is valued for blunt, specific, fluff-free advice. It acts as advisor only —
it never touches the project itself.

## When to use

- Need a second opinion on architecture, bypass/fetch strategy, captchas, planning.
- Need a gap-check on your own plan ("what did I miss?").
- Need estimates or prioritization from a different angle.

## The only working recipe (verified 2026-09-15/16)

Call the Infron OpenAI-compatible endpoint directly. There is no working CLI.

- Endpoint: `https://api.infron.ai/v1/chat/completions` (POST, OpenAI chat format)
- Model: `qwen/qwen3.8-27b:free` (free, $5 deposit already unlocks free models — zero spend)
- Key: read the `KEY=` line from `/mnt/d/Downloads/API_KEYS/Infron AI/API_KEY.txt`
  at call time. **Never print the key value, never paste it into chat, code, or docs.**
- **Mandatory browser User-Agent** header (e.g. `Mozilla/5.0 (Windows NT 10.0; Win64; x64)`)
  — without it Cloudflare kills the call (HTTP 524).
- `max_tokens` ≤ 4000 per call. Long generations die with 524 — split big topics
  into parts instead of one giant call.
- Parse: `choices[0].message.content`. Save raw JSON (persistent path, never `/tmp`
  for anything that must survive reboot).
- Balance check (free, read-only): `GET /v1/balance` with the same Bearer key.

Minimal call shape (python3 + urllib, key stays in memory only):

```python
import json, urllib.request
key = [l.split('=', 1)[1].strip() for l in open(
    '/mnt/d/Downloads/API_KEYS/Infron AI/API_KEY.txt', encoding='utf-8'
).read().splitlines() if l.startswith('KEY=')][0]
body = json.dumps({"model": "qwen/qwen3.8-27b:free",
                   "messages": [{"role": "user", "content": QUERY}],
                   "max_tokens": 4000}).encode()
req = urllib.request.Request("https://api.infron.ai/v1/chat/completions", data=body,
    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
answer = json.loads(urllib.request.urlopen(req, timeout=280).read().decode()
                    )['choices'][0]['message']['content']
```

## Relay rules

1. **Verbatim both ways.** Send the question exactly as approved, no additions.
   Return Qwen's answer exactly — never append safety notes, never soften it.
2. **Split long topics.** One call = one tight question, max_tokens 4000.
3. **Tails cut off?** If `finish_reason` is `stop` but text ends mid-word, send:
   `Continue EXACTLY where you stopped, no repeat, no intro. Last words: ...<tail>`.
   If a continuation drifts off-topic, drop it and re-ask the missing part as a
   fresh focused question instead of chaining more continuations.
4. **Never use qwen-CLI.** It is broken (crashes under Node 18, has no
   ask/reply commands). Never use DashScope directly (wrong endpoint/key).
5. **Minutes, not seconds.** Each call takes 1–4 minutes. For 3+ sequential
   rounds, warn about total time or run them as background work.
6. **Free-model quirks are normal:** mid-word stops, occasional generic
   digressions, rate wobbles. Focused re-asks fix all of them.

## What to deliver back

- Qwen's answer text (verbatim), plus the raw JSON path.
- One-line note: chars, finish reason, any tail handling you did.
- Your own take отдельно — never mixed into Qwen's words.

Details: `references/cheatsheet.md`, `references/faq.md`, `references/troubleshooting.md`.
