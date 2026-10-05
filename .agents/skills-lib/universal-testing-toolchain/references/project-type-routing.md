# Project Type Routing

## Web app

Baseline:
- Run existing unit tests and linter.
- Add one Playwright smoke test for the main route.
- Add screenshots/traces on failure.

When UI quality matters:
- Add Playwright visual snapshots for stable pages.
- Add axe checks for accessibility basics.

## Static HTML or design artifact

Baseline:
- Open in browser or Playwright.
- Capture desktop and mobile screenshots.
- Check visible text, overflow, and console errors.

When pixel-match matters:
- Compare against a reference PNG with pixelmatch or Playwright snapshots.
- Save reference/current/diff images.
- Add a human review gate if the source is a design/PDF.

## PDF to editable HTML or catalog rendering

Baseline:
- Render PDF page and HTML page to images.
- Compare pixels.
- OCR the rendered images when PDF text extraction is unreliable.
- Verify browser-loaded fonts and glyph coverage.
- Check dashboard/source freshness.

Never rely only on extracted PDF text for final approval when the human-visible page says otherwise.

## API/backend

Baseline:
- Run existing service tests.
- Add tests for status codes, validation, auth boundaries, and error payloads.

When OpenAPI exists:
- Add Schemathesis smoke/fuzz checks.

When multiple services depend on contracts:
- Consider Pact.

## Python/data/automation

Baseline:
- Add pytest tests around core transformations and edge cases.
- Add fixture files small enough to review.
- Emit deterministic JSON/MD reports.

When input space is broad:
- Add Hypothesis property tests.

## Agent, MCP, plugin, or skill system

Baseline:
- Add manifest/schema validation.
- Add dry-run tests for commands and tool routing.
- Check that private data and credentials are not emitted.

When installing new capabilities:
- Record install command, run command, permissions, rollback, and first verification artifact.

## CI/release

Baseline:
- Confirm local command and CI command match.
- Upload test reports, screenshots, traces, logs, and diff images as artifacts.
- Make final status depend on test result plus artifact availability.
