#!/usr/bin/env python3
"""
Block Content Validator for VIP-DXB-RUS Telegram Bot

Validates content blocks to ensure they meet all requirements:
- Required fields (Type, Date, Text)
- Back button presence
- Emoji standards compliance
- Table structure validation
- Markdown formatting

Usage:
    python validate-block.py path/to/block.md
    python validate-block.py ../blocks/850-dubai-excursions.md
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


# Standard emoji mappings from emoji-standards.md
STANDARD_EMOJI = {
    'excursion': '🎭',
    'restaurant': '🍽️',
    'hotel': '🏨',
    'transport': '🚗',
    'service': '⭐',
    'info': 'ℹ️',
    'back': '🔙',
    'home': '🏠',
    'book': '📅',
    'contact': '📞',
    'location': '📍',
    'price': '💰',
    'time': '🕐',
    'calendar': '📆',
    'check': '✅',
    'cross': '❌',
}


class BlockValidator:
    """Validator for Telegram bot content blocks."""

    def __init__(self, file_path: str):
        """Initialize validator with file path."""
        self.file_path = Path(file_path)
        self.content = ""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_file(self) -> bool:
        """Load and read the block file."""
        if not self.file_path.exists():
            self.errors.append(f"File not found: {self.file_path}")
            return False

        if not self.file_path.suffix == '.md':
            self.errors.append(f"Invalid file type. Expected .md, got {self.file_path.suffix}")
            return False

        try:
            self.content = self.file_path.read_text(encoding='utf-8')
            return True
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False

    def validate_metadata(self) -> None:
        """Validate required metadata fields."""
        required_fields = {
            'Type': r'^Type:\s*(.+)$',
            'Date': r'^Date:\s*(\d{4}-\d{2}-\d{2})$',
        }

        for field_name, pattern in required_fields.items():
            match = re.search(pattern, self.content, re.MULTILINE)
            if not match:
                self.errors.append(f"Missing or invalid required field: {field_name}")
            elif field_name == 'Date':
                # Validate date format
                date_str = match.group(1)
                try:
                    year, month, day = map(int, date_str.split('-'))
                    if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                        self.errors.append(f"Invalid date value: {date_str}")
                except ValueError:
                    self.errors.append(f"Invalid date format: {date_str}")

    def validate_text_section(self) -> None:
        """Validate presence of text content section."""
        if not re.search(r'^##\s+Text', self.content, re.MULTILINE):
            self.errors.append("Missing '## Text' section")
            return

        # Extract text section
        text_match = re.search(r'^##\s+Text\s*$(.*?)(?=^##|\Z)',
                              self.content, re.MULTILINE | re.DOTALL)
        if text_match:
            text_content = text_match.group(1).strip()
            if not text_content:
                self.errors.append("Text section is empty")
            elif len(text_content) < 10:
                self.warnings.append("Text section seems too short (less than 10 characters)")

    def validate_back_button(self) -> None:
        """Validate presence of Back button."""
        # Check for Back button in buttons section
        back_patterns = [
            r'\[🔙\s*Back\]',
            r'\[Back\]',
            r'callback:\s*back_',
            r'callback:\s*menu_',
        ]

        has_back = any(re.search(pattern, self.content, re.IGNORECASE)
                      for pattern in back_patterns)

        if not has_back:
            self.errors.append("Missing Back button - every block must have navigation back")

    def validate_emoji_usage(self) -> None:
        """Validate emoji usage against standards."""
        # Extract all emoji from content
        emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\u2600-\u26FF]|[\u2700-\u27BF]'
        found_emoji = re.findall(emoji_pattern, self.content)

        if not found_emoji:
            self.warnings.append("No emoji found - consider adding emoji for better UX")
            return

        # Check button emoji
        button_pattern = r'\[([^\]]+)\]\(callback:'
        buttons = re.findall(button_pattern, self.content)

        buttons_without_emoji = [btn for btn in buttons if not re.search(emoji_pattern, btn)]
        if buttons_without_emoji:
            self.warnings.append(
                f"Buttons without emoji found: {', '.join(buttons_without_emoji[:3])}"
            )

    def validate_table_structure(self) -> None:
        """Validate table formatting if tables are present."""
        # Find all tables
        table_pattern = r'\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n)+'
        tables = re.findall(table_pattern, self.content)

        for i, table in enumerate(tables, 1):
            lines = table.strip().split('\n')
            if len(lines) < 3:
                self.errors.append(f"Table {i}: Invalid table - needs header, separator, and data rows")
                continue

            # Check column consistency
            header_cols = len(re.findall(r'\|', lines[0])) - 1
            separator_cols = len(re.findall(r'\|', lines[1])) - 1

            if header_cols != separator_cols:
                self.errors.append(
                    f"Table {i}: Column count mismatch between header ({header_cols}) "
                    f"and separator ({separator_cols})"
                )

            # Check data rows
            for row_num, line in enumerate(lines[2:], 3):
                row_cols = len(re.findall(r'\|', line)) - 1
                if row_cols != header_cols:
                    self.warnings.append(
                        f"Table {i}, Row {row_num}: Column count ({row_cols}) "
                        f"doesn't match header ({header_cols})"
                    )

    def validate_buttons(self) -> None:
        """Validate button formatting and structure."""
        if '## Buttons' not in self.content:
            self.warnings.append("No '## Buttons' section found")
            return

        # Extract buttons section
        buttons_match = re.search(r'^##\s+Buttons\s*$(.*?)(?=^##|\Z)',
                                 self.content, re.MULTILINE | re.DOTALL)
        if not buttons_match:
            return

        buttons_section = buttons_match.group(1)

        # Find all button definitions
        button_pattern = r'\[([^\]]+)\]\(callback:([^)]+)\)'
        buttons = re.findall(button_pattern, buttons_section)

        if not buttons:
            self.warnings.append("Buttons section exists but no valid buttons found")
            return

        # Validate callback format
        for label, callback in buttons:
            if not callback.strip():
                self.errors.append(f"Button '{label}' has empty callback")
            elif ' ' in callback.strip():
                self.warnings.append(
                    f"Button '{label}' callback contains spaces: '{callback}'"
                )

    def validate_id_in_filename(self) -> None:
        """Validate that filename contains valid ID."""
        filename = self.file_path.stem
        id_match = re.match(r'^(\d+)-', filename)

        if not id_match:
            self.errors.append(
                f"Filename must start with ID number (e.g., '850-name.md'): {filename}"
            )
        else:
            block_id = id_match.group(1)
            # Check if ID is mentioned in content
            if block_id not in self.content:
                self.warnings.append(
                    f"Block ID {block_id} from filename not found in content"
                )

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validations and return results."""
        if not self.load_file():
            return False, self.errors, self.warnings

        # Run all validation checks
        self.validate_metadata()
        self.validate_text_section()
        self.validate_back_button()
        self.validate_emoji_usage()
        self.validate_table_structure()
        self.validate_buttons()
        self.validate_id_in_filename()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings


def main():
    """Main entry point for the validator."""
    parser = argparse.ArgumentParser(
        description='Validate Telegram bot content blocks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate-block.py ../blocks/850-dubai-excursions.md
  python validate-block.py path/to/block.md
  python validate-block.py blocks/*.md
        """
    )
    parser.add_argument(
        'file',
        help='Path to the block markdown file to validate'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose output'
    )

    args = parser.parse_args()

    # Support glob patterns
    file_path = Path(args.file)
    if '*' in str(file_path):
        files = list(file_path.parent.glob(file_path.name))
    else:
        files = [file_path]

    total_files = len(files)
    valid_files = 0

    for file in files:
        if total_files > 1:
            print(f"\n{'='*60}")
            print(f"Validating: {file}")
            print('='*60)

        validator = BlockValidator(str(file))
        is_valid, errors, warnings = validator.validate()

        # Print results
        if is_valid:
            print(f"✅ VALID: {file.name}")
            valid_files += 1
        else:
            print(f"❌ INVALID: {file.name}")

        if errors:
            print(f"\n🔴 Errors ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")

        if warnings:
            print(f"\n🟡 Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")

        if not errors and not warnings:
            print("  No issues found!")

    # Summary for multiple files
    if total_files > 1:
        print(f"\n{'='*60}")
        print(f"Summary: {valid_files}/{total_files} files valid")
        print('='*60)

    # Exit code
    sys.exit(0 if valid_files == total_files else 1)


if __name__ == '__main__':
    main()
