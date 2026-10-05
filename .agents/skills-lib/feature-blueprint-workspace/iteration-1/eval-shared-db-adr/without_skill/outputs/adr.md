# ADR-001: Shared Database vs API Gateway for vipdxbrus.com and tourism-crm Integration

**Status:** Accepted
**Date:** 2026-03-14
**Decision makers:** Sukheil Ganeev (owner), Claude (technical advisor)
**Related issues:** I-102 (Database Integration master task), I-103..I-113

---

## Context

The vipdxbrus.com tourism website (Next.js 15, TypeScript, Tailwind CSS 4) and the tourism-crm back-office application (Next.js 16, TypeScript, Prisma v7) need to share data. Today these two systems are completely disconnected:

**vipdxbrus.com (the public website):**
- Serves 236 products across 13 categories from 24 static TypeScript files in `src/data/`
- Bookings are fake: `generateMockAvailability()` produces deterministic pseudo-random calendar slots
- 52 reviews are hardcoded demo entries in `reviews.ts`
- AI chat (Claude Haiku) is stateless; page refresh loses the conversation
- Favorites live only in the visitor's `localStorage` (lost on device switch or browser clear)
- Contact forms open WhatsApp directly; nothing is saved

**tourism-crm (the internal CRM):**
- 49 Prisma models (1,370 lines of schema), 32 enums, 7 applied migrations
- Hosted on Neon PostgreSQL, region eu-central-1 (Frankfurt)
- Has mature models for Products, Orders, Customers, Reviews, Loyalty, Promo Codes, Finance, Dynamic Pricing, and more
- Exposes ~160 REST API endpoints
- Uses JWT authentication (email + password)
- Running on Vercel with staging via Docker Compose

**The integration need:** The website must transition from static data to a real database so that bookings become functional, reviews come from real customers, the AI chat remembers conversations, and the CRM team can update products and prices without redeploying the website. Both applications are already backed by Neon PostgreSQL in the same region.

**The website plans to add 6 new tables:**
1. `website_products` — website-specific display data (bilingual content, slugs, old prices, images, type-specific JSON) linked to CRM's `products` table
2. `service_slots` — real availability calendar replacing mock generation
3. `website_reviews` — public reviews with moderation workflow
4. `chat_sessions` + `chat_messages` — AI conversation persistence
5. `visitor_favorites` — cross-device favorites via anonymous visitor cookie

---

## Decision

**We chose Option A: Shared Neon PostgreSQL database**, where both vipdxbrus.com and tourism-crm connect to the same Neon PostgreSQL instance through their own Prisma clients.

Specifically:
- Both applications point their `DATABASE_URL` to the same Neon database (eu-central-1 Frankfurt)
- Each application maintains its own `prisma/schema.prisma` file (separate schemas, shared database)
- **tourism-crm owns all migrations.** The website project never runs `prisma migrate dev`. All schema changes (including the 6 new website tables) are authored and applied from the CRM project
- The website uses `prisma db pull` to sync its local schema copy after CRM deploys new migrations
- Neon connection pooling (PgBouncer) is enabled to handle concurrent connections from both applications safely
- The website Prisma client is configured as read-mostly (reads from all tables, writes only to its own 6 tables: website_products, service_slots, website_reviews, chat_sessions, chat_messages, visitor_favorites)

---

## Alternatives Considered

### Option B: API Gateway (website calls CRM via REST API)

In this architecture, the website would never connect to the database directly. Instead, every data request (product catalog, availability, bookings, reviews) would go through HTTP calls to the CRM's REST API, making the CRM the sole gateway to PostgreSQL.

**How it would work:**
```
Browser -> vipdxbrus.com (Next.js) -> HTTP fetch -> tourism-crm API -> Prisma -> Neon PostgreSQL
```

**Advantages:**
- Clean separation of concerns: the website has zero knowledge of the database schema
- The CRM controls all data access, enforcing business rules in one place
- Independent deployability: schema changes in the CRM never affect the website as long as the API contract is stable
- Better security posture: one application has DB credentials instead of two
- Natural path toward microservices if the business grows

**Disadvantages:**
- **Latency:** Every product page load adds an HTTP round-trip (50-150ms per request) on top of the DB query. For a catalog with 236 products and ISR pages, this compounds significantly
- **Coupling at the API layer:** The website depends on the CRM being online. If the CRM is down for maintenance or deployment, the website cannot serve fresh data
- **Development overhead:** The CRM currently has ~160 API endpoints oriented toward internal use (authenticated JWT, admin-level operations). Building a separate public-facing read API layer (product catalog, availability, reviews) requires significant new work in the CRM project
- **Two-project coordination:** Every new feature (e.g., adding review submission from the website) requires synchronized changes in both projects: API endpoint in CRM + client call in website
- **No existing public API:** The CRM has no API designed for anonymous public consumption. Its endpoints assume authenticated admin/agent users. Building a public API layer would be a prerequisite
- **Double deployment risk:** A broken CRM deploy takes the website data offline too

### Option C: Completely separate database for the website

Each application gets its own Neon PostgreSQL database. Data is synchronized between them via cron jobs, webhooks, or event streams.

**Advantages:**
- Full independence: each application can evolve its schema freely
- No risk of one application's queries affecting the other's performance

**Disadvantages:**
- **Data duplication:** Products, orders, and customers exist in two databases, creating sync issues
- **Sync complexity:** Requires building and maintaining a synchronization layer (webhook listeners, conflict resolution, retry logic)
- **Eventual consistency:** Booking made on the website might not appear in the CRM for seconds or minutes, risking double-bookings
- **Neon cost:** Two databases means double the compute and storage costs
- **Defeats the purpose:** The whole point of integration is that the CRM sees website activity in real time

---

## Rationale (Why Shared DB Wins for Phase 1)

### 1. Speed of delivery

The website needs to move from static data to a database as quickly as possible. Shared DB requires adding 6 tables to the existing schema and connecting a second Prisma client. The API Gateway approach requires designing and building an entirely new public API surface in the CRM — a project comparable in scope to what we are trying to build on the website side.

**Estimated effort comparison:**
| Approach | Estimated effort |
|----------|-----------------|
| Shared DB | 18-22 hours (Prisma setup + 6 tables + seed + API routes on website) |
| API Gateway | 35-45 hours (public API layer in CRM + auth for anonymous access + client SDK on website + error handling + fallback) |

### 2. Zero latency penalty

With Shared DB, the website's API routes query PostgreSQL directly via Prisma. There is no HTTP hop between the website and the CRM. For ISR pages that revalidate every 5 minutes, this means the revalidation fetch is a direct DB query (~5-15ms) rather than a chained HTTP request (~50-150ms).

### 3. Real-time CRM visibility

When a booking is submitted on the website, the CRM dashboard sees it immediately because it is reading from the same `orders` table. With API Gateway, the website would POST to the CRM and the CRM would write to the DB — adding a middleman that provides no additional value at this scale.

### 4. Single source of truth from day one

Both applications read the same rows. There is no sync lag, no conflict resolution, no "eventually consistent" state. Product prices updated in the CRM are visible on the website after the next ISR revalidation (5 minutes max).

### 5. Already proven infrastructure

Neon PostgreSQL is already running, has 7 migrations applied, seed data loaded, and a mature 49-model schema. Adding 6 tables is an incremental extension, not a new infrastructure buildout.

### 6. Clear migration path to API Gateway later

Shared DB is explicitly designed as a Phase 1 strategy. The architecture supports a future migration to API Gateway:
- Website API routes already wrap all database access in a service layer (`product-service.ts`, etc.)
- Switching from `prisma.websiteProduct.findUnique()` to `fetch('https://crm.vipdxbrus.com/api/v1/products/...')` is a localized change in the service layer
- When the CRM is actively used by staff in parallel with high website traffic, upgrading to API Gateway provides better isolation

---

## Consequences

### Positive

- **Single DATABASE_URL** connects both projects to the same Neon instance, simplifying infrastructure
- **CRM sees all website activity** (bookings, reviews, chat sessions, favorites) in real-time without any sync layer
- **Shared user model possibility:** if website visitors later get accounts, they can be linked to CRM customers directly
- **Reuse CRM's existing Prisma ecosystem:** migration tooling, seed scripts, type generation all work across both projects
- **Fallback to static data** is built into the architecture: the website's `product-service.ts` tries DB first, falls back to static `.ts` files if unreachable

### Negative / Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Schema coupling:** CRM migration breaks website queries | Medium | High | Website uses its own 6 tables primarily; reads from CRM tables are simple lookups. CRM team (currently just the owner + Claude) coordinates all changes. Staging tests before production migration |
| **Connection pool exhaustion:** Two applications sharing one pool | Low-Medium | High | Neon PgBouncer enabled (`?pgbouncer=true` in connection string). Neon free tier allows 100 concurrent connections. Monitor via Neon dashboard |
| **Neon free tier limits:** 3 GiB storage, 100 compute hours/month | Medium | Medium | Current usage is well under limits. Monitor at 70% — upgrade to Launch plan ($19/month) if needed |
| **Prisma version mismatch:** CRM uses Prisma v7, website may use different version | Low | Medium | Pin both projects to the same major Prisma version. Currently both can use v7 |
| **No auth boundary:** Website has full write access to CRM tables | Low | Medium | Website Prisma client is configured to only write to its own 6 `website_*`/`chat_*`/`visitor_*` tables. Enforced at application layer (not DB-level), but acceptable for a single-team project |
| **Migration coordination:** All schema changes must go through CRM project | Low | Low | This is actually a positive constraint — single source of truth for migrations. Documented in both CLAUDE.md files |

### Operational

- **New env var:** `DATABASE_URL` must be added to vipdxbrus-website's `.env.local`, Vercel environment variables, GitHub Actions secrets, and Docker Compose file
- **New dependency:** `prisma` and `@prisma/client` packages added to vipdxbrus-website
- **New file:** `src/lib/prisma.ts` — Prisma client singleton with connection pooling
- **New file:** `prisma/schema.prisma` — website's view of the shared database
- **Migration workflow:** CRM creates migration -> deploys to Neon -> website runs `prisma db pull` -> regenerates client
- **Monitoring:** Neon dashboard for connection count, storage usage, query performance

---

## Implementation Outline

### Phase 1: Foundation (Prisma + Schema) — ~4 hours
1. Install Prisma in vipdxbrus-website
2. Add 6 new tables to CRM's `schema.prisma`
3. Extend `ProductCategory` enum with 6 missing categories (RESTAURANT, BEACH_CLUB, POOL, HOTEL, BUGGY, ADDITIONAL_SERVICE)
4. Run migration in CRM, deploy to Neon
5. `prisma db pull` in website, generate client
6. Configure `DATABASE_URL` across all environments

### Phase 2: Product Catalog Migration — ~5 hours
1. Seed script: migrate 82 products from static `.ts` files to `website_products`
2. API routes: `GET /api/products/[category]` and `GET /api/products/[category]/[slug]`
3. Service layer with DB-first + static fallback pattern

### Phase 3: Availability and Booking — ~3.5 hours
1. Seed availability slots for 3 months
2. `POST /api/bookings` with transactional capacity check
3. Update `AvailabilityCalendar.tsx` to fetch real data

### Phase 4: Reviews + Chat + Favorites — ~4.5 hours
1. Migrate 52 demo reviews to `website_reviews`
2. Chat session persistence with visitor cookie
3. Hybrid favorites: localStorage (instant) + DB (persistent)

### Phase 5: ISR + Deployment — ~3 hours
1. ISR with 5-minute revalidation for all product pages
2. Health check endpoint (`GET /api/health`)
3. `USE_STATIC_DATA=true` env var for emergency rollback

**Total estimated effort:** 18-22 hours across 5 phases.

---

## Future Evolution

When either of these conditions is met, evaluate migration to API Gateway (Option B):

1. **Multiple developers** are working on CRM and website simultaneously, and schema coupling becomes a bottleneck
2. **Website traffic** exceeds what the shared Neon connection pool can handle comfortably (>50 concurrent connections from website alone)
3. **Third-party integrations** (WhatsApp Business API, partner portals) also need data access, making a centralized API gateway the natural entry point

The migration path is straightforward because the website's data access is already encapsulated in a service layer. Replacing `prisma.websiteProduct.findUnique()` with `fetch('/api/v1/products/...')` is a localized change per service file.

---

## References

- **Database integration plan:** `D:/Downloads/vipdxbrus-website/docs/plans/database-integration-plan.md`
- **Technical specification:** `D:/Downloads/vipdxbrus-website/docs/plans/database-tech-spec.md`
- **Booking calendar architecture:** `D:/Downloads/vipdxbrus-website/docs/plans/booking-calendar-architecture.md`
- **CRM Prisma schema:** `D:/Downloads/tourism-crm/prisma/schema.prisma` (49 models, 32 enums, 1,370 lines)
- **Website static data:** `D:/Downloads/vipdxbrus-website/src/data/` (24 files, 236 products)
- **Website project CLAUDE.md:** `D:/Downloads/vipdxbrus-website/CLAUDE.md`
- **CRM project:** `D:/Downloads/tourism-crm/` (Next.js 16, Prisma v7, Neon PostgreSQL eu-central-1)
- **ISSUES.md:** I-102 through I-113 track all related tasks
- **Neon connection pooling docs:** https://neon.tech/docs/connect/connection-pooling
- **Prisma multi-project setup:** https://www.prisma.io/docs/guides/other/multi-project-setup
