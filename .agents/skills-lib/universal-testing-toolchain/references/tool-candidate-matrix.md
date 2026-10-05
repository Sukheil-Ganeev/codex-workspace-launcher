# Tool Candidate Matrix

Use this matrix for research and intake before adding testing tools.

| Area | Preferred tools | Use when | Install risk | Primary references |
| --- | --- | --- | --- | --- |
| Browser E2E | Playwright | Real browser flows, screenshots, traces, multi-browser checks | Low if Node project already exists | https://playwright.dev/docs/intro |
| Visual snapshots | Playwright snapshots | App/page screenshot regression | Low | https://playwright.dev/docs/test-snapshots |
| Custom image diff | pixelmatch | PNG-to-PNG comparison in local pipelines | Low | https://github.com/mapbox/pixelmatch |
| Visual dashboard | BackstopJS | Dedicated visual regression project, broad URL sets | Medium | https://github.com/garris/BackstopJS |
| Visual diff API | Resemble.js | JS image comparison and report customization | Low/medium | https://github.com/rsmbl/Resemble.js |
| JS unit tests | Vitest | Modern Vite/TypeScript projects | Low | https://vitest.dev/ |
| Existing JS tests | Jest | Repos already using Jest | Low if already present | https://jestjs.io/ |
| UI components | Testing Library | User-facing component behavior | Low | https://testing-library.com/ |
| Python tests | pytest | Python scripts, data tools, automation | Low | https://docs.pytest.org/ |
| Python property tests | Hypothesis | Edge cases, generated inputs | Medium | https://hypothesis.readthedocs.io/ |
| JS property tests | fast-check | Edge cases for parsers, validators, transformations | Medium | https://fast-check.dev/ |
| Mutation testing | Stryker | Proving tests catch real code changes | Medium/high runtime cost | https://stryker-mutator.io/ |
| API schema fuzzing | Schemathesis | OpenAPI-based API verification | Medium | https://schemathesis.readthedocs.io/ |
| API contracts | Pact | Consumer-provider service contracts | Medium/high process cost | https://docs.pact.io/ |
| Accessibility | axe-core, pa11y | Basic accessibility gates in browser flows | Low/medium | https://github.com/dequelabs/axe-core, https://github.com/pa11y/pa11y |
| PDF render | PyMuPDF, Poppler, pdfium, pdf.js | Rendering pages as images for visual truth | Medium; native deps may matter | https://pymupdf.readthedocs.io/, https://poppler.freedesktop.org/, https://mozilla.github.io/pdf.js/ |
| OCR baseline | OCRmyPDF, Tesseract | Local OCR/searchable PDF/text witness | Medium; native OCR deps | https://ocrmypdf.readthedocs.io/, https://github.com/tesseract-ocr/tesseract |
| Multilingual OCR | PaddleOCR, EasyOCR | Stylized/multilingual text where Tesseract is weak | Medium/high; model deps | https://github.com/PaddlePaddle/PaddleOCR, https://github.com/JaidedAI/EasyOCR |
| Fonts/glyphs | fontTools, opentype.js, fontkit, HarfBuzz | Cyrillic/Arabic/symbol glyph coverage, shaping, embedding | Medium | https://github.com/fonttools/fonttools, https://github.com/harfbuzz/harfbuzz |
| CI artifacts | GitHub Actions upload-artifact | Keep screenshots, traces, reports from failed runs | Low | https://docs.github.com/actions |

Selection rule: choose the smallest tool that proves the current risk. For catalog/PDF visual parity, use a combined witness: raster screenshot, pixel diff, OCR text, DOM text, font check, and dashboard freshness.
