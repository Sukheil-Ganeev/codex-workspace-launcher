# Breakdown: 5 New Categories for vipdxbrus.com

**Mode:** breakdown
**Date:** 2026-03-14
**Issues:** I-73 (SPA & Wellness), I-74 (Shopping Tours), I-75 (Photoshoots), I-76 (Visas), I-77 (Apartments)
**Existing pattern:** 13 categories, each with identical structure (data file + catalog page + detail page + Client component + layout + loading + OG image)

---

## Architecture Overview

Each new category requires the same 11 touchpoints:

```
1. src/data/types.ts           — interface + add to Service union
2. src/data/[category].ts      — CategoryConfig + data array (3-5 items min)
3. src/app/[cat]/page.tsx      — "use client" catalog page (PageShell + CatalogPage)
4. src/app/[cat]/layout.tsx    — Metadata export
5. src/app/[cat]/loading.tsx   — Skeleton loading state
6. src/app/[cat]/[slug]/page.tsx           — Server Component (generateStaticParams + generateMetadata)
7. src/app/[cat]/[slug]/[Name]Client.tsx   — "use client" detail page (ServiceDetailPage + renderSpecificFields)
8. src/app/[cat]/[slug]/opengraph-image.tsx — Dynamic OG image
9. src/data/translations.ts    — breadcrumb keys (RU + EN) + category-specific field labels
10. src/lib/search-index.ts    — import + catalog entry + CategoryGroupKey
11. Integration files: Navigation.tsx, Footer.tsx, sitemap.ts
```

---

## Dependency Graph

```
TASK-001 (types) ─────────┐
                          ├──► TASK-003..007 (data files)
TASK-002 (translations) ──┘         │
                                    ▼
                          TASK-008..012 (page.tsx catalog pages)
                          TASK-013..017 ([slug] detail pages)
                                    │
                                    ▼
                          TASK-018 (search-index)
                          TASK-019 (navigation + footer)
                          TASK-020 (sitemap)
                                    │
                                    ▼
                          TASK-021 (typecheck)
```

---

## Wave 1: Foundation (types + translations)

### TASK-001 — Define 5 new TypeScript interfaces in types.ts

**Description:** Add interfaces for Spa, ShoppingTour, Photoshoot, Visa, Apartment. Add all 5 to the `Service` union type.

**Files:**
- Modify: `src/data/types.ts`

**Plan:**
1. Add `SpaService` interface extending `BaseService` with `type: "spa"` + fields: `spaType: BiText` (hammam/massage/wellness), `treatmentDuration: BiText`, `genderRestriction: BiText` (mixed/women-only/men-only)
2. Add `ShoppingTour` interface extending `BaseService` with `type: "shopping-tour"` + fields: `shoppingType: BiText` (outlet/souk/mall), `brands: BiText[]`, `maxGroupSize: number`
3. Add `Photoshoot` interface extending `BaseService` with `type: "photoshoot"` + fields: `shootType: BiText` (portrait/couple/family/wedding), `photoCount: number`, `deliveryDays: number`, `retouchIncluded: boolean`
4. Add `Visa` interface extending `BaseService` with `type: "visa"` + fields: `visaType: BiText` (tourist/transit/business), `processingDays: number`, `validity: BiText`, `entries: BiText` (single/multiple)
5. Add `Apartment` interface extending `BaseService` with `type: "apartment"` + fields: `propertyType: BiText` (apartment/villa/penthouse), `bedrooms: number`, `area: number`, `pool: boolean`, `minNights: number`
6. Update `Service` union: add `| SpaService | ShoppingTour | Photoshoot | Visa | Apartment`

**Result:** `tsc --noEmit` passes with new types, `Service` union includes all 5.
**Depends on:** nothing
**Estimate:** 20 min

---

### TASK-002 — Add translation keys for 5 new categories

**Description:** Add breadcrumb labels and category-specific field translations for all 5 categories in both RU and EN.

**Files:**
- Modify: `src/data/translations.ts`

**Plan:**
1. Extend `Translations` interface — add to `breadcrumb`: `spa`, `shopping`, `photoshoots`, `visas`, `apartments`
2. Add new interface sections: `spa: { spaType, treatment, genderRestriction }`, `shopping: { shoppingType, brands, maxGroup }`, `photoshoot: { shootType, photoCount, delivery, retouch }`, `visa: { visaType, processing, validity, entries }`, `apartment: { propertyType, bedrooms, area, pool, minNights, perNight }`
3. Add RU values for all keys
4. Add EN values for all keys

**Result:** No TypeScript errors, all translation keys accessible via `t.breadcrumb.spa`, `t.spa.spaType`, etc.
**Depends on:** nothing
**Estimate:** 25 min

---

## Wave 2: Data Files (5 tasks in parallel)

### TASK-003 — Create src/data/spa.ts (I-73)

**Description:** Create data file for SPA & Wellness category with CategoryConfig (filters: city, spaType) and 3-5 starter services (hammam, Thai massage, wellness day pass).

**Files:**
- Create: `src/data/spa.ts`
- Read pattern: `src/data/restaurants.ts` (similar structure — venue-based, city filter)

**Plan:**
1. Define `spaConfig: CategoryConfig` with key "spa", title RU/EN, subtitle, seoText, heroImage (Unsplash placeholder), filters (city: Dubai/Abu Dhabi; type: hammam/massage/wellness)
2. Create `spas: SpaService[]` with 3-5 items. Each item: slug, title, descriptions, price, oldPrice, rating, image (Unsplash placeholder), included/notIncluded, faq, whatsappText, filterValues
3. Export both `spaConfig` and `spas`

**Result:** File compiles, exports match pattern of existing data files.
**Depends on:** TASK-001 (SpaService interface)
**Estimate:** 40 min

---

### TASK-004 — Create src/data/shopping.ts (I-74)

**Description:** Create data file for Shopping Tours category with CategoryConfig and 3-5 starter services (Gold Souk tour, Mall of Emirates VIP, Global Village, outlet tour).

**Files:**
- Create: `src/data/shopping.ts`
- Read pattern: `src/data/excursions.ts` (tour-based, with itinerary-like schedule)

**Plan:**
1. Define `shoppingConfig: CategoryConfig` with filters (city: Dubai/Abu Dhabi/Sharjah; type: souk/mall/outlet)
2. Create `shoppingTours: ShoppingTour[]` with 3-5 items including slug, title, descriptions, price, oldPrice, image, included (transport, guide), notIncluded (purchases), faq, whatsappText, filterValues
3. Export both

**Result:** File compiles, all items have required BaseService + ShoppingTour fields.
**Depends on:** TASK-001 (ShoppingTour interface)
**Estimate:** 40 min

---

### TASK-005 — Create src/data/photoshoots.ts (I-75)

**Description:** Create data file for Photoshoots category with CategoryConfig and 3-5 starter services (Dubai skyline shoot, desert sunset, Palm Jumeirah couple, wedding).

**Files:**
- Create: `src/data/photoshoots.ts`
- Read pattern: `src/data/water-activities.ts` (experience-based, outdoor)

**Plan:**
1. Define `photoshootConfig: CategoryConfig` with filters (city: Dubai/Abu Dhabi; type: portrait/couple/family/wedding)
2. Create `photoshoots: Photoshoot[]` with 3-5 items including slug, title, descriptions, price, oldPrice, image, included (photographer, retouching, N photos), notIncluded (extra prints, travel outside city), faq, whatsappText, filterValues
3. Export both

**Result:** File compiles, all items have type: "photoshoot" and required fields.
**Depends on:** TASK-001 (Photoshoot interface)
**Estimate:** 35 min

---

### TASK-006 — Create src/data/visas.ts (I-76)

**Description:** Create data file for Visas category. Extract and expand from existing visa card in services.ts. CategoryConfig with 3-5 visa types (tourist 30/90 day, transit, business, resident).

**Files:**
- Create: `src/data/visas.ts`
- Read: `src/data/services.ts` (has existing visa card to extract and expand)

**Plan:**
1. Define `visaConfig: CategoryConfig` with filters (type: tourist/transit/business; duration: 14-day/30-day/90-day)
2. Create `visas: Visa[]` with 4-5 items: tourist 30-day, tourist 90-day, transit 96-hour, business, plus multi-entry. Each with processingDays, validity, entries, documentsRequired in faq, whatsappText
3. Export both
4. Note: do NOT remove visa from services.ts yet (dormant code policy — leave until owner confirms migration)

**Result:** File compiles, realistic visa info for UAE.
**Depends on:** TASK-001 (Visa interface)
**Estimate:** 35 min

---

### TASK-007 — Create src/data/apartments.ts (I-77)

**Description:** Create data file for Apartments/Villas category with CategoryConfig and 3-5 starter listings (Marina apartment, Palm villa, JBR studio, Downtown penthouse).

**Files:**
- Create: `src/data/apartments.ts`
- Read pattern: `src/data/hotels.ts` (accommodation, similar fields)

**Plan:**
1. Define `apartmentConfig: CategoryConfig` with filters (city: Dubai/Abu Dhabi; type: apartment/villa/penthouse; bedrooms: studio/1BR/2BR/3+)
2. Create `apartments: Apartment[]` with 3-5 items: slug, title, descriptions, price (per night), oldPrice, image, included (WiFi, kitchen, parking), notIncluded (cleaning fee, security deposit), faq (check-in process, min stay), whatsappText, filterValues
3. Export both

**Result:** File compiles, all items have type: "apartment" and required fields.
**Depends on:** TASK-001 (Apartment interface)
**Estimate:** 40 min

---

## Wave 3: Catalog Pages (5 tasks in parallel)

### TASK-008 — Create src/app/spa/ catalog page structure

**Description:** Create catalog page, layout, and loading for SPA & Wellness.

**Files:**
- Create: `src/app/spa/page.tsx`
- Create: `src/app/spa/layout.tsx`
- Create: `src/app/spa/loading.tsx`

**Plan:**
1. `page.tsx`: "use client", import PageShell + CatalogPage + spaConfig + spas, render `<CatalogPage config={spaConfig} services={spas} categoryPath="/spa" />`
2. `layout.tsx`: Metadata export with title "SPA & Wellness в Дубае", description, openGraph, alternates canonical
3. `loading.tsx`: Copy skeleton from `src/app/excursions/loading.tsx` (identical pattern)

**Result:** `/spa` route renders catalog grid with filter panel.
**Depends on:** TASK-003 (spa data)
**Estimate:** 15 min

---

### TASK-009 — Create src/app/shopping/ catalog page structure

**Description:** Create catalog page, layout, and loading for Shopping Tours.

**Files:**
- Create: `src/app/shopping/page.tsx`
- Create: `src/app/shopping/layout.tsx`
- Create: `src/app/shopping/loading.tsx`

**Plan:**
1. `page.tsx`: "use client", import shoppingConfig + shoppingTours, CatalogPage
2. `layout.tsx`: Metadata for "Шопинг-туры в Дубае"
3. `loading.tsx`: Copy skeleton pattern

**Result:** `/shopping` route renders catalog.
**Depends on:** TASK-004 (shopping data)
**Estimate:** 15 min

---

### TASK-010 — Create src/app/photoshoots/ catalog page structure

**Description:** Create catalog page, layout, and loading for Photoshoots.

**Files:**
- Create: `src/app/photoshoots/page.tsx`
- Create: `src/app/photoshoots/layout.tsx`
- Create: `src/app/photoshoots/loading.tsx`

**Plan:**
1. `page.tsx`: "use client", import photoshootConfig + photoshoots, CatalogPage
2. `layout.tsx`: Metadata for "Фотосессии в Дубае"
3. `loading.tsx`: Copy skeleton pattern

**Result:** `/photoshoots` route renders catalog.
**Depends on:** TASK-005 (photoshoots data)
**Estimate:** 15 min

---

### TASK-011 — Create src/app/visas/ catalog page structure

**Description:** Create catalog page, layout, and loading for Visas.

**Files:**
- Create: `src/app/visas/page.tsx`
- Create: `src/app/visas/layout.tsx`
- Create: `src/app/visas/loading.tsx`

**Plan:**
1. `page.tsx`: "use client", import visaConfig + visas, CatalogPage
2. `layout.tsx`: Metadata for "Визы в ОАЭ"
3. `loading.tsx`: Copy skeleton pattern

**Result:** `/visas` route renders catalog.
**Depends on:** TASK-006 (visas data)
**Estimate:** 15 min

---

### TASK-012 — Create src/app/apartments/ catalog page structure

**Description:** Create catalog page, layout, and loading for Apartments/Villas.

**Files:**
- Create: `src/app/apartments/page.tsx`
- Create: `src/app/apartments/layout.tsx`
- Create: `src/app/apartments/loading.tsx`

**Plan:**
1. `page.tsx`: "use client", import apartmentConfig + apartments, CatalogPage
2. `layout.tsx`: Metadata for "Аренда квартир и вилл в Дубае"
3. `loading.tsx`: Copy skeleton pattern

**Result:** `/apartments` route renders catalog.
**Depends on:** TASK-007 (apartments data)
**Estimate:** 15 min

---

## Wave 4: Detail Pages (5 tasks in parallel)

### TASK-013 — Create src/app/spa/[slug]/ detail pages

**Description:** Create Server Component page, Client component, and OG image for SPA detail pages.

**Files:**
- Create: `src/app/spa/[slug]/page.tsx`
- Create: `src/app/spa/[slug]/SpaClient.tsx`
- Create: `src/app/spa/[slug]/opengraph-image.tsx`

**Plan:**
1. `page.tsx`: Server Component with `generateStaticParams()` from spas array, `generateMetadata()` with item title + description + OG, default export renders `<SpaClient slug={slug} />`
2. `SpaClient.tsx`: "use client", find spa by slug, ServiceNotFound fallback, `renderSpecificFields()` showing spaType, treatmentDuration, genderRestriction in specs grid (pattern from YachtClient), `routeTabLabel={t.detail.details}`, related = other spas
3. `opengraph-image.tsx`: Import spas + generateServiceOG, categoryLabel "SPA & Wellness"

**Result:** `/spa/[slug]` renders detail page with tabs, gallery, booking CTA, related services.
**Depends on:** TASK-003 (spa data), TASK-002 (translations)
**Estimate:** 30 min

---

### TASK-014 — Create src/app/shopping/[slug]/ detail pages

**Description:** Create Server Component, Client component, and OG image for Shopping Tour detail pages.

**Files:**
- Create: `src/app/shopping/[slug]/page.tsx`
- Create: `src/app/shopping/[slug]/ShoppingClient.tsx`
- Create: `src/app/shopping/[slug]/opengraph-image.tsx`

**Plan:**
1. `page.tsx`: generateStaticParams from shoppingTours, generateMetadata, render ShoppingClient
2. `ShoppingClient.tsx`: find by slug, renderSpecificFields showing shoppingType, brands list, maxGroupSize. `routeTabLabel={t.detail.program}` (tour-based, like excursions)
3. `opengraph-image.tsx`: categoryLabel "Шопинг-туры"

**Result:** `/shopping/[slug]` renders full detail page.
**Depends on:** TASK-004 (shopping data), TASK-002 (translations)
**Estimate:** 30 min

---

### TASK-015 — Create src/app/photoshoots/[slug]/ detail pages

**Description:** Create Server Component, Client component, and OG image for Photoshoot detail pages.

**Files:**
- Create: `src/app/photoshoots/[slug]/page.tsx`
- Create: `src/app/photoshoots/[slug]/PhotoshootClient.tsx`
- Create: `src/app/photoshoots/[slug]/opengraph-image.tsx`

**Plan:**
1. `page.tsx`: generateStaticParams from photoshoots, generateMetadata, render PhotoshootClient
2. `PhotoshootClient.tsx`: find by slug, renderSpecificFields showing shootType, photoCount, deliveryDays, retouchIncluded. `routeTabLabel={t.detail.details}`
3. `opengraph-image.tsx`: categoryLabel "Фотосессии"

**Result:** `/photoshoots/[slug]` renders full detail page.
**Depends on:** TASK-005 (photoshoots data), TASK-002 (translations)
**Estimate:** 30 min

---

### TASK-016 — Create src/app/visas/[slug]/ detail pages

**Description:** Create Server Component, Client component, and OG image for Visa detail pages.

**Files:**
- Create: `src/app/visas/[slug]/page.tsx`
- Create: `src/app/visas/[slug]/VisaClient.tsx`
- Create: `src/app/visas/[slug]/opengraph-image.tsx`

**Plan:**
1. `page.tsx`: generateStaticParams from visas, generateMetadata, render VisaClient
2. `VisaClient.tsx`: find by slug, renderSpecificFields showing visaType, processingDays, validity, entries in specs grid. `routeTabLabel={t.detail.details}`
3. `opengraph-image.tsx`: categoryLabel "Визы"

**Result:** `/visas/[slug]` renders full detail page.
**Depends on:** TASK-006 (visas data), TASK-002 (translations)
**Estimate:** 30 min

---

### TASK-017 — Create src/app/apartments/[slug]/ detail pages

**Description:** Create Server Component, Client component, and OG image for Apartment detail pages.

**Files:**
- Create: `src/app/apartments/[slug]/page.tsx`
- Create: `src/app/apartments/[slug]/ApartmentClient.tsx`
- Create: `src/app/apartments/[slug]/opengraph-image.tsx`

**Plan:**
1. `page.tsx`: generateStaticParams from apartments, generateMetadata, render ApartmentClient
2. `ApartmentClient.tsx`: find by slug, renderSpecificFields showing propertyType, bedrooms, area (sqm), pool, minNights in specs grid (pattern from HotelClient). `routeTabLabel={t.detail.details}`. Price note: "from $X/night"
3. `opengraph-image.tsx`: categoryLabel "Аренда квартир"

**Result:** `/apartments/[slug]` renders full detail page.
**Depends on:** TASK-007 (apartments data), TASK-002 (translations)
**Estimate:** 30 min

---

## Wave 5: Integration (sequential)

### TASK-018 — Add 5 new categories to search-index.ts

**Description:** Import all 5 new data files into search-index, add to catalog array with correct group assignments, update CategoryGroupKey if needed.

**Files:**
- Modify: `src/lib/search-index.ts`

**Plan:**
1. Add imports: `import { spas } from "@/data/spa"`, `import { shoppingTours } from "@/data/shopping"`, `import { photoshoots } from "@/data/photoshoots"`, `import { visas } from "@/data/visas"`, `import { apartments } from "@/data/apartments"`
2. Add to `catalog` array:
   - `{ services: spas, path: "/spa", label: { ru: "SPA & Wellness", en: "SPA & Wellness" }, group: "food" }` (leisure/wellness fits "food" group which is really "Food & Stay")
   - `{ services: shoppingTours, path: "/shopping", label: { ru: "Шопинг-туры", en: "Shopping Tours" }, group: "excursions" }` (tour-based)
   - `{ services: photoshoots, path: "/photoshoots", label: { ru: "Фотосессии", en: "Photoshoots" }, group: "transport" }` (services group)
   - `{ services: visas, path: "/visas", label: { ru: "Визы", en: "Visas" }, group: "transport" }` (services group)
   - `{ services: apartments, path: "/apartments", label: { ru: "Аренда квартир", en: "Apartments" }, group: "food" }` (accommodation = "Food & Stay" group)
3. Verify searchItems includes all new services

**Result:** All 5 categories searchable via SearchModal. City counts updated in CategoryGrid.
**Depends on:** TASK-003..007 (all data files)
**Estimate:** 15 min

---

### TASK-019 — Add 5 new categories to Navigation + Footer

**Description:** Add new category links to Navigation (mobile menu sections + "MORE" dropdown) and Footer service groups.

**Files:**
- Modify: `src/components/Navigation.tsx`
- Modify: `src/components/Footer.tsx`

**Plan:**
1. **Navigation.tsx — desktop `moreColumns`:** Add to "Services" column: `{ label: t.breadcrumb.spa, href: "/spa" }`, `{ label: t.breadcrumb.visas, href: "/visas" }`, `{ label: t.breadcrumb.apartments, href: "/apartments" }`. Add to new/existing column: photoshoots, shopping
2. **Navigation.tsx — `mobileSections`:** Add links to appropriate sections. Shopping under "EXCURSIONS". SPA, Apartments under "LEISURE". Visas, Photoshoots under "MORE"
3. **Footer.tsx — `serviceGroups`:** Add SPA + Apartments to "Food & Stay" group. Add Shopping to "Tours & Excursions". Add Photoshoots + Visas to "Transport & Services"

**Result:** All 5 categories accessible from both desktop and mobile navigation + footer.
**Depends on:** TASK-002 (translation keys for breadcrumbs)
**Estimate:** 25 min

---

### TASK-020 — Add 5 new categories to sitemap.ts

**Description:** Add catalog routes and detail page entries for all 5 categories to the XML sitemap.

**Files:**
- Modify: `src/app/sitemap.ts`

**Plan:**
1. Add imports: `import { spas } from "@/data/spa"`, `import { shoppingTours } from "@/data/shopping"`, `import { photoshoots } from "@/data/photoshoots"`, `import { visas } from "@/data/visas"`, `import { apartments } from "@/data/apartments"`
2. Add to `catalogRoutes` array: `"spa"`, `"shopping"`, `"photoshoots"`, `"visas"`, `"apartments"`
3. Add to `detailEntries`: spread all 5 arrays with their paths
4. Verify sitemap generates correct URLs

**Result:** /sitemap.xml includes all new catalog + detail URLs.
**Depends on:** TASK-003..007 (all data files)
**Estimate:** 10 min

---

## Wave 6: Verification

### TASK-021 — TypeScript check + build verification

**Description:** Run `tsc --noEmit` and `npm run build` to ensure zero errors across all 30+ new files.

**Files:**
- Read only (verification)

**Plan:**
1. Run `npx tsc --noEmit` — expect 0 errors
2. Run `npm run build` — expect successful build with new SSG pages
3. Verify new static pages appear in build output (5 catalog + N detail pages)
4. Check for any unused imports or missing translation keys
5. Fix any issues found

**Result:** Clean build, zero TypeScript errors, all new routes generate static pages.
**Depends on:** TASK-018, TASK-019, TASK-020 (all integration complete)
**Estimate:** 15 min

---

## Summary Table

| Task | Wave | Description | Files (create/modify) | Depends on | Estimate |
|------|------|-------------|----------------------|------------|----------|
| TASK-001 | 1 | 5 TypeScript interfaces in types.ts | M:1 | — | 20 min |
| TASK-002 | 1 | Translation keys (RU + EN) | M:1 | — | 25 min |
| TASK-003 | 2 | src/data/spa.ts | C:1 | T-001 | 40 min |
| TASK-004 | 2 | src/data/shopping.ts | C:1 | T-001 | 40 min |
| TASK-005 | 2 | src/data/photoshoots.ts | C:1 | T-001 | 35 min |
| TASK-006 | 2 | src/data/visas.ts | C:1 | T-001 | 35 min |
| TASK-007 | 2 | src/data/apartments.ts | C:1 | T-001 | 40 min |
| TASK-008 | 3 | src/app/spa/ (page+layout+loading) | C:3 | T-003 | 15 min |
| TASK-009 | 3 | src/app/shopping/ (page+layout+loading) | C:3 | T-004 | 15 min |
| TASK-010 | 3 | src/app/photoshoots/ (page+layout+loading) | C:3 | T-005 | 15 min |
| TASK-011 | 3 | src/app/visas/ (page+layout+loading) | C:3 | T-006 | 15 min |
| TASK-012 | 3 | src/app/apartments/ (page+layout+loading) | C:3 | T-007 | 15 min |
| TASK-013 | 4 | src/app/spa/[slug]/ (page+Client+OG) | C:3 | T-003, T-002 | 30 min |
| TASK-014 | 4 | src/app/shopping/[slug]/ (page+Client+OG) | C:3 | T-004, T-002 | 30 min |
| TASK-015 | 4 | src/app/photoshoots/[slug]/ (page+Client+OG) | C:3 | T-005, T-002 | 30 min |
| TASK-016 | 4 | src/app/visas/[slug]/ (page+Client+OG) | C:3 | T-006, T-002 | 30 min |
| TASK-017 | 4 | src/app/apartments/[slug]/ (page+Client+OG) | C:3 | T-007, T-002 | 30 min |
| TASK-018 | 5 | search-index.ts integration | M:1 | T-003..007 | 15 min |
| TASK-019 | 5 | Navigation.tsx + Footer.tsx | M:2 | T-002 | 25 min |
| TASK-020 | 5 | sitemap.ts | M:1 | T-003..007 | 10 min |
| TASK-021 | 6 | TypeScript check + build | — | T-018..020 | 15 min |

**Total:** 21 tasks, 6 waves
**Files created:** 35 new files
**Files modified:** 6 existing files (types.ts, translations.ts, search-index.ts, Navigation.tsx, Footer.tsx, sitemap.ts)
**Estimated total time:** ~9 hours (sequential) or ~4 hours (with parallel waves)

---

## Parallelism Plan for Subagents

For maximum speed with worktree agents:

| Wave | Tasks | Agents | Time |
|------|-------|--------|------|
| 1 | TASK-001, TASK-002 | 2 parallel | 25 min |
| 2 | TASK-003..007 | 5 parallel | 40 min |
| 3 | TASK-008..012 | 5 parallel | 15 min |
| 4 | TASK-013..017 | 5 parallel | 30 min |
| 5 | TASK-018..020 | 3 sequential (shared files) | 50 min |
| 6 | TASK-021 | 1 | 15 min |

**Critical path:** ~2h 55min with max parallelism.

---

## Non-Goals (out of scope)

- Real photos for new categories (use Unsplash placeholders; owner will provide later — relates to I-78)
- Real pricing data (use realistic estimates; owner confirms later — relates to I-26)
- CategoryGrid redesign (current 5 groups stay; new categories go to "MORE" in nav)
- Database migration (these are static .ts data files, matching existing pattern)
- Removing visa card from services.ts (dormant code — ask owner first)
- R2 CDN photo upload for new categories (separate task)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| translations.ts grows large | Slow IDE, longer compile | Future: split translations per locale file (not this task) |
| Navigation "MORE" dropdown too crowded | UX degradation | Group new items logically; consider 3-column "MORE" if needed |
| Service union type grows to 18+ variants | Type complexity | Already a pattern — TS handles it fine |
| search-index CategoryGroupKey doesn't map cleanly for new categories | Incorrect city counts in CategoryGrid | Assign to closest existing group (food = accommodation/wellness, excursions = tours, transport = services) |
