# Meta Messenger Bot -- Experience Log

## 2026-02-27: VIP-DXB CatalogBot -- Facebook Messenger Bot (Phase 20)

### Context
Built a production Facebook Messenger bot for a UAE tourism business (VIP-DXB CatalogBot). The bot is the 5th messaging platform added to the existing multi-platform architecture (Telegram + VK + Instagram DM + WhatsApp Cloud API).

### Project Stats
- **Files:** 13 new files in `facebook_bot/` (app, config, webhook_verify, meta_api, fsm, formatters, templates, handlers x4, __init__ x2)
- **Lines of code:** ~1,600 lines
- **Tests:** 148 new tests across 7 test files
- **DB table:** 1 (facebook_users with synthetic_user_id)
- **Total platforms:** Telegram, VK, Instagram, WhatsApp, Facebook -- shared SQLite DB (WAL)

### Top Lessons Learned

1. **messaging_type is MANDATORY for Facebook** -- every Send API call must include it. Instagram does NOT require it. Missing = 400 error. Default to "RESPONSE".

2. **Sender Actions dramatically improve UX** -- `mark_seen` on every incoming message + `typing_on` before processing. Instagram doesn't support this. Users feel the bot is "alive".

3. **Reuse webhook_verify.py from Instagram** -- same `META_APP_SECRET`, same HMAC-SHA256 algorithm, same `X-Hub-Signature-256` header. One-line import: `from instagram_bot.webhook_verify import verify_hmac`.

4. **PSID is Page-Scoped** -- same user has different PSIDs for different Pages. Never assume PSID == global user identity. Use synthetic_user_id for DB operations.

5. **Get Started requires explicit Messenger Profile API call** -- it does NOT appear automatically. Must POST to `/me/messenger_profile` with `{"get_started": {"payload": "GET_STARTED"}}`.

6. **User Profile API is a Facebook advantage** -- can get `first_name`, `last_name`, `profile_pic` by PSID. Instagram/WhatsApp don't expose this. Use it for personalized greetings.

7. **Synthetic user_id pattern scales well** -- negative IDs by platform (IG: -1..-999, WA: -1000..-1999, FB: -2000..-2999) let all platforms share booking/loyalty/analytics methods without changes.

8. **form_type prefix for analytics** -- `FB_GT` distinguishes Facebook bookings from `GT` (Telegram), `IG_GT` (Instagram), `WA_GT` (WhatsApp) in reports.

9. **In-memory FSM with 1h timeout is sufficient** -- no DB persistence needed. If process restarts, users tap Get Started. Memory usage trivial for typical volumes.

10. **Echo loop prevention** -- filter `sender.id == recipient.id` to avoid processing page's own messages.

### Architecture Decision: Separate FastAPI per Platform
- Each messenger platform runs as a separate FastAPI server on its own port (IG:8081, WA:8082, FB:8083)
- Shared SQLite DB with WAL mode for concurrent access
- Shared `bot/config.py` for common env vars, each bot re-exports + adds platform-specific vars
- Telegram manager notification via direct httpx POST (no aiogram dependency in webhook bots)
- Each bot has its own FSM manager (in-memory, platform-specific states)

### Gotchas Encountered
- Facebook webhook `object` is `"page"` (not `"instagram"`)
- Quick Reply title max 20 chars, button title max 20 chars
- Generic Template: title max 80 chars, subtitle max 80 chars
- Quick Replies max 13 buttons
- Generic Template max 10 elements (use 9+1 pagination pattern)
- `sender_action` does NOT need `messaging_type`
- Plain text only in Messenger (no HTML, no Markdown) -- use emoji for visual structure

### What Went Well
- Reusing patterns from Instagram and WhatsApp bots made implementation fast (~2 hours for full bot)
- Shared DB architecture with synthetic IDs required zero changes to core booking/loyalty logic
- Test infrastructure was trivially adapted from WhatsApp bot tests
- FastAPI + httpx + aiosqlite stack is production-proven across all 4 webhook-based bots

### What Could Be Improved
- Consider a shared base class for MetaAPI (Instagram, WhatsApp, Facebook share 80% of code)
- Unified FSM base class across platforms (only states differ)
- Auto-discovery of platform bots in `run_both.py` / `run_all.py`
