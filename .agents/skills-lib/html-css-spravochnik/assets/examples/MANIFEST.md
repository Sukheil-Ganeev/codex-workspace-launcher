# HTML/CSS Examples Manifest

Created: 2024-02-04
Total Examples: 9

## Examples Overview

### 1. tour-landing (Landing Page)
**Purpose:** Complete tour landing page with hero section, features, testimonials
**Files:** index.html, styles.css, script.js, README.md
**Features:**
- Sticky navbar with smooth scrolling
- Hero section with CTA
- Features grid (4 columns)
- Tour cards with pricing
- Pricing table
- Customer testimonials
- Booking form with validation
- Responsive design

**Use Case:** Main website for tour operator in Dubai

---

### 2. price-list (Dynamic Pricing)
**Purpose:** Interactive price list with currency conversion and group discounts
**Files:** index.html, styles.css, script.js, data.json, README.md
**Features:**
- Currency selector (AED, USD, RUB)
- Group size calculator
- Dynamic price updates
- Group discount cards
- Responsive pricing table
- API-ready data structure

**Technologies:** Vanilla JS, real-time calculations
**Use Case:** B2B pricing portal for travel agencies

---

### 3. booking-system (Reservation Management)
**Purpose:** Full booking form with live price calculation and local storage
**Files:** index.html, styles.css, script.js, config.json, README.md
**Features:**
- Multi-field booking form
- Tour selection with auto price update
- Adult/Children pricing tiers
- Summary panel (sticky)
- LocalStorage for persistence
- Date picker
- Form validation

**Technologies:** FormAPI, LocalStorage
**Use Case:** Booking page for tour website

---

### 4. tour-cards (Product Showcase)
**Purpose:** Dynamic card grid showcasing tour packages
**Files:** index.html, styles.css, script.js, data.json, README.md
**Features:**
- Grid layout (responsive 3-column)
- Dynamic card rendering from JSON
- Hover animations
- Feature lists
- Price display
- Action buttons
- Mobile-friendly

**Technologies:** ES6 Array.map(), Grid CSS
**Use Case:** Tour packages showcase/catalog

---

### 5. gallery (Photo Gallery)
**Purpose:** Lightbox photo gallery with modal overlay
**Files:** index.html, styles.css, script.js, README.md
**Features:**
- Grid photo layout
- Click-to-enlarge modal
- SVG placeholder images
- Close button (X)
- Image captions
- Smooth transitions
- Mobile optimized

**Technologies:** Modal pattern, SVG data URIs
**Use Case:** Trip photos showcase

---

### 6. calculator (Price Calculator)
**Purpose:** Interactive tour price calculator with multiple tiers
**Files:** index.html, styles.css, script.js, README.md
**Features:**
- Tour selection dropdown
- Adult/Children quantity inputs
- Real-time calculation
- Results display with breakdown
- Child discount (30%)
- Beautiful result formatting
- Input validation

**Technologies:** DOM manipulation, Math calculations
**Use Case:** Quick price estimation tool

---

### 7. maps-route (Google Maps Integration)
**Purpose:** Interactive map showing tour route from Dubai to desert
**Files:** index.html, styles.css, script.js, README.md
**Features:**
- Google Maps API integration
- Route markers (start/end)
- Map controls
- Route info panel
- Distance/Duration display
- Responsive layout
- Two-column design

**Technologies:** Google Maps API v3
**Requirements:** Valid Google Maps API key
**Use Case:** Visual route planning

---

### 8. contact-form (Contact/Support)
**Purpose:** Contact form with email validation and response feedback
**Files:** index.html, styles.css, script.js, README.md
**Features:**
- Contact form with validation
- Multiple input types (text, email, tel, textarea)
- Subject selection
- Success/Error status messages
- Contact info sidebar
- Business hours display
- Mobile responsive

**Technologies:** Form validation, DOM API
**Use Case:** Customer inquiries/support requests

---

### 9. sheets-integration (CRM/Bookings Database)
**Purpose:** Local booking management system with localStorage
**Files:** index.html, styles.css, script.js, README.md
**Features:**
- View existing bookings (table)
- Add new bookings (form)
- LocalStorage persistence
- Dynamic table rendering
- Form submission handling
- Status display
- Empty state handling

**Technologies:** LocalStorage API, Table DOM manipulation
**Extension:** Can be connected to Google Sheets API
**Use Case:** Internal booking management system

---

## File Structure
```
assets/examples/
├── tour-landing/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── README.md
│   └── images/
├── price-list/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── data.json
│   ├── README.md
│   └── images/
├── booking-system/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── config.json
│   ├── README.md
│   └── images/
├── tour-cards/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── data.json
│   ├── README.md
│   └── images/
├── gallery/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── README.md
│   └── images/
├── calculator/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── README.md
│   └── images/
├── maps-route/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── README.md
│   └── images/
├── contact-form/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── README.md
│   └── images/
└── sheets-integration/
    ├── index.html
    ├── styles.css
    ├── script.js
    ├── README.md
    └── images/
```

## Key Technologies Used
- HTML5 semantic markup
- CSS3 with gradients, transitions, grid/flex
- Vanilla JavaScript (ES6+)
- Google Maps API
- LocalStorage API
- JSON data formats

## Design System
- Primary Color: #667eea (Indigo)
- Secondary Color: #FF6B35 (Orange)
- Accent Color: #764ba2 (Purple)
- Font: Segoe UI (sans-serif)
- Responsive breakpoints: 768px, 1200px

## Features Implemented
- Responsive design (mobile-first)
- API-ready data structures
- Form validation
- Dynamic rendering
- Local data persistence
- Third-party integrations (Google Maps)
- Modern UI/UX patterns
- Accessibility considerations

## Ready for Production
All examples are:
- Fully functional
- Copy-paste ready
- Well-structured
- Documented
- Tested responsive
- Business-focused (UAE tourism)
