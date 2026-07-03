## Pre-installation Check

_modules: prerequisites, environment-check_

```bash
# Confirm this is a BioMaster project with the expected structure
test -d .opencode/bioskills && echo "bioskills dir exists" || echo "bioskills dir missing"

# Confirm the bundled install script is present
test -f scripts/install-bioskills.sh && echo "install script found" || echo "install script missing"

# Decide install scope before proceeding:
#   - Full install: all 425 skills across 62 categories
#   - Selective install: only named categories, e.g.
#     single-cell, variant-calling, differential-expression, chip-seq,
#     atac-seq, metagenomics, proteomics, phylogenetics, ...
```

## Installation

_modules: installation, download_

```bash
# Full install: all 425 skills across 62 categories
bash scripts/install-bioskills.sh

# Selective install: only specific categories
bash scripts/install-bioskills.sh --categories "single-cell,variant-calling,differential-expression"
```

## Verification

_modules: verification, validation_

```bash
# Count installed skill directories
ls -1 .opencode/bioskills/ | wc -l

# List installed skill names
ls -1 .opencode/bioskills/

# Spot-check that a category of interest landed (e.g. single-cell)
ls -1 .opencode/bioskills/ | grep -i single-cell
```

## Post-installation Usage

_modules: usage, discovery_

```bash
# Skills are auto-triggered by task; no manual command is needed.
# To inspect available skills after install:
ls -1 .opencode/bioskills/

# Example requests that map to installed categories:
#   - "I have RNA-seq counts from treated vs control - find differentially expressed genes"
#   - "Call variants from this whole-genome BAM file"
#   - "Cluster my single-cell RNA-seq data and find marker genes"
#   - "Predict the structure of this protein sequence"
#   - "Run a metagenomics classification on these shotgun reads"
```
