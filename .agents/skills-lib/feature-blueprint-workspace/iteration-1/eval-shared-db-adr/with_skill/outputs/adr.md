# ADR-006: Shared Database vs API Gateway for vipdxbrus.com + tourism-crm Integration

**Status:** Proposed
**Date:** 2026-03-14
**Deciders:** Sukheil Ganeev, architect

---

## Context

Two separate Next.js applications need to share data:

1. **vipdxbrus.com** -- the customer-facing tourism website (Next.js 15, TypeScript, Tailwind CSS 4). Currently uses static data files (`src/data/*.ts`, 236 products) with no database. Deployed on GCP VM via Docker + Cloudflare Tunnel.

2. **tourism-crm** -- the internal CRM system (Next.js 16, TypeScript, Tailwind CSS 4, Prisma 7). Has a mature PostgreSQL database on Neon (eu-central-1, Frankfurt) with 49 Prisma models, 32 enums, 7 migrations, ~160 API endpoints. Deployed on Vercel.

The website needs to transition from static data to a real database to support:
- Dynamic product catalog (prices, availability, slots)
- Booking calendar (Phase B -- real availability from DB)
- Chat sessions (AI assistant history)
- Visitor favorites (server-side persistence)
- Service reviews (moderated, from CRM)

The website plans to add 6 tables: `website_products`, `service_slots`, `website_reviews`, `chat_sessions`, `chat_messages`, `visitor_favorites`.

Both applications already use Prisma as their ORM. The CRM database is hosted on Neon PostgreSQL in eu-central-1 (Frankfurt), which is geographically close to the GCP VM (europe-west3-b, also Frankfurt).

Key constraint: Sukheil is a solo entrepreneur, not a programmer. Operational complexity must be minimal. There is no DevOps team.

## Decision

> We will use a Shared Neon PostgreSQL database: both vipdxbrus.com and tourism-crm connect to the same Neon instance via Prisma. The website adds its own 6 tables to the existing database. Each application maintains its own `schema.prisma` file scoped to the tables it owns.

## Consequences

### Positive (benefits we gain)
- **Single source of truth** -- product prices, availability, reviews updated in CRM are instantly visible on the website. No sync lag, no stale cache, no data duplication.
- **Zero operational overhead** -- no API gateway to deploy, monitor, scale, or secure. No inter-service networking to debug. One Neon instance to manage.
- **Minimal infrastructure cost** -- Neon free/pro tier covers both apps. No additional compute for an API layer.
- **Sub-millisecond data access** -- both apps are in Frankfurt (GCP europe-west3-b and Neon eu-central-1). Direct DB queries are faster than HTTP round-trips through an API gateway.
- **Prisma ecosystem reuse** -- both apps already use Prisma. Adding tables to the same DB requires no new tooling, no new dependency, no new auth mechanism.
- **Simpler development workflow** -- Sukheil (non-programmer) can manage one database, not two systems communicating via API. Fewer moving parts = fewer things to break.

### Negative / Trade-offs (drawbacks we accept)
- **Schema coupling** -- both apps share one PostgreSQL instance. A bad migration in one app can affect the other. Mitigation: each app owns its own tables with clear naming prefix (`website_*` for the site, existing CRM tables untouched). Migrations are reviewed before apply.
- **Connection pool contention** -- Neon has connection limits. Two apps sharing the pool could exhaust connections under load. Mitigation: Neon's serverless driver with connection pooling (PgBouncer built-in); the website is read-heavy with low write volume; CRM has limited internal users (~5 staff).
- **No independent deployability of data layer** -- if Neon goes down, both apps lose database access simultaneously. Mitigation: Neon has 99.95% SLA; both apps can degrade gracefully (website falls back to cached/static data, CRM shows maintenance page).
- **Tight coupling makes future separation harder** -- if apps diverge significantly (different cloud providers, different regions), untangling shared DB requires migration to API pattern. Mitigation: the 6 website tables are isolated by prefix and have no foreign keys to CRM tables, making future extraction straightforward.
- **Dual Prisma schemas** -- two `schema.prisma` files pointing at the same DB. Must coordinate to avoid migration conflicts. Mitigation: website uses `prisma db push` (no migration history) or its own migration directory; CRM keeps its existing `prisma migrate` flow.

### Neutral (side effects -- neither good nor bad)
- Website's `schema.prisma` will reference only the 6 `website_*` tables, not the full 49 CRM models. The schemas are independent files, not shared.
- Neon dashboard will show tables from both apps in one database. Clear naming convention (`website_*` prefix) prevents confusion.
- Both apps will need `DATABASE_URL` pointing to the same Neon connection string (with pooling endpoint for the website, direct endpoint for CRM migrations).
- Future features (booking calendar Phase B, trip planner Phase B) benefit from direct access to CRM data (operations, products, pricing) without building API endpoints first.

## Alternatives Considered

### Option A: API Gateway -- website calls CRM via REST API
- **Description:** vipdxbrus.com makes HTTP requests to tourism-crm API endpoints (e.g., `GET /api/products`, `POST /api/bookings`). The website has no direct database access. CRM is the single owner of all data.
- **Pros:**
  - Clean separation of concerns -- each app owns its data access layer
  - CRM controls all business logic and validation in one place
  - Website can be fully static/edge-deployed (no DB dependency)
  - Standard microservices pattern, well-documented
- **Cons:**
  - **Added latency:** Every data request is an HTTP round-trip (website GCP Frankfurt -> Vercel edge -> Neon Frankfurt). Even with caching, adds 50-200ms per request vs. <5ms direct DB query.
  - **CRM becomes a bottleneck:** Website traffic spikes (promotions, seasonal peaks) hit CRM API, potentially degrading CRM performance for internal staff.
  - **160+ endpoints already exist but are CRM-internal:** Exposing them to the website requires authentication layer (API keys/JWT), rate limiting, CORS configuration, and documentation. Significant development effort.
  - **New failure mode:** If Vercel has issues or CRM deploys a breaking change, the website breaks. Two points of failure instead of one.
  - **Operational complexity:** Sukheil would need to understand API versioning, error handling for HTTP failures, retry logic, caching invalidation. Too complex for a solo non-technical operator.
- **Rejected because:** The added latency, development cost (~2-3 weeks to build proper API layer with auth, rate limiting, error handling), and operational complexity outweigh the architectural purity. Both apps are owned by the same person, serve the same business, and are in the same region. The "clean separation" benefit is theoretical for a 1-person team.

### Option B: Separate databases with data replication
- **Description:** Website has its own Neon database. A sync process (cron job, CDC, or event-driven) copies relevant CRM data (products, prices, slots) to the website DB periodically.
- **Pros:**
  - Complete isolation -- one app cannot break the other's data
  - Each app can optimize its schema independently
  - Website DB can be read-optimized (denormalized)
- **Cons:**
  - **Data staleness:** Sync introduces lag. Price change in CRM may not appear on website for minutes/hours depending on sync frequency.
  - **Sync infrastructure:** Requires building and maintaining a replication pipeline (cron + scripts, or CDC with Debezium/equivalent). New moving part to monitor.
  - **Doubled storage cost:** Same data stored twice on Neon.
  - **Conflict resolution:** If both apps write (e.g., website creates a booking, CRM creates a booking), need conflict resolution strategy.
  - **Massive overengineering** for current scale (236 products, ~5 staff users, <1000 daily visitors).
- **Rejected because:** Introduces the most complexity (sync pipeline) with the least benefit at current scale. The business has 236 products and a small team -- replication infrastructure is enterprise-grade tooling for a startup-scale problem.

### Option C: Headless CMS (Strapi/Payload) as intermediary
- **Description:** Move product data to a headless CMS. Both website and CRM read/write to the CMS API. CMS owns the content layer.
- **Pros:**
  - Purpose-built for content management
  - Admin UI for non-technical users
  - Webhooks for cache invalidation
- **Cons:**
  - **Third system to maintain:** Now there are three applications (website + CRM + CMS) instead of two.
  - **CRM already has product management:** tourism-crm Wave 5 (Catalog) already built full product CRUD, supplier panel, and sub-resources. Duplicating this in a CMS is wasteful.
  - **Additional hosting cost:** CMS needs its own server/hosting.
  - **Migration effort:** Moving 49 Prisma models' worth of data relationships into a CMS is impractical.
- **Rejected because:** The CRM already is the content management system for this business. Adding a third tool creates redundancy and triples operational burden.

## References

- vipdxbrus.com project: `D:/Downloads/vipdxbrus-website/CLAUDE.md`
- tourism-crm project: `D:/Downloads/tourism-crm/` (v5.0.0, Waves 1-10 complete)
- Neon PostgreSQL: eu-central-1 (Frankfurt), 49 models, 32 enums, 7 migrations
- GCP VM: europe-west3-b (Frankfurt) -- same region as Neon
- Prisma shared database pattern: https://www.prisma.io/docs/guides/other/multi-schema
- Neon connection pooling: https://neon.tech/docs/connect/connection-pooling
- Related open thread in CLAUDE.md: "Integration with tourism-crm" (Phase 3)
- Booking calendar Phase B (ISSUES.md I-52): depends on this decision
