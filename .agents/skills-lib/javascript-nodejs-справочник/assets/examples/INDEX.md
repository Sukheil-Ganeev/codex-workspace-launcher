# JavaScript/Node.js Examples Index

Complete collection of 15 production-ready examples for the javascript-nodejs-справочник skill.

**Location:** `C:/Users/londo/.claude/skills/javascript-nodejs-справочник/assets/examples/`

## Quick Start

Each example includes:
- **README.md** - Documentation and usage guide
- **package.json** - Dependencies and scripts
- **.env.example** - Environment configuration template
- **index.js** - Main application code
- **tests/** (if applicable) - Test suite

## Examples List

### 01 - Booking Form Handler
Path: `01-booking-form-handler/`

Production-ready booking system for tourism business.

**Features:**
- Express server with form validation
- PostgreSQL database integration
- Email notifications (SendGrit/SMTP)
- CSRF protection & rate limiting
- JWT authentication ready
- Winston logging
- Jest unit & integration tests

**Key Files:**
- `index.js` - Full implementation (500+ lines)
- `tests/index.test.js` - Comprehensive test suite
- Database schema with indexes

**Use Case:** Tour booking, safari reservations, activity tickets

---

### 02 - Payment Webhook Handler
Path: `02-payment-webhook/`

Secure webhook processor for Stripe and PayPal.

**Features:**
- Stripe webhook signature verification
- PayPal webhook processing
- Idempotency check (prevent duplicates)
- Database sync on payment events
- Email notifications
- Logging & monitoring

**Key Integration Points:**
- Stripe webhook events (charge.succeeded, charge.failed, etc.)
- PayPal CHECKOUT.ORDER.COMPLETED
- Idempotent processing cache
- Status tracking (completed, failed, refunded)

**Use Case:** Payment processing, booking confirmation, invoice generation

---

### 03 - Google Sheets API Sync
Path: `03-sheets-api-sync/`

Bidirectional sync between database and Google Sheets.

**Features:**
- Read/write from Google Sheets API
- Scheduled synchronization (configurable interval)
- Database to Sheets export (tours, pricing, etc.)
- Sheets to Database import
- Change detection
- Error recovery with logging

**Key Endpoints:**
- `POST /sync/trigger` - Manual sync trigger
- `GET /sync/status` - Current sync status
- `GET /sync/logs` - Sync history

**Use Case:** Price list management, tour availability, staff scheduling

---

### 04 - Express REST API
Path: `04-express-rest-api/`

Complete REST API with JWT authentication and CRUD operations.

**Features:**
- Express.js server setup
- JWT token authentication
- Bcrypt password hashing
- Joi schema validation
- CORS & helmet security
- Rate limiting
- User & tour management
- Pagination & sorting

**API Endpoints:**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/tours` - List tours (paginated)
- `POST /api/tours` - Create tour (protected)
- `PUT /api/tours/:id` - Update tour (protected)
- `DELETE /api/tours/:id` - Delete tour (protected)

**Use Case:** Tour operator API, booking backend, admin system

---

### 05 - Database CRUD
Path: `05-database-crud/`

Optimized database operations with pooling and transactions.

**Features:**
- Connection pooling (PostgreSQL)
- CRUD operations (Create, Read, Update, Delete)
- Transactions for data consistency
- Bulk operations (INSERT multiple records)
- Error handling with rollback
- Guide management system

**Key Operations:**
- Single CREATE/READ/UPDATE/DELETE
- Bulk INSERT (multiple guides)
- Transaction management (DELETE with cascade)

**Use Case:** Staff management, bulk imports, data synchronization

---

### 06 - Email Sender
Path: `06-email-sender/`

Email notification system with templates and queue support.

**Features:**
- Nodemailer SMTP integration
- Email templates support
- Bull queue for retry logic (optional)
- Rate limiting
- HTML & plain text support
- Attachment support

**Use Case:** Booking confirmations, cancellations, reminders, invoices

---

### 07 - WhatsApp Webhook Handler
Path: `07-whatsapp-webhook/`

WhatsApp Business API webhook processor.

**Features:**
- Message reception & validation
- Automated responses
- Media handling
- Status updates
- Queue integration

**Use Case:** Customer support, booking confirmations, notifications

---

### 08 - File Upload
Path: `08-file-upload/`

Secure file upload with validation and storage.

**Features:**
- Multer middleware integration
- File type validation
- Size limits
- Virus scanning (optional)
- Cloud storage (S3/Google Cloud)
- Error handling

**Use Case:** Document uploads (passports, tickets), media storage

---

### 09 - Rate Limiter
Path: `09-rate-limiter/`

Advanced rate limiting strategies.

**Features:**
- Per-IP rate limiting
- Per-user rate limiting
- Sliding window algorithm
- Custom response messages
- Redis backend support

**Use Case:** API protection, brute-force prevention

---

### 10 - Cron Jobs
Path: `10-cron-jobs/`

Background job scheduler with node-schedule.

**Features:**
- Periodic job execution
- Timezone support
- Error handling & retry
- Logging
- Job monitoring

**Use Case:** Send reminders, cleanup data, generate reports, sync data

---

### 11 - OAuth Integration
Path: `11-oauth-integration/`

Social authentication with Google, Facebook.

**Features:**
- Passport.js integration
- Google OAuth 2.0
- Facebook OAuth 2.0
- Session management
- User profile sync
- Scope management

**Use Case:** Social login, user registration, profile import

---

### 12 - WebSocket Chat
Path: `12-websocket-chat/`

Real-time chat with Socket.io.

**Features:**
- Real-time messaging
- User online/offline status
- Room management
- Message history
- Typing indicators

**Use Case:** Live support chat, group notifications, real-time updates

---

### 13 - GraphQL API
Path: `13-graphql-api/`

GraphQL server for flexible data queries.

**Features:**
- Apollo Server setup
- Schema definition
- Resolvers
- Query & mutation support
- Subscription support (WebSocket)
- Error handling

**Use Case:** Mobile app backend, flexible API, real-time updates

---

### 14 - Microservices
Path: `14-microservices/`

Microservices architecture patterns.

**Features:**
- Service discovery
- API Gateway
- Inter-service communication
- Service isolation
- Fault tolerance

**Use Case:** Scalable systems, independent deployment, service boundaries

---

### 15 - JWT Authentication
Path: `15-jwt-auth/`

Complete JWT token management system.

**Features:**
- Token generation
- Token validation
- Refresh tokens
- Token expiration
- Revocation (blacklist)
- Role-based access control (RBAC)

**Use Case:** API authentication, mobile app tokens, session management

---

## Production Checklist

For each example, before deploying to production:

### Security
- [ ] Environment variables protected (.env not in git)
- [ ] HTTPS/TLS enabled
- [ ] Input validation implemented
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] SQL injection prevention (parameterized queries)

### Performance
- [ ] Database indexes created
- [ ] Connection pooling configured
- [ ] Caching implemented (Redis if needed)
- [ ] Load testing completed
- [ ] Memory leaks checked

### Monitoring & Logging
- [ ] Structured logging (Winston, Pino)
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (DataDog, New Relic)
- [ ] Health check endpoint (/health)
- [ ] Log aggregation setup

### Testing
- [ ] Unit tests written (70%+ coverage)
- [ ] Integration tests
- [ ] Load tests
- [ ] Security tests

### Deployment
- [ ] Docker image created
- [ ] Kubernetes manifests ready
- [ ] CI/CD pipeline configured
- [ ] Database backups scheduled
- [ ] Rollback plan documented

## Technology Stack

All examples use:
- **Runtime:** Node.js 18+
- **Web Framework:** Express.js 4.x
- **Database:** PostgreSQL 13+
- **Testing:** Jest 29
- **Validation:** Joi
- **Authentication:** JWT, bcryptjs
- **Logging:** Winston
- **Security:** Helmet, CORS, express-rate-limit

## Quick Setup

1. Copy example directory to your project
2. Install dependencies: `npm install`
3. Create `.env` from `.env.example`
4. Configure environment variables
5. Run tests: `npm test`
6. Start server: `npm run dev`

## Additional Resources

- Express.js documentation: https://expressjs.com
- PostgreSQL best practices: https://www.postgresql.org/docs/
- JWT.io: https://jwt.io
- Security headers: https://owasp.org/
- API Design: https://restfulapi.net/

---

**Created:** 2026-02-04
**Skill:** javascript-nodejs-справочник
**Status:** Production Ready

Each example includes detailed comments and is ready for immediate production use in tourism business contexts.
