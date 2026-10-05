# Code Review & Security Audit — Wave 1

**Reviewer:** Claude Opus 4.6 (without skill)
**Date:** 2026-03-14
**Scope:** I-81 (Payment methods), I-83 (Recently Viewed), I-86 (Combo links)

---

## Summary

All three changes are low-risk, well-implemented, and follow existing project patterns. No security vulnerabilities found. A few minor quality observations noted below.

**Verdict: PASS** — safe to commit and deploy.

---

## I-81: Payment Methods (StickyCTA.tsx)

### Change Description
- Payment pill text expanded: "Наличные" -> "Наличные (AED, USD, EUR)", etc.
- `flexWrap` changed from `"nowrap"` to `"wrap"` to accommodate longer text
- Crypto pill text restructured: bitcoin symbol moved outside the i18n ternary

### Security: CLEAN
- No user input involved; all text is hardcoded static content
- No XSS vectors — no dynamic HTML injection, no dynamic URLs
- WhatsApp link uses `encodeURIComponent()` on `whatsappText` prop — correct

### Code Quality

| # | Severity | Finding |
|---|----------|---------|
| 1 | **Low** | `whiteSpace: "nowrap"` on individual pills + `flexWrap: "wrap"` on container = correct approach. Pills stay on one line internally but wrap to next row. Good. |
| 2 | **Low** | Three payment pill `<span>` elements share identical styles (padding, border, borderRadius, fontSize, color, whiteSpace). Consider extracting to a shared style object or a small `PaymentPill` component to reduce duplication (~18 lines of repeated inline styles). Not blocking. |
| 3 | **Info** | The bitcoin symbol is now outside the i18n ternary: `B {lang === "RU" ? "Крипто" : "Crypto"} (USDT)`. This is fine — the bitcoin symbol is universal and doesn't need translation. |
| 4 | **Info** | Emoji characters are used in payment pills. These render inconsistently across platforms/browsers. Consider using SVG icons for consistency with the rest of the component (which uses inline SVGs for WhatsApp, Telegram, shield icons). Not blocking — current approach works. |

### Potential Bugs: NONE

---

## I-83: Recently Viewed — 14 Client Pages

### Change Description
- 14 `*Client.tsx` files each received:
  1. `import { useEffect } from "react"` (or added `useEffect` to existing import)
  2. `import { addToRecentlyViewed } from "@/components/RecentlyViewed"`
  3. A `useEffect` call: `if (item) addToRecentlyViewed(slug, "/category-path")`

### Files Modified
1. ExcursionClient.tsx (`/excursions`)
2. TicketClient.tsx (`/tickets`)
3. YachtClient.tsx (`/yachts`)
4. TransferClient.tsx (`/transfers`)
5. RestaurantClient.tsx (`/restaurants`)
6. HotelClient.tsx (`/hotels`)
7. CarRentalClient.tsx (`/car-rentals`)
8. BeachClubClient.tsx (`/beach-clubs`)
9. PoolClient.tsx (`/pools`)
10. WaterActivityClient.tsx (`/water-activities`)
11. BuggyClient.tsx (`/buggies`)
12. ComboClient.tsx (`/combos`)
13. ServiceClient.tsx (`/services`)
14. FlightDestinationClient.tsx (`/flights`)

### Security: CLEAN
- `addToRecentlyViewed` writes to `localStorage` only — no server communication, no cookies, no network requests
- Data stored: `{ slug, categoryPath, timestamp }` — no PII, no sensitive data
- `slug` comes from URL params but is validated against the data array (e.g., `buggies.find(b => b.slug === slug)`) before being passed to `addToRecentlyViewed` — the `if (item)` guard ensures only valid, known slugs are stored
- `JSON.parse` in `addToRecentlyViewed` is wrapped in try/catch — handles corrupted localStorage gracefully
- MAX_ITEMS = 8 cap prevents unbounded localStorage growth

### Code Quality

| # | Severity | Finding |
|---|----------|---------|
| 1 | **Low** | The `useEffect` dependency array includes the found object (e.g., `[slug, buggy]`). Since `buggy` is derived from `buggies.find()` during render, it will be a stable reference (same object from the static data array) as long as `slug` doesn't change. This means the effect won't re-fire unnecessarily. Correct. |
| 2 | **Low** | The `addToRecentlyViewed` function accesses `localStorage` directly without checking `typeof window !== "undefined"`. However, since it's always called inside a `useEffect` (which only runs client-side in React), this is safe. The try/catch also handles SSR edge cases. Acceptable. |
| 3 | **Info** | Pattern is consistent across all 14 files — identical structure, same import path, same guard pattern. Good consistency. |
| 4 | **Info** | `TicketClient.tsx` already had `useState` imported; `useEffect` was correctly added to the same import statement (`import { useState, useEffect }`). No duplicate imports. |
| 5 | **Low** | The `useRecentlyViewed` hook in `RecentlyViewed.tsx` reads from localStorage only once on mount (empty dependency array `[]`). This means if a user opens multiple service pages in new tabs, the RecentlyViewed section on the homepage won't update until a full page reload. This is acceptable for the current UX but worth noting. A `storage` event listener could sync across tabs. Not blocking. |

### Potential Bugs: NONE

---

## I-86: Combo Links (RelatedServices.tsx)

### Change Description
- CTA button changed from `<a href={whatsappUrl(waText)}>` (WhatsApp link) to `<Link href={...}>` (internal navigation to partner service page)
- Old WhatsApp code preserved as `// BACKUP:` comments (3 blocks)
- Import of `whatsappUrl` removed (kept as backup comment), `Link` from `next/link` added
- Several UI enhancements also present: swipe cue, scroll fade gradient, ref-based scroll detection

### Security: CLEAN
- Link `href` is constructed as `${partner.categoryPath}/${partner.slug}` — both values come from the static `searchItems` array (compile-time data), not user input
- `partner.categoryPath` values are hardcoded paths like `/excursions`, `/tickets`, etc. — no injection possible
- Removed the external `target="_blank"` link (WhatsApp) — the new internal `<Link>` is actually safer (no need for `rel="noopener noreferrer"`)
- No dynamic HTML injection anywhere in the component

### Code Quality

| # | Severity | Finding |
|---|----------|---------|
| 1 | **Medium** | `currentName` variable (lines 47-49) is now commented out as backup but `currentItem` (line 45) is still computed and used only for `totalSeparate` calculation (line 158-160). This is fine — `currentItem` serves a real purpose. |
| 2 | **Low** | Three `// BACKUP:` comment blocks (lines 10-11, 46-49, 151-155, 277-299) are retained. These are intentional per I-86 ("reverted by owner request"). Per project Dormant Code Policy, this is correct — commented code with context is explicitly allowed. |
| 3 | **Low** | The `<Link>` component (line 258) does not have `prefetch={false}`. Next.js will prefetch these routes when the link is in viewport. For combo cards in a scrollable container, this means potentially prefetching multiple service pages. This is actually beneficial for UX (instant navigation) but could increase bandwidth slightly. Not a problem. |
| 4 | **Info** | The indentation inside the `.map()` callback is mixed (2-space and 4-space at different levels, e.g., lines 145-162 vs 163-301). This is cosmetic and doesn't affect functionality, but could cause confusion in future diffs. |
| 5 | **Info** | `serviceBundles` is derived on every render via `getBundlesForService(currentSlug)`. Since `currentSlug` is a prop and the bundles data is static, this is fine and doesn't need memoization. |

### Potential Bugs

| # | Severity | Finding |
|---|----------|---------|
| 1 | **Low** | The `showSwipeCue` state initializer (`useState(serviceBundles.length > 1)`) and the corresponding `useEffect` both depend on `serviceBundles.length`. The useEffect (line 25-27) re-syncs when `currentSlug` changes, which handles the case where the component stays mounted but the slug changes (SPA navigation). This is correct. |

---

## Cross-Cutting Concerns

### localStorage Usage (I-83)
- **Storage key:** `vipdxbrus_recently_viewed` — namespaced, no collision risk
- **Data volume:** Max 8 items * ~80 bytes = ~640 bytes. Negligible
- **Privacy:** No PII stored (only slugs, category paths, timestamps)
- **GDPR:** localStorage for functional purposes (not tracking/analytics) — this is "strictly necessary" storage and does not require cookie consent under GDPR. However, since the site already has a CookieConsent component, consider documenting this localStorage usage in the privacy policy. Not blocking.

### Performance Impact
- **I-81:** Zero performance impact (text-only change)
- **I-83:** Each page load adds one `localStorage.getItem` + `JSON.parse` + `setItem` + `JSON.stringify` call. With 8 items max, this is microseconds. No measurable impact.
- **I-86:** Switching from external `<a>` to internal `<Link>` enables Next.js prefetching, which is a net UX improvement (faster navigation).

### Accessibility
- **I-81:** Payment text is plain text in `<span>` elements — screen-reader accessible
- **I-83:** No visible UI changes (the RecentlyViewed component was already built). The useEffect only writes to localStorage — no a11y impact
- **I-86:** `<Link>` from Next.js handles keyboard navigation and focus correctly. The removed `target="_blank"` is actually better for a11y (no unexpected new window)

---

## Recommendations (Non-Blocking)

1. **Extract PaymentPill component** (I-81) — reduce ~18 lines of duplicated inline styles per pill. Low priority.
2. **Consider `storage` event listener** (I-83) — for cross-tab sync of recently viewed items. Low priority, nice-to-have.
3. **Clean up indentation** in RelatedServices.tsx (I-86) — mixed 2/4-space indentation inside `.map()` callback. Cosmetic only.
4. **Document localStorage keys** — the project now uses `vipdxbrus_recently_viewed`, `vipdxbrus_popup_shown`, and `vipdxbrus_favorites`. Consider listing all localStorage keys in one place (e.g., constants.ts or a dedicated file) for maintainability.

---

## Final Verdict

| Change | Security | Quality | Bugs | Verdict |
|--------|----------|---------|------|---------|
| I-81 Payment Methods | CLEAN | Good | None | **PASS** |
| I-83 Recently Viewed | CLEAN | Good | None | **PASS** |
| I-86 Combo Links | CLEAN | Good | None | **PASS** |

**All three changes are safe to commit and deploy.**
