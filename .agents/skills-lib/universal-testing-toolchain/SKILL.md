---
name: universal-testing-toolchain
description: "Use when choosing, adding, auditing, or improving tests across projects: web apps, APIs, Python/data scripts, PDF/HTML/catalog rendering, OCR, fonts, visual regression, accessibility, CI, agents, and MCP tools."
---

# Universal Testing Toolchain

## Purpose

Use this skill as the test-routing layer before installing or writing tests. It turns a vague request like "add tests" or "find better QA tools" into a small, verified test plan that fits the project type.

Prefer project-local, minimal installs. Do not install a large tool stack into every project. First inspect existing test tools, then add only the missing layer that proves the current risk.

## First Pass

1. Identify project type:
   - Web/UI
   - API/backend
   - Python/data/automation
   - PDF/HTML/catalog/document rendering
   - Mobile/iOS/Android
   - Video/render pipeline
   - Agent/MCP/plugin system
   - CI/release workflow
2. Inspect existing setup before adding anything:
   - `package.json`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`
   - `pyproject.toml`, `pytest.ini`, `requirements.txt`
   - `playwright.config.*`, `vitest.config.*`, `jest.config.*`, `cypress.config.*`
   - `.github/workflows`, `Makefile`, `Taskfile.*`, local runbooks
3. Run the smallest existing test/smoke command to establish baseline.
4. Choose one to three missing test layers, not a giant stack.
5. Write or update an implementation note when the work is non-trivial.
6. Save evidence artifacts: JSON/MD reports, screenshots, traces, visual diffs, OCR witnesses, or CI logs.

## Test Layer Menu

Use this order unless the project already has a stronger convention:

1. Smoke test: proves the app/script starts and the critical path is reachable.
2. Unit/component tests: prove business logic and small UI units.
3. Integration/API/contract tests: prove module boundaries, schemas, services, and endpoints.
4. Browser E2E tests: prove real user flows in a browser.
5. Visual regression tests: prove pixels did not drift.
6. Accessibility tests: prove basic keyboard/semantic/contrast issues are caught.
7. Data/schema tests: prove CSV/JSON/XLSX/PDF-derived outputs have required fields and counts.
8. Property/mutation tests: prove edge cases and test strength for important logic.
9. OCR/font/document tests: prove visible text, Cyrillic/Arabic/symbol rendering, and PDF/HTML parity.
10. CI artifact tests: prove failures leave enough evidence to debug.

## Preferred Tools

### Web/UI

- Use Playwright first for browser E2E, screenshots, traces, and visual snapshots.
- Use Vitest for modern Vite/TypeScript unit tests unless the repo already uses Jest.
- Use Testing Library for React/Vue/Svelte component behavior.
- Use Cypress only when already adopted by the project.

### Visual Regression

- Start with Playwright snapshots for app pages.
- Use `pixelmatch` for custom PNG-to-PNG comparisons and fixed artifact pipelines.
- Use BackstopJS or Resemble.js when a project needs a dedicated visual dashboard or broader non-Playwright visual suite.
- Store reference/current/diff images as artifacts. Never call a page matched from text extraction alone.

### PDF, OCR, Fonts, Catalog HTML

- Use browser screenshots or PDF page renders as the source of visual truth.
- Use PyMuPDF, Poppler, pdfium, or pdf.js for page rasterization.
- Use OCRmyPDF/Tesseract for local searchable text baselines.
- Use EasyOCR or PaddleOCR when Tesseract struggles with layout, multilingual text, or stylized text.
- Use fontTools, opentype.js, fontkit, or HarfBuzz checks for glyph coverage, font loading, shaping, and Cyrillic/Arabic/symbol risk.
- For catalog pixel-match work, combine:
  - pixel diff
  - visual OCR witness
  - DOM text check
  - font loading check
  - dashboard freshness check
  - owner approval gate

### Python/Data/Automation

- Use pytest for tests.
- Use Hypothesis for edge-case/property tests.
- Use Great Expectations, Pandera, or custom schema validators only when tabular data quality is central.
- Keep script outputs deterministic and write JSON/MD reports.

### API/Backend

- Use existing framework test runner first.
- Use Schemathesis for OpenAPI/schema fuzzing.
- Use Pact for consumer-provider contracts when multiple services depend on each other.
- Use Newman/Postman only when the team already keeps collections as the API source.

### Security And Reliability

- Use axe-core/Playwright axe or pa11y for accessibility checks.
- Use Stryker for mutation testing when test strength matters.
- Use fast-check for JS property tests.
- Use existing security skills for auth, access control, sensitive data, and dependency risk.

### Mobile

- For iOS projects, prefer XcodeBuildMCP simulator test tools when available.
- For Android projects, use the available Android testing skill/tooling.
- Do not approximate mobile behavior with desktop browser screenshots when native UI is the target.

## Existing Skills To Combine

Use the narrowest relevant skill after this router:

- `e2e-testing` for end-to-end test creation.
- `playwright` and `playwright-interactive` for browser automation.
- `browser-harness` for browser smoke checks and screenshots.
- `frontend-testing-debugging` for web UI bug isolation.
- `test-driven-development` when implementing behavior changes.
- `write-tests` when covering local code changes.
- `fix-tests` when existing tests fail.
- `catalog-pdf-to-editable-html` for PDF-to-HTML visual parity.
- `code-review:review-local-changes` for review-first risk finding.
- `codex-security:validation` or specific security testing skills for security-sensitive work.

## Install Rules

- Prefer repo-local dev dependencies, not global installs.
- Do not install tools just because they are popular. Install only after mapping them to a risk.
- Do not upload private PDFs, screenshots, raw catalog pages, credentials, or customer data to cloud tools without explicit owner approval.
- Use local OCR and local image comparison first.
- For reusable cross-project guidance, create a skill or project QA lab document instead of copying scripts everywhere.
- For each new tool, record:
  - why it is needed
  - exact install command
  - exact run command
  - output artifacts
  - rollback/removal path

## Required Output

For any meaningful test tooling task, produce:

- current test baseline
- risk map
- chosen tools and rejected tools
- exact commands
- files changed
- verification result
- evidence artifacts
- clear status: PASS, FAIL, or BLOCKED

Use `references/tool-candidate-matrix.md` and `references/project-type-routing.md` when the choice is not obvious.
