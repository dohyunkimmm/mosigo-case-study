# MOSIGO Pretendard / Tossface final verification

Date: 2026-11-01 (Asia/Seoul)

## Scope

- Web case study: `index.html`, Tossface PNG icon at `assets/tossface-phone.png`
- Business plan: `downloads/mosigo_business_plan_20261031.pdf` (17 pages)
- Editable presentation: `downloads/mosigo_report.pptx` (11 slides)
- Presentation PDF: `downloads/mosigo_report_preview.pdf` (11 pages)
- Mobile fallback images: 34 plan WebP files + 22 slide WebP files (56 total)

## Verified after regeneration

- PPTX explicit text formatting uses Pretendard in Latin, East Asian and complex-script text runs.
- PowerPoint document theme, layouts, slide masters, notes master and nested theme XML no longer contain Aptos.
- Business plan PDF embeds Pretendard Regular and Bold; presentation PDF embeds Pretendard Regular and Bold. Both PDFs retain the expected page count.
- The image previews are generated from these published PDFs in both 800px and 1400px sizes.
- The site keeps Pretendard Variable in its CSS and the official Tossface phone PNG. No redesign of site copy or icon is part of this change.
- Market assumptions and business-model calculations were not changed.

## Regeneration and checks

- `.github/workflows/business-plan-pdf.yml`
- `.github/workflows/ppt-preview.yml`
- `.github/workflows/preview-pages.yml`
- `qa/check-document-design.py`

This file records the regenerated document state and triggers site QA against the post-generation repository commit. Live browser performance and physical-device Safari remain subject to their independent checks.
