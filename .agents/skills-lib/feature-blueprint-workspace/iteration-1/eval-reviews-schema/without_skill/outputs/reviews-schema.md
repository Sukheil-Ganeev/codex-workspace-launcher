# PostgreSQL Reviews Schema for vipdxbrus.com

## Overview

Production-ready PostgreSQL schema for client reviews on the tourism website vipdxbrus.com.
Designed to be Prisma-compatible, bilingual (RU/EN), with moderation workflow, photo attachments,
owner replies, and service binding by slug.

---

## Context & Design Decisions

### Current state
The site currently stores 52 reviews as static TypeScript data in `src/data/reviews.ts` with a `Review` interface in `src/data/types.ts`. Each review has bilingual text (RU/EN), optional photos (Unsplash URLs), optional owner response, rating 1-5, author name, city, and `serviceSlug` binding.

### Migration path
This schema is designed so that:
1. All 52 existing static reviews can be imported with `status: APPROVED` and `source: MANUAL_IMPORT`
2. The existing `Review` TypeScript interface maps cleanly to the new table structure
3. The site can gradually switch from static imports to database queries
4. Bilingual fields use separate columns (`_ru` / `_en`) rather than JSON, for indexing and type safety

### Key decisions
| Decision | Choice | Why |
|----------|--------|-----|
| Bilingual storage | Separate `_ru`/`_en` columns | Indexable, type-safe, matches existing BiText pattern |
| Photo storage | Separate `review_photos` table | Unlimited photos per review, individual ordering, R2 CDN URLs |
| Owner replies | Inline columns on review | 1:1 relationship, no need for separate table; keeps queries simple |
| Soft delete | `deleted_at` timestamp | Never lose data, easy restore, compliant with moderation audit |
| Service binding | `service_slug` VARCHAR | Matches existing slug system; no FK to services (services are static data, not in DB yet) |
| Rating constraint | CHECK 1-5 integer | Enforced at DB level, not just app level |
| Moderation | Enum status + `moderated_by`/`moderated_at` | Full audit trail of who approved/rejected and when |

---

## Prisma Schema

```prisma
// ──────────────────────────────────────────────
// Reviews system for vipdxbrus.com
// Add to your existing schema.prisma
// ──────────────────────────────────────────────

enum ReviewStatus {
  PENDING
  APPROVED
  REJECTED
}

enum ReviewSource {
  WEBSITE_FORM    // Submitted through site form
  WHATSAPP        // Extracted from WhatsApp chat
  GOOGLE          // Imported from Google Reviews
  MANUAL_IMPORT   // Migrated from static data (existing 52 reviews)
  ADMIN_CREATED   // Created by admin on behalf of client
}

model Review {
  id              String         @id @default(cuid())

  // ── Service binding ──
  serviceSlug     String         @map("service_slug")
  serviceCategory String?        @map("service_category")  // e.g. "excursion", "ticket", "yacht"

  // ── Author info ──
  authorNameRu    String         @map("author_name_ru")
  authorNameEn    String?        @map("author_name_en")
  authorCityRu    String?        @map("author_city_ru")
  authorCityEn    String?        @map("author_city_en")
  authorEmail     String?        @map("author_email")      // For follow-up, never displayed
  authorPhone     String?        @map("author_phone")      // For follow-up, never displayed

  // ── Review content ──
  rating          Int                                       // 1-5, enforced by CHECK constraint
  textRu          String         @map("text_ru")           @db.Text
  textEn          String?        @map("text_en")           @db.Text

  // ── Owner response ──
  responseRu      String?        @map("response_ru")       @db.Text
  responseEn      String?        @map("response_en")       @db.Text
  respondedAt     DateTime?      @map("responded_at")
  respondedBy     String?        @map("responded_by")      // Admin user ID or name

  // ── Moderation ──
  status          ReviewStatus   @default(PENDING)
  moderatedAt     DateTime?      @map("moderated_at")
  moderatedBy     String?        @map("moderated_by")      // Admin user ID or name
  rejectionReason String?        @map("rejection_reason")  // Why it was rejected

  // ── Metadata ──
  source          ReviewSource   @default(WEBSITE_FORM)
  verified        Boolean        @default(false)            // Verified purchase
  featured        Boolean        @default(false)            // Show on homepage/highlights
  helpfulCount    Int            @default(0) @map("helpful_count")  // "Was this helpful?" counter
  locale          String         @default("ru")             // Original language of submission

  // ── Timestamps ──
  reviewDate      DateTime       @map("review_date")        // When the experience happened
  createdAt       DateTime       @default(now()) @map("created_at")
  updatedAt       DateTime       @updatedAt @map("updated_at")
  deletedAt       DateTime?      @map("deleted_at")         // Soft delete

  // ── Relations ──
  photos          ReviewPhoto[]

  // ── Indexes ──
  @@index([serviceSlug, status])
  @@index([status, createdAt])
  @@index([serviceSlug, rating])
  @@index([featured, status])
  @@index([deletedAt])

  @@map("reviews")
}

model ReviewPhoto {
  id          String   @id @default(cuid())
  reviewId    String   @map("review_id")
  url         String                          // R2 CDN URL or external URL
  thumbnailUrl String? @map("thumbnail_url")  // Pre-generated thumbnail
  altRu       String?  @map("alt_ru")         // Alt text for accessibility
  altEn       String?  @map("alt_en")
  sortOrder   Int      @default(0) @map("sort_order")
  width       Int?                             // Original dimensions for layout
  height      Int?
  sizeBytes   Int?     @map("size_bytes")
  createdAt   DateTime @default(now()) @map("created_at")

  // ── Relations ──
  review      Review   @relation(fields: [reviewId], references: [id], onDelete: Cascade)

  // ── Indexes ──
  @@index([reviewId, sortOrder])

  @@map("review_photos")
}
```

---

## Raw SQL (equivalent, for reference / manual migrations)

```sql
-- ──────────────────────────────────────────────
-- ENUMS
-- ──────────────────────────────────────────────

CREATE TYPE review_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');

CREATE TYPE review_source AS ENUM (
  'WEBSITE_FORM',
  'WHATSAPP',
  'GOOGLE',
  'MANUAL_IMPORT',
  'ADMIN_CREATED'
);

-- ──────────────────────────────────────────────
-- REVIEWS TABLE
-- ──────────────────────────────────────────────

CREATE TABLE reviews (
  id                  TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,

  -- Service binding
  service_slug        VARCHAR(120) NOT NULL,
  service_category    VARCHAR(50),

  -- Author info
  author_name_ru      VARCHAR(200) NOT NULL,
  author_name_en      VARCHAR(200),
  author_city_ru      VARCHAR(100),
  author_city_en      VARCHAR(100),
  author_email        VARCHAR(254),
  author_phone        VARCHAR(20),

  -- Review content
  rating              INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  text_ru             TEXT NOT NULL,
  text_en             TEXT,

  -- Owner response
  response_ru         TEXT,
  response_en         TEXT,
  responded_at        TIMESTAMPTZ,
  responded_by        VARCHAR(100),

  -- Moderation
  status              review_status NOT NULL DEFAULT 'PENDING',
  moderated_at        TIMESTAMPTZ,
  moderated_by        VARCHAR(100),
  rejection_reason    TEXT,

  -- Metadata
  source              review_source NOT NULL DEFAULT 'WEBSITE_FORM',
  verified            BOOLEAN NOT NULL DEFAULT FALSE,
  featured            BOOLEAN NOT NULL DEFAULT FALSE,
  helpful_count       INTEGER NOT NULL DEFAULT 0,
  locale              VARCHAR(5) NOT NULL DEFAULT 'ru',

  -- Timestamps
  review_date         TIMESTAMPTZ NOT NULL,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at          TIMESTAMPTZ
);

-- ──────────────────────────────────────────────
-- REVIEW PHOTOS TABLE
-- ──────────────────────────────────────────────

CREATE TABLE review_photos (
  id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
  review_id       TEXT NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
  url             TEXT NOT NULL,
  thumbnail_url   TEXT,
  alt_ru          VARCHAR(300),
  alt_en          VARCHAR(300),
  sort_order      INTEGER NOT NULL DEFAULT 0,
  width           INTEGER,
  height          INTEGER,
  size_bytes      INTEGER,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ──────────────────────────────────────────────
-- INDEXES
-- ──────────────────────────────────────────────

-- Primary query: get approved reviews for a service page
CREATE INDEX idx_reviews_slug_status ON reviews(service_slug, status);

-- Moderation queue: show pending reviews newest first
CREATE INDEX idx_reviews_status_created ON reviews(status, created_at);

-- Rating analytics: average rating per service
CREATE INDEX idx_reviews_slug_rating ON reviews(service_slug, rating);

-- Homepage featured reviews
CREATE INDEX idx_reviews_featured ON reviews(featured, status);

-- Soft delete filter
CREATE INDEX idx_reviews_deleted ON reviews(deleted_at);

-- Photo lookup by review
CREATE INDEX idx_review_photos_review ON review_photos(review_id, sort_order);

-- ──────────────────────────────────────────────
-- AUTO-UPDATE updated_at TRIGGER
-- ──────────────────────────────────────────────

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_reviews_updated_at
  BEFORE UPDATE ON reviews
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_updated_at();
```

---

## Moderation Workflow

```
┌──────────────┐
│  New Review   │
│ (from form,   │
│  WhatsApp,    │
│  import)      │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────┐
│   PENDING    │────▶│    APPROVED     │
│              │     │ (visible on     │
│ (invisible   │     │  site, indexed  │
│  on site)    │     │  by search)     │
└──────┬───────┘     └─────────────────┘
       │
       ▼
┌──────────────┐
│   REJECTED   │
│ (invisible,  │
│  with reason)│
└──────────────┘
```

### Status transitions

| From | To | Who | When |
|------|----|-----|------|
| PENDING | APPROVED | Admin/Owner | Review passes moderation |
| PENDING | REJECTED | Admin/Owner | Spam, inappropriate, fake |
| REJECTED | APPROVED | Admin/Owner | Reconsideration |
| APPROVED | REJECTED | Admin/Owner | Late discovery of issue |
| Any | soft-deleted | Admin/Owner | `deleted_at` set, review hidden everywhere |

### Moderation rules (business logic, not DB-level)
- All `WEBSITE_FORM` reviews start as `PENDING`
- `MANUAL_IMPORT` reviews (existing 52) are inserted as `APPROVED`
- `ADMIN_CREATED` reviews can be set directly to `APPROVED`
- `rejection_reason` is required when status = `REJECTED` (enforce in app)
- `moderated_at` and `moderated_by` set whenever status changes from `PENDING`

---

## Common Queries

### 1. Get approved reviews for a service page (with photos)

```sql
SELECT r.*,
       json_agg(
         json_build_object(
           'url', rp.url,
           'thumbnailUrl', rp.thumbnail_url,
           'altRu', rp.alt_ru,
           'altEn', rp.alt_en
         ) ORDER BY rp.sort_order
       ) FILTER (WHERE rp.id IS NOT NULL) AS photos
FROM reviews r
LEFT JOIN review_photos rp ON rp.review_id = r.id
WHERE r.service_slug = 'desert-safari-sunset'
  AND r.status = 'APPROVED'
  AND r.deleted_at IS NULL
GROUP BY r.id
ORDER BY r.review_date DESC;
```

**Prisma equivalent:**
```typescript
const reviews = await prisma.review.findMany({
  where: {
    serviceSlug: 'desert-safari-sunset',
    status: 'APPROVED',
    deletedAt: null,
  },
  include: { photos: { orderBy: { sortOrder: 'asc' } } },
  orderBy: { reviewDate: 'desc' },
});
```

### 2. Get average rating and count per service

```sql
SELECT service_slug,
       COUNT(*) AS review_count,
       ROUND(AVG(rating)::numeric, 1) AS avg_rating
FROM reviews
WHERE status = 'APPROVED' AND deleted_at IS NULL
GROUP BY service_slug
ORDER BY review_count DESC;
```

### 3. Moderation queue (pending reviews, newest first)

```sql
SELECT r.id, r.author_name_ru, r.service_slug, r.rating,
       LEFT(r.text_ru, 100) AS preview, r.source, r.created_at
FROM reviews r
WHERE r.status = 'PENDING' AND r.deleted_at IS NULL
ORDER BY r.created_at DESC;
```

### 4. Featured reviews for homepage

```sql
SELECT r.*,
       json_agg(
         json_build_object('url', rp.url, 'thumbnailUrl', rp.thumbnail_url)
         ORDER BY rp.sort_order
       ) FILTER (WHERE rp.id IS NOT NULL) AS photos
FROM reviews r
LEFT JOIN review_photos rp ON rp.review_id = r.id
WHERE r.featured = TRUE
  AND r.status = 'APPROVED'
  AND r.deleted_at IS NULL
GROUP BY r.id
ORDER BY r.review_date DESC
LIMIT 6;
```

### 5. Rating breakdown for a service (star distribution)

```sql
SELECT rating, COUNT(*) AS count
FROM reviews
WHERE service_slug = 'desert-safari-sunset'
  AND status = 'APPROVED'
  AND deleted_at IS NULL
GROUP BY rating
ORDER BY rating DESC;
```

### 6. Approve a review

```sql
UPDATE reviews
SET status = 'APPROVED',
    moderated_at = NOW(),
    moderated_by = 'sukheil'
WHERE id = 'cuid_xxx'
  AND status = 'PENDING';
```

### 7. Add owner response

```sql
UPDATE reviews
SET response_ru = 'Спасибо за отзыв! Ждём вас снова!',
    response_en = 'Thank you for the review! See you again!',
    responded_at = NOW(),
    responded_by = 'sukheil'
WHERE id = 'cuid_xxx';
```

---

## Migration Script: Static Data to Database

This script imports the existing 52 reviews from `src/data/reviews.ts` into the database.

```typescript
// scripts/migrate-reviews.ts
// Run: npx tsx scripts/migrate-reviews.ts

import { PrismaClient } from '@prisma/client';
import { reviews } from '../src/data/reviews';

const prisma = new PrismaClient();

async function migrateReviews() {
  console.log(`Migrating ${reviews.length} static reviews...`);

  for (const r of reviews) {
    const review = await prisma.review.create({
      data: {
        serviceSlug: r.serviceSlug,
        authorNameRu: r.author.RU,
        authorNameEn: r.author.EN || null,
        authorCityRu: r.city?.RU || null,
        authorCityEn: r.city?.EN || null,
        rating: r.rating,
        textRu: r.text.RU,
        textEn: r.text.EN || null,
        responseRu: r.response?.RU || null,
        responseEn: r.response?.EN || null,
        respondedAt: r.response ? new Date(r.date) : null,
        respondedBy: r.response ? 'sukheil' : null,
        status: 'APPROVED',
        source: 'MANUAL_IMPORT',
        verified: r.verified ?? false,
        featured: false,
        locale: 'ru',
        reviewDate: new Date(r.date),
        photos: r.photos
          ? {
              create: r.photos.map((url, index) => ({
                url,
                sortOrder: index,
              })),
            }
          : undefined,
      },
    });

    console.log(`  Imported: ${review.id} (${r.serviceSlug})`);
  }

  console.log(`Done. ${reviews.length} reviews imported.`);
}

migrateReviews()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

---

## API Endpoints (recommended structure)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| `GET` | `/api/reviews?slug={slug}` | Public: approved reviews for a service | None |
| `GET` | `/api/reviews/stats?slug={slug}` | Public: avg rating + count | None |
| `GET` | `/api/reviews/featured` | Public: featured reviews for homepage | None |
| `POST` | `/api/reviews` | Submit new review (goes to PENDING) | None (with rate limiting + captcha) |
| `GET` | `/api/admin/reviews?status=PENDING` | Admin: moderation queue | Admin |
| `PATCH` | `/api/admin/reviews/{id}/approve` | Admin: approve review | Admin |
| `PATCH` | `/api/admin/reviews/{id}/reject` | Admin: reject review | Admin |
| `PATCH` | `/api/admin/reviews/{id}/respond` | Admin: add owner response | Admin |
| `DELETE` | `/api/admin/reviews/{id}` | Admin: soft delete | Admin |
| `POST` | `/api/admin/reviews/{id}/photos` | Admin: add photos to review | Admin |

---

## Security & Validation

### Input validation (app level)

```typescript
// Zod schema for review submission
const ReviewSubmitSchema = z.object({
  serviceSlug: z.string().min(1).max(120),
  authorNameRu: z.string().min(2).max(200).trim(),
  authorNameEn: z.string().max(200).trim().optional(),
  authorCityRu: z.string().max(100).trim().optional(),
  authorCityEn: z.string().max(100).trim().optional(),
  authorEmail: z.string().email().optional(),
  rating: z.number().int().min(1).max(5),
  textRu: z.string().min(10).max(5000).trim(),
  textEn: z.string().max(5000).trim().optional(),
  reviewDate: z.string().datetime(),
});

// Zod schema for owner response
const ReviewResponseSchema = z.object({
  responseRu: z.string().min(1).max(2000).trim(),
  responseEn: z.string().max(2000).trim().optional(),
});
```

### Anti-spam measures
- Rate limit: max 3 reviews per IP per day
- Honeypot hidden field in form
- Minimum text length: 10 characters
- Duplicate detection: same `service_slug` + similar `text_ru` within 24h
- Optional: reCAPTCHA v3 or Cloudflare Turnstile

### Data privacy
- `author_email` and `author_phone` are **never** exposed in public API responses
- Admin API returns them only for authenticated admin users
- Soft delete preserves data for audit but hides from all queries

---

## Photo Upload Flow

```
1. User selects photos in review form
2. Frontend uploads to /api/upload/review-photo (pre-signed R2 URL)
3. R2 stores original at: reviews/{reviewId}/{uuid}.webp
4. Thumbnail generated at: reviews/{reviewId}/{uuid}_thumb.webp
5. On review submit, photo URLs are saved to review_photos table
6. Photos linked to review via review_id FK (CASCADE delete)
```

### R2 CDN structure
```
pub-5ae97056834749bd97c9ff1dca1f1631.r2.dev/
  reviews/
    {review_cuid}/
      photo_01.webp        (full size, max 1920px)
      photo_01_thumb.webp   (thumbnail, 400px)
      photo_02.webp
      photo_02_thumb.webp
```

---

## Performance Considerations

| Concern | Solution |
|---------|----------|
| Hot query: reviews by slug | Composite index `(service_slug, status)` |
| Moderation queue | Index `(status, created_at)` for PENDING sort |
| Homepage featured | Index `(featured, status)` |
| Rating aggregation | Index `(service_slug, rating)` for GROUP BY |
| Photo JOINs | Index `(review_id, sort_order)` |
| Soft delete filtering | All queries include `WHERE deleted_at IS NULL`; index on `deleted_at` |
| Future: full-text search | Add `tsvector` column + GIN index on `text_ru` when needed |
| Future: pagination | Cursor-based using `created_at` + `id` (not OFFSET) |

### Estimated scale
- Current: 52 reviews (migrated from static)
- Year 1: ~200-500 reviews (organic + WhatsApp imports)
- Year 3: ~1,000-3,000 reviews
- Photos: ~2-5 per review with photos, ~30% of reviews have photos

This scale is well within PostgreSQL's comfort zone. No partitioning or sharding needed.

---

## Future Extensions (not in initial schema)

These are noted for awareness but should NOT be implemented now:

1. **Review tags** (e.g., "family", "romantic", "adventure") -- separate `review_tags` join table
2. **Sentiment analysis** -- `sentiment_score FLOAT` column, populated by AI batch job
3. **Review threads** (replies to replies) -- `parent_id` self-referencing FK
4. **Verified purchase link** -- `order_id` FK to orders table (when CRM integration is live)
5. **Translation automation** -- `auto_translated BOOLEAN` flag for machine-translated EN text
6. **Review request system** -- separate `review_requests` table for follow-up emails/WhatsApp
7. **Aggregate cache** -- materialized view for per-service avg rating + count (when >1000 reviews)
