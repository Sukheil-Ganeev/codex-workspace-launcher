# Code Review & Security Audit: Wave 2 Categories

**Reviewer:** Claude Opus 4.6 (without Integration Guardian skill)
**Date:** 2026-03-14
**Scope:** 20 new files + 5 modified files (spa, shopping, photoshoots, visas, apartments)

---

## Executive Summary

Overall quality: **GOOD** -- the 5 new categories follow the established project patterns closely and integrate correctly into the existing architecture. No critical security vulnerabilities found. A handful of minor inconsistencies and improvements are noted below.

**Verdict:** Safe to ship with the noted observations.

---

## 1. Security Analysis

### 1.1 XSS / Injection

| Check | Status | Notes |
|-------|--------|-------|
| User input rendering | PASS | All data is static (hardcoded in `.ts` data files). No user-supplied content is rendered unsafely. React auto-escapes all text content. |
| URL handling | PASS | All URLs are hardcoded strings (Unsplash CDN, WhatsApp deep links). No dynamic URL construction from user input. |
| WhatsApp text injection | PASS | `whatsappText` values are static strings, not user-generated. They are used in WhatsApp deep links which are URL-encoded by the browser. |
| Query parameter handling | PASS | Slugs come from `generateStaticParams()` which only returns known static values. The `params.slug` is used in `.find()` against a fixed array -- no SQL, no eval, no template interpolation. |
| Unsafe HTML rendering | PASS | No usage of unsafe innerHTML patterns anywhere in the 20 new files. All content rendered through JSX text nodes with automatic escaping. |

### 1.2 External Resources

| Check | Status | Notes |
|-------|--------|-------|
| Image origins | INFO | `spa.ts` and `photoshoots.ts` use empty strings for `image` and `images` (`image: ""`, `images: []`). `visas.ts` and `apartments.ts` use Unsplash URLs. `shopping.ts` also uses empty strings. Unsplash is a trusted CDN, but these should ideally use R2 CDN (`pub-5ae97056834749bd97c9ff1dca1f1631.r2.dev`). |
| Hero images in configs | INFO | All 5 `*Config` objects use Unsplash URLs for `heroImage`. Consistent with existing categories but could benefit from migration to R2 CDN eventually. |

### 1.3 Data Integrity

| Check | Status | Notes |
|-------|--------|-------|
| Slug uniqueness (within category) | PASS | All slugs within each data file are unique. |
| Slug uniqueness (cross-category) | PASS | No slug collisions between the 5 new categories or with the existing 13 categories. |
| Price/oldPrice relationship | PASS | All items have `oldPrice > price` (discount is always positive). |

---

## 2. TypeScript Typing Analysis

### 2.1 Type Usage Per Category

| Category | Data Type Used | Correct? | Notes |
|----------|---------------|----------|-------|
| `spa.ts` | `BaseService[]` | YES | SPA items have no extended fields -- `BaseService` is appropriate. |
| `shopping.ts` | `Excursion[]` | YES | Shopping tours use `itinerary`, `groupSize`, `transport` which are `Excursion`-specific fields. |
| `photoshoots.ts` | `Photoshoot` (custom) | YES | Extends `BaseService` with `photographer`, `droneIncluded`, `editedPhotos`, `deliveryDays`. Type is defined in the same file -- not in `types.ts`. |
| `visas.ts` | `AdditionalService[]` | YES | Uses `serviceCategory`, `processingTime`, `documentsRequired` from `AdditionalService`. |
| `apartments.ts` | `Hotel[]` | YES | Reuses `Hotel` type with `stars`, `area`, `checkIn`, `checkOut`, `breakfastIncluded`. Semantically reasonable since apartments share hotel-like fields. |

### 2.2 Type Issues

| ID | Severity | File | Issue |
|----|----------|------|-------|
| T-01 | LOW | `photoshoots.ts` | `Photoshoot` interface defined locally in the data file rather than in `types.ts` where all other service types live. The `Service` union type in `types.ts` (line 165) does NOT include `Photoshoot`. This means any code that exhaustively switches on `Service.type` will not handle `"photoshoot"`. Currently no such code exists, but it is a forward-compatibility risk. |
| T-02 | LOW | `spa.ts` | Uses `BaseService[]` directly without a `type` discriminator field. Existing pattern for all other categories is to have a `type` field (e.g., `type: "excursion"`, `type: "hotel"`). SPA items lack this. This is harmless currently since `BaseService` does not require `type`, but breaks the project-wide convention. |
| T-03 | LOW | `apartments.ts` | Uses `type: "hotel"` for apartment items. While technically valid for the `Hotel` type, it may cause confusion in analytics or search filtering since these are conceptually different from hotels. A dedicated `type: "apartment"` with its own type would be more precise. |

---

## 3. Pattern Conformance (vs. Existing 13 Categories)

### 3.1 Three-File Architecture (page.tsx / [slug]/page.tsx / [slug]/*Client.tsx)

| Category | Catalog page | Detail page (server) | Detail client | Pattern match |
|----------|-------------|---------------------|---------------|---------------|
| spa | `"use client"` CatalogPage | Server component with `generateStaticParams` + `generateMetadata` | SpaClient.tsx | FULL MATCH |
| shopping | `"use client"` CatalogPage | Server component with `generateStaticParams` + `generateMetadata` | ShoppingClient.tsx | FULL MATCH |
| photoshoots | `"use client"` CatalogPage | Server component with `generateStaticParams` + `generateMetadata` | PhotoshootClient.tsx | FULL MATCH |
| visas | `"use client"` CatalogPage | Server component with `generateStaticParams` + `generateMetadata` | VisaClient.tsx | FULL MATCH |
| apartments | `"use client"` CatalogPage | Server component with `generateStaticParams` + `generateMetadata` | ApartmentClient.tsx | FULL MATCH |

All 5 categories follow the exact Server/Client split pattern documented in project rules.

### 3.2 Client Component Features

| Feature | spa | shopping | photoshoots | visas | apartments | Expected |
|---------|-----|----------|-------------|-------|------------|----------|
| `useLanguage()` | YES | YES | YES | YES | YES | YES |
| `addToRecentlyViewed()` | YES | YES | YES | YES | YES | YES |
| `ServiceNotFound` fallback | YES | YES | YES | YES | YES | YES |
| `ServiceDetailPage` wrapper | YES | YES | YES | YES | YES | YES |
| Related services (`.slice(0,3)`) | YES | YES | YES | YES | YES | YES |
| `renderSpecificFields()` | NO | YES | YES | YES | YES | Varies |
| `routeTabLabel` | `t.detail.details` | `t.detail.program` | `t.detail.details` | `t.detail.details` | `t.detail.details` | Varies by category |

### 3.3 routeTabLabel Correctness

Per project rules in `project-rules.md`:
- "Программа" for excursions -> `shopping` uses `t.detail.program` (CORRECT -- shopping tours are excursion-type)
- "Детали" for restaurants, hotels, pools, beach-clubs, car-rentals, services -> `spa`, `photoshoots`, `visas`, `apartments` use `t.detail.details` (CORRECT)

### 3.4 SEO Metadata

All 5 `[slug]/page.tsx` files:
- Export `generateStaticParams()` for SSG -- CORRECT
- Export `generateMetadata()` with `title`, `description`, `openGraph`, `twitter` -- CORRECT
- Handle missing item with fallback title "Not found | VIP-DXB-RUS" -- CORRECT
- Title format: `${item.title.RU} -- [Category] | VIP-DXB-RUS` -- CONSISTENT

---

## 4. Integration Correctness

### 4.1 Search Index (`search-index.ts`)

| Check | Status |
|-------|--------|
| All 5 data arrays imported | PASS (lines 28-32) |
| All 5 added to `catalog[]` | PASS (lines 82-86) |
| Paths match app routes | PASS (`/spa`, `/shopping`, `/photoshoots`, `/visas`, `/apartments`) |
| Labels bilingual (ru/en) | PASS |
| Group assignments reasonable | SEE NOTE |

**Group Assignment Review:**

| Category | Assigned Group | Reasonable? |
|----------|---------------|-------------|
| spa | `food` | ACCEPTABLE -- grouped with hotels, restaurants. Could argue for a dedicated "wellness" group but `food` is the "Food & Stay" group. |
| shopping | `excursions` | CORRECT -- shopping tours are guided excursions. |
| photoshoots | `excursions` | ACCEPTABLE -- guided experience similar to excursions. |
| visas | `transport` | ACCEPTABLE -- grouped with transfers, car-rentals, services in "Transport & Services". |
| apartments | `food` | ACCEPTABLE -- `food` group is "Food & Stay", apartments fit under "Stay". |

### 4.2 Sitemap (`sitemap.ts`)

| Check | Status |
|-------|--------|
| All 5 data arrays imported | PASS (lines 14-20) |
| Catalog index pages listed | PASS (lines 126-130) |
| Detail page slugs mapped | PASS (lines 155-159) |
| Routes match app directory structure | PASS |

### 4.3 Navigation (`Navigation.tsx`)

| Check | Status |
|-------|--------|
| All 5 in desktop "MORE" dropdown | PASS (lines 109-113) |
| All 5 in mobile menu sections | PASS (lines 175-179) |
| Translation keys used (`t.breadcrumb.*`) | PASS |
| Links use correct paths | PASS |

### 4.4 Footer (`Footer.tsx`)

| Check | Status |
|-------|--------|
| spa in "Food & Stay" group | PASS (line 123) |
| shopping in "Tours & Excursions" group | PASS (line 100) |
| photoshoots in "Tours & Excursions" group | PASS (line 101) |
| visas in "Transport & Services" group | PASS (line 133) |
| apartments in "Food & Stay" group | PASS (line 124) |
| Grouping matches search-index groups | PASS |

### 4.5 Translations (`translations.ts`)

| Check | Status |
|-------|--------|
| `breadcrumb.spa` defined (RU/EN) | PASS |
| `breadcrumb.shopping` defined (RU/EN) | PASS |
| `breadcrumb.photoshoots` defined (RU/EN) | PASS |
| `breadcrumb.visas` defined (RU/EN) | PASS |
| `breadcrumb.apartments` defined (RU/EN) | PASS |
| `additionalService.*` keys (used by VisaClient) | PASS |
| `detail.details` key (used by 4 clients) | PASS |
| `detail.program` key (used by ShoppingClient) | PASS |
| `detail.itinerary` key (used by ShoppingClient) | PASS |

---

## 5. Cross-Category Consistency

### 5.1 Data Quality

| Category | Items | All have oldPrice? | All have rating? | Empty image/images? |
|----------|-------|--------------------|------------------|---------------------|
| spa | 4 | YES | YES | YES -- all `image: ""`, `images: []` |
| shopping | 4 | YES | YES | YES -- all `image: ""`, `images: []` |
| photoshoots | 4 | YES | YES | YES -- all `image: ""`, `images: []` |
| visas | 4 | YES | YES | NO -- all have Unsplash URLs |
| apartments | 4 | YES | YES | NO -- all have Unsplash URLs |

**Note:** `spa`, `shopping`, `photoshoots` have empty `image`/`images` fields. This means:
- Service cards will show no thumbnail in catalog views
- OG images will be empty in metadata (each `[slug]/page.tsx` checks `item.images?.[0]` and returns empty array if falsy)
- This is likely intentional (placeholder for future R2 CDN upload) but worth flagging

### 5.2 FAQ / WhatsApp text

All items across all 5 categories have:
- At least 2 FAQ entries -- PASS
- WhatsApp text in both RU and EN -- PASS
- WhatsApp text starts with greeting pattern -- PASS (consistent)

### 5.3 Filter Values

| Category | Filters defined | All items have `filterValues`? | Values match filter options? |
|----------|----------------|-------------------------------|------------------------------|
| spa | `city`, `type` | YES | YES |
| shopping | `type`, `duration` | YES | YES |
| photoshoots | `style`, `duration` | YES | YES |
| visas | `visaType`, `duration` | YES | YES |
| apartments | `area`, `rooms` | YES | YES |

---

## 6. Findings Summary

### Critical (0)
None.

### High (0)
None.

### Medium (0)
None.

### Low (4)

| ID | Category | Finding | Impact | Recommendation |
|----|----------|---------|--------|----------------|
| L-01 | photoshoots.ts | `Photoshoot` type defined in data file instead of `types.ts`. Not included in the `Service` union type. | No current breakage. Future exhaustive type checks on `Service` would miss photoshoots. | Move `Photoshoot` interface to `types.ts`, add to `Service` union. |
| L-02 | spa.ts | SPA items lack a `type` discriminator field, unlike all other 17 category data files. | No current breakage. Inconsistency with project convention. | Add `type: "spa"` field and create `Spa` interface extending `BaseService` in `types.ts`. |
| L-03 | apartments.ts | Apartments reuse `type: "hotel"` and `Hotel` interface. Semantically imprecise. | Could cause confusion if analytics or filtering logic switches on `type`. | Consider a dedicated `Apartment` type or at minimum document the reuse. |
| L-04 | spa/shopping/photoshoots | Empty `image` and `images` fields. OG images will be empty for these items. | No thumbnails in card views, no social preview images when shared. | Upload images to R2 CDN and update data files. Track in ISSUES.md. |

### Info (2)

| ID | Category | Finding |
|----|----------|---------|
| I-01 | All configs | Hero images use Unsplash URLs instead of R2 CDN. Functional but not ideal for production (external dependency, potential rate limits). |
| I-02 | search-index.ts | Group names `food` and `transport` are slightly misleading for spa/apartments and visas respectively, but the groups actually represent "Food & Stay" and "Transport & Services" per the translation keys. No action needed. |

---

## 7. Conclusion

The Wave 2 integration of 5 new categories is well-executed:

1. **Security:** No XSS, injection, or data integrity vulnerabilities. All data is static and React-escaped.
2. **Architecture:** All 5 categories perfectly follow the Server/Client split pattern with `generateStaticParams`, `generateMetadata`, `PageShell`, `CatalogPage`, `ServiceDetailPage`, and `ServiceNotFound`.
3. **Integration:** Search index, sitemap, navigation (desktop + mobile), footer, and translations all correctly include the new categories.
4. **Consistency:** routeTabLabel values follow project rules. FAQ structure, WhatsApp text patterns, and filter values are all consistent.
5. **TypeScript:** Types are functionally correct but have minor consistency issues (L-01, L-02, L-03) that could be addressed in a future cleanup pass.

**Recommendation:** Merge as-is. Track L-01 through L-04 in ISSUES.md for future improvement.
