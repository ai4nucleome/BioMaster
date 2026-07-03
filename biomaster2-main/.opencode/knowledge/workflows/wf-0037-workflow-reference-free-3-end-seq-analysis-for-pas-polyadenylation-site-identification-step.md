---
id: wf-0037
title: 'Workflow: Reference-free 3′ end-seq analysis for PAS (polyadenylation site)
  identification. Step...'
summary: 'Workflow: Reference-free 3′ end-seq analysis for PAS (polyadenylation site)
  identification. Step 1: Quality Control and Adapter Trimming Tool: fastp Description:
  Remove sequencing adapters and low-quality bases from r...'
keywords:
- workflow
- 'Workflow: Reference-free 3′ end-seq analysis for PAS (polyadenylation site) identification.
  Step'
- 'Workflow: Reference-free 3′ end-seq analysis for PAS (polyadenylation site) identification.
  Step 1: Quality Control and Adapter Trimming Tool: fastp Description: Remove sequencing
  adapters and low-quality bases from raw 3′ end-seq FASTQ reads. Input: Raw FASTQ
  file (single-end) Output: Trimmed FASTQ file Step 2: 3′ End Extraction Tool: extract_3p_end
  Description: Extract the last 20 nucleotides from each read without alignment'
- 'producing a FASTA file of 3′ ends. Input: Trimmed FASTQ file Output: FASTA file
  containing 3′ end reads Note: This is an internal logic operation'
- 'not a script or command. Step 3: PAS Clustering Tool: internal logic Description:
  Cluster identical or similar 3′ end sequences to identify high-confidence polyadenylation
  sites (PAS). Input: FASTA file with 3′ end reads Output: PAS_sites.tsv listing representative
  PAS sequences and their abundance Note: This is an internal reasoning step and should
  not be linked to an external tool'
path: .opencode/knowledge/workflows/wf-0037-workflow-reference-free-3-end-seq-analysis-for-pas-polyadenylation-site-identification-step.md
origin_source: workflow
origin_page: 39
source_entry_index: 29
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: workflow
---

# Workflow: Reference-free 3′ end-seq analysis for PAS (polyadenylation site) identification. Step...

## One-line description

Workflow: Reference-free 3′ end-seq analysis for PAS (polyadenylation site) identification. Step 1: Quality Control and Adapter Trimming Tool: fastp Description: Remove sequencing adapters and low-quality bases from r...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `39`
- Source entry index: `29`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0037`
- Analysis/tool category: `workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Workflow: Reference-free 3′ end-seq analysis for PAS (polyadenylation site) identification. Step 1: Quality Control and Adapter Trimming Tool: fastp Description: Remove sequencing adapters and low-quality bases from raw 3′ end-seq FASTQ reads. Input: Raw FASTQ file (single-end) Output: Trimmed FASTQ file Step 2: 3′ End Extraction Tool: extract_3p_end Description: Extract the last 20 nucleotides from each read without alignment, producing a FASTA file of 3′ ends. Input: Trimmed FASTQ file Output: FASTA file containing 3′ end reads Note: This is an internal logic operation, not a script or command. Step 3: PAS Clustering Tool: internal logic Description: Cluster identical or similar 3′ end sequences to identify high-confidence polyadenylation sites (PAS). Input: FASTA file with 3′ end reads Output: PAS_sites.tsv listing representative PAS sequences and their abundance Note: This is an internal reasoning step and should not be linked to an external tool.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
