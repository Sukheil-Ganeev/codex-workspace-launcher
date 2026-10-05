#!/usr/bin/env python3
"""
Booking Form Validator for VIP-DXB-RUS Telegram Bot

Validates booking forms to ensure they meet all requirements:
- Required fields (name, phone, email, date)
- Variable prefix validation
- Field type validation (TEXT, PHONE, EMAIL, DATE, etc.)
- Choice options validation (2-6 variants)
- Form structure compliance

Usage:
    python validate-form.py FORM-NAME.md
    python validate-form.py ../forms/FORM-DESERT-SAFARI.md
    python validate-form.py forms/*.md
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional


# Valid field types
VALID_FIELD_TYPES = {
    'TEXT': 'Single line text input',
    'TEXTAREA': 'Multi-line text input',
    'PHONE': 'Phone number (with validation)',
    'EMAIL': 'Email address (with validation)',
    'DATE': 'Date picker',
    'TIME': 'Time picker',
    'NUMBER': 'Numeric input',
    'CHOICE': 'Multiple choice (2-6 options)',
    'CHECKBOX': 'Yes/No checkbox',
}

# Required standard fields
REQUIRED_FIELDS = {
    'name': {'types': ['TEXT'], 'required': True},
    'phone': {'types': ['PHONE'], 'required': True},
    'email': {'types': ['EMAIL'], 'required': True},
    'date': {'types': ['DATE'], 'required': True},
}


class FormValidator:
    """Validator for booking forms."""

    def __init__(self, file_path: str):
        """Initialize validator with file path."""
        self.file_path = Path(file_path)
        self.content = ""
        self.form_name = ""
        self.fields: List[Dict] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_file(self) -> bool:
        """Load and read the form file."""
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

    def extract_form_name(self) -> None:
        """Extract form name from filename."""
        filename = self.file_path.stem

        if not filename.startswith('FORM-'):
            self.errors.append(
                f"Form filename must start with 'FORM-' prefix: {filename}"
            )
            return

        self.form_name = filename[5:]  # Remove 'FORM-' prefix

        # Validate form name format (should be UPPERCASE-WITH-DASHES)
        if not re.match(r'^[A-Z][A-Z0-9-]*$', self.form_name):
            self.warnings.append(
                f"Form name should be in UPPERCASE-WITH-DASHES format: {self.form_name}"
            )

    def validate_header(self) -> None:
        """Validate form header section."""
        # Check for main heading
        if not re.search(r'^#\s+FORM-', self.content, re.MULTILINE):
            self.errors.append("Missing main heading (should start with '# FORM-')")

        # Check for required metadata
        required_metadata = ['Type:', 'Date:', 'Status:']
        for meta in required_metadata:
            if meta not in self.content:
                self.errors.append(f"Missing required metadata: {meta}")

        # Validate form type
        type_match = re.search(r'^Type:\s*(.+)$', self.content, re.MULTILINE)
        if type_match:
            form_type = type_match.group(1).strip()
            if form_type.lower() != 'booking form':
                self.warnings.append(
                    f"Unexpected form type: '{form_type}' (expected 'Booking Form')"
                )

    def parse_fields(self) -> None:
        """Parse all form fields from content."""
        # Find fields section
        fields_match = re.search(
            r'^##\s+Fields\s*$(.*?)(?=^##|\Z)',
            self.content,
            re.MULTILINE | re.DOTALL
        )

        if not fields_match:
            self.errors.append("Missing '## Fields' section")
            return

        fields_section = fields_match.group(1)

        # Parse individual fields (format: ### variable_name)
        field_pattern = r'^###\s+(\w+)\s*$(.*?)(?=^###|\Z)'
        field_matches = re.finditer(field_pattern, fields_section, re.MULTILINE | re.DOTALL)

        for match in field_matches:
            var_name = match.group(1)
            field_content = match.group(2).strip()

            field_data = {
                'variable': var_name,
                'label': None,
                'type': None,
                'required': False,
                'choices': [],
                'validation': None,
                'placeholder': None,
            }

            # Extract field properties
            for line in field_content.split('\n'):
                line = line.strip()
                if line.startswith('- **Label:**'):
                    field_data['label'] = line.split('**Label:**')[1].strip()
                elif line.startswith('- **Type:**'):
                    field_data['type'] = line.split('**Type:**')[1].strip()
                elif line.startswith('- **Required:**'):
                    req_value = line.split('**Required:**')[1].strip().lower()
                    field_data['required'] = req_value in ['yes', 'true', '✅']
                elif line.startswith('- **Choices:**'):
                    choices_text = line.split('**Choices:**')[1].strip()
                    field_data['choices'] = [c.strip() for c in choices_text.split(',')]
                elif line.startswith('- **Validation:**'):
                    field_data['validation'] = line.split('**Validation:**')[1].strip()
                elif line.startswith('- **Placeholder:**'):
                    field_data['placeholder'] = line.split('**Placeholder:**')[1].strip()

            self.fields.append(field_data)

    def validate_variable_prefix(self) -> None:
        """Validate that all variables use correct prefix."""
        if not self.form_name:
            return

        expected_prefix = f"{self.form_name.lower().replace('-', '_')}_"

        for field in self.fields:
            var_name = field['variable']

            # Standard fields (name, phone, email, date) don't need prefix
            if var_name in REQUIRED_FIELDS:
                continue

            if not var_name.startswith(expected_prefix):
                self.errors.append(
                    f"Variable '{var_name}' must start with prefix '{expected_prefix}'"
                )

    def validate_required_fields(self) -> None:
        """Validate presence of required standard fields."""
        field_vars = {f['variable'] for f in self.fields}

        for req_field, config in REQUIRED_FIELDS.items():
            if req_field not in field_vars:
                self.errors.append(f"Missing required field: {req_field}")
                continue

            # Find the field and validate type
            field = next(f for f in self.fields if f['variable'] == req_field)

            if field['type'] not in config['types']:
                self.errors.append(
                    f"Field '{req_field}' must be of type {' or '.join(config['types'])}, "
                    f"got '{field['type']}'"
                )

            if not field['required']:
                self.errors.append(f"Field '{req_field}' must be marked as required")

    def validate_field_types(self) -> None:
        """Validate that all field types are valid."""
        for field in self.fields:
            field_type = field['type']

            if not field_type:
                self.errors.append(f"Field '{field['variable']}' is missing type")
                continue

            if field_type not in VALID_FIELD_TYPES:
                self.errors.append(
                    f"Field '{field['variable']}' has invalid type: '{field_type}'. "
                    f"Valid types: {', '.join(VALID_FIELD_TYPES.keys())}"
                )

    def validate_choice_fields(self) -> None:
        """Validate CHOICE type fields have 2-6 options."""
        for field in self.fields:
            if field['type'] == 'CHOICE':
                num_choices = len(field['choices'])

                if num_choices < 2:
                    self.errors.append(
                        f"CHOICE field '{field['variable']}' must have at least 2 options, "
                        f"found {num_choices}"
                    )
                elif num_choices > 6:
                    self.warnings.append(
                        f"CHOICE field '{field['variable']}' has {num_choices} options "
                        f"(recommended: 2-6 for better UX)"
                    )

                # Check for empty choices
                if any(not c or c.isspace() for c in field['choices']):
                    self.errors.append(
                        f"CHOICE field '{field['variable']}' has empty options"
                    )

    def validate_field_labels(self) -> None:
        """Validate that all fields have labels."""
        for field in self.fields:
            if not field['label']:
                self.warnings.append(
                    f"Field '{field['variable']}' is missing a label"
                )

    def validate_validation_rules(self) -> None:
        """Validate field validation rules."""
        for field in self.fields:
            field_type = field['type']
            validation = field['validation']

            # PHONE and EMAIL should have validation
            if field_type == 'PHONE' and not validation:
                self.warnings.append(
                    f"PHONE field '{field['variable']}' should have validation rules"
                )
            elif field_type == 'EMAIL' and not validation:
                self.warnings.append(
                    f"EMAIL field '{field['variable']}' should have validation rules"
                )

    def validate_submit_section(self) -> None:
        """Validate submit button configuration."""
        if '## Submit' not in self.content:
            self.errors.append("Missing '## Submit' section")
            return

        submit_match = re.search(
            r'^##\s+Submit\s*$(.*?)(?=^##|\Z)',
            self.content,
            re.MULTILINE | re.DOTALL
        )

        if submit_match:
            submit_section = submit_match.group(1)

            # Check for button text
            if 'Button:' not in submit_section:
                self.warnings.append("Submit section missing button text specification")

            # Check for callback
            if 'Callback:' not in submit_section:
                self.errors.append("Submit section missing callback specification")

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validations and return results."""
        if not self.load_file():
            return False, self.errors, self.warnings

        # Run all validation checks
        self.extract_form_name()
        self.validate_header()
        self.parse_fields()
        self.validate_variable_prefix()
        self.validate_required_fields()
        self.validate_field_types()
        self.validate_choice_fields()
        self.validate_field_labels()
        self.validate_validation_rules()
        self.validate_submit_section()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings


def main():
    """Main entry point for the validator."""
    parser = argparse.ArgumentParser(
        description='Validate Telegram bot booking forms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate-form.py FORM-DESERT-SAFARI.md
  python validate-form.py ../forms/FORM-HOTEL-BOOKING.md
  python validate-form.py forms/FORM-*.md
        """
    )
    parser.add_argument(
        'file',
        help='Path to the form markdown file to validate'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose output including field details'
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

        validator = FormValidator(str(file))
        is_valid, errors, warnings = validator.validate()

        # Print results
        if is_valid:
            print(f"✅ VALID: {file.name}")
            valid_files += 1
        else:
            print(f"❌ INVALID: {file.name}")

        if args.verbose and validator.fields:
            print(f"\n📋 Found {len(validator.fields)} fields:")
            for field in validator.fields:
                req = "Required" if field['required'] else "Optional"
                print(f"  - {field['variable']} ({field['type']}) - {req}")

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
