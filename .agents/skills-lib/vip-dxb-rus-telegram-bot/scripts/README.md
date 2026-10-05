# VIP-DXB-RUS Bot Scripts

Automation scripts for managing and validating Telegram bot content blocks and forms.

## Overview

This directory contains Python scripts to help with:
- **Validation**: Check blocks and forms for errors
- **Generation**: Create new blocks with proper structure
- **Fixing**: Automatically repair empty/placeholder blocks

## Scripts

### 1. validate-block.py

Validates content blocks to ensure they meet all requirements.

**Features:**
- Checks required fields (Type, Date, Text)
- Validates Back button presence
- Verifies emoji usage against standards
- Validates table structure
- Checks button formatting
- Validates metadata

**Usage:**
```bash
# Validate single block
python validate-block.py ../blocks/850-dubai-excursions.md

# Validate multiple blocks with glob
python validate-block.py ../blocks/*.md

# Verbose output
python validate-block.py -v path/to/block.md
```

**Exit codes:**
- `0`: All files valid
- `1`: One or more files invalid

**Example output:**
```
✅ VALID: 850-dubai-excursions.md
  No issues found!

❌ INVALID: 851-desert-safari.md

🔴 Errors (2):
  - Missing required field: Date
  - Missing Back button - every block must have navigation back

🟡 Warnings (1):
  - Text section seems too short (less than 10 characters)
```

---

### 2. validate-form.py

Validates booking forms for proper structure and fields.

**Features:**
- Checks all required fields (name, phone, email, date)
- Validates variable prefix consistency
- Verifies field types (TEXT, PHONE, EMAIL, DATE, etc.)
- Checks CHOICE options (must have 2-6 variants)
- Validates form metadata

**Usage:**
```bash
# Validate single form
python validate-form.py FORM-DESERT-SAFARI.md

# Validate multiple forms
python validate-form.py ../forms/FORM-*.md

# Verbose output with field details
python validate-form.py -v FORM-HOTEL-BOOKING.md
```

**Exit codes:**
- `0`: All forms valid
- `1`: One or more forms invalid

**Example output:**
```
✅ VALID: FORM-DESERT-SAFARI.md

📋 Found 6 fields:
  - name (TEXT) - Required
  - phone (PHONE) - Required
  - email (EMAIL) - Required
  - date (DATE) - Required
  - desert_safari_time (CHOICE) - Required
  - desert_safari_package (CHOICE) - Optional

🟡 Warnings (1):
  - PHONE field 'phone' should have validation rules
```

---

### 3. generate-block.py

Generates new content blocks with proper structure and standards.

**Features:**
- Auto-generates next available block ID
- Creates properly formatted markdown
- Includes standard emoji
- Adds navigation buttons
- Supports multiple block types
- Follows naming conventions

**Block types:**
- `excursion` - Tours and excursions
- `restaurant` - Dining venues
- `hotel` - Accommodation
- `transport` - Transportation services
- `service` - General services
- `info` - Information pages

**Usage:**
```bash
# Generate excursion block
python generate-block.py --type excursion --name "Desert Safari" --emirate Dubai

# Generate restaurant block
python generate-block.py --type restaurant --name "Fine Dining" --emirate "Abu Dhabi"

# Generate with custom ID and parent
python generate-block.py --type hotel --name "Luxury Resort" --emirate Dubai --id 1050 --parent 900

# Generate to specific location
python generate-block.py --type info --name "Visa Info" --emirate UAE --output ../blocks/custom.md
```

**Options:**
- `--type, -t`: Block type (required)
- `--name, -n`: Block name/title (required)
- `--emirate, -e`: Emirate or location (required)
- `--parent, -p`: Parent block ID for navigation
- `--id`: Custom block ID (auto-generated if not provided)
- `--output, -o`: Custom output file path
- `--output-dir, -d`: Output directory (default: current directory)

**Example output:**
```
✅ Block generated successfully!
   ID: 1050
   File: C:/Users/londo/.claude/skills/vip-dxb-rus-telegram-bot/blocks/1050-desert-safari.md
   Type: excursion
   Name: Desert Safari

📝 Next steps:
   1. Edit the content in 1050-desert-safari.md
   2. Add media files
   3. Validate with: python validate-block.py 1050-desert-safari.md
```

---

### 4. fix-empty-blocks.py

Automatically fixes empty/placeholder blocks with proper content.

**Features:**
- Fixes 32 critical empty blocks (850-886)
- Adds "Section under development" message
- Creates proper navigation structure
- Generates Back buttons
- Includes metadata and TODOs
- Supports dry-run mode

**Fixed block ranges:**
- **850-856**: Dubai excursions
- **860-866**: Abu Dhabi excursions
- **870-876**: Sharjah excursions
- **880-886**: Other emirates excursions

**Usage:**
```bash
# Fix all empty blocks
python fix-empty-blocks.py --output-dir ../blocks

# Dry run (preview changes without writing)
python fix-empty-blocks.py --dry-run

# Fix specific blocks only
python fix-empty-blocks.py --blocks 850,860,870 --output-dir ./output

# Generate summary report
python fix-empty-blocks.py --output-dir ../blocks --report
```

**Options:**
- `--output-dir, -o`: Output directory for fixed blocks (default: ./blocks)
- `--blocks, -b`: Comma-separated list of block IDs to fix (default: all)
- `--dry-run`: Preview changes without writing files
- `--report, -r`: Generate summary report after fixing

**Example output:**
```
Fixing 32 blocks...
Output directory: ../blocks

Processing 850: Dubai Excursions (menu)...
  ✅ Created: 850-dubai-excursions.md

Processing 851: Desert Safari Dubai (excursion)...
  ✅ Created: 851-desert-safari-dubai.md

...

============================================================
✅ Fixed 32 blocks successfully!
📁 Output: ../blocks
📄 Report: ../blocks/FIX-REPORT.md
============================================================

📝 Next steps:
   1. Review generated files
   2. Add detailed content
   3. Validate: python validate-block.py blocks/*.md
```

---

## Installation

All scripts use Python 3.6+ standard library. No additional dependencies required.

**Requirements:**
- Python 3.6 or higher
- UTF-8 file encoding support

**Setup:**
```bash
# Make scripts executable (Linux/Mac)
chmod +x *.py

# Verify Python version
python --version
```

---

## Workflow Examples

### Creating New Content

1. **Generate a new block:**
```bash
python generate-block.py --type excursion --name "Hatta Mountain Tour" --emirate Dubai --output-dir ../blocks
```

2. **Edit the generated file** to add detailed content

3. **Validate the block:**
```bash
python validate-block.py ../blocks/1050-hatta-mountain-tour.md
```

4. **Fix any errors** reported by validation

5. **Re-validate** until clean

---

### Fixing Empty Blocks

1. **Preview changes (dry run):**
```bash
python fix-empty-blocks.py --dry-run --output-dir ../blocks
```

2. **Fix all blocks:**
```bash
python fix-empty-blocks.py --output-dir ../blocks --report
```

3. **Review the generated files**

4. **Validate all fixed blocks:**
```bash
python validate-block.py ../blocks/*.md
```

---

### Form Validation Workflow

1. **Create a booking form** (manually)

2. **Validate the form:**
```bash
python validate-form.py ../forms/FORM-DESERT-SAFARI.md -v
```

3. **Fix errors** based on validation output

4. **Re-validate** to ensure compliance

---

## Standards and Conventions

### Block Naming
- Format: `{ID}-{slug}.md`
- Example: `850-dubai-excursions.md`
- ID is numeric (3-4 digits)
- Slug is lowercase with hyphens

### Form Naming
- Format: `FORM-{NAME}.md`
- Example: `FORM-DESERT-SAFARI.md`
- Name is uppercase with hyphens

### Variable Naming
- Standard fields: `name`, `phone`, `email`, `date`
- Custom fields: `{formname}_{fieldname}`
- Example: `desert_safari_time`

### Emoji Standards
Refer to `../references/emoji-standards.md` for approved emoji usage.

---

## Troubleshooting

### Script won't run
```bash
# Check Python version
python --version

# Try python3 instead
python3 validate-block.py file.md

# Check file permissions
ls -la *.py
```

### Encoding errors
All scripts use UTF-8. Ensure your terminal supports UTF-8:
```bash
# Windows
chcp 65001

# Linux/Mac
export LANG=en_US.UTF-8
```

### Validation fails
Common issues:
- Missing required fields
- Incorrect date format (use YYYY-MM-DD)
- Missing Back button
- Invalid table structure
- Wrong variable prefix in forms

---

## Contributing

When modifying scripts:
1. Maintain docstrings
2. Add argparse help text
3. Include usage examples
4. Handle errors gracefully
5. Test with sample data

---

## Support

For issues or questions:
- Check script help: `python script.py --help`
- Review examples in this README
- Consult main SKILL.md documentation
- Test with `--dry-run` first

---

## Version History

**v1.0.0** (2026-02-01)
- Initial release
- Four core scripts
- Comprehensive validation
- Block generation
- Empty block fixing

---

## License

Part of VIP-DXB-RUS Telegram Bot skill for Claude Code.
