# Integration Guardian — Security & Integration Review
## Wave 1: I-81, I-83, I-86

**Mode:** `audit` (OWASP Top 10 + hardcoded secrets + integration safety)
**Project:** vipdxbrus-website (Next.js 15 + TypeScript)
**Reviewer:** Integration Guardian skill
**Date:** 2026-03-14
**Scope:** 3 changes (I-81, I-83, I-86), ~17 files total

---

## Executive Summary

| Severity | Count | Details |
|----------|-------|---------|
| CRITICAL | 0 | No critical vulnerabilities found |
| HIGH | 0 | No high-severity issues found |
| MEDIUM | 1 | useEffect dependency warning (object reference) |
| LOW | 2 | Minor improvements suggested |
| INFO | 3 | Observations, no action required |

**Verdict: PASS** — All three changes are safe for production deployment.

---

## I-81: Payment Methods — Currency Detail in StickyCTA

**File:** `src/components/StickyCTA.tsx` (lines 422-469)

### Security Checklist

| Check | Status | Notes |
|-------|--------|-------|
| Hardcoded secrets | PASS | No API keys, tokens, or credentials in the file |
| XSS vulnerability | PASS | Payment pills use static text only (no user input) |
| Sensitive data exposure | PASS | Currency names (AED, USD, EUR, RUB, KZT, USDT) are public knowledge, not PII |
| OWASP A03 (Injection) | N/A | No database queries, no user input processing |
| OWASP A05 (Misconfiguration) | PASS | No security-relevant configuration |

### Currency Accuracy

| Payment Method | Currencies Listed | Correct? |
|----------------|-------------------|----------|
| Cash | AED, USD, EUR | YES — matches business profile |
| Transfers | RUB, KZT, AED, USD | YES — matches CLAUDE.md: "AED/USD/RUB/KZT" |
| Crypto | USDT | YES — matches business profile |

### Findings

**[INFO-01] Static text only — no injection risk**
The payment pills are hardcoded strings conditionally rendered by `lang` prop. No user input flows into these strings. The `lang` prop is typed as `"RU" | "EN"` (line 22), limiting its values. No sanitization needed.

**[INFO-02] WhatsApp link is properly encoded**
Line 46: `encodeURIComponent(whatsappText)` correctly encodes the WhatsApp pre-filled text. The `whatsappText` prop comes from the parent page's static data, not from URL params or user input.

**[LOW-01] Phone number consistency**
The WhatsApp number `971565906911` (line 46) matches the canonical `WA_NUMBER` in `src/lib/constants.ts`. However, it's constructed inline rather than imported from constants. This is acceptable since `StickyCTA` receives `whatsappText` as a prop and builds the link locally, but worth noting for future maintenance.

---

## I-83: Recently Viewed — Integration on 14 Pages

**Files:** 14 `*Client.tsx` files + `src/components/RecentlyViewed.tsx`

### Security Checklist

| Check | Status | Notes |
|-------|--------|-------|
| XSS via slug | PASS | Slug is validated against static data before use |
| localStorage injection | PASS | Data is JSON.parse'd in try/catch, no eval |
| Memory leak | PASS | useEffect cleanup not needed (synchronous call) |
| OWASP A03 (Injection) | PASS | No SQL, no dynamic HTML rendering of slug |
| Prototype pollution | PASS | JSON.parse of localStorage is safe (no object merge) |

### Detailed Analysis

#### XSS via slug — NOT VULNERABLE

The data flow is:

1. `slug` comes from Next.js route params (`page.tsx` line 42: `const { slug } = await params`)
2. Pages use `generateStaticParams()` (e.g., `excursions.map(item => ({ slug: item.slug }))`) — only pre-defined slugs are valid at build time
3. In `*Client.tsx`, the slug is validated against static data: `excursions.find(e => e.slug === slug)` — if no match, the component renders "Not Found"
4. `addToRecentlyViewed(slug, categoryPath)` only stores to localStorage if the item exists
5. In `RecentlyViewed.tsx` (line 73-78), stored items are resolved against `searchItems` — unknown slugs are silently dropped
6. The slug is never injected into raw HTML or similar unsafe patterns

**Conclusion:** Even if an attacker crafts a URL with a malicious slug, the `.find()` returns `undefined`, the "Not Found" page renders, and `addToRecentlyViewed` is never called.

#### useEffect Dependencies

All 14 files follow the same pattern:
```tsx
useEffect(() => {
  if (item) addToRecentlyViewed(slug, "/category");
}, [slug, item]);
```

**[MEDIUM-01] Object reference in useEffect dependency array**

In files where `item` is an object found via `.find()`, the dependency `item` (e.g., `excursion`, `ticket`, `yacht`) is a reference from a static array. Since the data arrays are module-level constants, the reference is stable between renders — the same object is returned every time for the same slug.

However, there is a subtle concern: if the data ever becomes dynamic (fetched from API), the object reference would change on every render, causing `addToRecentlyViewed` to fire repeatedly. Current risk is **zero** because all data is static, but for future-proofing:

**Recommendation:** Consider using `!!item` (boolean) instead of `item` in the dependency array, or moving the guard inside the effect with only `[slug]` as dependency. Example:
```tsx
useEffect(() => {
  const found = excursions.find(e => e.slug === slug);
  if (found) addToRecentlyViewed(slug, "/excursions");
}, [slug]);
```

This is a **code quality** recommendation, not a security issue.

#### localStorage Safety

`addToRecentlyViewed` (RecentlyViewed.tsx lines 28-39):
- Wrapped in `try/catch` — handles `localStorage` quota exceeded or unavailable (private browsing)
- `JSON.parse` of stored data — safe, no `eval`
- `MAX_ITEMS = 8` — prevents unbounded storage growth
- Duplicate prevention: `items.filter(i => i.slug !== slug)` before `unshift`
- No sensitive data stored (only slug strings and timestamps)

**[INFO-03] No PII in localStorage**
The recently viewed storage contains only `slug`, `categoryPath`, and `timestamp`. No user-identifiable information is persisted.

#### Memory Leak Analysis

`addToRecentlyViewed` is a synchronous function call (localStorage read/write). It does not:
- Create subscriptions
- Set intervals/timeouts
- Add event listeners
- Allocate persistent resources

Therefore, no cleanup function is needed in the useEffect. **No memory leak risk.**

---

## I-86: Combo CTA — WhatsApp to Service Page Link

**File:** `src/components/RelatedServices.tsx`

### Security Checklist

| Check | Status | Notes |
|-------|--------|-------|
| Broken links | PASS | Links are built from static search index data |
| Open redirect | PASS | Internal links only (no external URLs) |
| XSS via partner data | PASS | Data comes from static bundles/search-index |
| WhatsApp backup preserved | PASS | Commented out with clear `// BACKUP` markers |
| OWASP A01 (Broken Access) | N/A | No authentication involved |

### Detailed Analysis

#### Link Construction Safety

Line 258-259:
```tsx
<Link href={`${partner.categoryPath}/${partner.slug}`}>
```

- `partner` is resolved from `searchItems.find(s => s.slug === partnerSlug)` (line 146)
- `partnerSlug` comes from `getPartnerSlug(bundle, currentSlug)` which indexes into `bundle.slugs` — a hardcoded static array in `data/bundles.ts`
- `partner.categoryPath` is one of the hardcoded paths like `/excursions`, `/tickets`, etc. (from `search-index.ts` catalog array)
- `partner.slug` is from static data files

**No open redirect risk** — the `<Link>` component generates internal Next.js navigation. Even if somehow a malformed slug existed, it would navigate to a non-existent internal page (404), not an external site.

#### Null Safety

Line 147: `if (!partner) return null;` — correctly handles the case where a bundle references a slug that doesn't exist in the search index. This prevents rendering a card with undefined data.

#### Backup Preservation

The WhatsApp link code is properly preserved as comments:
- Line 10-11: Import backup comment
- Line 46-49: `currentName` variable backup
- Line 151-155: WhatsApp message text backup
- Line 277-299: Full `<a>` element backup

All marked with `// BACKUP: ... (reverted by owner request, I-86)` — clear provenance tracking.

**[LOW-02] Dead import comment**
Line 10-11 has a commented-out import of `whatsappUrl`. This is intentional dormant code per project policy (CLAUDE.md: Dormant Code Policy). No action needed, correctly preserved.

---

## Cross-Cutting Concerns

### Hardcoded Secrets Scan

| File | Finding |
|------|---------|
| `src/lib/constants.ts` | Contains phone number, email, Telegram username — **public contact info**, not secrets |
| `src/app/api/chat/route.ts` | API key via `process.env.ANTHROPIC_API_KEY` — **correctly uses env var** |
| `.gitignore` | `.env`, `.env.local`, `.env.*.local`, `.env.production` — **all excluded from git** |
| `StickyCTA.tsx` | No secrets |
| `RelatedServices.tsx` | No secrets |
| `RecentlyViewed.tsx` | No secrets |

**Result: PASS** — No hardcoded secrets found.

### OWASP Top 10 Relevance

| OWASP Category | Applicable? | Status |
|----------------|-------------|--------|
| A01 Broken Access Control | No | Static site, no auth on these components |
| A02 Cryptographic Failures | No | No encryption/hashing in changed code |
| A03 Injection | Yes (XSS) | PASS — no user input rendered unsafely |
| A04 Insecure Design | No | Standard React/Next.js patterns |
| A05 Security Misconfiguration | Partial | PASS — .env in .gitignore |
| A06 Vulnerable Components | No | No new dependencies added |
| A07 Auth Failures | No | No auth in scope |
| A08 Data Integrity | No | No serialization/deserialization of untrusted data |
| A09 Logging Failures | N/A | Client-side components, server logs not in scope |
| A10 SSRF | No | No server-side requests in changed code |

### Webhook / CI Relevance

These changes are purely client-side React components. No webhook endpoints, no CI pipeline changes, no dependency updates. Modes `webhook`, `deps`, and `ci` of Integration Guardian are **not applicable** to this wave.

---

## Summary of Findings

| ID | Severity | Component | Finding | Recommendation |
|----|----------|-----------|---------|----------------|
| MEDIUM-01 | MEDIUM | I-83 | Object reference in useEffect deps | Use `[slug]` only, move `.find()` inside effect |
| LOW-01 | LOW | I-81 | WA link built inline, not from constants import | Acceptable, note for maintenance |
| LOW-02 | LOW | I-86 | Commented import (dormant code) | Correctly preserved per project policy |
| INFO-01 | INFO | I-81 | Payment pills are static text, no injection | No action |
| INFO-02 | INFO | I-81 | WhatsApp text properly encoded | No action |
| INFO-03 | INFO | I-83 | No PII in localStorage | No action |

---

## Verdict

**ALL THREE CHANGES ARE SAFE FOR PRODUCTION.**

- No security vulnerabilities found
- No hardcoded secrets
- No XSS vectors
- No memory leaks
- No broken links
- Currency information is accurate and matches business profile
- Backup code properly preserved with clear attribution
- useEffect patterns are functional (MEDIUM-01 is a code quality recommendation, not a blocker)
