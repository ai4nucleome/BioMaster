---
id: wf-0039
title: 'CAGE-seq Core Analysis Workflow must include:Step 1: BAM File Validation and
  Preprocessing Descri...'
summary: 'CAGE-seq Core Analysis Workflow must include:Step 1: BAM File Validation
  and Preprocessing Description: Verify BAM file integrity, perform coordinate sorting,
  and generate index file.Input Required: Raw BAM file with...'
keywords:
- workflow
- 'CAGE-seq Core Analysis Workflow must include:Step 1: BAM File Validation and Preprocessing
  Descri'
- 'CAGE-seq Core Analysis Workflow must include:Step 1: BAM File Validation and Preprocessing
  Description: Verify BAM file integrity'
- perform coordinate sorting
- 'and generate index file.Input Required: Raw BAM file with genomic coordinates.Expected
  Output: Sorted BAM file (sorted.bam) and index file (sorted.bam.bai).Tools Used:
  samtools.Step 2: TSS Signal Extraction Description: Extract 5'' end positions of
  sequencing reads from sorted BAM file. Input Required: Sorted BAM file (sorted.bam)
  from Step 1. Expected Output: Text file containing 5'' end positions (5prime_positions.txt).Tools
  Used: samtools + awk. Step 3: TSS Clustering Analysis Description: Perform density-based
  clustering of 5'' end positions to identify transcription start site (TSS) clusters.
  Input Required: 5'' end position file (5prime_positions.txt) from Step2. Expected
  Output: TSS cluster file in BED format (tss_clusters.bed). Tools Used: paraclu'
- samtools
path: .opencode/knowledge/workflows/wf-0039-cage-seq-core-analysis-workflow-must-include-step-1-bam-file-validation-and-preprocessing-descri.md
origin_source: workflow
origin_page: 41
source_entry_index: 31
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: workflow
---

# CAGE-seq Core Analysis Workflow must include:Step 1: BAM File Validation and Preprocessing Descri...

## One-line description

CAGE-seq Core Analysis Workflow must include:Step 1: BAM File Validation and Preprocessing Description: Verify BAM file integrity, perform coordinate sorting, and generate index file.Input Required: Raw BAM file with...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `41`
- Source entry index: `31`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0039`
- Analysis/tool category: `workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
CAGE-seq Core Analysis Workflow must include:Step 1: BAM File Validation and Preprocessing Description: Verify BAM file integrity, perform coordinate sorting, and generate index file.Input Required: Raw BAM file with genomic coordinates.Expected Output: Sorted BAM file (sorted.bam) and index file (sorted.bam.bai).Tools Used: samtools.Step 2: TSS Signal Extraction Description: Extract 5' end positions of sequencing reads from sorted BAM file. Input Required: Sorted BAM file (sorted.bam) from Step 1. Expected Output: Text file containing 5' end positions (5prime_positions.txt).Tools Used: samtools + awk. Step 3: TSS Clustering Analysis Description: Perform density-based clustering of 5' end positions to identify transcription start site (TSS) clusters. Input Required: 5' end position file (5prime_positions.txt) from Step2. Expected Output: TSS cluster file in BED format (tss_clusters.bed). Tools Used: paraclu.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
