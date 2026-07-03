---
id: wf-0032
title: RIP-seq Data Analysis Workflow for Identifying Enriched Genes Bound by RNA-Binding
  Proteins (RBPs...
summary: 'RIP-seq Data Analysis Workflow for Identifying Enriched Genes Bound by RNA-Binding
  Proteins (RBPs): Step 1: Adapter and Quality Trimming (Cutadapt) Description: Remove
  adapter sequences and perform quality trimming to...'
keywords:
- chipseq-peak
- workflow
- RIP-seq Data Analysis Workflow for Identifying Enriched Genes Bound by RNA-Binding
  Proteins (RBPs
- 'RIP-seq Data Analysis Workflow for Identifying Enriched Genes Bound by RNA-Binding
  Proteins (RBPs): Step 1: Adapter and Quality Trimming (Cutadapt) Description: Remove
  adapter sequences and perform quality trimming to ensure high-quality reads for
  accurate downstream analysis. Input Required: Raw FASTQ files from RIP and input
  control samples. Expected Output: Cleaned and trimmed FASTQ files. Tools Used: Cutadapt'
- 'FastQC. Step 2: Read Alignment to Reference Genome (STAR) Description: Align cleaned
  reads to the reference genome to obtain mapped reads. Input Required: Trimmed FASTQ
  files from Step 1. Expected Output: BAM files with genome-aligned reads. Tools Used:
  STAR aligner. Step 3: Peak Calling to Identify RBP Binding Regions (exomePeak or
  CLIPper) Description: Detect RBP-bound regions by comparing RIP samples to input
  controls. Input Required: BAM files from Step 2. Expected Output: BED or peak files
  representing significant RBP binding sites. Tools Used: exomePeak (R)'
- 'CLIPper. Step 4: Annotation of Peaks to Genes (ChIPseeker or BEDTools) Description:
  Map the detected peaks to genomic features (e.g'
- UTRs
- CDS
- 'promoters) to associate with genes. Input Required: Peak files and'
- FastQC
- Cutadapt
- STAR
- bedtools
path: .opencode/knowledge/workflows/wf-0032-rip-seq-data-analysis-workflow-for-identifying-enriched-genes-bound-by-rna-binding-proteins-rbps.md
origin_source: workflow
origin_page: 34
source_entry_index: 24
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: chipseq-peak
---

# RIP-seq Data Analysis Workflow for Identifying Enriched Genes Bound by RNA-Binding Proteins (RBPs...

## One-line description

RIP-seq Data Analysis Workflow for Identifying Enriched Genes Bound by RNA-Binding Proteins (RBPs): Step 1: Adapter and Quality Trimming (Cutadapt) Description: Remove adapter sequences and perform quality trimming to...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `34`
- Source entry index: `24`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0032`
- Analysis/tool category: `chipseq-peak`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
RIP-seq Data Analysis Workflow for Identifying Enriched Genes Bound by RNA-Binding Proteins (RBPs): Step 1: Adapter and Quality Trimming (Cutadapt) Description: Remove adapter sequences and perform quality trimming to ensure high-quality reads for accurate downstream analysis. Input Required: Raw FASTQ files from RIP and input control samples. Expected Output: Cleaned and trimmed FASTQ files. Tools Used: Cutadapt, FastQC. Step 2: Read Alignment to Reference Genome (STAR) Description: Align cleaned reads to the reference genome to obtain mapped reads. Input Required: Trimmed FASTQ files from Step 1. Expected Output: BAM files with genome-aligned reads. Tools Used: STAR aligner. Step 3: Peak Calling to Identify RBP Binding Regions (exomePeak or CLIPper) Description: Detect RBP-bound regions by comparing RIP samples to input controls. Input Required: BAM files from Step 2. Expected Output: BED or peak files representing significant RBP binding sites. Tools Used: exomePeak (R), CLIPper. Step 4: Annotation of Peaks to Genes (ChIPseeker or BEDTools) Description: Map the detected peaks to genomic features (e.g., UTRs, CDS, promoters) to associate with genes. Input Required: Peak files and genome annotation (GTF). Expected Output: Annotated peak-gene pairs. Tools Used: ChIPseeker, BEDTools. Step 5: Differential Enrichment Analysis (DESeq2) Description: Compare RIP vs input read counts over genes or peaks to find enriched targets. Input Required: Count matrix of reads over genes or peaks. Expected Output: List of significantly enriched genes bound by RBP. Tools Used: DESeq2. Step 6: Visualization and Validation Description: Visualize binding patterns and validate enriched genes. Input Required: Enrichment results and BAM files. Expected Output: Genome browser tracks, heatmaps, and ranked gene lists. Tools Used: IGV, R packages (ggplot2, pheatmap).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
