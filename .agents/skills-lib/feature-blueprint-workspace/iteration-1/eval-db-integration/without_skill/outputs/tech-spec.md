# Tech Spec: Database Integration — vipdxbrus.com + tourism-crm

**Version:** 1.0
**Date:** 2026-03-14
**Author:** Claude Opus 4.6 (automated)
**Status:** DRAFT — awaiting owner approval

---

## 1. Executive Summary

Migrate the vipdxbrus.com website from 24 static TypeScript data files (`src/data/*.ts`) to a PostgreSQL database shared with the existing tourism-crm application. This enables real-time content management, real booking workflows, persistent AI chat history, server-synced favorites, and verified customer reviews.

**Current state:** 236 products hardcoded across 13 category files, 52 demo reviews, mock booking availability generated via deterministic pseudo-random algorithm, AI chat with no history persistence, favorites in localStorage only.

**Target state:** All product data served from PostgreSQL (Neon, eu-central-1), managed through tourism-crm admin UI, with real-time availability, persistent user sessions, and server-synced state.

---

## 2. Scope

### In scope (5 domains)

| # | Domain | Current State | Target State |
|---|--------|---------------|--------------|
| 1 | **Product Catalog** | 24 `.ts` files, 236 products, BiText fields | CRM `Product` model + new website-specific extensions |
| 2 | **Booking / Availability** | `generateMockAvailability()` — deterministic fake data | Real time slots from DB, tied to CRM `Order` flow |
| 3 | **Reviews** | 52 hardcoded `Review` objects in `reviews.ts` | DB-backed reviews linked to CRM `CustomerReview` + website-specific fields |
| 4 | **AI Chat** | In-memory `chatHistoryRef` (lost on page refresh) | Persistent conversations in DB, linked to anonymous/authenticated sessions |
| 5 | **Favorites / Wishlist** | `localStorage` via `useSyncExternalStore` | Server-synced for authenticated users, localStorage fallback for anonymous |

### Out of scope (Phase 4+)

- User authentication / registration UI on the website
- Payment processing (stays WhatsApp-based for now)
- Full CMS / admin panel for website content (managed via CRM)
- Real-time notifications / WebSockets
- Server-side i18n (stays client-side `LanguageContext`)
- Trip Planner Phase B, Flights Phase B

---

## 3. Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                    Cloudflare Tunnel                  │
│                   vipdxbrus.com                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Next.js 15 (vipdxbrus-website)                      │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │ Server       │  │ Client       │                  │
│  │ Components   │  │ Components   │                  │
│  │ (page.tsx)   │  │ (*Client.tsx)│                  │
│  └──────┬───────┘  └──────┬───────┘                  │
│         │                 │                          │
│  ┌──────▼─────────────────▼───────┐                  │
│  │     API Routes (Next.js)       │                  │
│  │  /api/products                 │                  │
│  │  /api/availability             │                  │
│  │  /api/reviews                  │                  │
│  │  /api/chat (existing)          │                  │
│  │  /api/favorites                │                  │
│  │  /api/session                  │                  │
│  └──────────────┬─────────────────┘                  │
│                 │                                    │
├─────────────────┼────────────────────────────────────┤
│                 │ Prisma Client (shared schema)      │
│                 ▼                                    │
│  ┌──────────────────────────────────┐                │
│  │  Neon PostgreSQL (eu-central-1)  │                │
│  │  ┌──────────┐  ┌──────────────┐  │                │
│  │  │ CRM      │  │ Website      │  │                │
│  │  │ Tables   │  │ Tables       │  │                │
│  │  │ (49      │  │ (new, ws_    │  │                │
│  │  │  models) │  │  prefix)     │  │                │
│  │  └──────────┘  └──────────────┘  │                │
│  └──────────────────────────────────┘                │
│                 ▲                                    │
│                 │ Prisma Client                       │
│  ┌──────────────┴─────────────────┐                  │
│  │  Next.js 16 (tourism-crm)      │                  │
│  │  tourism-crm.vercel.app        │                  │
│  └────────────────────────────────┘                  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Key architectural decisions

1. **Shared database, separate schemas (table prefixes).** Both apps connect to the same Neon PostgreSQL instance. Website-specific tables use `ws_` prefix (e.g., `ws_reviews`, `ws_chat_sessions`). CRM tables remain unchanged.

2. **Separate Prisma schemas.** The website gets its own `prisma/schema.prisma` that imports only the CRM models it needs (read-only) plus website-specific models. This avoids schema conflicts and allows independent migrations.

3. **Data access layer.** A new `src/lib/db/` directory provides typed service functions (e.g., `getProducts()`, `getAvailability()`) that abstract the database. Components never import Prisma directly.

4. **ISR (Incremental Static Regeneration).** Product catalog pages use `revalidate: 300` (5 minutes). This maintains the current static generation performance while allowing CRM updates to propagate within 5 minutes without redeploying.

5. **Graceful degradation.** If the database is unreachable, the site falls back to a static JSON cache generated at build time. Critical for uptime.

---

## 4. Database Schema Design

### 4.1 Reused CRM Models (read-only from website)

The website reads these CRM tables directly:

| CRM Model | Website Usage |
|-----------|---------------|
| `Product` | Core product data (name, description, price, category, images) |
| `ProductPhoto` | Product image gallery |
| `ProductFaq` | FAQ tab content |
| `Supplier` | Supplier info for availability blackouts |
| `SupplierBlackout` | Dates when service is unavailable |
| `SeasonalPrice` | Dynamic pricing per season |
| `Customer` | Linked to reviews (optional) |

### 4.2 New Website Models (ws_ prefix)

```prisma
// ================================================
// WEBSITE PRODUCT EXTENSION
// Supplements CRM Product with website-specific fields
// ================================================

model WsProductExtension {
  id              String   @id @default(cuid())
  productId       String   @unique @map("product_id")

  // Slug for URL routing (CRM uses SKU, website uses slug)
  slug            String   @unique

  // Website-specific content (BiText pattern: RU + EN)
  fullDescriptionRu  String?  @map("full_description_ru")
  fullDescriptionEn  String?  @map("full_description_en")

  // Duration display text
  durationRu      String?  @map("duration_ru")
  durationEn      String?  @map("duration_en")

  // Location display text
  locationRu      String?  @map("location_ru")
  locationEn      String?  @map("location_en")

  // Badge (e.g., "Хит", "Новинка")
  badgeRu         String?  @map("badge_ru")
  badgeEn         String?  @map("badge_en")

  // What's included / not included (JSON arrays of BiText)
  included        Json?    // [{ru: "...", en: "..."}]
  notIncluded     Json?    @map("not_included")
  highlights      Json?

  // Directions / How to get there
  directions      Json?    // Directions type as JSON

  // WhatsApp booking message template
  whatsappTextRu  String?  @map("whatsapp_text_ru")
  whatsappTextEn  String?  @map("whatsapp_text_en")

  // Category-specific extended fields (stored as JSON)
  // e.g., for Yacht: {brand, length, capacity, cabins, crew, pricePerHour, minHours, marina}
  // e.g., for Ticket: {park, tiers, skipLine, validityDays}
  typeSpecificData Json?   @map("type_specific_data")

  // Filter values for catalog filtering
  filterValues    Json?    @map("filter_values")

  // SEO
  seoTitleRu      String?  @map("seo_title_ru")
  seoTitleEn      String?  @map("seo_title_en")
  seoDescRu       String?  @map("seo_desc_ru")
  seoDescEn       String?  @map("seo_desc_en")

  // Promo
  promoEndDate    DateTime? @map("promo_end_date")
  oldPrice        Decimal?  @map("old_price") @db.Decimal(10, 2)

  // Display order
  sortOrder       Int      @default(0) @map("sort_order")
  isPublished     Boolean  @default(true) @map("is_published")

  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  // Relations
  availability    WsAvailabilitySlot[]
  reviews         WsReview[]
  experienceCards WsExperienceCard[]
  itinerarySteps  WsItineraryStep[]

  @@index([slug])
  @@index([isPublished])
  @@index([sortOrder])
  @@map("ws_product_extensions")
}

// ================================================
// EXPERIENCE CARDS (photo + caption for product pages)
// ================================================

model WsExperienceCard {
  id          String  @id @default(cuid())
  extensionId String  @map("extension_id")
  extension   WsProductExtension @relation(fields: [extensionId], references: [id], onDelete: Cascade)
  image       String
  captionRu   String? @map("caption_ru")
  captionEn   String? @map("caption_en")
  sortOrder   Int     @default(0) @map("sort_order")

  @@index([extensionId])
  @@map("ws_experience_cards")
}

// ================================================
// ITINERARY STEPS (for excursions)
// ================================================

model WsItineraryStep {
  id          String  @id @default(cuid())
  extensionId String  @map("extension_id")
  extension   WsProductExtension @relation(fields: [extensionId], references: [id], onDelete: Cascade)
  time        String  // "09:00"
  pointRu     String  @map("point_ru")
  pointEn     String  @map("point_en")
  sortOrder   Int     @default(0) @map("sort_order")

  @@index([extensionId])
  @@map("ws_itinerary_steps")
}

// ================================================
// AVAILABILITY & BOOKING SLOTS
// Replaces generateMockAvailability()
// ================================================

model WsAvailabilitySlot {
  id              String   @id @default(cuid())
  extensionId     String   @map("extension_id")
  extension       WsProductExtension @relation(fields: [extensionId], references: [id], onDelete: Cascade)

  date            DateTime @db.Date
  time            String   // "09:00", "14:00", "18:00"
  labelRu         String?  @map("label_ru")
  labelEn         String?  @map("label_en")

  maxCapacity     Int      @map("max_capacity")
  bookedCount     Int      @default(0) @map("booked_count")
  price           Decimal  @db.Decimal(10, 2)

  status          String   @default("available") // available | full | blocked
  blockedReason   String?  @map("blocked_reason")

  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  bookingRequests WsBookingRequest[]

  @@unique([extensionId, date, time])
  @@index([extensionId, date])
  @@index([date])
  @@index([status])
  @@map("ws_availability_slots")
}

model WsBookingRequest {
  id              String   @id @default(cuid())
  slotId          String   @map("slot_id")
  slot            WsAvailabilitySlot @relation(fields: [slotId], references: [id])

  // Can link to CRM Order once confirmed
  crmOrderId      String?  @map("crm_order_id")

  // Guest info (may not have CRM customer record yet)
  guestName       String?  @map("guest_name")
  guestPhone      String?  @map("guest_phone")
  guestEmail      String?  @map("guest_email")

  participants    Int      @default(1)
  totalPrice      Decimal  @db.Decimal(10, 2) @map("total_price")
  currency        String   @default("AED")

  status          String   @default("pending") // pending | confirmed | cancelled
  source          String   @default("website") // website | whatsapp | crm

  notes           String?
  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  @@index([slotId])
  @@index([crmOrderId])
  @@index([status])
  @@index([createdAt])
  @@map("ws_booking_requests")
}

// ================================================
// REVIEWS
// Extends CRM CustomerReview with website-display fields
// ================================================

model WsReview {
  id              String   @id @default(cuid())
  extensionId     String   @map("extension_id")
  extension       WsProductExtension @relation(fields: [extensionId], references: [id], onDelete: Cascade)

  // Optional link to CRM customer review
  crmReviewId     String?  @map("crm_review_id")

  // Author info (displayed on website)
  authorRu        String   @map("author_ru")
  authorEn        String   @map("author_en")
  cityRu          String?  @map("city_ru")
  cityEn          String?  @map("city_en")

  date            DateTime @db.Date
  rating          Int      // 1-5

  // Review text (BiText)
  textRu          String   @map("text_ru")
  textEn          String   @map("text_en")

  // Review photos (URLs)
  photos          String[] @default([])

  // Verification
  verified        Boolean  @default(false)
  verifiedSource  String?  @map("verified_source") // whatsapp | google | manual

  // Owner response (BiText)
  responseRu      String?  @map("response_ru")
  responseEn      String?  @map("response_en")

  // Moderation
  isApproved      Boolean  @default(false) @map("is_approved")
  isPublished     Boolean  @default(false) @map("is_published")

  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  @@index([extensionId])
  @@index([rating])
  @@index([isPublished])
  @@index([date])
  @@map("ws_reviews")
}

// ================================================
// AI CHAT SESSIONS
// Persists conversation history
// ================================================

model WsChatSession {
  id              String   @id @default(cuid())

  // Anonymous session ID (cookie-based) or authenticated user
  sessionToken    String   @unique @map("session_token")
  crmCustomerId   String?  @map("crm_customer_id")

  // Session metadata
  language        String   @default("ru") // ru | en
  userAgent       String?  @map("user_agent")
  ipAddress       String?  @map("ip_address")

  // Rate limiting
  messageCount    Int      @default(0) @map("message_count")
  lastMessageAt   DateTime? @map("last_message_at")

  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  messages        WsChatMessage[]

  @@index([sessionToken])
  @@index([crmCustomerId])
  @@index([createdAt])
  @@map("ws_chat_sessions")
}

model WsChatMessage {
  id              String   @id @default(cuid())
  sessionId       String   @map("session_id")
  session         WsChatSession @relation(fields: [sessionId], references: [id], onDelete: Cascade)

  role            String   // user | assistant
  content         String

  // Token usage tracking (for cost monitoring)
  inputTokens     Int?     @map("input_tokens")
  outputTokens    Int?     @map("output_tokens")

  createdAt       DateTime @default(now()) @map("created_at")

  @@index([sessionId])
  @@index([createdAt])
  @@map("ws_chat_messages")
}

// ================================================
// FAVORITES (server-synced)
// ================================================

model WsFavorite {
  id              String   @id @default(cuid())

  // Session-based (anonymous) or customer-based
  sessionToken    String?  @map("session_token")
  crmCustomerId   String?  @map("crm_customer_id")

  productSlug     String   @map("product_slug")

  createdAt       DateTime @default(now()) @map("created_at")

  @@unique([sessionToken, productSlug])
  @@unique([crmCustomerId, productSlug])
  @@index([sessionToken])
  @@index([crmCustomerId])
  @@map("ws_favorites")
}

// ================================================
// CATEGORY CONFIGURATION
// Replaces hardcoded CategoryConfig objects
// ================================================

model WsCategoryConfig {
  id              String   @id @default(cuid())
  key             String   @unique // "excursions", "tickets", etc.

  titleRu         String   @map("title_ru")
  titleEn         String   @map("title_en")
  subtitleRu      String?  @map("subtitle_ru")
  subtitleEn      String?  @map("subtitle_en")
  seoTextRu       String?  @map("seo_text_ru")
  seoTextEn       String?  @map("seo_text_en")
  heroImage       String?  @map("hero_image")

  // Filter configuration (JSON)
  filters         Json?    // FilterGroup[]

  sortOrder       Int      @default(0) @map("sort_order")
  isActive        Boolean  @default(true) @map("is_active")

  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  @@map("ws_category_configs")
}

// ================================================
// BUNDLES
// Replaces bundles.ts
// ================================================

model WsBundle {
  id              String   @id @default(cuid())

  slug1           String   // First product slug
  slug2           String   // Second product slug
  comboPrice      Decimal  @map("combo_price") @db.Decimal(10, 2)
  savings         Decimal  @db.Decimal(10, 2)

  titleRu         String   @map("title_ru")
  titleEn         String   @map("title_en")

  isActive        Boolean  @default(true) @map("is_active")
  sortOrder       Int      @default(0) @map("sort_order")

  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  @@unique([slug1, slug2])
  @@map("ws_bundles")
}
```

### 4.3 Category-to-CRM mapping

The website has 15 service types; CRM has 10 `ProductCategory` enum values. Mapping:

| Website Type | CRM ProductCategory | Notes |
|-------------|---------------------|-------|
| `excursion` | `CITY_TOUR`, `DESERT`, `GROUP_TOUR`, `INDIVIDUAL_TOUR` | Map by subcategory |
| `ticket` | `TICKETS` | Direct |
| `yacht` | `YACHT` | Direct |
| `transfer` | `TRANSFER` | Direct |
| `combo` | `COMBO` | Direct |
| `water-activity` | `WATER` | Direct |
| `buggy` | `DESERT` | Subcategory = "buggy" |
| `beach-club` | (new) | Add to CRM enum or use subcategory |
| `restaurant` | (new) | Add to CRM enum or use subcategory |
| `pool` | (new) | Add to CRM enum or use subcategory |
| `hotel` | (new) | Add to CRM enum or use subcategory |
| `car-rental` | `CAR_RENTAL` | Direct |
| `additional-service` | (new) | Add to CRM enum or use subcategory |

**Decision needed:** Either extend CRM's `ProductCategory` enum with `BEACH_CLUB`, `RESTAURANT`, `POOL`, `HOTEL`, `ADDITIONAL_SERVICE` -- OR use a `subcategory` string field on the CRM Product model (it already has one). Recommended: use `subcategory` to avoid CRM schema migration for categories that CRM doesn't directly manage.

---

## 5. Data Access Layer

### 5.1 Directory structure

```
src/
├── lib/
│   └── db/
│       ├── prisma.ts           # Prisma client singleton
│       ├── products.ts         # getProducts(), getProductBySlug(), getProductsByCategory()
│       ├── availability.ts     # getAvailability(), createBookingRequest()
│       ├── reviews.ts          # getReviews(), submitReview(), getAverageRating()
│       ├── chat.ts             # getChatSession(), saveChatMessage()
│       ├── favorites.ts        # getFavorites(), toggleFavorite()
│       ├── bundles.ts          # getBundles()
│       ├── categories.ts       # getCategoryConfig()
│       └── cache.ts            # Static JSON cache generation + fallback
```

### 5.2 Prisma client singleton

```typescript
// src/lib/db/prisma.ts
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma = globalForPrisma.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

### 5.3 Product service (example)

```typescript
// src/lib/db/products.ts
import { prisma } from './prisma';
import { unstable_cache } from 'next/cache';

export interface WebsiteProduct {
  slug: string;
  type: string;
  title: { RU: string; EN: string };
  description: { RU: string; EN: string };
  fullDescription: { RU: string; EN: string };
  price: number;
  oldPrice?: number;
  rating: number;
  reviewCount: number;
  image: string;
  images: string[];
  // ... all BaseService fields
  typeSpecificData: Record<string, unknown>;
}

// Cached product fetch with 5-minute revalidation
export const getProducts = unstable_cache(
  async (category?: string): Promise<WebsiteProduct[]> => {
    const extensions = await prisma.wsProductExtension.findMany({
      where: {
        isPublished: true,
        ...(category ? { /* filter by CRM product category */ } : {}),
      },
      include: {
        reviews: { where: { isPublished: true } },
        experienceCards: { orderBy: { sortOrder: 'asc' } },
        itinerarySteps: { orderBy: { sortOrder: 'asc' } },
      },
      orderBy: { sortOrder: 'asc' },
    });

    // Join with CRM Product data
    const productIds = extensions.map(e => e.productId);
    const crmProducts = await prisma.product.findMany({
      where: { id: { in: productIds } },
      include: { photos: true, faqs: true },
    });

    // Merge and transform
    return extensions.map(ext => {
      const crm = crmProducts.find(p => p.id === ext.productId);
      return transformToWebsiteProduct(ext, crm);
    });
  },
  ['products'],
  { revalidate: 300, tags: ['products'] }
);

export const getProductBySlug = unstable_cache(
  async (slug: string): Promise<WebsiteProduct | null> => {
    // ... similar pattern
  },
  ['product-by-slug'],
  { revalidate: 300, tags: ['products'] }
);
```

### 5.4 Static fallback cache

At build time, generate a JSON snapshot:

```typescript
// src/lib/db/cache.ts
import fs from 'fs';
import path from 'path';

const CACHE_DIR = path.join(process.cwd(), '.cache');

export async function generateStaticCache() {
  const products = await getProducts();
  fs.mkdirSync(CACHE_DIR, { recursive: true });
  fs.writeFileSync(
    path.join(CACHE_DIR, 'products.json'),
    JSON.stringify(products)
  );
  // ... same for reviews, categories, bundles
}

export function getStaticFallback<T>(key: string): T | null {
  try {
    const filePath = path.join(CACHE_DIR, `${key}.json`);
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch {
    return null;
  }
}
```

---

## 6. API Routes

### 6.1 New routes

| Route | Method | Purpose | Auth |
|-------|--------|---------|------|
| `GET /api/products` | GET | List products (with filters, pagination) | Public |
| `GET /api/products/[slug]` | GET | Single product detail | Public |
| `GET /api/products/[slug]/availability` | GET | Availability slots for next 3 months | Public |
| `POST /api/booking-request` | POST | Submit booking request (pre-WhatsApp) | Public |
| `GET /api/reviews` | GET | List reviews (by product slug) | Public |
| `POST /api/reviews` | POST | Submit a new review | Public (rate-limited) |
| `POST /api/chat` | POST | Send chat message (existing, enhanced) | Public (rate-limited) |
| `GET /api/chat/history` | GET | Retrieve chat history for session | Session cookie |
| `GET /api/favorites` | GET | Get favorites for session | Session cookie |
| `POST /api/favorites` | POST | Toggle favorite | Session cookie |
| `GET /api/bundles` | GET | Get active bundles | Public |
| `GET /api/categories` | GET | Get category configs | Public |
| `POST /api/revalidate` | POST | Webhook to invalidate ISR cache | Secret token |

### 6.2 Revalidation webhook

CRM triggers this when product data changes:

```typescript
// src/app/api/revalidate/route.ts
import { revalidateTag } from 'next/cache';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const token = request.headers.get('x-revalidate-token');
  if (token !== process.env.REVALIDATE_SECRET) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { tags } = await request.json();
  // tags: ["products"] | ["reviews"] | ["availability"]
  for (const tag of tags) {
    revalidateTag(tag);
  }

  return Response.json({ revalidated: true });
}
```

---

## 7. Migration Strategy

### 7.1 Phases

```
Phase A: Schema + DAL + Dual-read          (2-3 weeks)
Phase B: Write paths + CRM integration     (2-3 weeks)
Phase C: Cut over + remove static files    (1 week)
Phase D: Advanced features                 (2-3 weeks)
```

### Phase A: Schema + Data Access Layer + Dual-read

**Goal:** Website reads from DB but falls back to static files. Zero user-facing changes.

1. **Add Prisma to vipdxbrus-website**
   ```bash
   npm install prisma @prisma/client
   npx prisma init
   ```

2. **Create website Prisma schema** with all `ws_*` models + read-only references to CRM models.

3. **Run migrations** against Neon PostgreSQL:
   ```bash
   DATABASE_URL="neon_url" npx prisma migrate dev --name init-website-tables
   ```

4. **Seed data:** Script to transform all 24 `.ts` files into database records:
   ```bash
   npx ts-node scripts/seed-from-static.ts
   ```
   This script reads each `src/data/*.ts` file, creates CRM `Product` records (if not existing, matched by name), creates `WsProductExtension` records with all website-specific fields, and creates `WsReview` records from `reviews.ts`.

5. **Build data access layer** (`src/lib/db/*.ts`).

6. **Dual-read pattern:** Each page/component checks DB first, falls back to static import:
   ```typescript
   const product = await getProductBySlug(slug) ?? getStaticProduct(slug);
   ```

7. **Deploy and verify:** No user-facing changes, but data now comes from DB when available.

**Files to create:**
- `prisma/schema.prisma` (website schema)
- `src/lib/db/prisma.ts`
- `src/lib/db/products.ts`
- `src/lib/db/reviews.ts`
- `src/lib/db/availability.ts`
- `src/lib/db/chat.ts`
- `src/lib/db/favorites.ts`
- `src/lib/db/bundles.ts`
- `src/lib/db/categories.ts`
- `src/lib/db/cache.ts`
- `scripts/seed-from-static.ts`

**Files to modify:**
- `package.json` (add Prisma dependencies)
- `next.config.ts` (add `serverExternalPackages: ['@prisma/client']` if needed)
- `.env.local` (add `DATABASE_URL`)
- `Dockerfile` (add `npx prisma generate` to build step)
- `.github/workflows/deploy.yml` (add DATABASE_URL secret)

### Phase B: Write Paths + CRM Integration

**Goal:** Enable real booking requests, review submissions, persistent chat, server-synced favorites.

1. **Booking requests:**
   - Replace `handleBook()` in `AvailabilityCalendar.tsx` to POST to `/api/booking-request` before opening WhatsApp.
   - Store booking request in `ws_booking_requests`.
   - CRM webhook or cron picks up pending requests and creates CRM Orders.

2. **Reviews:**
   - Build review submission form (component already has ReviewSection tab).
   - POST to `/api/reviews` with rate limiting + honeypot spam prevention.
   - Reviews default to `isApproved: false` (moderation via CRM).

3. **AI Chat persistence:**
   - Generate session token (cookie) on first chat open.
   - Store messages in `ws_chat_messages`.
   - Load history on page refresh via `/api/chat/history`.
   - Modify existing `/api/chat/route.ts` to save messages to DB.

4. **Favorites sync:**
   - Create session cookie for anonymous users.
   - POST/GET `/api/favorites` for server-synced state.
   - Keep localStorage as offline fallback.
   - Merge localStorage favorites into DB on first API call.

5. **CRM -> Website webhook:**
   - When CRM product is updated, call `/api/revalidate` to bust ISR cache.
   - When CRM admin approves a review, set `isPublished: true`.

**Files to create:**
- `src/app/api/products/route.ts`
- `src/app/api/products/[slug]/route.ts`
- `src/app/api/products/[slug]/availability/route.ts`
- `src/app/api/booking-request/route.ts`
- `src/app/api/reviews/route.ts`
- `src/app/api/chat/history/route.ts`
- `src/app/api/favorites/route.ts`
- `src/app/api/bundles/route.ts`
- `src/app/api/categories/route.ts`
- `src/app/api/revalidate/route.ts`
- `src/app/api/session/route.ts`

**Files to modify:**
- `src/app/api/chat/route.ts` (add DB persistence)
- `src/components/AvailabilityCalendar.tsx` (use real data, add booking API call)
- `src/components/ReviewSection.tsx` (add submission form)
- `src/components/AiAssistant.tsx` (load/save chat history)
- `src/hooks/useFavorites.ts` (add server sync)
- `src/components/FavoriteButton.tsx` (use updated hook)

### Phase C: Cut Over

**Goal:** Remove static data files, DB is the sole source of truth.

1. Remove dual-read fallback — DB only.
2. Delete or archive `src/data/*.ts` files (keep as backup reference).
3. Update `search-index.ts` to read from DB instead of static imports.
4. Update `generateStaticParams()` in all `[slug]/page.tsx` to query DB.
5. Full regression test.

**Files to delete/archive:**
- `src/data/excursions.ts`
- `src/data/tickets.ts`
- `src/data/yachts.ts`
- `src/data/transfers.ts`
- `src/data/combos.ts`
- `src/data/water-activities.ts`
- `src/data/buggies.ts`
- `src/data/beach-clubs.ts`
- `src/data/restaurants.ts`
- `src/data/pools.ts`
- `src/data/hotels.ts`
- `src/data/car-rentals.ts`
- `src/data/services.ts`
- `src/data/reviews.ts`
- `src/data/bundles.ts`
- `src/data/booking-availability.ts`
- `src/data/booking-types.ts`
- `src/data/faq.ts`
- `src/data/flights.ts` (keep if Flights Phase B not started)
- `src/data/city-data.ts` (keep until city pages also migrated)

**Files to modify:**
- `src/lib/search-index.ts` (replace 13 static imports with DB query)
- All `[slug]/page.tsx` files (update `generateStaticParams`)
- `src/data/types.ts` (keep as TypeScript interface definitions, but no longer export data)

### Phase D: Advanced Features

1. **Availability management UI in CRM:** CRUD for `ws_availability_slots`, bulk slot generation, blackout date management.
2. **Review moderation UI in CRM:** Approve/reject reviews, respond to reviews.
3. **Chat analytics dashboard:** View conversations, extract leads, link to CRM customers.
4. **Authenticated users:** Login via phone/WhatsApp OTP, persistent profile, favorites/reviews linked to customer.
5. **Real-time availability:** WebSocket or polling for slot updates during booking flow.

---

## 8. Data Seeding Script

### 8.1 Strategy

Transform the existing 24 static `.ts` data files into DB records. The script runs once during Phase A.

```typescript
// scripts/seed-from-static.ts
//
// 1. For each category (excursions, tickets, etc.):
//    a. Read the static array
//    b. Create or match CRM Product record (by name)
//    c. Create WsProductExtension with all BiText fields
//    d. Create related records (itinerary steps, experience cards)
//
// 2. Seed reviews from reviews.ts
//    a. Match by serviceSlug -> WsProductExtension.slug
//    b. Create WsReview records (all pre-approved, pre-published)
//
// 3. Seed category configs from each *Config export
//    a. Create WsCategoryConfig records
//
// 4. Seed bundles from bundles.ts
//    a. Create WsBundle records
//
// 5. Generate availability slots for next 3 months
//    a. For each product, create slots based on current mock algorithm
//    b. This provides initial data identical to current mock behavior
```

### 8.2 Data volume estimates

| Entity | Count | Notes |
|--------|-------|-------|
| Products (CRM) | 236 | New or matched to existing CRM products |
| Product Extensions | 236 | 1:1 with products |
| Experience Cards | ~200 | Estimated from data files |
| Itinerary Steps | ~50 | Excursions only |
| Reviews | 52 | All from reviews.ts |
| Category Configs | 13 | One per category |
| Bundles | 13 | From bundles.ts |
| Availability Slots | ~21,000 | 236 products x 90 days x ~1 slot avg |

---

## 9. Environment Variables

### New variables for vipdxbrus-website

| Variable | Required | Example | Where |
|----------|----------|---------|-------|
| `DATABASE_URL` | Yes | `postgresql://...@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require` | `.env.local`, Vercel/Docker |
| `REVALIDATE_SECRET` | Yes | Random 32-char string | `.env.local`, CRM env |
| `SESSION_SECRET` | Yes | Random 64-char string (for signing cookies) | `.env.local`, Docker |

### Variables to add to CRM (tourism-crm)

| Variable | Purpose |
|----------|---------|
| `WEBSITE_REVALIDATE_URL` | `https://vipdxbrus.com/api/revalidate` |
| `WEBSITE_REVALIDATE_SECRET` | Same as website's `REVALIDATE_SECRET` |

---

## 10. Component Impact Analysis

### Components that will change

| Component | Current Data Source | New Data Source | Complexity |
|-----------|-------------------|-----------------|------------|
| `CatalogPage.tsx` | Static import from category `.ts` | `getProducts(category)` via server component | Medium |
| `ServiceDetailPage.tsx` | Props from `page.tsx` (static) | Props from `page.tsx` (DB query) | Low |
| `AvailabilityCalendar.tsx` | `generateMockAvailability()` | `/api/products/[slug]/availability` | High |
| `ReviewSection.tsx` | Props (static reviews) | `/api/reviews?slug=X` + submission form | High |
| `AiAssistant.tsx` | In-memory `chatHistoryRef` | `/api/chat` + `/api/chat/history` | Medium |
| `FavoriteButton.tsx` | `useFavorites()` (localStorage) | `useFavorites()` (localStorage + server sync) | Medium |
| `SearchModal.tsx` | `search-index.ts` (static) | `search-index.ts` (DB-backed) | Low |
| `ServiceCard.tsx` | Props (no change needed) | Props (no change needed) | None |
| `FilterPanel.tsx` | Static config | DB-backed config | Low |
| `SocialProofToast.tsx` | Static reviews | DB reviews | Low |
| `Testimonials.tsx` | Static reviews | DB reviews | Low |
| `RelatedServices.tsx` | Static product list | DB product list | Low |
| `RecentlyViewed.tsx` | localStorage (no change) | No change | None |

### Pages that will change (generateStaticParams)

All 14 `[slug]/page.tsx` files currently call `generateStaticParams()` which returns hardcoded slugs from static imports. These will change to query the DB:

```typescript
export async function generateStaticParams() {
  const products = await getProducts('excursions');
  return products.map(p => ({ slug: p.slug }));
}
```

---

## 11. Performance Considerations

### 11.1 Caching strategy

| Layer | Mechanism | TTL | Invalidation |
|-------|-----------|-----|-------------|
| **CDN** | Cloudflare (existing) | Controlled by headers | Automatic |
| **ISR** | Next.js `revalidate` | 300s (5 min) | On-demand via `/api/revalidate` |
| **Data layer** | `unstable_cache` | 300s | Tag-based (`revalidateTag`) |
| **Client** | React state + SWR pattern | Session | Manual refetch |

### 11.2 Database query optimization

- **Connection pooling:** Neon provides built-in connection pooling via the `?pgbouncer=true` query parameter. Use `directUrl` for migrations, pooled URL for runtime.
- **Indexes:** All foreign keys and frequently-queried fields have indexes (see schema above).
- **Selective loading:** Use Prisma `select` to fetch only needed fields. Never load full product with all relations when only slug + title + price is needed (e.g., for catalog cards).
- **Batch queries:** Use `prisma.$queryRaw` for complex aggregations (review averages, availability summaries) rather than N+1 queries.

### 11.3 Bundle size impact

- `@prisma/client` is server-only (not bundled to client).
- No client-side impact. API routes and server components only.
- Estimated dependency addition: ~2MB to `node_modules`, 0KB to client bundle.

---

## 12. Security Considerations

### 12.1 Database access

- Website has **read-only** access to CRM tables (enforced via Prisma schema — no mutation methods exposed for CRM models).
- Write access only to `ws_*` tables.
- `DATABASE_URL` never exposed to client (server-only).

### 12.2 API rate limiting

| Endpoint | Rate Limit | Window |
|----------|-----------|--------|
| `POST /api/chat` | 10/min (existing) | 1 minute |
| `POST /api/reviews` | 3/hour per IP | 1 hour |
| `POST /api/booking-request` | 5/min per IP | 1 minute |
| `POST /api/favorites` | 30/min per session | 1 minute |
| `POST /api/revalidate` | Token-gated | N/A |

### 12.3 Input validation

- All user inputs sanitized (existing pattern from `/api/chat`).
- Review text: max 2000 chars, HTML stripped, profanity filter.
- Booking request: validate date is future, participants 1-20, price matches slot.
- Session tokens: signed cookies (httpOnly, secure, sameSite: strict).

### 12.4 CSRF protection

- POST routes check `Origin` header matches `vipdxbrus.com`.
- Revalidation webhook uses shared secret.

---

## 13. Testing Strategy

### 13.1 Unit tests

- Data access layer functions (mocked Prisma).
- Seeding script correctness (static data -> DB records).
- BiText transformation utilities.

### 13.2 Integration tests

- API routes with test database (Neon branch or local PostgreSQL via Docker).
- Dual-read fallback behavior.
- Rate limiting behavior.

### 13.3 E2E tests

- Product catalog renders correctly from DB.
- Availability calendar shows real slots.
- Review submission flow.
- Chat history persistence across page refreshes.
- Favorites sync between tabs.

### 13.4 Data integrity

- Verify all 236 products seeded correctly.
- Verify all 52 reviews mapped to correct products.
- Verify `generateStaticParams()` returns correct slugs from DB.
- Compare rendered pages (static vs. DB) for pixel-level differences.

---

## 14. Rollback Plan

### If Phase A fails
- Remove `prisma/` directory and `@prisma/client` dependency.
- Revert data access layer changes.
- Site continues to work from static files (current state).

### If Phase B fails
- Disable new API routes.
- Revert component changes to use static imports.
- DB data is preserved for future attempt.

### If Phase C fails (after cutover)
- Re-add static data files from git history.
- Re-enable dual-read pattern.
- Static files act as complete fallback.

**Zero-downtime rollback:** At every phase, the static `.ts` files remain in the repository until Phase C is verified stable. Rolling back is always a `git revert` away.

---

## 15. Dependencies & New Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `prisma` | ^6.x | Schema management, migrations, CLI |
| `@prisma/client` | ^6.x | Database ORM (runtime) |
| `@prisma/adapter-neon` | ^6.x | Neon serverless driver adapter |
| `@neondatabase/serverless` | ^1.x | Neon serverless PostgreSQL driver |

No other new dependencies required. The website already uses Next.js 15 which provides `unstable_cache`, `revalidateTag`, and all needed server-side primitives.

---

## 16. Deployment Changes

### Docker (current deployment)

```dockerfile
# Add to Dockerfile (after npm install, before build)
RUN npx prisma generate
```

### GitHub Actions (deploy.yml)

```yaml
# Add DATABASE_URL to secrets
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}

# Add migration step before build
- name: Run Prisma migrations
  run: npx prisma migrate deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Cloudflare Tunnel

No changes needed. The tunnel proxies all traffic to the Docker container on port 3100, which remains unchanged.

---

## 17. Effort Estimates

| Phase | Duration | Effort | Risk |
|-------|----------|--------|------|
| **A: Schema + DAL + Dual-read** | 2-3 weeks | 40-60 hours | Low (no user-facing changes) |
| **B: Write paths + CRM integration** | 2-3 weeks | 40-60 hours | Medium (new API surfaces) |
| **C: Cut over** | 1 week | 15-20 hours | Medium (removal of fallback) |
| **D: Advanced features** | 2-3 weeks | 30-50 hours | Low (additive) |
| **Total** | 7-10 weeks | 125-190 hours | |

### Critical path

1. Prisma schema design (blocks everything)
2. Seeding script (blocks Phase A verification)
3. CRM webhook integration (blocks Phase B)
4. Availability slot management in CRM (blocks real booking flow)

---

## 18. Open Questions (Need Owner Decision)

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | **CRM category enum extension** | A) Add 5 new enum values to CRM. B) Use `subcategory` string field. | B — less CRM disruption |
| 2 | **User authentication** | A) Phone OTP. B) WhatsApp OTP. C) Defer to Phase D. | C — defer, use anonymous sessions |
| 3 | **Review moderation** | A) Auto-approve verified reviews. B) All manual. C) AI moderation. | B — all manual via CRM |
| 4 | **Availability slot generation** | A) CRM admin creates manually. B) Bulk generator with rules. C) Sync from supplier APIs. | B — bulk generator in CRM |
| 5 | **Chat history retention** | A) 30 days. B) 90 days. C) Indefinite. | A — 30 days with auto-cleanup |
| 6 | **Shared Prisma schema or separate?** | A) Monorepo Prisma package. B) Copy CRM models to website schema. C) Prisma multi-schema. | B — copy read-only models (simplest) |
| 7 | **Blog posts and FAQ** | A) Move to DB now. B) Keep static. | B — keep static (low change frequency) |
| 8 | **Flights data** | A) Move to DB. B) Keep static until Flights Phase B. | B — keep static |

---

## 19. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Neon DB downtime | Site shows stale/no data | Low | Static JSON fallback cache (generated at build time) |
| Schema conflicts between CRM and website migrations | Migration failures | Medium | Separate Prisma schemas, `ws_` table prefix |
| Seeding data loss / corruption | Missing products on site | Medium | Automated comparison script (static vs DB), review before cutover |
| Performance regression (N+1 queries) | Slow page loads | Medium | Prisma query logging, `unstable_cache`, selective `include` |
| CRM Product model changes break website | Type errors, missing fields | Medium | Pin website's CRM model copies, update manually when CRM schema changes |
| Cold start latency (Neon serverless) | First request slow (~1s) | Low | Neon's auto-suspend is configurable, keep-alive cron optional |

---

## 20. Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| All 236 products render correctly from DB | 100% parity with current static site | Automated comparison script |
| Page load time (LCP) | < 2.5s (no regression from current) | Lighthouse CI |
| Availability calendar shows real slots | Manual QA | Test booking flow end-to-end |
| Reviews display correctly | 52 migrated reviews render identically | Visual comparison |
| AI chat history persists across page refreshes | Manual QA | Refresh page, check history loads |
| Favorites sync between devices (same session) | Manual QA | Toggle favorite, verify in different tab |
| CRM product update reflects on site within 5 min | Automated test | Update CRM -> wait -> check site |
| Zero downtime during migration | No 5xx errors | Monitoring / Sentry |

---

## Appendix A: Type Mapping Reference

### BaseService (TypeScript) -> Product (CRM) + WsProductExtension (DB)

| TypeScript Field | DB Location | Column |
|-----------------|-------------|--------|
| `slug` | `WsProductExtension` | `slug` |
| `title.RU` | `Product` | `name` |
| `title.EN` | `Product` | `name_en` |
| `category` | `Product` | `category` + `subcategory` |
| `description.RU` | `Product` | `description` |
| `description.EN` | `Product` | `description_en` |
| `fullDescription` | `WsProductExtension` | `full_description_ru/en` |
| `duration` | `WsProductExtension` | `duration_ru/en` (also `Product.duration`) |
| `location` | `WsProductExtension` | `location_ru/en` |
| `price` | `Product` | `sell_price` |
| `oldPrice` | `WsProductExtension` | `old_price` |
| `rating` | Computed | AVG of `ws_reviews.rating` |
| `reviews` (count) | Computed | COUNT of `ws_reviews` |
| `badge` | `WsProductExtension` | `badge_ru/en` |
| `image` | `ProductPhoto` | `url` WHERE `is_main = true` |
| `images` | `ProductPhoto` | `url` ORDER BY `sort_order` |
| `included` | `WsProductExtension` | `included` (JSON) |
| `notIncluded` | `WsProductExtension` | `not_included` (JSON) |
| `highlights` | `WsProductExtension` | `highlights` (JSON) |
| `experienceCards` | `WsExperienceCard` | Related records |
| `directions` | `WsProductExtension` | `directions` (JSON) |
| `faq` | `ProductFaq` (CRM) | Related records |
| `whatsappText` | `WsProductExtension` | `whatsapp_text_ru/en` |
| `filterValues` | `WsProductExtension` | `filter_values` (JSON) |
| `promoEndDate` | `WsProductExtension` | `promo_end_date` |

### Type-specific fields (stored in `type_specific_data` JSON)

| Type | Fields in JSON |
|------|---------------|
| Excursion | `groupSize`, `transport` + itinerary in `WsItineraryStep` |
| Ticket | `park`, `tiers`, `skipLine`, `validityDays` |
| Yacht | `brand`, `length`, `capacity`, `cabins`, `crew`, `pricePerHour`, `minHours`, `marina` |
| Transfer | `vehicleClass`, `vehicleModel`, `passengers`, `luggage`, `route` |
| Combo | `items`, `savings`, `daysRequired` |
| WaterActivity | `activityType`, `minAge`, `difficultyLevel`, `equipmentIncluded` |
| Buggy | `vehicleType`, `engineCC`, `passengers`, `safetyGear` |
| BeachClub | `poolAccess`, `beachAccess`, `dresscode`, `minSpend` |
| Restaurant | `cuisine`, `dressCode`, `priceRange`, `reservationRequired` |
| Pool | `venue`, `timeSlot`, `towelsIncluded`, `infinity` |
| Hotel | `stars`, `area`, `checkIn`, `checkOut`, `breakfastIncluded` |
| CarRental | `vehicleClass`, `vehicleModel`, `transmission`, `deposit`, `withDriver`, `minDays` |
| AdditionalService | `serviceCategory`, `processingTime`, `documentsRequired` |

---

## Appendix B: CRM Integration Points

### CRM -> Website (data flows)

| Trigger | CRM Action | Website Effect |
|---------|-----------|----------------|
| Product created/updated | POST `/api/revalidate` `{tags: ["products"]}` | ISR cache busted, next request fetches fresh data |
| Review approved | UPDATE `ws_reviews` SET `is_published = true` | Review appears on site within 5 min |
| Availability slot created | Direct DB write (same database) | Availability shows on next calendar load |
| Order confirmed for booking request | UPDATE `ws_booking_requests` SET `crm_order_id`, `status = "confirmed"` | Booking slot `booked_count` incremented |
| Seasonal price changed | POST `/api/revalidate` `{tags: ["products"]}` | Prices update on site |

### Website -> CRM (data flows)

| Trigger | Website Action | CRM Effect |
|---------|---------------|------------|
| Booking request submitted | INSERT `ws_booking_requests` | CRM cron/webhook picks up pending requests, creates Order |
| Review submitted | INSERT `ws_reviews` (unpublished) | Appears in CRM moderation queue |
| Chat conversation | INSERT `ws_chat_messages` | CRM can query chat sessions for lead extraction |
| UTM/referrer captured | INSERT `ws_favorites` / analytics | Linked to CRM customer if authenticated |
