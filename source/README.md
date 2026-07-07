# BioMaster Source Assets

This directory contains publication-facing and deployment-facing assets for the
BioMaster release candidate. The files here are intended for the project README,
static site, manuscript-related communication, and future documentation.

## Directory Layout

```text
source/
├── Biomaster.svg
├── UI.png
└── figures/
    ├── manuscript-fig1.pdf
    ├── overview.png
    ├── task-coverage.png
    ├── multistep-success.png
    ├── reliability.png
    ├── reliability.svg
    ├── open-source-llms.png
    └── open-source-llms.svg
```

## Asset Inventory

| File | Type | Intended use |
| --- | --- | --- |
| `Biomaster.svg` | SVG logo | README, static site favicon/logo, presentation material |
| `UI.png` | PNG screenshot/asset | Interface illustration in documentation or release notes |
| `figures/manuscript-fig1.pdf` | PDF figure source | Manuscript-related figure reference |
| `figures/overview.png` | PNG figure | Static site and README architecture overview |
| `figures/task-coverage.png` | PNG figure | Benchmark coverage visualization |
| `figures/multistep-success.png` | PNG figure | Multi-step workflow success visualization |
| `figures/reliability.png` | PNG figure | Representative case-study/reliability visualization |
| `figures/reliability.svg` | SVG source | Editable/vector reliability figure |
| `figures/open-source-llms.png` | PNG figure | Open-source LLM benchmark visualization |
| `figures/open-source-llms.svg` | SVG source | Editable/vector open-source LLM figure |

## Maintenance Policy

- Prefer `PNG` or `SVG` for web deployment.
- Preserve `PDF` or `SVG` originals when they come from manuscript materials.
- Keep filenames descriptive and stable so README and static site links do not break.
- Do not store generated workflow outputs, temporary screenshots, SQLite caches, or raw analysis result directories here.
- Keep all quantitative claims consistent with the accepted manuscript and verified benchmark records.
