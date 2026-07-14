# BioMaster Source Assets

This directory contains publication-facing and deployment-facing assets for the
BioMaster v2.0-alpha1 release. The files here are intended for the project README,
static site, manuscript-related communication, and future documentation.

## Directory Layout

```text
source/
├── Biomaster.svg
└── figures/
    ├── manuscript-fig1.pdf
    ├── reliability.svg
    └── open-source-llms.svg
```

## Asset Inventory

| File | Type | Intended use |
| --- | --- | --- |
| `Biomaster.svg` | SVG logo | README, static site favicon/logo, presentation material |
| `figures/manuscript-fig1.pdf` | PDF figure source | Manuscript-related figure reference |
| `figures/reliability.svg` | SVG source | Editable/vector reliability figure |
| `figures/open-source-llms.svg` | SVG source | Editable/vector open-source LLM figure |

## Maintenance Policy

- Prefer `PNG` or `SVG` for web deployment.
- Preserve `PDF` or `SVG` originals when they come from manuscript materials.
- Keep filenames descriptive and stable so README and static site links do not break.
- Do not store generated workflow outputs, temporary screenshots, SQLite caches, or raw analysis result directories here.
- Keep all quantitative claims consistent with the published article and verified benchmark records.
