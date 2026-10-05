# Task Breakdown: 5 New Categories for vipdxbrus.com

## Overview

Add 5 new service categories to the website following the existing 13-category pattern:

| # | Issue | Category | Slug | Type Name |
|---|-------|----------|------|-----------|
| 1 | I-73 | SPA & Wellness | `spa` | `Spa` |
| 2 | I-74 | Shopping Tours | `shopping` | `ShoppingTour` |
| 3 | I-75 | Photoshoots | `photoshoots` | `Photoshoot` |
| 4 | I-76 | Visas | `visas` | `Visa` |
| 5 | I-77 | Apartments & Villas | `apartments` | `Apartment` |

---

## Architecture: Existing Pattern (13 categories)

Each category consists of exactly this set of files and registry entries:

### Per-category files (5 files each)
1. **Data file:** `src/data/{slug}.ts` — exports typed array + `CategoryConfig`
2. **Catalog page:** `src/app/{slug}/page.tsx` — `"use client"`, wraps `CatalogPage` in `PageShell`
3. **Detail page (server):** `src/app/{slug}/[slug]/page.tsx` — `generateStaticParams`, `generateMetadata`, renders Client
4. **Detail page (client):** `src/app/{slug}/[slug]/{Name}Client.tsx` — `"use client"`, wraps `ServiceDetailPage` in `PageShell`
5. **Type interface:** added to `src/data/types.ts` — extends `BaseService`, added to `Service` union

### Cross-cutting registries (7 files to update ONCE for all 5 categories)
1. `src/data/types.ts` — add 5 new interfaces + update `Service` union type
2. `src/data/translations.ts` — add breadcrumb keys (RU + EN sections), detail-specific keys
3. `src/lib/search-index.ts` — add 5 imports + 5 catalog entries
4. `src/lib/city-services.ts` — add 5 imports + 5 catalog entries
5. `src/app/sitemap.ts` — add 5 imports + 5 catalog routes + 5 detail entry arrays
6. `src/components/Navigation.tsx` — add links to `mainNavItems`, `moreColumns`, `mobileSections`
7. `src/components/Footer.tsx` — add links to `serviceGroups`

---

## Task Decomposition

### Task 0: Preparation (shared, do first)
**Goal:** Add all 5 type interfaces and update shared registries so per-category agents can work independently.

**Files to modify:**
- `src/data/types.ts` (5 new interfaces + Service union)
- `src/data/translations.ts` (breadcrumb keys, detail section keys)

**Details:**

#### types.ts — New Interfaces

```typescript
// SPA & Wellness (I-73)
export interface Spa extends BaseService {
  type: "spa";
  spaType: BiText;           // "hammam" | "massage" | "wellness-center" | "sauna"
  treatments: BiText[];       // list of available treatments
  gender: BiText;             // "mixed" | "women-only" | "men-only"
  minSessionMinutes: number;
  reservationRequired: boolean;
}

// Shopping Tours (I-74)
export interface ShoppingTour extends BaseService {
  type: "shopping-tour";
  destinations: BiText[];     // Gold Souk, Mall of Emirates, etc.
  shoppingType: BiText;       // "luxury" | "outlets" | "traditional" | "mixed"
  groupSize: BiText;
  transport: BiText;
  taxRefund: boolean;
}

// Photoshoots (I-75)
export interface Photoshoot extends BaseService {
  type: "photoshoot";
  shootType: BiText;          // "portrait" | "couple" | "family" | "wedding" | "content"
  photosCount: number;        // number of edited photos
  retouchIncluded: boolean;
  deliveryDays: number;
  locations: BiText[];
}

// Visas (I-76)
export interface Visa extends BaseService {
  type: "visa";
  visaType: BiText;           // "tourist" | "transit" | "business" | "freelance"
  validityDays: number;
  processingDays: number;
  documentsRequired: BiText[];
  multipleEntry: boolean;
}

// Apartments & Villas (I-77)
export interface Apartment extends BaseService {
  type: "apartment";
  propertyType: BiText;       // "apartment" | "villa" | "penthouse" | "studio"
  bedrooms: number;
  area: BiText;               // neighborhood
  checkIn: string;
  checkOut: string;
  minNights: number;
  amenities: BiText[];
}
```

Update `Service` union:
```typescript
export type Service = Excursion | Ticket | Yacht | Transfer | Combo | WaterActivity | Buggy | BeachClub | Restaurant | Pool | Hotel | CarRental | AdditionalService | Spa | ShoppingTour | Photoshoot | Visa | Apartment;
```

#### translations.ts — New Keys

Add to `breadcrumb` interface and both RU/EN objects:
```
spa: "SPA & Wellness" / "SPA & Wellness"
shopping: "Шопинг-туры" / "Shopping Tours"
photoshoots: "Фотосессии" / "Photoshoots"
visas: "Визы" / "Visas"
apartments: "Аренда жилья" / "Apartments & Villas"
```

Add detail-specific translation sections for each category (e.g., `spa: { spaType, treatments, gender, session }`, etc.)

**Estimate:** 1 agent, ~30 min

---

### Task 1: SPA & Wellness (I-73)
**Goal:** Full category: data file with 5-8 services, catalog page, detail page with custom fields.

**Files to create:**
- `src/data/spa.ts`
- `src/app/spa/page.tsx`
- `src/app/spa/[slug]/page.tsx`
- `src/app/spa/[slug]/SpaClient.tsx`

**Data file pattern** (`src/data/spa.ts`):
- Export `spaConfig: CategoryConfig` with key `"spa"`, title, subtitle, seoText, heroImage, filters
- Filters: city (dubai/abu-dhabi), spaType (hammam/massage/wellness/sauna), gender (mixed/women/men)
- Export `spaServices: Spa[]` with 5-8 services
- Example services: Traditional Hammam, Thai Massage at 5-star hotel, Talise Spa Jumeirah, Float therapy, Moroccan Hammam, Women-only wellness day

**Catalog page** (`src/app/spa/page.tsx`):
```tsx
"use client";
import PageShell from "@/components/PageShell";
import CatalogPage from "@/components/CatalogPage";
import { spaServices, spaConfig } from "@/data/spa";

export default function SpaPage() {
  return (
    <PageShell>
      <CatalogPage config={spaConfig} services={spaServices} categoryPath="/spa" />
    </PageShell>
  );
}
```

**Detail server page** (`src/app/spa/[slug]/page.tsx`):
- `generateStaticParams` from `spaServices`
- `generateMetadata` with SEO title: `{title} -- SPA & Wellness в ОАЭ | VIP-DXB-RUS`
- Renders `<SpaClient slug={slug} />`

**Detail client** (`src/app/spa/[slug]/SpaClient.tsx`):
- `routeTabLabel={t.detail.details}` (spa/wellness/hotels/pools/beach-clubs/restaurants/car-rentals/services all use "details")
- `renderSpecificFields` shows: spa type, treatments list, gender policy, session duration, reservation status

**Estimate:** 1 agent, ~25 min

---

### Task 2: Shopping Tours (I-74)
**Goal:** Full category with 5-8 shopping tour services.

**Files to create:**
- `src/data/shopping.ts`
- `src/app/shopping/page.tsx`
- `src/app/shopping/[slug]/page.tsx`
- `src/app/shopping/[slug]/ShoppingClient.tsx`

**Data specifics:**
- Filters: city, shoppingType (luxury/outlets/traditional/mixed), audience (solo/couples/groups)
- Example services: Gold Souk walking tour, Dubai Mall VIP shopping, Global Village, Outlet Village trip, Deira Old Souk, Mall of the Emirates experience, Dubai Design District tour
- seoText highlighting tax refund, brand deals, guide assistance

**Detail client:**
- `routeTabLabel={t.detail.program}` (similar to excursions -- itinerary-based)
- `renderSpecificFields`: destinations list, shopping type, group size, transport, tax refund badge

**Estimate:** 1 agent, ~25 min

---

### Task 3: Photoshoots (I-75)
**Goal:** Full category with 5-8 photoshoot packages.

**Files to create:**
- `src/data/photoshoots.ts`
- `src/app/photoshoots/page.tsx`
- `src/app/photoshoots/[slug]/page.tsx`
- `src/app/photoshoots/[slug]/PhotoshootClient.tsx`

**Data specifics:**
- Filters: city, shootType (portrait/couple/family/wedding/content-creation), duration (1h/2h/half-day)
- Example services: Classic Dubai portrait (Burj Khalifa, Marina), Couple shoot at desert sunset, Family at Palm Jumeirah, Wedding pre-shoot, Content creation for influencers, Luxury yacht photo session, Old Dubai styled shoot
- High-ticket category (owner noted: trend, high check)

**Detail client:**
- `routeTabLabel={t.detail.details}`
- `renderSpecificFields`: shoot type, edited photos count, retouch included badge, delivery days, locations list

**Estimate:** 1 agent, ~25 min

---

### Task 4: Visas (I-76)
**Goal:** Extract visa from AdditionalService into standalone category with proper visa types.

**Files to create:**
- `src/data/visas.ts`
- `src/app/visas/page.tsx`
- `src/app/visas/[slug]/page.tsx`
- `src/app/visas/[slug]/VisaClient.tsx`

**Data specifics:**
- ISSUES.md notes: currently 1 card in `services.ts`. Needs: tourist, transit, business visa types
- Filters: visaType (tourist/transit/business/freelance), validityDays (14/30/60/90), processingTime (express/standard)
- Example services: UAE Tourist Visa 30 days, UAE Transit Visa 48h, UAE Tourist Visa 60 days, Business Visa, Express Tourist Visa (24h), Multi-entry Tourist Visa
- seoText: emphasize fast processing, document delivery to hotel, VIP-DXB-RUS handles paperwork

**Detail client:**
- `routeTabLabel={t.detail.details}`
- `renderSpecificFields`: visa type, validity days, processing time, documents required list, multiple entry badge

**Migration note:** Consider whether to remove the visa entry from `services.ts` (AdditionalService). Decision point for owner: keep it in both places or remove from services? Recommend removing from services and adding a cross-link.

**Estimate:** 1 agent, ~25 min

---

### Task 5: Apartments & Villas (I-77)
**Goal:** Full category for short-term property rentals (Airbnb-style).

**Files to create:**
- `src/data/apartments.ts`
- `src/app/apartments/page.tsx`
- `src/app/apartments/[slug]/page.tsx`
- `src/app/apartments/[slug]/ApartmentClient.tsx`

**Data specifics:**
- Filters: area (palm-jumeirah/marina/downtown/jbr/business-bay), propertyType (apartment/villa/penthouse/studio), bedrooms (1/2/3/4+)
- Example services: Marina 2BR with sea view, Palm Jumeirah villa 4BR pool, Downtown studio Burj Khalifa view, JBR beachfront apartment, Business Bay 1BR luxury tower, Palm penthouse 3BR, Jumeirah Beach villa
- Structurally similar to Hotels but with minNights, bedrooms, amenities instead of stars/breakfast

**Detail client:**
- `routeTabLabel={t.detail.details}`
- `renderSpecificFields`: property type, bedrooms, area, check-in/out times, min nights, amenities chips

**Estimate:** 1 agent, ~25 min

---

### Task 6: Cross-cutting Registry Updates
**Goal:** Wire all 5 new categories into search, sitemap, navigation, footer, city pages.

**Files to modify:**
1. `src/lib/search-index.ts` — add 5 imports, 5 catalog entries, update `CategoryGroupKey` type
2. `src/lib/city-services.ts` — add 5 imports, 5 catalog entries
3. `src/app/sitemap.ts` — add 5 imports, 5 catalog routes, 5 detail entry arrays
4. `src/components/Navigation.tsx` — update `mainNavItems`, `moreColumns`, `mobileSections`
5. `src/components/Footer.tsx` — update `serviceGroups`

**Navigation placement plan:**

Desktop `mainNavItems` changes:
- "ОТДЫХ/LEISURE" dropdown: add `{ label: t.breadcrumb.spa, href: "/spa" }`
- "ЭКСКУРСИИ/EXCURSIONS" dropdown: add `{ label: t.breadcrumb.shopping, href: "/shopping" }`
- "ЕЩЁ/MORE" columns: add photoshoots, visas, apartments under "Услуги/Services"

Mobile `mobileSections` changes:
- "ОТДЫХ" section: add SPA & Wellness
- "ЭКСКУРСИИ" section: add Shopping Tours
- "ЕЩЁ" section: add Photoshoots, Visas, Apartments

Footer `serviceGroups` changes:
- "Отдых" group: add SPA
- "Экскурсии" group: add Shopping Tours
- "Услуги" group: add Photoshoots, Visas, Apartments

`search-index.ts` — `CategoryGroupKey` and `catalog` array:
- spa: group `"food"` (leisure/wellness fits with hotels/restaurants)
- shopping: group `"excursions"` (tour-based, similar to excursions)
- photoshoots: group `"transport"` (services group, alongside car-rentals, services)
- visas: group `"transport"` (services group)
- apartments: group `"food"` (accommodation, alongside hotels)

OR create a new group key `"lifestyle"` for spa, photoshoots, apartments. Decision for owner.

**Estimate:** 1 agent, ~30 min

---

### Task 7: Verification & Build Check
**Goal:** Ensure everything compiles and no regressions.

**Steps:**
1. Run `npm run typecheck` (tsc --noEmit) -- must pass
2. Run `npm run build` -- must succeed with all new static pages generated
3. Verify new pages appear in build output (check for `spa`, `shopping`, `photoshoots`, `visas`, `apartments` routes)
4. Spot-check: open 1 catalog page + 1 detail page per category in dev
5. Verify search-index includes new services (check total count increased)
6. Verify sitemap.ts output includes new URLs

**Estimate:** 1 agent, ~15 min

---

## Execution Plan

### Wave 1 (parallel: 1 agent)
- **Task 0:** Type definitions + translations (shared foundation)

### Wave 2 (parallel: 5 agents, independent)
- **Task 1:** SPA & Wellness (I-73)
- **Task 2:** Shopping Tours (I-74)
- **Task 3:** Photoshoots (I-75)
- **Task 4:** Visas (I-76)
- **Task 5:** Apartments & Villas (I-77)

### Wave 3 (sequential after Wave 2)
- **Task 6:** Cross-cutting registries (navigation, search, sitemap, footer, city-services)

### Wave 4 (sequential after Wave 3)
- **Task 7:** Build verification

---

## File Impact Summary

### New files (20 total)
| Category | Files |
|----------|-------|
| SPA | `src/data/spa.ts`, `src/app/spa/page.tsx`, `src/app/spa/[slug]/page.tsx`, `src/app/spa/[slug]/SpaClient.tsx` |
| Shopping | `src/data/shopping.ts`, `src/app/shopping/page.tsx`, `src/app/shopping/[slug]/page.tsx`, `src/app/shopping/[slug]/ShoppingClient.tsx` |
| Photoshoots | `src/data/photoshoots.ts`, `src/app/photoshoots/page.tsx`, `src/app/photoshoots/[slug]/page.tsx`, `src/app/photoshoots/[slug]/PhotoshootClient.tsx` |
| Visas | `src/data/visas.ts`, `src/app/visas/page.tsx`, `src/app/visas/[slug]/page.tsx`, `src/app/visas/[slug]/VisaClient.tsx` |
| Apartments | `src/data/apartments.ts`, `src/app/apartments/page.tsx`, `src/app/apartments/[slug]/page.tsx`, `src/app/apartments/[slug]/ApartmentClient.tsx` |

### Modified files (7 total)
| File | What changes |
|------|-------------|
| `src/data/types.ts` | +5 interfaces, update Service union |
| `src/data/translations.ts` | +breadcrumb keys (5), +detail sections (5), in both RU and EN |
| `src/lib/search-index.ts` | +5 imports, +5 catalog entries, possibly update CategoryGroupKey |
| `src/lib/city-services.ts` | +5 imports, +5 catalog entries |
| `src/app/sitemap.ts` | +5 imports, +5 catalog routes, +5 detail entry arrays |
| `src/components/Navigation.tsx` | +links in mainNavItems, moreColumns, mobileSections |
| `src/components/Footer.tsx` | +links in serviceGroups |

### Potentially modified (owner decision)
| File | Why |
|------|-----|
| `src/data/services.ts` | Remove visa entry if migrating to standalone `visas.ts` |
| `src/components/CategoryGrid.tsx` | If adding new group key for new categories |

---

## Decisions Needed from Owner

1. **Visa migration:** Remove visa card from `services.ts` (AdditionalService) after creating `visas.ts`? Or keep in both places?
2. **Navigation grouping:** Where exactly to place 5 new categories in desktop/mobile nav? Suggested placement above -- confirm or adjust.
3. **CategoryGrid groups:** Add new group (e.g., `"lifestyle"`) for spa/photoshoots/apartments, or distribute into existing groups?
4. **Product data:** How many services per category to start? Suggested 5-8 each. Owner to provide real products or use realistic placeholders?
5. **Images:** Use Unsplash placeholders initially, then upload real photos to R2 CDN later? Or prepare R2 images first?
6. **routeTabLabel for Shopping Tours:** Use "Программа" (like excursions, itinerary-based) or "Детали"?

---

## Estimated Total

| Task | Agents | Time |
|------|--------|------|
| Task 0: Types + Translations | 1 | ~30 min |
| Tasks 1-5: 5 Categories (parallel) | 5 | ~25 min |
| Task 6: Registries | 1 | ~30 min |
| Task 7: Verification | 1 | ~15 min |
| **Total (with parallelism)** | **8** | **~1.5 hours** |
| **Total (sequential)** | **1** | **~3 hours** |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Wave 2 agents conflict on `types.ts` | Task 0 completes ALL type definitions first; Wave 2 agents only READ types.ts |
| Translation keys missing | Task 0 adds ALL breadcrumb + detail keys for all 5 categories |
| Search index breaks | Task 6 agent handles ALL search-index changes in one pass |
| Navigation overflow (18 categories) | Redesign dropdown groupings -- may need a 6th main nav item or reorganize |
| Visa data duplication | Clear owner decision before starting Task 4 |
| Build failure | Task 7 catches issues; each agent should also run typecheck locally |
