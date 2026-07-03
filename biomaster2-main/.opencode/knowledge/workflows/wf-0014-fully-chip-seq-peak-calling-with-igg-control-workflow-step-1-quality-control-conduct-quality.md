---
id: wf-0014
title: 'Fully ChIP-seq Peak Calling with IgG Control Workflow: Step 1: Quality Control
  - Conduct quality...'
summary: 'Fully ChIP-seq Peak Calling with IgG Control Workflow: Step 1: Quality Control
  - Conduct quality control on raw sequencing data to ensure data integrity and quality.
  This step involves checking read quality scores, id...'
keywords:
- chipseq-peak
- workflow
- 'Fully ChIP-seq Peak Calling with IgG Control Workflow: Step 1: Quality Control
  - Conduct quality'
- Fully ChIP-seq Peak Calling
- 'with IgG Control Workflow: Step 1: Quality Control - Conduct quality control on
  raw sequencing data to ensure data integrity and quality'
- This step involves checking read quality scores
- identifying adapter sequences
- and trimming low-quality bases
- 'Input Required: Raw FASTQ files'
- 'Expected Output: Cleaned and quality-checked FASTQ files'
- 'Tools Used: FastQC'
- Trimmomatic
- Cutadapt
- 'Step 2: Alignment - Align reads to the reference genome to map sequencing data
  to genomic coordinates'
- 'Input Required: Cleaned FASTQ files from Step 1 and the reference genome'
- 'Expected Output: Sorted BAM file containing aligned reads'
- 'Tools Used: BWA-MEM'
- Bowtie2
- STAR
- 'Step 3: SAM'
- BAM Conversion & Processing - Convert SAM files to BAM format
- sort them
- and remove PCR duplicates to improve downstream analysis accuracy
- 'Input Required: SAM file from Step 2'
- 'Expected Output: De-duplicated BAM file'
- 'Tools Used: SAMtools'
- Picard
- 'Step 4: Signal Track Generation - Generate signal track files for visualizing ChIP
  enrichment in genome browsers such as IGV'
- 'Input Required: De-duplicated BAM file from Step 3'
- 'Expected Output: BigWig signal track file'
- 'Tools Used: deep'
- FastQC
- BWA
- samtools
path: .opencode/knowledge/workflows/wf-0014-fully-chip-seq-peak-calling-with-igg-control-workflow-step-1-quality-control-conduct-quality.md
origin_source: workflow
origin_page: 16
source_entry_index: 6
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: chipseq-peak
---

# Fully ChIP-seq Peak Calling with IgG Control Workflow: Step 1: Quality Control - Conduct quality...

## One-line description

Fully ChIP-seq Peak Calling with IgG Control Workflow: Step 1: Quality Control - Conduct quality control on raw sequencing data to ensure data integrity and quality. This step involves checking read quality scores, id...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `16`
- Source entry index: `6`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0014`
- Analysis/tool category: `chipseq-peak`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Fully ChIP-seq Peak Calling  with IgG Control Workflow: Step 1: Quality Control - Conduct quality control on raw sequencing data to ensure data integrity and quality.  This step involves checking read quality scores, identifying adapter sequences, and trimming low-quality bases.  Input Required: Raw FASTQ files.  Expected Output: Cleaned and quality-checked FASTQ files.  Tools Used: FastQC, Trimmomatic, Cutadapt.  Step 2: Alignment - Align reads to the reference genome to map sequencing data to genomic coordinates.  Input Required: Cleaned FASTQ files from Step 1 and the reference genome.  Expected Output: Sorted BAM file containing aligned reads.  Tools Used: BWA-MEM, Bowtie2, STAR.  Step 3: SAM/BAM Conversion & Processing - Convert SAM files to BAM format, sort them, and remove PCR duplicates to improve downstream analysis accuracy.  Input Required: SAM file from Step 2.  Expected Output: De-duplicated BAM file.  Tools Used: SAMtools, Picard.  Step 4: Signal Track Generation - Generate signal track files for visualizing ChIP enrichment in genome browsers such as IGV.  Input Required: De-duplicated BAM file from Step 3.  Expected Output: BigWig signal track file.  Tools Used: deeptools, bedGraphToBigWig.  Step 5: Peak Calling - Call peaks to identify enriched genomic regions for CBX7 binding using IgG as control.  Input Required: De-duplicated BAM file from Step 3 and IgG control BAM file.  Expected Output: NarrowPeak file containing identified peaks.  Tools Used: MACS3.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
