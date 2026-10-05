# Tech Spec: Quick Compare — Side-by-Side Service Comparison

**Feature:** Quick Compare
**Project:** VIP-DXB-RUS Tourism Website (vipdxbrus.com)
**Author:** Claude Opus 4.6
**Date:** 2026-03-14
**Status:** DRAFT — awaiting owner approval

---

## 1. Problem Statement

Users browsing the catalog (13 categories, 236+ products) have no efficient way to compare services side by side. They must open multiple tabs or remember details from different cards to make a decision. This creates friction in the purchase funnel — users leave to compare on competitor sites (Klook, Booking.com, Kayak) and may not return.

### Business Impact
- **Reduced bounce on catalog pages** — users stay on-site to compare instead of leaving
- **Higher conversion to WhatsApp CTA** — comparison clarifies value, prompts action
- **Competitive parity** — Klook, Kayak, and Booking.com all offer comparison features

### User Story
> As a tourist browsing excursions in Dubai, I want to compare 2-3 options side by side (price, duration, rating, highlights) so I can quickly decide which one to book via WhatsApp.

---

## 2. Scope

### In Scope (MVP)
- "Compare" checkbox on ServiceCard (catalog pages only)
- Floating CompareBar at the bottom of the screen (shows selected count, thumbnails)
- CompareModal with side-by-side table when user clicks "Compare (N)"
- Maximum 3 items (hard limit)
- Comparison attributes: image, title, price/oldPrice, duration, location/city, rating, reviews count, highlights, category
- CTA button per column: "Book via WhatsApp" (pre-filled message with service name)
- State persisted in localStorage (survives page navigation within session)
- Mobile-responsive: stacked cards on mobile, columns on desktop
- i18n: RU/EN translations

### Out of Scope (Future)
- Cross-category comparison warnings/restrictions (MVP allows comparing any services)
- Share comparison link (URL with slugs)
- PDF export of comparison
- Server-side comparison (no API needed — all data is static)
- Integration with trip-planner or booking calendar
- Comparison history

---

## 3. Technical Architecture

### 3.1 Stack & Constraints
- **Framework:** Next.js 15 (App Router, React 19)
- **Language:** TypeScript (strict)
- **Styling:** Tailwind CSS 4 + inline `style={}` (project convention — see existing components)
- **State:** `useSyncExternalStore` + localStorage (same pattern as `useFavorites`)
- **Rendering:** Client Components only (state, interactivity)
- **Modal loading:** `next/dynamic` with `ssr: false` (project convention for modals)
- **Brand:** Copper #C4896E, Tenor Sans headings, Montserrat body, luxury minimalism

### 3.2 New Files

| File | Type | Purpose |
|------|------|---------|
| `src/hooks/useCompare.ts` | Hook | Compare state management (localStorage + useSyncExternalStore) |
| `src/components/CompareCheckbox.tsx` | Client Component | Checkbox overlay on ServiceCard |
| `src/components/CompareBar.tsx` | Client Component | Floating bottom bar with count + thumbnails |
| `src/components/CompareModal.tsx` | Client Component | Full-screen modal with comparison table |

### 3.3 Modified Files

| File | Change |
|------|--------|
| `src/components/ServiceCard.tsx` | Add `CompareCheckbox` overlay (top-left, below badge) |
| `src/components/CatalogPage.tsx` | Render `CompareBar` (floating, outside grid) |
| `src/data/translations.ts` | Add `compare` namespace with RU/EN keys |
| `src/lib/analytics.ts` | Add compare-related event helpers |

### 3.4 Unchanged Files (explicitly NOT touched)
- `ServiceDetailPage.tsx` — compare is catalog-level only in MVP
- `search-index.ts` — compare uses same `BaseService` data, no index changes
- `FeaturedServices.tsx` — homepage cards do not get compare in MVP
- `CityLandingPage.tsx` — city page cards do not get compare in MVP
- All `src/data/*.ts` files — no data model changes

---

## 4. Detailed Design

### 4.1 `useCompare` Hook

**Pattern:** Mirrors `useFavorites` exactly — `useSyncExternalStore` + localStorage + custom event for cross-component sync.

```typescript
// src/hooks/useCompare.ts

const STORAGE_KEY = "vipdxbrus_compare";
const MAX_ITEMS = 3;
const CHANGE_EVENT = "vipdxbrus:compare-changed";

interface CompareItem {
  slug: string;
  categoryPath: string;  // needed to resolve full data from search-index
}

interface UseCompareReturn {
  items: CompareItem[];
  count: number;
  isComparing: (slug: string) => boolean;
  toggleCompare: (slug: string, categoryPath: string) => void;
  removeFromCompare: (slug: string) => void;
  clearAll: () => void;
  isFull: boolean;  // count >= MAX_ITEMS
}
```

**Key behaviors:**
- `toggleCompare` — if item exists, remove it; if not and count < 3, add it; if count >= 3, do nothing (button becomes disabled/shows tooltip)
- Custom event `vipdxbrus:compare-changed` dispatched on every write — ensures CompareBar and CompareCheckbox stay in sync across the component tree
- `getServerSnapshot` returns empty array (SSR-safe)
- Cached parsed result (same pattern as favorites) to maintain referential stability

**localStorage format:**
```json
[
  { "slug": "desert-safari-sunset", "categoryPath": "/excursions" },
  { "slug": "burj-khalifa-124", "categoryPath": "/tickets" }
]
```

### 4.2 `CompareCheckbox` Component

**Location on card:** Top-left corner, below the badge (if present), visually next to the existing FavoriteButton (top-right).

**Behavior:**
- Unchecked state: semi-transparent circle with compare icon (two overlapping squares or a scales icon)
- Checked state: copper-filled circle with white checkmark
- Hover: shows tooltip "Compare" / "Сравнить"
- If compare list is full (3 items) and this item is NOT in the list: checkbox is visually disabled (opacity 0.4), hover tooltip says "Max 3 items" / "Максимум 3"
- Click calls `toggleCompare(slug, categoryPath)` — stops propagation (card is clickable)
- Animation: subtle scale pulse on toggle (same `heart-pop` keyframe reuse)

**Props:**
```typescript
interface CompareCheckboxProps {
  slug: string;
  categoryPath: string;
}
```

**Visual specs:**
- Size: 32x32px (matches FavoriteButton)
- Position: `absolute`, `top: var(--space-2)`, `left: var(--space-2)`, `z-index: 10`
- Background: `rgba(255,255,255,0.85)` with `backdrop-filter: blur(4px)` (matches FavoriteButton)
- Checked: `background-color: var(--color-copper)`, icon color `#FFFFFF`
- Unchecked icon: two overlapping rectangles (compare metaphor), color `var(--color-text-secondary)`

### 4.3 `CompareBar` — Floating Bottom Bar

**Pattern:** Similar to `CatalogStickyBar` — fixed bottom, hidden when 0 items, animated slide-up.

**Behavior:**
- Hidden when `count === 0`
- Shows when `count >= 1`
- Displays: thumbnail images of selected items (circular, 40px) + "Compare (N)" button + "Clear" link
- On mobile (<768px): full-width bar, thumbnails smaller (32px)
- On desktop (>=768px): centered bar with max-width, rounded corners, subtle shadow
- Hides when mobile menu is open (`data-mobile-menu-open`) — same pattern as StickyCTA
- Hides when footer is visible — same IntersectionObserver pattern as CatalogStickyBar
- Spacer div prevents content from being hidden behind the bar

**Z-index:** Uses `var(--z-sticky)` — same layer as CatalogStickyBar. Since CompareBar replaces CatalogStickyBar's visual space when active, they share the z-layer. CatalogStickyBar is mobile-only (`md:hidden`), CompareBar is both — so they coexist without overlap (CompareBar renders ABOVE CatalogStickyBar with slightly higher z).

**Visual specs:**
- Height: 64px (desktop), 56px (mobile) + safe-area-inset-bottom
- Background: `rgba(253, 251, 249, 0.96)` with `backdrop-filter: blur(18px)` (matches existing bars)
- Border-top: `0.8px solid var(--color-border)`
- Shadow: `var(--shadow-sticky)`
- "Compare" button: copper background, white text, pill shape — matches project CTA style
- "Clear all" link: text-only, `var(--color-text-secondary)`, underline on hover
- Thumbnail: circular with `border: 2px solid var(--color-copper)`, `object-fit: cover`
- Remove "x" on each thumbnail: 16px circle, top-right of thumbnail, `var(--color-text-secondary)`

**Layout (desktop):**
```
[ thumb1 ] [ thumb2 ] [ thumb3 ]    Compare (2)    Clear all
```

**Layout (mobile):**
```
[ t1 ] [ t2 ] [ t3 ]   [ Compare (2) ]   [ x ]
```

### 4.4 `CompareModal` — Comparison Table

**Pattern:** Same modal pattern as `SearchModal` — backdrop + centered panel, close on Escape, body scroll lock.

**Loading:** `next/dynamic` with `ssr: false` (project convention for modals):
```typescript
const CompareModal = dynamic(() => import("@/components/CompareModal"), { ssr: false });
```

**Data resolution:** The modal receives an array of slugs + categoryPaths. It resolves full service data by:
1. Importing `searchItems` from `search-index.ts` for lightweight data (name, price, image, categoryLabel)
2. For detailed fields (duration, location, rating, reviews, highlights), it imports directly from the corresponding data file using a resolver function

**Resolver approach (avoids importing all 13 data files in the modal):**

```typescript
// src/lib/compare-resolver.ts
import { searchItems } from "@/lib/search-index";
import type { BaseService } from "@/data/types";

// Import all catalog sources (tree-shaken since search-index already imports them)
import { excursions } from "@/data/excursions";
import { tickets } from "@/data/tickets";
// ... (all 13 data files — same imports as search-index.ts)

const allServices: BaseService[] = [
  ...excursions, ...tickets, ...yachts, ...transfers,
  ...combos, ...waterActivities, ...buggies, ...beachClubs,
  ...restaurants, ...pools, ...hotels, ...carRentals, ...additionalServices,
];

export function resolveServices(slugs: string[]): BaseService[] {
  return slugs
    .map(slug => allServices.find(s => s.slug === slug))
    .filter((s): s is BaseService => s !== undefined);
}
```

> **Note:** Since `search-index.ts` already imports all 13 data files, there is zero additional bundle cost. The resolver simply provides access to the full `BaseService` objects rather than the lightweight `SearchItem` projections.

**Modal layout:**

Desktop (>=768px): Side-by-side columns (2 or 3 columns, equal width)
```
+--------------------------------------------------+
|  Compare Services                           [x]  |
+--------------------------------------------------+
|   [Image 1]     |   [Image 2]     |   [Image 3]  |
|   Title 1       |   Title 2       |   Title 3     |
|   Category      |   Category      |   Category    |
|   ★ 4.8 (120)   |   ★ 4.5 (85)    |   ★ 4.9 (200) |
|   ~6 hours      |   ~4 hours      |   ~8 hours    |
|   Dubai         |   Abu Dhabi     |   Desert      |
|   $65 ~~$85~~   |   $120          |   $90 ~~$110~~ |
|                  |                 |               |
|   Highlights:   |   Highlights:   |   Highlights: |
|   - Dune bash   |   - VIP access  |   - Overnight |
|   - BBQ dinner  |   - Skip line   |   - Camel ride|
|   - Fire show   |   - Guide       |   - Stargazing|
|                  |                 |               |
|  [WhatsApp ❯]   |  [WhatsApp ❯]   |  [WhatsApp ❯] |
|   [Remove]      |   [Remove]      |   [Remove]    |
+--------------------------------------------------+
```

Mobile (<768px): Horizontal scroll with snap, or stacked vertical cards
```
+------------------------+
| Compare         [x]   |
+------------------------+
| ← [Card 1] [Card 2] → |
|   (swipe to scroll)    |
+------------------------+
```

**Comparison rows (in order):**

| Row | Field | Source |
|-----|-------|--------|
| 1 | Image (thumbnail) | `BaseService.image` |
| 2 | Title | `BaseService.title[lang]` |
| 3 | Category | `BaseService.category[lang]` |
| 4 | Rating + Reviews | `BaseService.rating` + `BaseService.reviews` |
| 5 | Duration | `BaseService.duration[lang]` |
| 6 | Location | `BaseService.location[lang]` |
| 7 | Price (with oldPrice strikethrough) | `BaseService.price`, `BaseService.oldPrice` |
| 8 | Highlights (bullet list, max 5) | `BaseService.highlights?.[lang]` (first 5 items) |
| 9 | WhatsApp CTA button | Pre-filled: "Hi! I'm comparing: [Title]. Can you help?" |
| 10 | Remove button | Calls `removeFromCompare(slug)` |

**Styling:**
- Modal background: `#FFFFFF`
- Backdrop: `rgba(26, 23, 20, 0.6)` with `backdrop-filter: blur(4px)` (matches SearchModal)
- Modal z-index: `9990` (matches SearchModal)
- Max-width: `960px` (3 columns), `640px` (2 columns)
- Column divider: `1px solid var(--color-border-light)`
- Price: copper color, same size as card price
- CTA button: full-width copper pill, matches StickyCTA WhatsApp button style
- "Remove" link: small, text-secondary, below CTA
- Close button: top-right "X", 40x40px touch target

---

## 5. Translations

New namespace `compare` in `src/data/translations.ts`:

```typescript
compare: {
  add: string;           // "Compare" / "Сравнить"
  remove: string;        // "Remove" / "Убрать"
  compare: string;       // "Compare" / "Сравнить"
  compareN: string;      // "Compare ({n})" / "Сравнить ({n})"
  clearAll: string;      // "Clear all" / "Очистить"
  maxItems: string;      // "Max 3 items" / "Максимум 3"
  title: string;         // "Compare Services" / "Сравнение услуг"
  duration: string;      // "Duration" / "Длительность"
  location: string;      // "Location" / "Город"
  rating: string;        // "Rating" / "Рейтинг"
  reviews: string;       // "reviews" / "отзывов"
  price: string;         // "Price" / "Цена"
  highlights: string;    // "Highlights" / "Особенности"
  bookVia: string;       // "Book via WhatsApp" / "Забронировать в WhatsApp"
  emptyState: string;    // "Select services to compare" / "Выберите услуги для сравнения"
  removeItem: string;    // "Remove from comparison" / "Убрать из сравнения"
}
```

**RU values:**
```typescript
compare: {
  add: "Сравнить",
  remove: "Убрать",
  compare: "Сравнить",
  compareN: "Сравнить",
  clearAll: "Очистить",
  maxItems: "Максимум 3",
  title: "Сравнение услуг",
  duration: "Длительность",
  location: "Город",
  rating: "Рейтинг",
  reviews: "отзывов",
  price: "Цена",
  highlights: "Особенности",
  bookVia: "Забронировать в WhatsApp",
  emptyState: "Выберите услуги для сравнения",
  removeItem: "Убрать из сравнения",
}
```

**EN values:**
```typescript
compare: {
  add: "Compare",
  remove: "Remove",
  compare: "Compare",
  compareN: "Compare",
  clearAll: "Clear all",
  maxItems: "Max 3 items",
  title: "Compare Services",
  duration: "Duration",
  location: "Location",
  rating: "Rating",
  reviews: "reviews",
  price: "Price",
  highlights: "Highlights",
  bookVia: "Book via WhatsApp",
  emptyState: "Select services to compare",
  removeItem: "Remove from comparison",
}
```

---

## 6. Analytics Events

New events in `src/lib/analytics.ts`:

| Event Name | Category | Label | When |
|------------|----------|-------|------|
| `compare_add` | `compare` | `{slug}` | User adds item to compare |
| `compare_remove` | `compare` | `{slug}` | User removes item from compare |
| `compare_open_modal` | `compare` | `{count}` | User opens compare modal |
| `compare_close_modal` | `compare` | `{count}` | User closes compare modal |
| `compare_click_whatsapp` | `conversion` | `{slug}` | User clicks WhatsApp CTA inside compare modal |
| `compare_clear_all` | `compare` | `{count}` | User clears all compared items |

```typescript
// Addition to events object in analytics.ts
compareAdd: (slug: string) => trackEvent("compare_add", "compare", slug),
compareRemove: (slug: string) => trackEvent("compare_remove", "compare", slug),
compareOpenModal: (count: number) => trackEvent("compare_open_modal", "compare", String(count)),
compareCloseModal: (count: number) => trackEvent("compare_close_modal", "compare", String(count)),
compareClickWhatsApp: (slug: string) => trackEvent("compare_click_whatsapp", "conversion", slug),
compareClearAll: (count: number) => trackEvent("compare_clear_all", "compare", String(count)),
```

---

## 7. ServiceCard Modification

The `ServiceCard` component needs minimal changes:

### New prop
```typescript
interface ServiceCardProps {
  // ... existing props ...
  showCompare?: boolean;    // default: false — only true on catalog pages
  categoryPath?: string;    // needed for compare context (e.g. "/excursions")
}
```

### Render change
Inside the image container (`<div className="relative overflow-hidden">`), add CompareCheckbox next to FavoriteButton:

```tsx
{/* Compare checkbox — top-left */}
{showCompare && categoryPath && slug && (
  <div className="absolute" style={{ top: "var(--space-2)", left: "var(--space-2)", zIndex: 10 }}>
    <CompareCheckbox slug={slug} categoryPath={categoryPath} />
  </div>
)}

{/* Favorite heart — top-right (existing) */}
{cardSlug && (
  <div className="absolute" style={{ top: "var(--space-2)", right: "var(--space-2)", zIndex: 10 }}>
    <FavoriteButton slug={cardSlug} variant="card" />
  </div>
)}
```

**Badge conflict:** The existing badge occupies `top: var(--space-3), left: var(--space-3)`. When badge is present, the CompareCheckbox position should shift down: `top: badge ? "calc(var(--space-3) + 34px)" : "var(--space-2)"`. The badge height is approximately 28-30px (padding 6px + font ~16px), so 34px offset ensures no overlap.

### CatalogPage change
Pass `showCompare` and `categoryPath` to each ServiceCard:

```tsx
<ServiceCard
  key={service.slug}
  // ... existing props ...
  showCompare={true}
  categoryPath={categoryPath}
/>
```

Add CompareBar after the grid:

```tsx
<CompareBar />
```

Where CompareBar is loaded with `next/dynamic`:
```tsx
const CompareBar = dynamic(() => import("@/components/CompareBar"), { ssr: false });
```

---

## 8. Interaction Flow

### Happy Path
1. User opens `/excursions` catalog page
2. Browses cards, sees compare checkbox (top-left) on each card
3. Clicks checkbox on "Desert Safari" card — checkbox fills with copper, CompareBar slides up from bottom showing 1 thumbnail
4. Clicks checkbox on "Abu Dhabi City Tour" — CompareBar updates to show 2 thumbnails + "Compare (2)" button
5. Clicks "Compare (2)" button on CompareBar
6. CompareModal opens with side-by-side columns
7. User reviews price, duration, rating, highlights
8. Clicks "Book via WhatsApp" on the preferred service
9. WhatsApp opens with pre-filled message: "Hi! I'm interested in Desert Safari. Can you help me book?"

### Edge Cases

| Scenario | Behavior |
|----------|----------|
| User selects 3rd item, then tries to add 4th | Checkbox disabled (opacity 0.4), tooltip "Max 3" |
| User navigates from /excursions to /tickets | CompareBar persists (localStorage), items from /excursions still shown |
| User removes all items from CompareBar | CompareBar slides down and hides |
| User opens modal with 1 item | Modal opens but shows single column with message "Add more services to compare" |
| User refreshes page | Compare state restored from localStorage |
| Service has no highlights | "Highlights" row shows "—" for that column |
| Service has no oldPrice | Only current price shown (no strikethrough) |
| User clicks card area (not checkbox) | Navigates to detail page (existing behavior, unchanged) |
| Mobile user with CatalogStickyBar visible | CompareBar appears above CatalogStickyBar (higher z-index by 1) |
| User opens mobile menu | CompareBar hides (same pattern as CatalogStickyBar) |
| Footer becomes visible | CompareBar hides (IntersectionObserver pattern) |

---

## 9. Accessibility

| Requirement | Implementation |
|-------------|---------------|
| Keyboard navigation | CompareCheckbox is a `<button>` with `tabIndex={0}`, activates on Enter/Space |
| Screen reader | `aria-label` on checkbox: "Add Desert Safari to comparison" / "Remove Desert Safari from comparison" |
| Screen reader | CompareBar has `role="status"` and `aria-live="polite"` to announce count changes |
| Screen reader | CompareModal has `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing to title |
| Focus trap | Modal traps focus (Tab cycles within modal, Shift+Tab wraps) |
| Escape key | Closes modal |
| Reduced motion | Transitions respect `prefers-reduced-motion: reduce` |
| Touch target | All interactive elements >= 44x44px touch area (buttons, checkboxes) |
| Color contrast | Copper on white (#C4896E on #FFFFFF) is 3.2:1 — for decorative/large text only. Labels use `--color-text-primary` (#1A1714) which is 16:1 |

---

## 10. Performance

| Concern | Mitigation |
|---------|------------|
| Bundle size | CompareModal loaded via `next/dynamic` (code-split), only fetched when user opens it |
| CompareBar render | Lightweight — only renders slug list + tiny thumbnails, no heavy computation |
| localStorage reads | Cached with `useSyncExternalStore` + snapshot memoization (same as favorites) |
| Re-renders | `useSyncExternalStore` ensures components only re-render when localStorage actually changes |
| Data resolution | `resolveServices` is O(n) scan of ~236 items — negligible, runs only when modal opens |
| Images in modal | Use `<ImageWithSkeleton>` (existing component) with `loading="lazy"` |
| Thumbnails in bar | Tiny (40px) — browser cache hit since catalog cards already loaded the same URLs |

---

## 11. Mobile Considerations

Since 70%+ of traffic is mobile:

| Aspect | Design Decision |
|--------|----------------|
| CompareCheckbox size | 32x32px button, 44x44px touch area (extra padding) |
| CompareBar height | 56px + safe-area-inset-bottom |
| CompareBar layout | Thumbnails left, "Compare" button right, "Clear" is "x" icon |
| CompareModal | Full-screen (100vh, 100vw) on mobile, no margin |
| Modal columns | Horizontal scroll with `scroll-snap-type: x mandatory` on mobile |
| Each column width | `min-width: 280px` on mobile scroll |
| CTA button | Full-width per column, 48px height |
| Interaction with CatalogStickyBar | CompareBar z-index = `calc(var(--z-sticky) + 1)` — appears above |
| Spacer element | Dynamic spacer div (same pattern as StickyCTA) prevents content cutoff |

---

## 12. Dependency Map

```
useCompare.ts (hook)
  ├── CompareCheckbox.tsx (reads isComparing, toggleCompare, isFull)
  ├── CompareBar.tsx (reads items, count, clearAll)
  │   └── CompareModal.tsx (reads items, removeFromCompare, clearAll)
  │       └── compare-resolver.ts (resolves slugs to BaseService[])
  │           └── search-index.ts / data/*.ts (data source)
  └── analytics.ts (event tracking)

ServiceCard.tsx
  └── CompareCheckbox.tsx (conditional render via showCompare prop)

CatalogPage.tsx
  ├── ServiceCard.tsx (passes showCompare + categoryPath)
  └── CompareBar.tsx (rendered at page level)

translations.ts
  └── compare namespace (consumed by all compare components)
```

---

## 13. Implementation Plan

### Phase 1: Core Hook + Checkbox (Day 1)
1. Create `src/hooks/useCompare.ts` — localStorage + useSyncExternalStore
2. Create `src/components/CompareCheckbox.tsx` — checkbox button
3. Modify `src/components/ServiceCard.tsx` — add `showCompare` prop + CompareCheckbox
4. Modify `src/components/CatalogPage.tsx` — pass `showCompare={true}` to cards
5. Add `compare` namespace to `src/data/translations.ts`
6. **Test:** Toggle compare on cards, verify localStorage updates, verify cross-tab sync

### Phase 2: Floating Bar (Day 1-2)
1. Create `src/components/CompareBar.tsx` — floating bar with thumbnails
2. Add to `CatalogPage.tsx` — render below grid
3. Implement show/hide logic (menu-open, footer-visible, count === 0)
4. Add analytics events to `src/lib/analytics.ts`
5. **Test:** Bar appears/disappears correctly, thumbnails update, mobile layout

### Phase 3: Comparison Modal (Day 2)
1. Create `src/lib/compare-resolver.ts` — slug-to-BaseService resolver
2. Create `src/components/CompareModal.tsx` — side-by-side table
3. Dynamic import in CompareBar
4. WhatsApp CTA per column with pre-filled message
5. Mobile horizontal scroll layout
6. **Test:** Modal opens, data correct, WhatsApp links work, Escape closes, focus trap

### Phase 4: Polish + QA (Day 3)
1. Accessibility audit (keyboard nav, screen reader, focus trap)
2. Mobile testing (various screen sizes, safe-area-inset)
3. Edge case testing (1 item, 3 items, refresh, cross-page navigation)
4. Animation polish (slide transitions, reduced motion)
5. Brand consistency review (copper tones, font hierarchy, spacing)

**Estimated total effort:** 3 days (1 developer)

---

## 14. Testing Checklist

### Functional
- [ ] Add item to compare from catalog card
- [ ] Remove item from compare via checkbox toggle
- [ ] Remove item from compare via CompareBar thumbnail "x"
- [ ] Remove item from compare via modal "Remove" button
- [ ] Clear all items via CompareBar
- [ ] CompareBar appears when count >= 1
- [ ] CompareBar hides when count === 0
- [ ] CompareBar hides when mobile menu opens
- [ ] CompareBar hides when footer is visible
- [ ] Modal opens with correct data for 2 items
- [ ] Modal opens with correct data for 3 items
- [ ] Modal shows "add more" message for 1 item
- [ ] 4th item checkbox is disabled when 3 items selected
- [ ] WhatsApp CTA opens correct pre-filled message
- [ ] State persists after page navigation (catalog to catalog)
- [ ] State persists after page refresh
- [ ] Cross-category comparison works (excursion + ticket)

### i18n
- [ ] All text shows correctly in RU
- [ ] All text shows correctly in EN
- [ ] Language switch updates compare UI instantly

### Responsive
- [ ] Desktop: 2-3 column modal layout
- [ ] Tablet: 2 column modal layout
- [ ] Mobile: horizontal scroll modal layout
- [ ] CompareBar adapts to mobile width
- [ ] Safe area inset respected on iOS

### Accessibility
- [ ] Checkbox reachable via Tab key
- [ ] Checkbox activates via Enter/Space
- [ ] Modal traps focus
- [ ] Escape closes modal
- [ ] Screen reader announces checkbox state changes
- [ ] Screen reader announces compare count changes

### Performance
- [ ] CompareModal is code-split (not in initial bundle)
- [ ] No layout shift when CompareBar appears
- [ ] Smooth 60fps animations

---

## 15. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| CompareBar conflicts with CatalogStickyBar (mobile) | Visual overlap, confusing UX | CompareBar gets z-index +1 above CatalogStickyBar; both share hide-on-footer logic |
| Badge + CompareCheckbox overlap on card | Visual clutter in top-left | Dynamic positioning: checkbox shifts down when badge present |
| Too many localStorage keys | Minor — localStorage has 5MB limit | All compare data is one key, max ~200 bytes |
| User compares services from different categories | Mismatch in available attributes | Show "—" for missing fields; all services share BaseService fields so core attributes always exist |
| Modal performance with 3 high-res images | Slow modal open on 3G | Use `ImageWithSkeleton` with lazy loading; modal images are thumbnail-size (not full gallery images) |

---

## 16. Competitor Reference

| Feature | Klook | Kayak | Booking.com | Our Implementation |
|---------|-------|-------|-------------|-------------------|
| Max items | 4 | 3 | 3 | 3 |
| Compare trigger | Checkbox on card | "Compare" button | Heart + compare | Checkbox overlay on card |
| Floating bar | Yes, bottom | Yes, bottom | No (inline) | Yes, bottom floating bar |
| Comparison view | Side-by-side table | Side-by-side cards | Side-by-side modal | Side-by-side modal |
| Cross-category | No (same category only) | N/A (flights only) | Yes (hotels + apartments) | Yes (any services) |
| Mobile layout | Horizontal scroll | Stacked | Horizontal scroll | Horizontal scroll with snap |
| CTA | "Book" button | "View deal" | "Reserve" | WhatsApp CTA (brand-specific) |
| Persist state | Session only | No | Session only | localStorage (persists) |

---

## 17. Open Questions

| # | Question | Default if no answer |
|---|----------|---------------------|
| 1 | Should compare be restricted to same-category items only? | No — allow cross-category (users compare excursion vs ticket combo) |
| 2 | Should compare checkbox appear on homepage FeaturedServices cards? | No — catalog pages only in MVP |
| 3 | Should the modal show the "included/not included" lists? | No — too verbose for comparison; highlights suffice for MVP |
| 4 | Should there be a "Compare" page (URL route) instead of modal? | No — modal is lighter; URL route is a future enhancement |
| 5 | Should compare state clear after 24 hours? | No — clear on explicit action only; localStorage persists until cleared |

---

## 18. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Compare feature usage | 5%+ of catalog visitors add at least 1 item | GA4 `compare_add` events / catalog page views |
| Modal open rate | 60%+ of users who add 2+ items open the modal | GA4 `compare_open_modal` / users with 2+ `compare_add` |
| WhatsApp conversion from compare | 15%+ of modal opens result in WhatsApp click | GA4 `compare_click_whatsapp` / `compare_open_modal` |
| Bounce rate reduction on catalog | -5% | GA4 catalog page bounce rate before/after |

---

## Appendix A: WhatsApp Pre-filled Message Template

**From CompareModal (per-service CTA):**
```
RU: "Здравствуйте! Сравнивал(а) услуги на сайте и хочу узнать подробнее о: {title}. Цена на сайте: {price} AED. Можно забронировать?"
EN: "Hi! I was comparing services on your website and I'd like to know more about: {title}. Price listed: {price} AED. Can I book?"
```

**Variables:** `{title}` = `BaseService.title[lang]`, `{price}` = `BaseService.price`

---

## Appendix B: CSS Custom Properties Used

All styling uses existing project CSS custom properties — no new variables needed:

| Property | Usage |
|----------|-------|
| `--color-copper` | Checkbox active, CTA buttons, price |
| `--color-copper-hover` | CTA hover state |
| `--color-border` | Bar border, column dividers |
| `--color-border-light` | Table row separators |
| `--color-text-primary` | Titles, labels |
| `--color-text-secondary` | Meta text, disabled states |
| `--color-text-tertiary` | Subtle hints |
| `--color-peach` | Modal header gradient accent |
| `--space-*` | All spacing (2, 3, 4, 5, 6, 8) |
| `--text-body-sm` | Body text, labels |
| `--text-price` | Price display |
| `--text-price-old` | Strikethrough old price |
| `--text-cta-sm` | CTA button text |
| `--weight-light/medium/semibold` | Font weights |
| `--radius-pill` | CTA button border-radius |
| `--z-sticky` | Floating bar z-index |
| `--shadow-sticky` | Floating bar shadow |
| `--duration-base/fast` | Transition durations |
| `--nav-height` | Used for modal positioning |
| `--font-body/heading` | Font families |
| `--tracking-cta/badge` | Letter spacing |
