---
id: wf-0030
title: 'Ribo-seq Data Analysis Workflow for Identifying Translated ORFs:'
summary: 'Ribo-seq Data Analysis Workflow for Identifying Translated ORFs: Step 1:
  Adapter and Quality Trimming (Cutadapt) Description: Remove adapter sequences and
  low-quality bases from raw Ribo-seq reads. Input Required: Raw...'
keywords:
- annotation-comparison
- workflow
- Ribo-seq Data Analysis Workflow for Identifying Translated ORFs
- 'Step 1: Adapter and Quality Trimming (Cutadapt)

  Description: Remove adapter sequences and low-quality bases from raw Ribo-seq reads.

  Input Required: Raw FASTQ files containing Ribo-seq reads.

  Expected Output: Cleaned FASTQ files with adapter sequences and low-quality bases
  removed.

  Tools Used: Cutadapt'
- 'Step 2: rRNA'
- tRNA Filtering (optional if without rRNA
- 'tRNA file) (Bowtie)

  Description: Align reads to rRNA and tRNA sequences to remove contamination.

  Input Required: Cleaned FASTQ files from Step 1.

  Expected Output: FASTQ files with non-rRNA'
- 'tRNA reads.

  Tools Used: Bowtie'
- 'Step 3: Genome or Transcriptome Mapping

  Description: Align filtered reads to the reference genome or transcriptome to determine
  ribosome positions.

  Input Required: Filtered FASTQ files from Step 2.

  Expected Output: BAM files with mapped ribosome footprints'
- 'Step 4: Indendetection of short and long active ORFs'
- 'Tools Used: ribotricer'
- Cutadapt
path: .opencode/knowledge/workflows/wf-0030-ribo-seq-data-analysis-workflow-for-identifying-translated-orfs.md
origin_source: workflow
origin_page: 32
source_entry_index: 22
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: annotation-comparison
---

# Ribo-seq Data Analysis Workflow for Identifying Translated ORFs:

## One-line description

Ribo-seq Data Analysis Workflow for Identifying Translated ORFs: Step 1: Adapter and Quality Trimming (Cutadapt) Description: Remove adapter sequences and low-quality bases from raw Ribo-seq reads. Input Required: Raw...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `32`
- Source entry index: `22`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0030`
- Analysis/tool category: `annotation-comparison`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Ribo-seq Data Analysis Workflow for Identifying Translated ORFs:

Step 1: Adapter and Quality Trimming (Cutadapt)
Description: Remove adapter sequences and low-quality bases from raw Ribo-seq reads.
Input Required: Raw FASTQ files containing Ribo-seq reads.
Expected Output: Cleaned FASTQ files with adapter sequences and low-quality bases removed.
Tools Used: Cutadapt.

Step 2: rRNA/tRNA Filtering (optional if without rRNA/tRNA file) (Bowtie)
Description: Align reads to rRNA and tRNA sequences to remove contamination.
Input Required: Cleaned FASTQ files from Step 1.
Expected Output: FASTQ files with non-rRNA/tRNA reads.
Tools Used: Bowtie.

Step 3: Genome or Transcriptome Mapping
Description: Align filtered reads to the reference genome or transcriptome to determine ribosome positions.
Input Required: Filtered FASTQ files from Step 2.
Expected Output: BAM files with mapped ribosome footprints.

Step 4: Indendetection of short and long active ORFs 
 Tools Used: ribotricer
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
