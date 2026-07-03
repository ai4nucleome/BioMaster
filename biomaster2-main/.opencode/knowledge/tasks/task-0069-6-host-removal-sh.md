---
id: task-0069
title: '6. host_removal.sh:'
summary: '6. host_removal.sh: remove host gene in filtered fastq file. Input : filtered
  fastq file Output : a bam file. Usage Run the following in the container ./scripts/host_removal.sh
  <fa> <fastq> <out> # fa: host gene fasta...'
keywords:
- host-removal
- host_removal.sh
- 6. host_removal.sh
- 'remove host gene in filtered fastq file.

  Input : filtered fastq file'
- 'Output : a bam file.

  Usage

  Run the following in the container

  '
- scripts
- host_removal.sh <fa> <fastq> <out>
- '# fa'
- 'host gene fasta file.

  # fastq : filtered fastq file.

  # out : name of output bam file'
path: .opencode/knowledge/tasks/task-0069-6-host-removal-sh.md
origin_source: host_removal.sh
origin_page: 69
source_entry_index: 65
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: host-removal
---

# 6. host_removal.sh:

## One-line description

6. host_removal.sh: remove host gene in filtered fastq file. Input : filtered fastq file Output : a bam file. Usage Run the following in the container ./scripts/host_removal.sh <fa> <fastq> <out> # fa: host gene fasta...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `host_removal.sh`
- Origin page: `69`
- Source entry index: `65`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0069`
- Analysis/tool category: `host-removal`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
6. host_removal.sh:
 remove host gene in filtered fastq file.
Input : filtered fastq file 
Output : a bam file.
Usage
Run the following in the container
./scripts/host_removal.sh <fa> <fastq> <out>  # fa:  host gene fasta file.
# fastq : filtered fastq file.
# out : name of output bam file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
