---
id: wf-0038
title: 'Step 1: Perform internal logic quality control and adapter trimming on long-read
  RNA-seq reads (e...'
summary: 'Step 1: Perform internal logic quality control and adapter trimming on long-read
  RNA-seq reads (e.g., PacBio) to remove low-quality bases (Q < 10), N bases, and
  known adapter sequences. Input: raw FASTQ file. Output:...'
keywords:
- rnaseq-de
- workflow
- 'Step 1: Perform internal logic quality control and adapter trimming on long-read
  RNA-seq reads (e'
- 'Step 1: Perform internal logic quality control and adapter trimming on long-read
  RNA-seq reads (e.g'
- PacBio) to remove low-quality bases (Q < 10)
- N bases
- 'and known adapter sequences. Input: raw FASTQ file. Output: trimmed FASTQ file.
  Tool: internal logic. Step 2: Align the trimmed reads to the mouse reference genome
  using minimap2 with long-read RNA-seq parameters (-ax splice -uf -k14). Input: trimmed
  FASTQ file and reference genome (FASTA). Output: SAM file. Tool: minimap2. Step
  3: Convert the SAM file to BAM format using samtools. Input: SAM file. Output: BAM
  file. Tool: samtools. Step 4: Sort and index the BAM file using samtools. Input:
  BAM file. Output: sorted BAM file. Tool: samtools. Step 5: Quantify transcript isoform
  expression using featureCounts with GTF annotation. Use options -t exon -g transcript_id
  to perform isoform-level counting. Input: sorted BAM file and GTF annotation file.
  Output: isoform expression matrix. Tool: featureCounts. Note: This is a reference-based
  pipeline optimized for long-read RNA-seq and avoids R entirely'
- samtools
- featureCounts
path: .opencode/knowledge/workflows/wf-0038-step-1-perform-internal-logic-quality-control-and-adapter-trimming-on-long-read-rna-seq-reads-e.md
origin_source: workflow
origin_page: 40
source_entry_index: 30
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: rnaseq-de
---

# Step 1: Perform internal logic quality control and adapter trimming on long-read RNA-seq reads (e...

## One-line description

Step 1: Perform internal logic quality control and adapter trimming on long-read RNA-seq reads (e.g., PacBio) to remove low-quality bases (Q < 10), N bases, and known adapter sequences. Input: raw FASTQ file. Output:...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `40`
- Source entry index: `30`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0038`
- Analysis/tool category: `rnaseq-de`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Step 1: Perform internal logic quality control and adapter trimming on long-read RNA-seq reads (e.g., PacBio) to remove low-quality bases (Q < 10), N bases, and known adapter sequences. Input: raw FASTQ file. Output: trimmed FASTQ file. Tool: internal logic. Step 2: Align the trimmed reads to the mouse reference genome using minimap2 with long-read RNA-seq parameters (-ax splice -uf -k14). Input: trimmed FASTQ file and reference genome (FASTA). Output: SAM file. Tool: minimap2. Step 3: Convert the SAM file to BAM format using samtools. Input: SAM file. Output: BAM file. Tool: samtools. Step 4: Sort and index the BAM file using samtools. Input: BAM file. Output: sorted BAM file. Tool: samtools. Step 5: Quantify transcript isoform expression using featureCounts with GTF annotation. Use options -t exon -g transcript_id to perform isoform-level counting. Input: sorted BAM file and GTF annotation file. Output: isoform expression matrix. Tool: featureCounts. Note: This is a reference-based pipeline optimized for long-read RNA-seq and avoids R entirely.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
