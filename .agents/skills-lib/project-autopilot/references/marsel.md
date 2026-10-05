# Marsel project adapter

Project root: `/root/Данные-Марселя`. Read its `AGENTS.md`, `docs/strategy-v1/ACCEPTANCE.md` and latest workstream releases. `data/` is a read-only symlink to the working files; use `derived/` for outputs. Never mix Sukheil or Kamilya sources into this project.

Current deterministic controller: `python3 scripts/coordination/project-autopilot-v1/controller.py scan`, then `next` or `status`. Its SQLite backlog and status live under `derived/coordination/project-autopilot-v1/`. It observes exact full-text builder process handles and pinned project releases; it does not dispatch an AI or accept its output. Cross-check source hashes/quality reviews before acting on a proposed task.

Known source scope: C1/C3/C5 frame = 9,966,240 Business-source rows, not unique messages or proven business content; the full structural index has no text. Contact frame v1+v2 = 874,660 observations and 82,909 phone-HMAC keys, not people; structural graph has no role/person assertions. Existing Codex RAG works only on bounded Business candidates and independently grounded citations. Contact roles and seller policies remain candidates.

Use separate full-text, contact, role, seller and independent-quality workstreams. Reports should return to this Codex task through the verified `codex-report-delivery` queue when using external executors; ACK locally without report loops. This root has no Git repository, so use versioned releases and exact SHA receipts while Git/PR remains unavailable. Do not initialize a repo containing raw data merely to satisfy PR formatting.
