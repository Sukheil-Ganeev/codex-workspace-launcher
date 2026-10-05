# Integration Guardian Review: Wave 2 Categories

**Mode:** `audit` (Security & Integration review)
**Project:** D:/Downloads/vipdxbrus-website/
**Date:** 2026-03-14
**Reviewer:** Integration Guardian skill (Claude Opus 4.6)

---

## Scope

5 new categories (20 new files) + 5 modified integration files:

| Category | Data file | Catalog page | Detail page | Client component |
|----------|-----------|-------------|-------------|------------------|
| SPA & Wellness | `src/data/spa.ts` | `src/app/spa/page.tsx` | `src/app/spa/[slug]/page.tsx` | `src/app/spa/[slug]/SpaClient.tsx` |
| Shopping Tours | `src/data/shopping.ts` | `src/app/shopping/page.tsx` | `src/app/shopping/[slug]/page.tsx` | `src/app/shopping/[slug]/ShoppingClient.tsx` |
| Photoshoots | `src/data/photoshoots.ts` | `src/app/photoshoots/page.tsx` | `src/app/photoshoots/[slug]/page.tsx` | `src/app/photoshoots/[slug]/PhotoshootClient.tsx` |
| Visas | `src/data/visas.ts` | `src/app/visas/page.tsx` | `src/app/visas/[slug]/page.tsx` | `src/app/visas/[slug]/VisaClient.tsx` |
| Apartments | `src/data/apartments.ts` | `src/app/apartments/page.tsx` | `src/app/apartments/[slug]/page.tsx` | `src/app/apartments/[slug]/ApartmentClient.tsx` |

**Integration files:**
- `src/data/translations.ts` -- new breadcrumb keys
- `src/lib/search-index.ts` -- new imports and catalog entries
- `src/components/Navigation.tsx` -- new links in "MORE" menu
- `src/components/Footer.tsx` -- new links in service groups
- `src/app/sitemap.ts` -- new URL entries

---

## 1. SECURITY

### 1.1 Hardcoded Secrets

| Check | Result |
|-------|--------|
| Hardcoded passwords/tokens in data files | PASS -- none found |
| Hardcoded API keys in page/client components | PASS -- none found |
| Secrets in search-index or sitemap | PASS -- none found |

### 1.2 XSS via Slug / User Input

| Check | Result |
|-------|--------|
| Unsafe innerHTML usage in any new file | PASS -- not used anywhere |
| Slug handling in `[slug]/page.tsx` | PASS -- slugs are looked up via `.find()` against static data arrays; no slug value is rendered as raw HTML |
| Slug handling in Client components | PASS -- slug is matched against static data; unmatched slugs show `ServiceNotFound` component |
| User input rendered directly | PASS -- all text comes from static data files (BiText objects), never from URL params |

### 1.3 SQL Injection

| Check | Result |
|-------|--------|
| Database queries in new files | N/A -- no database interactions; all data is static TypeScript arrays |

### 1.4 CORS / Security Misconfiguration

| Check | Result |
|-------|--------|
| New API routes | N/A -- no new API routes; all pages are SSG/SSR with static data |
| `.env` exposure | N/A -- no new environment variables introduced |

### 1.5 External URLs

| Check | Result |
|-------|--------|
| Unsplash images (hero/catalog) | INFO -- spa, photoshoots, apartments use Unsplash URLs for `heroImage`. This is consistent with project pattern but means images are loaded from third-party CDN. Not a security issue, but worth noting for CSP headers. |
| Visa data images | INFO -- visas.ts uses Unsplash URLs for `image` and `images[]` arrays (unlike spa/shopping/photoshoots which use empty strings). This is an inconsistency but not a security risk. |

**Verdict: PASS -- No security vulnerabilities found.**

---

## 2. CODE QUALITY

### 2.1 Architecture Pattern Compliance (Server/Client Split)

All 5 categories follow the established project pattern:

| Component | Pattern | spa | shopping | photoshoots | visas | apartments |
|-----------|---------|-----|----------|-------------|-------|------------|
| `page.tsx` (catalog) | `"use client"` + PageShell + CatalogPage | PASS | PASS | PASS | PASS | PASS |
| `[slug]/page.tsx` | Server Component + generateStaticParams + generateMetadata | PASS | PASS | PASS | PASS | PASS |
| `[slug]/*Client.tsx` | `"use client"` + useLanguage + PageShell + ServiceDetailPage | PASS | PASS | PASS | PASS | PASS |
| Data file | Typed export + CategoryConfig + array | PASS | PASS | PASS | PASS | PASS |

### 2.2 Type Safety

| Check | Result |
|-------|--------|
| spa.ts | Uses `BaseService` from types.ts -- PASS |
| shopping.ts | Uses `Excursion` from types.ts (has itinerary, groupSize, transport) -- PASS |
| photoshoots.ts | Defines custom `Photoshoot` interface extending `BaseService` -- PASS |
| visas.ts | Uses `AdditionalService` from types.ts (has serviceCategory, processingTime, documentsRequired) -- PASS |
| apartments.ts | Uses `Hotel` from types.ts (has stars, area, checkIn, checkOut, breakfastIncluded) -- PASS |
| Client components | Proper type casting in `ShoppingClient` (`as Excursion`), `PhotoshootClient` (`as Photoshoot`), `VisaClient` (`as AdditionalService`), `ApartmentClient` (`as Hotel`) -- PASS |

### 2.3 `generateStaticParams` and `generateMetadata`

| Check | Result |
|-------|--------|
| All 5 `[slug]/page.tsx` export `generateStaticParams` | PASS |
| All 5 `[slug]/page.tsx` export `generateMetadata` | PASS |
| Metadata uses `params: Promise<{ slug: string }>` with `await` (Next.js 15 pattern) | PASS |
| Not-found fallback in metadata (`if (!item)`) | PASS |
| OpenGraph + Twitter card metadata | PASS |
| OG images use `item.images?.[0]` with fallback to empty array | PASS |

### 2.4 routeTabLabel Assignment

Per project rules (CLAUDE.md), `routeTabLabel` depends on category:
- "Program" for excursions
- "Tariffs" for tickets
- "Details" for restaurants, hotels, pools, beach-clubs, car-rentals, services

| Category | routeTabLabel used | Correct? |
|----------|-------------------|----------|
| SPA | `t.detail.details` | PASS |
| Shopping | `t.detail.program` | PASS (excursion-type with itinerary) |
| Photoshoots | `t.detail.details` | PASS |
| Visas | `t.detail.details` | PASS |
| Apartments | `t.detail.details` | PASS |

### 2.5 Recently Viewed Integration

| Check | Result |
|-------|--------|
| `addToRecentlyViewed` called in all 5 Client components | PASS |
| Called inside `useEffect` with proper dependencies `[slug, service]` | PASS |
| Guarded with `if (service)` check | PASS |

### 2.6 Related Services

| Check | Result |
|-------|--------|
| All 5 Client components compute `related` services | PASS |
| Filter excludes current slug | PASS |
| Limited to `.slice(0, 3)` | PASS |

---

## 3. CONSISTENCY

### 3.1 Cross-Category Consistency

All 5 categories follow the exact same 4-file pattern that existing categories (hotels, restaurants, etc.) use. No deviations.

### 3.2 Data Structure Consistency

| Field | spa | shopping | photoshoots | visas | apartments |
|-------|-----|----------|-------------|-------|------------|
| slug | PASS | PASS | PASS | PASS | PASS |
| title (BiText) | PASS | PASS | PASS | PASS | PASS |
| category (BiText) | PASS | PASS | PASS | PASS | PASS |
| description (BiText) | PASS | PASS | PASS | PASS | PASS |
| fullDescription (BiText) | PASS | PASS | PASS | PASS | PASS |
| price + oldPrice | PASS | PASS | PASS | PASS | PASS |
| rating + reviews | PASS | PASS | PASS | PASS | PASS |
| image + images | PASS | PASS | PASS | PASS | PASS |
| included + notIncluded | PASS | PASS | PASS | PASS | PASS |
| highlights | PASS | PASS | PASS | PASS | PASS |
| faq | PASS | PASS | PASS | PASS | PASS |
| whatsappText | PASS | PASS | PASS | PASS | PASS |
| filterValues | PASS | PASS | PASS | PASS | PASS |

### 3.3 Item Count per Category

| Category | Items | Has oldPrice on all? |
|----------|-------|---------------------|
| SPA | 4 | PASS (all 4) |
| Shopping | 4 | PASS (all 4) |
| Photoshoots | 4 | PASS (all 4) |
| Visas | 4 | PASS (all 4) |
| Apartments | 4 | PASS (all 4) |

This satisfies the project rule: "ALL cards must show oldPrice + price".

### 3.4 Category-Specific Fields

| Category | Type used | Extra fields | Correct? |
|----------|-----------|-------------|----------|
| SPA | `BaseService` | None (plain services) | PASS |
| Shopping | `Excursion` | itinerary, groupSize, transport | PASS |
| Photoshoots | Custom `Photoshoot` | photographer, droneIncluded, editedPhotos, deliveryDays | PASS |
| Visas | `AdditionalService` | serviceCategory, processingTime, documentsRequired, directions | PASS |
| Apartments | `Hotel` | stars, area, checkIn, checkOut, breakfastIncluded, directions | PASS |

---

## 4. INTEGRATION

### 4.1 Navigation (Navigation.tsx)

| Check | Result |
|-------|--------|
| `/spa` in "MORE" dropdown | PASS (line 109, 175) |
| `/shopping` in "MORE" dropdown | PASS (line 110, 176) |
| `/photoshoots` in "MORE" dropdown | PASS (line 111, 177) |
| `/visas` in "MORE" dropdown | PASS (line 112, 178) |
| `/apartments` in "MORE" dropdown | PASS (line 113, 179) |
| Uses `t.breadcrumb.*` for labels | PASS |
| Appears in both desktop and mobile menus | PASS (lines 109-113 for desktop, 175-179 for mobile) |

### 4.2 Footer (Footer.tsx)

| Check | Result |
|-------|--------|
| `/shopping` in "Tours & Excursions" group | PASS (line 99) |
| `/photoshoots` in "Tours & Excursions" group | PASS (line 100) |
| `/spa` in "Food & Stay" group | PASS (line 123) |
| `/apartments` in "Food & Stay" group | PASS (line 124) |
| `/visas` in "Transport & Services" group | PASS (line 133) |
| All use `t.breadcrumb.*` labels | PASS |
| Grouping is logically consistent | PASS |

### 4.3 Search Index (search-index.ts)

| Check | Result |
|-------|--------|
| `spa` imported and in catalog array | PASS (line 28, 82) |
| `shoppingTours` imported and in catalog array | PASS (line 29, 83) |
| `photoshoots` imported and in catalog array | PASS (line 30, 84) |
| `visas` imported and in catalog array | PASS (line 31, 85) |
| `apartments` imported and in catalog array | PASS (line 32, 86) |
| Correct paths: `/spa`, `/shopping`, `/photoshoots`, `/visas`, `/apartments` | PASS |
| Group assignments logical | PASS |

Group assignments:
- spa -> `food` group (correct: wellness/food category)
- shopping -> `excursions` group (correct: tour-type)
- photoshoots -> `excursions` group (correct: activity-type)
- visas -> `transport` group (correct: services/transport)
- apartments -> `food` group (correct: stay/accommodation)

### 4.4 Sitemap (sitemap.ts)

| Check | Result |
|-------|--------|
| All 5 data files imported | PASS (lines 14-20) |
| All 5 in `catalogRoutes` array | PASS (lines 126-130) |
| All 5 in `detailEntries` for slug pages | PASS (lines 154-159) |
| Correct variable names used (`shoppingTours`, not `shopping`) | PASS |
| Priority and changeFrequency match other categories | PASS |

### 4.5 Translations (translations.ts)

| Check | Result |
|-------|--------|
| `breadcrumb.spa` defined in type interface | PASS (line 272) |
| `breadcrumb.shopping` defined | PASS (line 273) |
| `breadcrumb.photoshoots` defined | PASS (line 274) |
| `breadcrumb.visas` defined | PASS (line 275) |
| `breadcrumb.apartments` defined | PASS (line 276) |
| RU translations present | PASS (lines 893-897) |
| EN translations present | PASS (lines 1512-1516) |
| `additionalService.*` keys exist (used by VisaClient) | PASS (lines 946-949, 1565-1568) |

---

## 5. FINDINGS

### CRITICAL: None

### HIGH: None

### MEDIUM: None

### LOW (Informational)

| ID | Finding | Severity | Files | Recommendation |
|----|---------|----------|-------|----------------|
| L-01 | SPA, photoshoots have empty `image: ""` and `images: []` | INFO | `spa.ts`, `photoshoots.ts` | Not a bug (existing categories like buggies also have empty images before CDN upload). Will need R2 CDN images before production polish. |
| L-02 | Shopping tours also have `image: ""` and `images: []` | INFO | `shopping.ts` | Same as L-01. |
| L-03 | Visas uses Unsplash URLs for images while other new categories use empty strings | INFO | `visas.ts` | Inconsistency in approach -- some categories have Unsplash placeholders, others are empty. Not a security risk, just a consistency note. |
| L-04 | Apartments uses Unsplash URLs for images (consistent with visas) | INFO | `apartments.ts` | Same pattern as visas. Unsplash URLs are fine as placeholders. |
| L-05 | `heroImage` in configs uses Unsplash URLs | INFO | All 5 config objects | Consistent with existing categories. Not a security issue. Unsplash images have proper HTTPS URLs. |

---

## 6. SUMMARY

| Area | Status | Notes |
|------|--------|-------|
| **Security** | PASS | No hardcoded secrets, no XSS vectors, no SQL injection, no unsafe innerHTML |
| **Code Quality** | PASS | All files follow established project patterns exactly |
| **TypeScript** | PASS | Proper types used: `BaseService`, `Excursion`, custom `Photoshoot`, `AdditionalService`, `Hotel` |
| **Consistency** | PASS | All 5 categories follow identical 4-file structure |
| **Integration: Navigation** | PASS | All 5 in desktop + mobile "MORE" menu |
| **Integration: Footer** | PASS | All 5 in correct service groups |
| **Integration: Search** | PASS | All 5 in search index with correct paths and groups |
| **Integration: Sitemap** | PASS | All 5 catalog + detail pages in sitemap |
| **Integration: Translations** | PASS | All breadcrumb keys defined in RU + EN |
| **Integration: Recently Viewed** | PASS | All Client components call `addToRecentlyViewed` |
| **Project Rules** | PASS | oldPrice on all items, routeTabLabel correct per category |

### Overall Verdict: PASS

All 20 new files and 5 modified integration files pass the security audit and code quality review. The implementation is consistent with the existing 13 categories in the project. No blocking issues found.

---

*Generated by Integration Guardian skill, audit mode.*
