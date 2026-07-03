---
id: wf-0040
title: 'DNase-seq analysis workflow must include: Step 1: Data Preprocessing and Quality
  Control. Descrip...'
summary: 'DNase-seq analysis workflow must include: Step 1: Data Preprocessing and
  Quality Control. Description: Remove low-quality sequences, adapter contaminants,
  and short reads from raw FASTQ files to ensure data reliabilit...'
keywords:
- chipseq-peak
- workflow
- 'DNase-seq analysis workflow must include: Step 1: Data Preprocessing and Quality
  Control. Descrip'
- 'DNase-seq analysis workflow must include: Step 1: Data Preprocessing and Quality
  Control. Description: Remove low-quality sequences'
- adapter contaminants
- 'and short reads from raw FASTQ files to ensure data reliability. This involves
  quality assessment and filtering. Input Required: Raw paired-end FASTQ files . Expected
  Output: Cleaned paired-end FASTQ files'
- FastQC quality control reports (HTML files in
- 'fastqc_results). Tools Used: FastQC for quality assessment'
- 'Trimmomatic for adapter trimming and quality filtering. Step 2: Sequence Alignment.
  Description: Align filtered reads to the reference genome using precomputed indices.
  Input Required: Cleaned FASTQ files from Step 1'
- 'reference genome index files. Expected Output: Unsorted SAM file containing aligned
  reads (e.g'
- 'sample_aligned.sam). Tools Used: Bowtie2 for sequence alignment. Step 3: BAM File
  Processing and Duplicate Removal. Description: Convert SAM to BAM format'
- sort reads by genomic coordinates
- remove PCR duplicates
- 'and generate BAM indices. Input Required: Unsorted SAM file (sample_aligned.sam).
  Expected Output: Deduplicated and sorted BAM file (sample_dedup.bam)'
- BAM index file (sample_dedup.bam.bai). Tools Used
- FastQC
- Trimmomatic
- Bowtie2
path: .opencode/knowledge/workflows/wf-0040-dnase-seq-analysis-workflow-must-include-step-1-data-preprocessing-and-quality-control-descrip.md
origin_source: workflow
origin_page: 42
source_entry_index: 32
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: chipseq-peak
---

# DNase-seq analysis workflow must include: Step 1: Data Preprocessing and Quality Control. Descrip...

## One-line description

DNase-seq analysis workflow must include: Step 1: Data Preprocessing and Quality Control. Description: Remove low-quality sequences, adapter contaminants, and short reads from raw FASTQ files to ensure data reliabilit...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `42`
- Source entry index: `32`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0040`
- Analysis/tool category: `chipseq-peak`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
DNase-seq analysis workflow must include: Step 1: Data Preprocessing and Quality Control. Description: Remove low-quality sequences, adapter contaminants, and short reads from raw FASTQ files to ensure data reliability. This involves quality assessment and filtering. Input Required: Raw paired-end FASTQ files . Expected Output: Cleaned paired-end FASTQ files, FastQC quality control reports (HTML files in ./fastqc_results). Tools Used: FastQC for quality assessment, Trimmomatic for adapter trimming and quality filtering. Step 2: Sequence Alignment. Description: Align filtered reads to the reference genome using precomputed indices. Input Required: Cleaned FASTQ files from Step 1, reference genome index files. Expected Output: Unsorted SAM file containing aligned reads (e.g., sample_aligned.sam). Tools Used: Bowtie2 for sequence alignment. Step 3: BAM File Processing and Duplicate Removal. Description: Convert SAM to BAM format, sort reads by genomic coordinates, remove PCR duplicates, and generate BAM indices. Input Required: Unsorted SAM file (sample_aligned.sam). Expected Output: Deduplicated and sorted BAM file (sample_dedup.bam), BAM index file (sample_dedup.bam.bai). Tools Used: samtools for format conversion, sorting, and indexing, Picard MarkDuplicates for PCR duplicate removal. Step 4: DHSs Identification (Peak Calling). Description: Identify chromatin open regions (DNase I hypersensitive sites, DHSs) and generate significant peak files. Input Required: Deduplicated BAM file (`sample_dedup.bam`). Expected Output: Peak files (`.narrowPeak`), containing genomic coordinates and statistical significance scores. Tools Used: MACS2 (parameters: `-nomodel --extsize 200`).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
