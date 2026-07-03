---
id: task-0051
title: 'Tool: featureCounts'
summary: 'Tool: featureCounts Purpose: Count reads mapped to genomic features such
  as genes or exons for isoform or gene expression quantification. Input: Sorted and
  indexed BAM file, GTF annotation file Output: Read count matr...'
keywords:
- featurecounts
- featureCounts
- 'Tool: featureCounts'
- 'Tool: featureCounts

  Purpose: Count reads mapped to genomic features such as genes or exons for isoform
  or gene expression quantification.

  Input: Sorted and indexed BAM file'
- 'GTF annotation file

  Output: Read count matrix

  Command Example: featureCounts -a annotation.gtf -o counts.txt aligned.bam

  Note: Supports long-read BAM input as long as it''s properly aligned and sorted'
path: .opencode/knowledge/tasks/task-0051-tool-featurecounts.md
origin_source: featureCounts
origin_page: 52
source_entry_index: 47
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: featurecounts
---

# Tool: featureCounts

## One-line description

Tool: featureCounts Purpose: Count reads mapped to genomic features such as genes or exons for isoform or gene expression quantification. Input: Sorted and indexed BAM file, GTF annotation file Output: Read count matr...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `featureCounts`
- Origin page: `52`
- Source entry index: `47`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0051`
- Analysis/tool category: `featurecounts`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Tool: featureCounts
Purpose: Count reads mapped to genomic features such as genes or exons for isoform or gene expression quantification.
Input: Sorted and indexed BAM file, GTF annotation file
Output: Read count matrix
Command Example: featureCounts -a annotation.gtf -o counts.txt aligned.bam
Note: Supports long-read BAM input as long as it's properly aligned and sorted.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
