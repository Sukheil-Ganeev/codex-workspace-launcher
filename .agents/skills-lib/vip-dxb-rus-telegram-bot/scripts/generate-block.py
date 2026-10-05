#!/usr/bin/env python3
"""
Block Generator for VIP-DXB-RUS Telegram Bot

Generates new content blocks with proper structure and standards:
- Auto-generates next available ID
- Creates properly formatted markdown
- Includes standard emoji
- Adds navigation buttons
- Follows naming conventions

Usage:
    python generate-block.py --type excursion --name "Desert Safari" --emirate Dubai
    python generate-block.py --type restaurant --name "Fine Dining" --emirate "Abu Dhabi"
    python generate-block.py --type info --name "Visa Information" --output custom.md
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# Block type configurations
BLOCK_TYPES = {
    'excursion': {
        'emoji': '🎭',
        'parent': 'excursions',
        'template': 'excursion_template',
    },
    'restaurant': {
        'emoji': '🍽️',
        'parent': 'restaurants',
        'template': 'restaurant_template',
    },
    'hotel': {
        'emoji': '🏨',
        'parent': 'hotels',
        'template': 'hotel_template',
    },
    'transport': {
        'emoji': '🚗',
        'parent': 'transport',
        'template': 'transport_template',
    },
    'service': {
        'emoji': '⭐',
        'parent': 'services',
        'template': 'service_template',
    },
    'info': {
        'emoji': 'ℹ️',
        'parent': 'information',
        'template': 'info_template',
    },
}

# Emirates list
EMIRATES = [
    'Dubai',
    'Abu Dhabi',
    'Sharjah',
    'Ajman',
    'Umm Al Quwain',
    'Ras Al Khaimah',
    'Fujairah',
    'UAE',  # For country-wide services
]


class BlockGenerator:
    """Generator for new content blocks."""

    def __init__(self, block_type: str, name: str, emirate: str,
                 parent_id: Optional[str] = None, output_dir: Optional[str] = None):
        """Initialize generator with block parameters."""
        self.block_type = block_type.lower()
        self.name = name
        self.emirate = emirate
        self.parent_id = parent_id
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.block_id = None
        self.filename = None

    def generate_next_id(self, blocks_dir: Optional[Path] = None) -> str:
        """Generate next available block ID."""
        if not blocks_dir:
            blocks_dir = self.output_dir

        if not blocks_dir.exists():
            print(f"⚠️  Blocks directory not found: {blocks_dir}")
            print("   Using default starting ID: 1000")
            return "1000"

        # Find all existing block IDs
        existing_ids = []
        for file in blocks_dir.glob('*.md'):
            match = re.match(r'^(\d+)-', file.stem)
            if match:
                existing_ids.append(int(match.group(1)))

        if not existing_ids:
            return "1000"

        # Generate next ID (increment by 10 for spacing)
        next_id = max(existing_ids) + 10
        return str(next_id)

    def generate_slug(self) -> str:
        """Generate URL-friendly slug from name."""
        slug = self.name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces/hyphens
        slug = slug.strip('-')                 # Remove leading/trailing hyphens
        return slug

    def generate_filename(self) -> str:
        """Generate filename for the block."""
        slug = self.generate_slug()
        return f"{self.block_id}-{slug}.md"

    def get_template_excursion(self) -> str:
        """Generate excursion block template."""
        emoji = BLOCK_TYPES['excursion']['emoji']
        return f"""# {emoji} {self.name}

Type: Excursion
Emirate: {self.emirate}
Date: {datetime.now().strftime('%Y-%m-%d')}
Status: Active

## Text

**{emoji} {self.name}**

Discover the beauty and excitement of {self.name} in {self.emirate}.

**📍 Location:** {self.emirate}
**🕐 Duration:** [Duration here]
**💰 Price:** From [Price] AED

### What's Included

| Included | Details |
|----------|---------|
| ✅ | [Feature 1] |
| ✅ | [Feature 2] |
| ✅ | [Feature 3] |

### Highlights

- [Highlight 1]
- [Highlight 2]
- [Highlight 3]

**Ready to book?** Click below to reserve your spot!

## Media

[Add photos/videos here]

## Buttons

[📅 Book Now](callback:form_booking_{self.block_id})
[📞 Contact Us](callback:contact_support)
[🔙 Back](callback:menu_{self.parent_id or 'excursions'})

## Metadata

- Category: Excursion
- Tags: {self.emirate}, excursion, tourism
- Price Range: [Price range]
- Language: Russian
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""

    def get_template_restaurant(self) -> str:
        """Generate restaurant block template."""
        emoji = BLOCK_TYPES['restaurant']['emoji']
        return f"""# {emoji} {self.name}

Type: Restaurant
Emirate: {self.emirate}
Date: {datetime.now().strftime('%Y-%m-%d')}
Status: Active

## Text

**{emoji} {self.name}**

Experience exceptional dining at {self.name} in {self.emirate}.

**📍 Location:** {self.emirate}
**🍽️ Cuisine:** [Cuisine type]
**💰 Price:** [Price range] AED

### Restaurant Features

| Feature | Description |
|---------|-------------|
| Cuisine | [Cuisine type] |
| Atmosphere | [Atmosphere] |
| Specialty | [Specialty dishes] |
| Dress Code | [Dress code] |

### Menu Highlights

- [Dish 1]
- [Dish 2]
- [Dish 3]

**Make a reservation today!**

## Media

[Add photos here]

## Buttons

[📅 Reserve Table](callback:form_reservation_{self.block_id})
[📞 Contact](callback:contact_support)
[🔙 Back](callback:menu_{self.parent_id or 'restaurants'})

## Metadata

- Category: Restaurant
- Tags: {self.emirate}, dining, restaurant
- Cuisine: [Cuisine type]
- Language: Russian
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""

    def get_template_hotel(self) -> str:
        """Generate hotel block template."""
        emoji = BLOCK_TYPES['hotel']['emoji']
        return f"""# {emoji} {self.name}

Type: Hotel
Emirate: {self.emirate}
Date: {datetime.now().strftime('%Y-%m-%d')}
Status: Active

## Text

**{emoji} {self.name}**

Luxurious accommodation at {self.name} in {self.emirate}.

**📍 Location:** {self.emirate}
**⭐ Rating:** [Star rating]
**💰 Price:** From [Price] AED/night

### Hotel Amenities

| Amenity | Available |
|---------|-----------|
| ✅ Pool | Yes |
| ✅ Spa | Yes |
| ✅ Restaurant | Yes |
| ✅ Gym | Yes |

### Room Types

- [Room type 1]
- [Room type 2]
- [Room type 3]

**Book your stay now!**

## Media

[Add hotel photos here]

## Buttons

[📅 Book Room](callback:form_hotel_{self.block_id})
[📞 Contact](callback:contact_support)
[🔙 Back](callback:menu_{self.parent_id or 'hotels'})

## Metadata

- Category: Hotel
- Tags: {self.emirate}, hotel, accommodation
- Rating: [Star rating]
- Language: Russian
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""

    def get_template_info(self) -> str:
        """Generate information block template."""
        emoji = BLOCK_TYPES['info']['emoji']
        return f"""# {emoji} {self.name}

Type: Information
Emirate: {self.emirate}
Date: {datetime.now().strftime('%Y-%m-%d')}
Status: Active

## Text

**{emoji} {self.name}**

Important information about {self.name} in {self.emirate}.

### Key Information

| Topic | Details |
|-------|---------|
| [Topic 1] | [Details] |
| [Topic 2] | [Details] |
| [Topic 3] | [Details] |

### Important Notes

- [Note 1]
- [Note 2]
- [Note 3]

**Need more information?** Contact our support team.

## Buttons

[📞 Contact Support](callback:contact_support)
[🔙 Back](callback:menu_{self.parent_id or 'main'})

## Metadata

- Category: Information
- Tags: {self.emirate}, info, guide
- Language: Russian
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""

    def get_template_generic(self) -> str:
        """Generate generic block template."""
        emoji = BLOCK_TYPES.get(self.block_type, {}).get('emoji', '📄')
        return f"""# {emoji} {self.name}

Type: {self.block_type.capitalize()}
Emirate: {self.emirate}
Date: {datetime.now().strftime('%Y-%m-%d')}
Status: Active

## Text

**{emoji} {self.name}**

[Add content description here]

**📍 Location:** {self.emirate}

### Features

- [Feature 1]
- [Feature 2]
- [Feature 3]

## Buttons

[📅 Book Now](callback:form_booking_{self.block_id})
[📞 Contact](callback:contact_support)
[🔙 Back](callback:menu_{self.parent_id or 'main'})

## Metadata

- Category: {self.block_type.capitalize()}
- Tags: {self.emirate}, {self.block_type}
- Language: Russian
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""

    def generate_content(self) -> str:
        """Generate block content based on type."""
        template_method = f"get_template_{self.block_type}"

        if hasattr(self, template_method):
            return getattr(self, template_method)()
        else:
            return self.get_template_generic()

    def save_block(self, content: str, output_path: Optional[Path] = None) -> Path:
        """Save generated block to file."""
        if output_path:
            file_path = output_path
        else:
            file_path = self.output_dir / self.filename

        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        file_path.write_text(content, encoding='utf-8')

        return file_path

    def generate(self, custom_id: Optional[str] = None,
                output_path: Optional[Path] = None) -> Path:
        """Generate and save the block."""
        # Generate or use custom ID
        if custom_id:
            self.block_id = custom_id
        else:
            self.block_id = self.generate_next_id()

        # Generate filename
        self.filename = self.generate_filename()

        # Generate content
        content = self.generate_content()

        # Save block
        file_path = self.save_block(content, output_path)

        return file_path


def main():
    """Main entry point for the generator."""
    parser = argparse.ArgumentParser(
        description='Generate new Telegram bot content blocks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available block types:
  {', '.join(BLOCK_TYPES.keys())}

Available emirates:
  {', '.join(EMIRATES)}

Examples:
  python generate-block.py --type excursion --name "Desert Safari" --emirate Dubai
  python generate-block.py --type restaurant --name "Fine Dining" --emirate "Abu Dhabi"
  python generate-block.py --type info --name "Visa Info" --emirate UAE --output custom.md
  python generate-block.py --type hotel --name "Luxury Resort" --emirate Dubai --id 1050
        """
    )
    parser.add_argument(
        '--type', '-t',
        required=True,
        choices=list(BLOCK_TYPES.keys()),
        help='Type of block to generate'
    )
    parser.add_argument(
        '--name', '-n',
        required=True,
        help='Name/title of the block'
    )
    parser.add_argument(
        '--emirate', '-e',
        required=True,
        help='Emirate or location'
    )
    parser.add_argument(
        '--parent', '-p',
        help='Parent block ID for navigation'
    )
    parser.add_argument(
        '--id',
        help='Custom block ID (auto-generated if not provided)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (defaults to auto-generated filename)'
    )
    parser.add_argument(
        '--output-dir', '-d',
        default='.',
        help='Output directory (default: current directory)'
    )

    args = parser.parse_args()

    # Validate emirate
    if args.emirate not in EMIRATES:
        print(f"⚠️  Warning: '{args.emirate}' is not in standard emirates list")
        print(f"   Available: {', '.join(EMIRATES)}")
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            sys.exit(1)

    # Create generator
    generator = BlockGenerator(
        block_type=args.type,
        name=args.name,
        emirate=args.emirate,
        parent_id=args.parent,
        output_dir=args.output_dir
    )

    # Generate block
    try:
        output_path = Path(args.output) if args.output else None
        file_path = generator.generate(custom_id=args.id, output_path=output_path)

        print(f"✅ Block generated successfully!")
        print(f"   ID: {generator.block_id}")
        print(f"   File: {file_path}")
        print(f"   Type: {args.type}")
        print(f"   Name: {args.name}")
        print(f"\n📝 Next steps:")
        print(f"   1. Edit the content in {file_path}")
        print(f"   2. Add media files")
        print(f"   3. Validate with: python validate-block.py {file_path}")

    except Exception as e:
        print(f"❌ Error generating block: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
