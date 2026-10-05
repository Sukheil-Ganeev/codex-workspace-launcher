# VIP-DXB-RUS Telegram Bot Skill

Comprehensive skill for working with VIP-DXB-RUS tourism bot for UAE.

## Structure

```
vip-dxb-rus-telegram-bot/
├── SKILL.md                    # Main skill file (916 lines, complete reference)
├── README.md                   # This file (quick start guide)
├── CHANGELOG.md                # Version history and release notes
├── marketplace.json            # Skill metadata and statistics
│
├── references/                 # Quick reference guides (8 files)
│   ├── block-templates.md      # Ready-to-use block templates
│   ├── form-fields-reference.md # All 110 form fields detailed
│   ├── emoji-standards.md       # Emoji usage guide
│   ├── bug-fixes-guide.md       # How to fix common bugs
│   ├── variables-cheatsheet.md  # Quick variable reference
│   ├── faq.md                   # Frequently asked questions
│   ├── troubleshooting.md       # Common problems and solutions
│   └── cheatsheet.md            # Quick reference card
│
├── assets/
│   ├── templates/              # Production-ready templates (5 files)
│   │   ├── block-excursion.md
│   │   ├── block-menu.md
│   │   ├── block-service-card.md
│   │   ├── form-template.md
│   │   └── payment-confirmation.md
│   │
│   └── examples/               # Real-world examples (5 files)
│       ├── excursion-dubai-modern.md
│       ├── form-yacht-example.md
│       ├── menu-parks-dubai.md
│       ├── service-pool-aura.md
│       └── bugfix-empty-block.md
│
└── scripts/                    # Automation tools (4 files)
    ├── validate-navigation.py  # Check navigation integrity
    ├── check-back-buttons.py   # Find missing Back buttons
    ├── export-variables.py     # Export variables documentation
    └── generate-docs.py        # Auto-generate documentation
```

**Total:** 30 files in comprehensive skill package

## Quick Start

### Use This Skill When

- Creating new bot content (excursions, parks, services)
- Designing booking forms
- Fixing navigation bugs (empty blocks, missing Back buttons)
- Adding new emirates or service categories
- Writing system prompts for Claude API integration
- Debugging form variables

### Templates & Examples Available

**Templates** (`assets/templates/`):
- `block-excursion.md` - Standard excursion card template
- `block-menu.md` - Menu/submenu structure template
- `block-service-card.md` - Service card with booking button
- `form-template.md` - Complete form creation template
- `payment-confirmation.md` - Payment confirmation message

**Examples** (`assets/examples/`):
- `excursion-dubai-modern.md` - Real excursion (block 101)
- `form-yacht-example.md` - Complex 13-field form
- `menu-parks-dubai.md` - Multi-level menu (18 categories)
- `service-pool-aura.md` - Service with form integration
- `bugfix-empty-block.md` - How to fix empty block bug

Copy templates to start new content. Study examples for best practices.

### Key Numbers

- **187 blocks** across 4 emirates
- **11 forms** (10 working + 1 empty)
- **113 variables** with prefixes
- **43 excursions** (Dubai 13, Abu Dhabi 8, RAK 13, Fujairah 9)
- **20 critical bugs** (empty blocks without Back buttons)
- **30 files** in skill package (templates, examples, scripts, references)
- **5 templates** ready to copy
- **5 real examples** for best practices
- **4 automation scripts** for validation and documentation

### Block ID Ranges (Quick Reference)

```
001-003   Commands (/start, /balls, /staff)
010-013   Main menus (emirates)
100-113   Dubai excursions
200-208   Abu Dhabi excursions
300-313   RAK excursions
400-409   Fujairah excursions
500-560   Dubai parks
600-607   Abu Dhabi parks
700-799   Cruises
800-899   Water activities, buggies, pools
850-889   Beach clubs, hotels, restaurants, SPA
950-999   Service blocks (loyalty, payments)
```

### Form Prefixes (Quick Reference)

```
gt_      Group excursions (8 fields)
pt_      Private excursions (9 fields)
buggy_   Buggy & safari (10 fields)
rent_    Car rental (13 fields, with file uploads)
pool_    Infinity pools (11 fields)
beach_   Beach clubs (12 fields)
spa_     SPA services (13 fields)
tr_      Transfer (12 fields)
yacht_   Yacht rental (13 fields, most detailed)
rest_    Restaurant (9 fields)
```

## Critical Bugs to Fix

### Priority 1: Empty Blocks (16 total)

User gets stuck - no way to navigate back!

- **850** Beach clubs (Dubai, Abu Dhabi, RAK, Fujairah)
- **860** Hotels (Dubai, Abu Dhabi, RAK, Fujairah)
- **870** Restaurants (Dubai, Abu Dhabi, RAK, Fujairah)
- **880** SPA/Wellness (Dubai, Abu Dhabi, RAK, Fujairah)

**Quick Fix:** Add text "Section under development" + Back button

### Priority 2: FORM-CRUISE Empty

9 cruise cards link to empty form!

**Fix:** Add 11 fields (copy from FORM-YACHT structure)

### Priority 3: Missing Back Buttons

- **201** Jeep Safari (Abu Dhabi)
- **600** Parks (Abu Dhabi from Fujairah)

## Common Workflows

### Add New Excursion

1. Choose emirate → Determine block ID
2. Create card using template (see `references/block-templates.md`)
3. Add emoji + name to excursion menu
4. Link to FORM-GT and FORM-PT
5. Add Back button
6. Test flow

### Add New Service

1. Assign block ID range
2. Create menu + service cards
3. Design or reuse form
4. Add to main menu
5. Test complete booking flow

### Fix Empty Block

1. Identify block ID
2. Add minimum content:
   - Text: "Section under development" or description
   - Button: ⬅ Back to parent menu
3. Test navigation
4. Mark for future completion

## Documentation Standards

### Block Documentation Template

See `references/block-templates.md` for complete templates.

Minimum required:
- Block ID and name
- Message text
- All buttons (including Back!)
- Incoming paths (where users come from)
- Variables used/set

### Variable Naming Convention

```
[prefix]_[field_name]
```

Examples:
- `gt_client_name` (group tour client name)
- `buggy_duration` (buggy rental duration)
- `spa_technique` (SPA massage technique)

### File Naming

```
Blocks: [ID]-[NAME].md
Forms:  FORM-[NAME].md
```

## Best Practices

### Content Creation

✅ **DO:**
- Always include ⬅ Back button
- Use emoji matching category
- Keep text concise (1-3 sentences)
- Use {{FIRST_NAME_TEXT}} for personalization
- Test all navigation paths

❌ **DON'T:**
- Create blocks without Back button
- Use inconsistent emoji
- Write long descriptions (save for forms)
- Forget to link buttons to blocks
- Skip documentation

### Form Design

✅ **DO:**
- Start with required fields (name, phone, email, date)
- Group related fields
- Limit choices to 2-6 options
- Include "Skip" for optional choices
- Validate data types

❌ **DON'T:**
- Make optional fields required
- Create more than 6 choice buttons
- Forget phone/email validation
- Use unclear field names
- Skip variable documentation

## Integration Examples

### Claude API System Prompt

```python
system_prompt = """You are VIP-DXB-RUS tourism assistant for UAE.

Services: excursions, parks, car rental, yachts, SPA, restaurants
Emirates: Dubai, Abu Dhabi, Ras Al Khaimah, Fujairah
Language: Russian

Help users:
1. Navigate bot structure (187 blocks)
2. Answer service questions
3. Explain booking process
4. Compare group vs private tours
5. Provide prices and details

Response format:
- Friendly and professional Russian
- Include block IDs when referencing
- Use appropriate emoji
- Clarify emirate availability
"""
```

### Few-Shot Examples for Service Queries

```python
examples = [
    {
        "user": "Какие есть экскурсии из Дубая?",
        "assistant": "Из Дубая доступно 13 экскурсий (101-113):\n\n🏙️ Современный Дубай\n🕌 Абу-Даби\n🌊 Индийский океан\n...\n\nКаждая доступна в групповом (FORM-GT) или приватном (FORM-PT) формате."
    },
    {
        "user": "Как забронировать бассейн?",
        "assistant": "Бронирование через FORM-POOL (11 полей):\n\n1. Выбор бассейна (Aura/Cloud22/Address/SLLS)\n2. Дата и сеанс (утро/день/закат/ночь)\n3. Вид (Пальма/Бурдж/Марина)\n4. Ряд (1-я линия/в воде/VIP кабана)\n5. Контактные данные\n\nБассейны доступны только в Дубае."
    }
]
```

## Testing Checklist

### Before Publishing New Content

- [ ] All blocks have Back buttons
- [ ] All buttons link to existing blocks
- [ ] Forms have all required fields
- [ ] Variables follow naming convention (prefix_name)
- [ ] Navigation flow tested (menu → card → form → confirmation)
- [ ] Text uses correct emoji
- [ ] No typos in button text
- [ ] Documentation updated (FULL-EXPORT.md)

### Before Deploying New Form

- [ ] All required fields present (name, phone, email, date)
- [ ] Choice options clear and limited (2-6 per field)
- [ ] Variables documented in ALL-VARIABLES.md
- [ ] Form linked from service cards
- [ ] Payment confirmation block created (980-995)
- [ ] Complete booking flow tested
- [ ] Manager notification configured

## Troubleshooting

### User Stuck in Block

**Symptom:** User can't navigate back
**Cause:** Missing Back button
**Fix:** Add ⬅ Назад button to parent menu

### Form Won't Submit

**Symptom:** "Send" button doesn't work
**Cause:** Validation error or missing field
**Fix:** Check required fields, validate data types

### Service Not in Menu

**Symptom:** Can't find service in bot
**Cause:** Button not added to menu
**Fix:** Add button with correct block ID to appropriate menu

## Success Metrics

Monitor:
- **Navigation success rate** (% completing booking)
- **Form completion rate** (% submitting forms)
- **Bug escape rate** (% stuck users)
- **Variable coverage** (% documented)
- **Content completeness** (% filled vs placeholders)

## Source Documentation

Original analysis based on:
- `D:/Downloads/VIP-DXB-RUS-BOT-DOCS/` (240 files)
- 4 subagent analysis reports
- Complete forms documentation
- Bug tracker files
- Mermaid architecture diagrams

## Scripts

Automation tools in `scripts/` directory:

### `validate-navigation.py`
Validates bot navigation integrity:
- Checks all blocks have Back buttons
- Verifies all button links exist
- Detects circular references
- Reports orphaned blocks

**Usage:** `python scripts/validate-navigation.py [path-to-bot-docs]`

### `check-back-buttons.py`
Scans for missing Back buttons:
- Scans all 187 blocks
- Identifies missing Back buttons
- Generates priority-ranked fix report
- Exports to CSV/JSON

**Usage:** `python scripts/check-back-buttons.py --export=report.csv`

### `export-variables.py`
Exports variable documentation:
- Extracts all 113 variables
- Groups by prefix (gt_, pt_, buggy_, etc.)
- Validates naming conventions
- Generates markdown documentation

**Usage:** `python scripts/export-variables.py --output=variables.md`

### `generate-docs.py`
Auto-generates documentation:
- Creates block documentation
- Builds form field tables
- Generates navigation maps
- Updates FULL-EXPORT.md

**Usage:** `python scripts/generate-docs.py --format=markdown`

## Version History

**v1.0.0** (2026-02-01)
- Initial comprehensive release (30 files)
- 187 blocks documented
- 11 forms analyzed
- 113 variables cataloged
- 20 critical bugs identified
- 5 templates + 5 examples created
- 4 automation scripts added
- 8 reference guides completed

## Next Steps

1. Fix 16 empty blocks (add text + Back button)
2. Complete FORM-CRUISE (11 fields)
3. Add booking buttons (water activities, parks)
4. Standardize emoji usage (⬅️ for Back)
5. Fill placeholder content (cruises, buggies)
6. Create automated testing scripts
7. Set up user journey monitoring

---

**Status:** Production Ready
**Coverage:** 100% of bot architecture
**Last Updated:** 2026-02-01
