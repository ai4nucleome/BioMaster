---
id: task-0061
title: '1. methy_iden.sh:'
summary: '1. methy_iden.sh: Do modified basecalling from nanopore pod5 files. Input
  : a file folder containing nanopore files in fast5/pod5 format and a reference genome
  fa file Output : a bam file. Usage Run the following in t...'
keywords:
- methy-iden
- methy_iden.sh
- 1. methy_iden.sh
- Do modified basecalling from nanopore pod5 files
- 'Input : a file folder containing nanopore files in fast5'
- 'pod5 format and a reference genome fa file

  Output : a bam file.

  Usage

  Run the following in the container

  '
- scripts
- 'methy_iden.sh <pod5dir> <ref> <out>

  # pod5dir: Path of a file folder containing nanopore files in fast5'
- 'pod5 format.

  # ref : reference genome fa file

  # out : name of output bam file'
path: .opencode/knowledge/tasks/task-0061-1-methy-iden-sh.md
origin_source: methy_iden.sh
origin_page: 62
source_entry_index: 57
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: methy-iden
---

# 1. methy_iden.sh:

## One-line description

1. methy_iden.sh: Do modified basecalling from nanopore pod5 files. Input : a file folder containing nanopore files in fast5/pod5 format and a reference genome fa file Output : a bam file. Usage Run the following in t...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `methy_iden.sh`
- Origin page: `62`
- Source entry index: `57`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0061`
- Analysis/tool category: `methy-iden`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
1. methy_iden.sh:
 Do modified basecalling from nanopore pod5 files. 
Input : a file folder containing nanopore files in fast5/pod5 format and a reference genome fa file
Output : a bam file.
Usage
Run the following in the container
./scripts/methy_iden.sh <pod5dir> <ref> <out>
# pod5dir: Path of a file folder containing nanopore files in fast5/pod5 format.
# ref : reference genome fa file
# out : name of output bam file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
