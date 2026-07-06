## MiXCR Processing

_modules: align, assemble, clonotype-export, mixcr_

```bash
# Align reads to V(D)J segments
mixcr align -s hsa -p rna-seq \
    R1.fastq.gz R2.fastq.gz \
    aligned.vdjca

# Assemble clonotypes
mixcr assemble aligned.vdjca clones.clns

# Export clonotype table
mixcr exportClones clones.clns clones.txt
```

## VDJtools Analysis

_modules: diversity, overlap, repertoire, vdjtools_

```bash
# Convert to VDJtools format
vdjtools Convert -S mixcr clones.txt vdjtools/

# Diversity metrics
vdjtools CalcDiversityStats vdjtools/clones.txt diversity/

# Sample overlap / pairwise distances
vdjtools CalcPairwiseDistances vdjtools/*.txt overlap/
```

## Visualization

_modules: visualization, spectratype, vj-usage_

```bash
# Spectratype plot (CDR3 length distribution)
vdjtools PlotFancySpectratype vdjtools/clones.txt spectra/

# V/J gene usage plot
vdjtools PlotFancyVJUsage vdjtools/clones.txt usage/
```

## QC and Validation

_modules: qc, validation, reporting_

```bash
# MiXCR writes a report alongside each align/assemble run (e.g. align_report.txt, assemble_report.txt).
# 1. After alignment: open the align report and check the V/J assignment rate (typical >70%).
# 2. After assembly: open the assemble report and verify clonotype count and read coverage.
# 3. After diversity: inspect the diversity/ output (Shannon, Simpson, Gini, etc.) and
#    compare the values to the expected range for the sample type.
```
