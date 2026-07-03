---
id: task-0021
title: Quick Guide to DiffBind
summary: '## Quick Guide to DiffBind **DiffBind** is an R/Bioconductor package for
  analyzing differential binding (peaks) in ChIP-seq or ATAC-seq data. Below is a
  concise workflow: --- ### 1. Installation & Setup ```r if (!requ...'
keywords:
- deseq2
- Diffbind
- Quick Guide to DiffBind
- '## Quick Guide to DiffBind'
- '**DiffBind** is an R'
- Bioconductor package for analyzing differential binding (peaks) in ChIP-seq or ATAC-seq
  data. Below is a concise workflow
- '### 1. Installation & Setup

  ```r

  if (!requireNamespace("BiocManager"'
- quietly=TRUE))
- install.packages("BiocManager")
- BiocManager::install("DiffBind")
- 'library(DiffBind)

  ```'
- '### 2. Prepare Input Files'
- '**SampleSheet.csv**: Each row describes one sample'
- including columns
- '`SampleID`'
- '`Tissue`'
- '`Factor`'
- '`Condition`'
- '`Replicate`'
- '`bamReads`'
- '`bamControl` (paths to BAM files)'
- '`Peaks` (path to called peak file)'
- '`PeakCaller` (e.g'
- MACS2)
- 'Example:

  ```csv

  SampleID'
- Tissue
- Factor
- Condition
- Replicate
- bamReads
- bamControl
- Peaks
- 'PeakCaller

  S1'
- MCF7
- ER
- Responsive
- '1'
- S1.bam
- S1_input.bam
- S1_peaks.bed
- 'macs2

  S2'
- '2'
- S2.bam
- S2_input.bam
- S2_peaks.bed
- 'macs2

  ...

  ```'
- '### 3. Read & Merge Peaks

  ```r

  # Read metadata from CSV and merge overlapping peaks

  dbObj <- dba(sampleSheet = "SampleSheet.csv")

  plot(dbObj)'
- '# Heatmap of sample correlations

  ```'
- '### 4. Count Reads in Peaks

  ```r

  # Counts reads from BAM files in merged peak regions

  # bUseSummarizeOverlaps=TRUE uses a more standa'
- DESeq2
path: .opencode/knowledge/tasks/task-0021-quick-guide-to-diffbind.md
origin_source: Diffbind
origin_page: 22
source_entry_index: 17
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-r-package
tool: deseq2
---

# Quick Guide to DiffBind

## One-line description

## Quick Guide to DiffBind **DiffBind** is an R/Bioconductor package for analyzing differential binding (peaks) in ChIP-seq or ATAC-seq data. Below is a concise workflow: --- ### 1. Installation & Setup ```r if (!requ...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `Diffbind`
- Origin page: `22`
- Source entry index: `17`
- Source subindex: `1`
- Canonical skill: `exec-r-package`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-r-package`
- Registry ID: `task-0021`
- Analysis/tool category: `deseq2`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
## Quick Guide to DiffBind

**DiffBind** is an R/Bioconductor package for analyzing differential binding (peaks) in ChIP-seq or ATAC-seq data. Below is a concise workflow:

---

### 1. Installation & Setup
~~~r
if (!requireNamespace("BiocManager", quietly=TRUE))
    install.packages("BiocManager")

BiocManager::install("DiffBind")

library(DiffBind)
~~~

---

### 2. Prepare Input Files

- **SampleSheet.csv**: Each row describes one sample, including columns:
  - `SampleID`, `Tissue`, `Factor`, `Condition`, `Replicate`
  - `bamReads`, `bamControl` (paths to BAM files)
  - `Peaks` (path to called peak file)
  - `PeakCaller` (e.g., MACS2)

Example:
~~~csv
SampleID,Tissue,Factor,Condition,Replicate,bamReads,bamControl,Peaks,PeakCaller
S1,MCF7,ER,Responsive,1,S1.bam,S1_input.bam,S1_peaks.bed,macs2
S2,MCF7,ER,Responsive,2,S2.bam,S2_input.bam,S2_peaks.bed,macs2
...
~~~

---

### 3. Read & Merge Peaks
~~~r
# Read metadata from CSV and merge overlapping peaks
dbObj <- dba(sampleSheet = "SampleSheet.csv")
plot(dbObj)  # Heatmap of sample correlations
~~~

---

### 4. Count Reads in Peaks
~~~r
# Counts reads from BAM files in merged peak regions
# bUseSummarizeOverlaps=TRUE uses a more standardized counting method
dbObj <- dba.count(dbObj, bUseSummarizeOverlaps=TRUE)

# Optional: library size normalization
dbObj <- dba.normalize(dbObj)
~~~

---

### 5. Differential Analysis

1. **Set contrast** (which groups to compare):
~~~r
# Example: Condition = "Resistant" vs. "Responsive", with "Responsive" as baseline
# or specify a design formula including multiple factors

dbObj <- dba.contrast(dbObj, reorderMeta=list(Condition="Responsive"))
~~~

2. **Run differential binding** (using DESeq2 by default):
~~~r
dbObj <- dba.analyze(dbObj)

# Show results (number of significantly changed sites)
dba.show(dbObj, bContrasts=TRUE)
~~~

3. **Extract differentially bound peaks**:
~~~r
dbSites <- dba.report(dbObj)

# Convert to data frame, filter by FDR, save as BED
out <- as.data.frame(dbSites)
sigPeaks <- out[out$FDR < 0.05, c("seqnames","start","end","strand","Fold")]
write.table(sigPeaks, "diffbind_sig_peaks.bed", sep="\t", row.names=FALSE, col.names=FALSE)
~~~

---

### 6. Visualization

- **Heatmap**:
  ~~~r
  dba.plotHeatmap(dbObj)
  ~~~

- **PCA**:
  ~~~r
  dba.plotPCA(dbObj, label=DBA_CONDITION)
  ~~~

- **Venn Diagram** (overlaps):
  ~~~r
  dba.plotVenn(dbObj, contrast=1)
  ~~~

- **Volcano Plot**:
  ~~~r
  dba.plotVolcano(dbObj)
  ~~~

---

### Key Points
1. **SampleSheet** + **peak files** + **BAM files** required.
2. Merged peaks → read counting → normalization → differential analysis.
3. Results are retrieved via `dba.report()`. Visualization includes heatmaps, PCA, venn diagrams.
4. By default, **DESeq2** is used, but **edgeR** can also be specified.

For more detail, see the [DiffBind vignette](https://bioconductor.org/packages/release/bioc/vignettes/DiffBind/inst/doc/DiffBind.pdf).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
