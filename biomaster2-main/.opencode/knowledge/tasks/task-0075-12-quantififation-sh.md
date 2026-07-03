---
id: task-0075
title: '12. quantififation.sh:'
summary: '12. quantififation.sh: Generate transcripts and gene_abundance tsv file
  from the sorted bam file. Input : the sorted bam file Output : a transcripts gtf
  file and a gene_abundance tsv file. Usage Run the following in t...'
keywords:
- quantififation
- quantififation.sh
- 12. quantififation.sh
- '12. quantififation.sh:

  Generate transcripts and'
- 'gene_abundance tsv file from the sorted bam file.

  Input : the sorted bam file

  Output : a transcripts gtf file and a gene_abundance tsv file'
- 'Usage

  Run the following in the container.

  '
- scripts
- quantififation.sh <bam> <transcripts_gtf> <out>
- '# bam'
- the sorted bam file
- '# transcripts_gtf'
- 'name of output transcripts gtf file.

  # out : name of output gene_abundance tsv file'
path: .opencode/knowledge/tasks/task-0075-12-quantififation-sh.md
origin_source: quantififation.sh
origin_page: 75
source_entry_index: 71
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: quantififation
---

# 12. quantififation.sh:

## One-line description

12. quantififation.sh: Generate transcripts and gene_abundance tsv file from the sorted bam file. Input : the sorted bam file Output : a transcripts gtf file and a gene_abundance tsv file. Usage Run the following in t...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `quantififation.sh`
- Origin page: `75`
- Source entry index: `71`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0075`
- Analysis/tool category: `quantififation`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
12. quantififation.sh:
Generate transcripts and  gene_abundance tsv file from the sorted bam file.
Input : the sorted bam file
Output : a transcripts gtf file and a gene_abundance tsv file. 
Usage
Run the following in the container.
./scripts/quantififation.sh <bam> <transcripts_gtf> <out> 
# bam :  the sorted bam file. 
# transcripts_gtf :  name of output transcripts gtf file.
# out : name of output gene_abundance tsv file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
