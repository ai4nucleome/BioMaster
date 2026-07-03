---
id: wf-0031
title: 'CLIP-seq Data Analysis Workflow for Identifying Protein-RNA Cross-Link Sites:
  Step 1: Adapter and...'
summary: 'CLIP-seq Data Analysis Workflow for Identifying Protein-RNA Cross-Link Sites:
  Step 1: Adapter and Quality Trimming (Cutadapt) Description: Remove adapter sequences
  and perform quality trimming to prepare high-quality...'
keywords:
- workflow
- 'CLIP-seq Data Analysis Workflow for Identifying Protein-RNA Cross-Link Sites: Step
  1: Adapter and'
- 'CLIP-seq Data Analysis Workflow for Identifying Protein-RNA Cross-Link Sites: Step
  1: Adapter and Quality Trimming (Cutadapt) Description: Remove adapter sequences
  and perform quality trimming to prepare high-quality reads for downstream analysis.
  Input Required: Raw FASTQ files containing sequencing reads. Expected Output: Trimmed
  FASTQ files with adapter sequences removed and low-quality bases trimmed. Tools
  Used: Cutadapt. Step 2: Pre-mapping to rRNA and tRNA Sequences (Bowtie 2) Description:
  Align reads to rRNA and tRNA sequences to filter out non-specific reads. Input Required:
  Trimmed FASTQ files from Step 1. Expected Output: BAM files with aligned reads to
  rRNA and tRNA sequences. Tools Used: Bowtie 2. Step 3: Genome Mapping (STAR) Description:
  Align filtered reads to the reference genome for accurate mapping. Input Required:
  BAM files from Step 2. Expected Output: BAM files with reads mapped to the genome.
  Tools Used: STAR aligner. Step 4: UMI-based Deduplication (UMI-tools) Description:
  Identify and collapse PCR duplicates based on Unique Molecular Identifiers (UMIs)
  to ensure data accuracy. Input Required: BAM files from Step 3. Expected Output:
  Deduplicated BAM files. To'
- Cutadapt
- STAR
path: .opencode/knowledge/workflows/wf-0031-clip-seq-data-analysis-workflow-for-identifying-protein-rna-cross-link-sites-step-1-adapter-and.md
origin_source: workflow
origin_page: 33
source_entry_index: 23
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: workflow
---

# CLIP-seq Data Analysis Workflow for Identifying Protein-RNA Cross-Link Sites: Step 1: Adapter and...

## One-line description

CLIP-seq Data Analysis Workflow for Identifying Protein-RNA Cross-Link Sites: Step 1: Adapter and Quality Trimming (Cutadapt) Description: Remove adapter sequences and perform quality trimming to prepare high-quality...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `33`
- Source entry index: `23`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0031`
- Analysis/tool category: `workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
CLIP-seq Data Analysis Workflow for Identifying Protein-RNA Cross-Link Sites: Step 1: Adapter and Quality Trimming (Cutadapt) Description: Remove adapter sequences and perform quality trimming to prepare high-quality reads for downstream analysis. Input Required: Raw FASTQ files containing sequencing reads. Expected Output: Trimmed FASTQ files with adapter sequences removed and low-quality bases trimmed. Tools Used: Cutadapt. Step 2: Pre-mapping to rRNA and tRNA Sequences (Bowtie 2) Description: Align reads to rRNA and tRNA sequences to filter out non-specific reads. Input Required: Trimmed FASTQ files from Step 1. Expected Output: BAM files with aligned reads to rRNA and tRNA sequences. Tools Used: Bowtie 2. Step 3: Genome Mapping (STAR) Description: Align filtered reads to the reference genome for accurate mapping. Input Required: BAM files from Step 2. Expected Output: BAM files with reads mapped to the genome. Tools Used: STAR aligner. Step 4: UMI-based Deduplication (UMI-tools) Description: Identify and collapse PCR duplicates based on Unique Molecular Identifiers (UMIs) to ensure data accuracy. Input Required: BAM files from Step 3. Expected Output: Deduplicated BAM files. Tools Used: UMI-tools. Step 5: Crosslink Identification (BEDTools) Description: Identify crosslink sites by analyzing the deduplicated reads. Input Required: Deduplicated BAM files from Step 4. Expected Output: BED files containing identified crosslink sites. Tools Used: BEDTools.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
