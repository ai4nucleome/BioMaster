---
id: task-0046
title: 'Tool: STAR'
summary: 'Tool: STAR Purpose: Align 3′ end-seq reads to a reference genome with high
  precision. Input: Trimmed FASTQ file and genome index Output: Sorted BAM file Command
  Example: STAR --runThreadN 4 --genomeDir ./genome_index...'
keywords:
- star
- task
- 'Tool: STAR'
- 'Tool: STAR

  Purpose: Align 3′ end-seq reads to a reference genome with high precision.

  Input: Trimmed FASTQ file and genome index

  Output: Sorted BAM file

  Command Example'
- STAR --runThreadN 4 --genomeDir
- genome_index --readFilesIn trimmed.fastq.gz --readFilesCommand zcat --outFileNamePrefix
- output
- sample --outSAMtype BAM SortedByCoordinate
- STAR
path: .opencode/knowledge/tasks/task-0046-tool-star.md
origin_source: task
origin_page: 47
source_entry_index: 42
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: star
---

# Tool: STAR

## One-line description

Tool: STAR Purpose: Align 3′ end-seq reads to a reference genome with high precision. Input: Trimmed FASTQ file and genome index Output: Sorted BAM file Command Example: STAR --runThreadN 4 --genomeDir ./genome_index...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `task`
- Origin page: `47`
- Source entry index: `42`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0046`
- Analysis/tool category: `star`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Tool: STAR
Purpose: Align 3′ end-seq reads to a reference genome with high precision.
Input: Trimmed FASTQ file and genome index
Output: Sorted BAM file
Command Example:
  STAR --runThreadN 4 --genomeDir ./genome_index --readFilesIn trimmed.fastq.gz --readFilesCommand zcat --outFileNamePrefix ./output/sample --outSAMtype BAM SortedByCoordinate
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
