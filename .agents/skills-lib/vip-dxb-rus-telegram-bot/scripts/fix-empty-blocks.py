#!/usr/bin/env python3
"""
Empty Blocks Fixer for VIP-DXB-RUS Telegram Bot

Automatically fixes empty/placeholder blocks:
- Adds "Section under development" message
- Adds Back button to parent menu
- Creates proper file structure
- Generates documentation

Fixes these critical blocks:
- 850: Dubai Excursions
- 851-856: Specific Dubai excursions
- 860: Abu Dhabi Excursions
- 861-866: Specific Abu Dhabi excursions
- 870: Sharjah Excursions
- 871-876: Specific Sharjah excursions
- 880: Other Emirates Excursions
- 881-886: Specific other emirates excursions

Usage:
    python fix-empty-blocks.py --output-dir ../blocks
    python fix-empty-blocks.py --dry-run
    python fix-empty-blocks.py --blocks 850,860,870 --output-dir ./output
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


# Critical empty blocks configuration
EMPTY_BLOCKS = {
    # Dubai Excursions
    '850': {
        'name': 'Dubai Excursions',
        'parent': '800',
        'type': 'menu',
        'emirate': 'Dubai',
        'description': 'Main menu for Dubai excursions and tours',
    },
    '851': {
        'name': 'Desert Safari Dubai',
        'parent': '850',
        'type': 'excursion',
        'emirate': 'Dubai',
        'description': 'Desert safari experience in Dubai',
    },
    '852': {
        'name': 'City Tour Dubai',
        'parent': '850',
        'type': 'excursion',
        'emirate': 'Dubai',
        'description': 'Comprehensive city tour of Dubai',
    },
    '853': {
        'name': 'Burj Khalifa Tour',
        'parent': '850',
        'type': 'excursion',
        'emirate': 'Dubai',
        'description': 'Visit to Burj Khalifa observation deck',
    },
    '854': {
        'name': 'Dubai Marina Cruise',
        'parent': '850',
        'type': 'excursion',
        'emirate': 'Dubai',
        'description': 'Evening cruise in Dubai Marina',
    },
    '855': {
        'name': 'Dubai Parks and Resorts',
        'parent': '850',
        'type': 'excursion',
        'emirate': 'Dubai',
        'description': 'Theme parks and entertainment',
    },
    '856': {
        'name': 'Dubai Aquarium',
        'parent': '850',
        'type': 'excursion',
        'emirate': 'Dubai',
        'description': 'Dubai Mall Aquarium visit',
    },

    # Abu Dhabi Excursions
    '860': {
        'name': 'Abu Dhabi Excursions',
        'parent': '800',
        'type': 'menu',
        'emirate': 'Abu Dhabi',
        'description': 'Main menu for Abu Dhabi excursions',
    },
    '861': {
        'name': 'Sheikh Zayed Mosque',
        'parent': '860',
        'type': 'excursion',
        'emirate': 'Abu Dhabi',
        'description': 'Visit to the Grand Mosque',
    },
    '862': {
        'name': 'Louvre Abu Dhabi',
        'parent': '860',
        'type': 'excursion',
        'emirate': 'Abu Dhabi',
        'description': 'Museum tour and cultural experience',
    },
    '863': {
        'name': 'Ferrari World',
        'parent': '860',
        'type': 'excursion',
        'emirate': 'Abu Dhabi',
        'description': 'Theme park visit',
    },
    '864': {
        'name': 'Yas Island',
        'parent': '860',
        'type': 'excursion',
        'emirate': 'Abu Dhabi',
        'description': 'Entertainment island tour',
    },
    '865': {
        'name': 'Abu Dhabi City Tour',
        'parent': '860',
        'type': 'excursion',
        'emirate': 'Abu Dhabi',
        'description': 'Comprehensive city tour',
    },
    '866': {
        'name': 'Qasr Al Watan',
        'parent': '860',
        'type': 'excursion',
        'emirate': 'Abu Dhabi',
        'description': 'Presidential palace tour',
    },

    # Sharjah Excursions
    '870': {
        'name': 'Sharjah Excursions',
        'parent': '800',
        'type': 'menu',
        'emirate': 'Sharjah',
        'description': 'Main menu for Sharjah excursions',
    },
    '871': {
        'name': 'Sharjah Heritage Tour',
        'parent': '870',
        'type': 'excursion',
        'emirate': 'Sharjah',
        'description': 'Cultural heritage experience',
    },
    '872': {
        'name': 'Sharjah Museums',
        'parent': '870',
        'type': 'excursion',
        'emirate': 'Sharjah',
        'description': 'Museum tours in Sharjah',
    },
    '873': {
        'name': 'Al Qasba',
        'parent': '870',
        'type': 'excursion',
        'emirate': 'Sharjah',
        'description': 'Entertainment and dining area',
    },
    '874': {
        'name': 'Sharjah Aquarium',
        'parent': '870',
        'type': 'excursion',
        'emirate': 'Sharjah',
        'description': 'Marine life experience',
    },
    '875': {
        'name': 'Sharjah Desert Park',
        'parent': '870',
        'type': 'excursion',
        'emirate': 'Sharjah',
        'description': 'Wildlife and nature park',
    },
    '876': {
        'name': 'Sharjah Art Foundation',
        'parent': '870',
        'type': 'excursion',
        'emirate': 'Sharjah',
        'description': 'Art galleries and exhibitions',
    },

    # Other Emirates Excursions
    '880': {
        'name': 'Other Emirates Excursions',
        'parent': '800',
        'type': 'menu',
        'emirate': 'UAE',
        'description': 'Excursions in other emirates',
    },
    '881': {
        'name': 'Jebel Jais (RAK)',
        'parent': '880',
        'type': 'excursion',
        'emirate': 'Ras Al Khaimah',
        'description': 'Mountain adventure and zipline',
    },
    '882': {
        'name': 'Fujairah Beach',
        'parent': '880',
        'type': 'excursion',
        'emirate': 'Fujairah',
        'description': 'Beach resort experience',
    },
    '883': {
        'name': 'Ajman Museum',
        'parent': '880',
        'type': 'excursion',
        'emirate': 'Ajman',
        'description': 'Historical museum tour',
    },
    '884': {
        'name': 'UAQ Mangroves',
        'parent': '880',
        'type': 'excursion',
        'emirate': 'Umm Al Quwain',
        'description': 'Mangrove kayaking tour',
    },
    '885': {
        'name': 'Hatta Mountain Tour',
        'parent': '880',
        'type': 'excursion',
        'emirate': 'Dubai (Hatta)',
        'description': 'Mountain and heritage village',
    },
    '886': {
        'name': 'Dibba Diving',
        'parent': '880',
        'type': 'excursion',
        'emirate': 'Fujairah',
        'description': 'Scuba diving experience',
    },
}


class BlockFixer:
    """Fixes empty/placeholder blocks."""

    def __init__(self, output_dir: Path, dry_run: bool = False):
        """Initialize fixer."""
        self.output_dir = output_dir
        self.dry_run = dry_run
        self.fixed_count = 0

    def generate_menu_block(self, block_id: str, config: Dict) -> str:
        """Generate menu block content."""
        return f"""# 🎭 {config['name']}

Type: Menu
Emirate: {config['emirate']}
Date: {datetime.now().strftime('%Y-%m-%d')}
Status: Under Development

## Text

**🎭 {config['name']}**

This section is currently under development. We are working on adding exciting excursions and tours in {config['emirate']}.

**Coming soon:**
- Detailed tour descriptions
- Pricing information
- Booking options
- Photo galleries

📞 For immediate assistance, please contact our support team.

## Buttons

[📞 Contact Support](callback:contact_support)
[🔙 Back to Excursions](callback:menu_{config['parent']})

## Metadata

- Category: Menu
- Block ID: {block_id}
- Parent: {config['parent']}
- Tags: {config['emirate']}, excursions, menu
- Status: Under Development
- Language: Russian
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}

## Notes

**Development Status:** This is a placeholder block.

**TODO:**
- [ ] Add list of available excursions
- [ ] Create sub-blocks for each excursion
- [ ] Add pricing information
- [ ] Include photos and media
"""

    def generate_excursion_block(self, block_id: str, config: Dict) -> str:
        """Generate excursion block content."""
        return f"""# 🎭 {config['name']}

Type: Excursion
Emirate: {config['emirate']}
Date: {datetime.now().strftime('%Y-%m-%d')}
Status: Under Development

## Text

**🎭 {config['name']}**

{config['description']}

This excursion is currently under development. Detailed information will be available soon.

**📍 Location:** {config['emirate']}
**🕐 Duration:** To be announced
**💰 Price:** Contact for pricing

### What's Included

Content coming soon...

### Highlights

- More information will be added soon
- Detailed itinerary in development
- Pricing and booking options coming

📞 **Interested?** Contact our team for more information and early booking.

## Media

[Photos will be added]

## Buttons

[📞 Contact for Details](callback:contact_support)
[🔙 Back](callback:menu_{config['parent']})

## Metadata

- Category: Excursion
- Block ID: {block_id}
- Parent: {config['parent']}
- Tags: {config['emirate']}, excursion, under development
- Status: Under Development
- Language: Russian
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}

## Notes

**Development Status:** Placeholder block - content needs to be added.

**TODO:**
- [ ] Add detailed description
- [ ] Include pricing information
- [ ] Add itinerary details
- [ ] Upload photos
- [ ] Create booking form
- [ ] Add customer reviews
"""

    def generate_block_content(self, block_id: str, config: Dict) -> str:
        """Generate block content based on type."""
        if config['type'] == 'menu':
            return self.generate_menu_block(block_id, config)
        elif config['type'] == 'excursion':
            return self.generate_excursion_block(block_id, config)
        else:
            return self.generate_excursion_block(block_id, config)

    def generate_filename(self, block_id: str, config: Dict) -> str:
        """Generate filename for block."""
        name_slug = config['name'].lower()
        name_slug = name_slug.replace(' ', '-')
        name_slug = name_slug.replace('(', '').replace(')', '')
        return f"{block_id}-{name_slug}.md"

    def fix_block(self, block_id: str, config: Dict) -> Optional[Path]:
        """Fix a single block."""
        # Generate content
        content = self.generate_block_content(block_id, config)

        # Generate filename
        filename = self.generate_filename(block_id, config)
        file_path = self.output_dir / filename

        if self.dry_run:
            print(f"  [DRY RUN] Would create: {file_path}")
            return None

        # Create directory if needed
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Write file
        file_path.write_text(content, encoding='utf-8')
        self.fixed_count += 1

        return file_path

    def fix_all(self, block_ids: Optional[List[str]] = None) -> int:
        """Fix all specified blocks."""
        if block_ids:
            blocks_to_fix = {bid: EMPTY_BLOCKS[bid] for bid in block_ids
                           if bid in EMPTY_BLOCKS}
        else:
            blocks_to_fix = EMPTY_BLOCKS

        if not blocks_to_fix:
            print("❌ No valid blocks to fix")
            return 0

        print(f"{'🔍 DRY RUN - ' if self.dry_run else ''}Fixing {len(blocks_to_fix)} blocks...")
        print(f"Output directory: {self.output_dir}")
        print()

        for block_id, config in blocks_to_fix.items():
            print(f"Processing {block_id}: {config['name']} ({config['type']})...")

            try:
                file_path = self.fix_block(block_id, config)
                if file_path:
                    print(f"  ✅ Created: {file_path.name}")
            except Exception as e:
                print(f"  ❌ Error: {e}")

        return self.fixed_count

    def generate_summary_report(self) -> str:
        """Generate summary report of fixes."""
        report = f"""# Empty Blocks Fix Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Output Directory: {self.output_dir}
Blocks Fixed: {self.fixed_count}

## Fixed Blocks

"""
        for block_id, config in EMPTY_BLOCKS.items():
            filename = self.generate_filename(block_id, config)
            report += f"- **{block_id}**: {config['name']} ({config['type']}) - `{filename}`\n"

        report += """

## Next Steps

1. Review each generated block
2. Add detailed content and descriptions
3. Upload relevant media files
4. Create booking forms where needed
5. Test navigation flow
6. Validate all blocks with `validate-block.py`

## Block Structure

Each fixed block includes:
- Proper metadata (Type, Date, Status)
- "Under Development" message
- Back button navigation
- Placeholder for future content
- TODO checklist

## Validation

Run validation on all fixed blocks:
```bash
python validate-block.py blocks/*.md
```
"""
        return report


def main():
    """Main entry point for the fixer."""
    parser = argparse.ArgumentParser(
        description='Fix empty/placeholder blocks for VIP-DXB-RUS bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
This script fixes {len(EMPTY_BLOCKS)} critical empty blocks:
- Dubai excursions (850-856)
- Abu Dhabi excursions (860-866)
- Sharjah excursions (870-876)
- Other emirates excursions (880-886)

Examples:
  python fix-empty-blocks.py --output-dir ../blocks
  python fix-empty-blocks.py --dry-run
  python fix-empty-blocks.py --blocks 850,860,870 --output-dir ./output
  python fix-empty-blocks.py --output-dir ../blocks --report
        """
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='./blocks',
        help='Output directory for fixed blocks (default: ./blocks)'
    )
    parser.add_argument(
        '--blocks', '-b',
        help='Comma-separated list of block IDs to fix (default: all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Generate summary report after fixing'
    )

    args = parser.parse_args()

    # Parse block IDs if specified
    block_ids = None
    if args.blocks:
        block_ids = [bid.strip() for bid in args.blocks.split(',')]
        invalid_ids = [bid for bid in block_ids if bid not in EMPTY_BLOCKS]
        if invalid_ids:
            print(f"❌ Invalid block IDs: {', '.join(invalid_ids)}")
            print(f"Valid IDs: {', '.join(EMPTY_BLOCKS.keys())}")
            sys.exit(1)

    # Create fixer
    output_dir = Path(args.output_dir)
    fixer = BlockFixer(output_dir, dry_run=args.dry_run)

    # Fix blocks
    try:
        fixed_count = fixer.fix_all(block_ids)

        print()
        print('='*60)
        if args.dry_run:
            print(f"🔍 DRY RUN: Would fix {len(block_ids or EMPTY_BLOCKS)} blocks")
        else:
            print(f"✅ Fixed {fixed_count} blocks successfully!")
            print(f"📁 Output: {output_dir}")

        # Generate report if requested
        if args.report and not args.dry_run:
            report = fixer.generate_summary_report()
            report_path = output_dir / 'FIX-REPORT.md'
            report_path.write_text(report, encoding='utf-8')
            print(f"📄 Report: {report_path}")

        print('='*60)

        if not args.dry_run:
            print("\n📝 Next steps:")
            print("   1. Review generated files")
            print("   2. Add detailed content")
            print("   3. Validate: python validate-block.py blocks/*.md")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
