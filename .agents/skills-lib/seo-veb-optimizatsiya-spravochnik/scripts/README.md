# SEO Automation Scripts - Complete Toolkit

12 production-ready Node.js scripts for SEO optimization and monitoring. Designed for tourism websites in UAE.

## Installation

```bash
cd scripts/
npm install
cp .env.example .env
# Edit .env with your configuration
```

## Scripts Overview

### 1. Google Search Console Analytics
**File:** `01-google-search-console.js`
**Command:** `npm run gsc`
**Features:**
- Fetch impressions, clicks, CTR from GSC
- Top queries and pages analysis
- Position breakdown reporting
- Export to CSV

**Usage:**
```bash
npm run gsc
```

---

### 2. Rank Position Tracker
**File:** `02-rank-tracker.js`
**Command:** `npm run rank`
**Features:**
- Track keyword positions over time
- Compare with historical data
- Alert on significant drops
- Identify gainers and losers

**Usage:**
```bash
npm run rank
```

---

### 3. Backlink Monitor
**File:** `03-backlink-monitor.js`
**Command:** `npm run backlinks`
**Features:**
- Monitor new backlinks
- Track lost backlinks
- Analyze backlink quality (DR score)
- Identify backlink opportunities

**Configuration:**
- Requires Ahrefs or SEMrush API key (optional)
- Uses mock data for demo

---

### 4. Competitor Analysis
**File:** `04-competitor-analysis.js`
**Command:** `npm run competitor`
**Features:**
- Analyze competitor keywords
- Identify keyword gaps
- Calculate opportunity scores
- Content gap analysis

**Preset Competitors:**
- viator.com
- getyourguide.com
- klook.com

---

### 5. Technical SEO Audit
**File:** `05-seo-audit.js`
**Command:** `npm run audit`
**Features:**
- Meta tags validation
- Heading structure check
- Image alt text analysis
- Core Web Vitals assessment
- Mobile compatibility
- Structured data validation
- Overall score calculation

**Audit Checks:**
- Title tags (50-60 chars)
- Meta descriptions (150-160 chars)
- H1 structure
- Image optimization
- Internal links
- Performance metrics

---

### 6. Sitemap Generator
**File:** `06-sitemap-generator.js`
**Command:** `npm run sitemap`
**Features:**
- Auto-generate XML sitemap
- Create robots.txt
- Validate sitemap structure
- Handle 50K URL limit

**Output Files:**
- `./exports/sitemap.xml`
- `./exports/robots.txt`

---

### 7. Schema.org Validator
**File:** `07-schema-validator.js`
**Command:** `npm run schema`
**Features:**
- Validate JSON-LD schemas
- Check required fields
- Verify schema types
- Identify missing properties
- Export validation results

**Supported Schema Types:**
- Organization
- Product (Tours)
- LocalBusiness
- FAQPage
- Event
- BlogPosting

---

### 8. Meta Tags Optimizer
**File:** `08-meta-optimizer.js`
**Command:** `npm run meta`
**Features:**
- Title tag optimization (50-60 chars)
- Meta description analysis (150-160 chars)
- Keyword presence check
- Call-to-action detection
- Overall score per page

**Optimization Tips:**
- Title best practices
- Description compelling copy
- Keyword density analysis

---

### 9. Keyword Research Tool
**File:** `09-keyword-research.js`
**Command:** `npm run keywords`
**Features:**
- Keyword volume analysis
- Difficulty scoring
- Search intent classification
- Opportunity calculation
- Priority ranking

**Intent Types:**
- Informational
- Commercial
- Transactional
- Navigational

**Priority Levels:**
- CRITICAL: High volume, low difficulty
- HIGH: Good balance
- MEDIUM: Moderate difficulty
- LOW: Hard to rank

---

### 10. Content Optimizer
**File:** `10-content-optimizer.js`
**Command:** `npm run content`
**Features:**
- Word count analysis
- Keyword density check
- Readability assessment
- Heading structure validation
- Content length recommendations

**Content Metrics:**
- Word count (recommended 1500+)
- Keyword mentions and density (1-3%)
- Flesch Reading Ease score
- Heading hierarchy

---

### 11. Image Optimizer
**File:** `11-image-optimizer.js`
**Command:** `npm run images`
**Features:**
- Alt text validation
- Image format analysis
- Compression recommendations
- WebP conversion suggestions
- Size optimization

**Checks:**
- Missing alt text
- File size (recommended <100KB)
- Image dimensions
- WebP availability
- Potential savings calculation

---

### 12. Performance Monitor
**File:** `12-performance-monitor.js`
**Command:** `npm run performance`
**Features:**
- Core Web Vitals monitoring
- Lighthouse scores
- PageSpeed metrics
- Mobile vs desktop comparison
- Optimization recommendations

**Metrics:**
- LCP (Largest Contentful Paint) < 2.5s
- FID (First Input Delay) < 100ms
- CLS (Cumulative Layout Shift) < 0.1
- INP (Interaction to Next Paint) < 200ms
- TTFB (Time to First Byte) < 600ms

---

## Configuration

### Environment Variables (.env)

```env
# Google APIs
GOOGLE_CREDENTIALS_PATH=./config/google-credentials.json
GOOGLE_PROPERTY_URL=https://example.com

# Website
WEBSITE_URL=https://example.com
WEBSITE_DOMAIN=example.com

# Optional APIs
SEMRUSH_API_KEY=your_key
AHREFS_API_KEY=your_key

# Export settings
EXPORT_PATH=./exports
CSV_EXPORT=true
JSON_EXPORT=true

# Alerts
RANKING_DROP_THRESHOLD=5
TRAFFIC_DROP_THRESHOLD=20
```

### Google Credentials Setup

1. Create service account in Google Cloud Console
2. Download JSON credentials
3. Save to `./config/google-credentials.json`
4. Grant permissions:
   - Google Search Console API
   - Google Analytics API
   - PageSpeed Insights API

---

## Usage Examples

### Run All Audits
```bash
npm run audit      # Technical SEO audit
npm run meta       # Meta tags check
npm run content    # Content analysis
npm run images     # Image optimization
npm run schema     # Schema validation
```

### Monitoring
```bash
npm run gsc        # Google Search Console data
npm run rank       # Keyword rankings
npm run backlinks  # Backlink analysis
npm run competitor # Competitor research
npm run performance # Core Web Vitals
```

### Setup
```bash
npm run sitemap    # Generate sitemap
npm run keywords   # Keyword research
```

---

## Output Exports

All scripts export data to `./exports/`:

- `gsc-top-queries.csv` - Top performing queries
- `gsc-top-pages.csv` - Top performing pages
- `rank-history.json` - Ranking history
- `backlink-history.json` - Backlink tracking
- `sitemap.xml` - XML sitemap
- `robots.txt` - Robots file
- `schema-validation.json` - Schema validation results

---

## Performance Benchmarks

**Script execution times:**
- GSC Analytics: 2-3 seconds
- Rank Tracker: 2-3 seconds
- SEO Audit: 1-2 seconds
- Meta Optimizer: <1 second
- Content Analysis: <1 second
- Image Analysis: <1 second
- Schema Validation: 1-2 seconds
- Sitemap Generation: <1 second

---

## Error Handling

All scripts include:
- Try-catch error handling
- Detailed error messages
- Graceful failures
- Retry logic for API calls
- Timeout protection

---

## Integration

### Cron Jobs (Linux/Mac)
```bash
# Daily GSC analysis at 8 AM
0 8 * * * cd /path/to/scripts && npm run gsc >> logs/gsc.log 2>&1

# Daily rank tracking at 9 AM
0 9 * * * cd /path/to/scripts && npm run rank >> logs/rank.log 2>&1

# Weekly performance check
0 10 * * 0 cd /path/to/scripts && npm run performance >> logs/performance.log 2>&1
```

### Docker
```dockerfile
FROM node:18-slim
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "run", "gsc"]
```

---

## Support & Documentation

- See main SKILL.md for SEO theory
- See references/ for detailed guides
- Check examples/ for implementation samples
- Read experience/ for lessons learned

---

## License

All scripts are provided as-is for SEO optimization purposes.

---

## Created

2026-02-04 | SEO Automation Toolkit v1.0
