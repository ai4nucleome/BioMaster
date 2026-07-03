---
id: task-0064
title: '1. basecaller.sh:'
summary: '1. basecaller.sh: do simplex basecalling. Input : a file folder containing
  nanopore files in fast5/pod5 format Output : a bam file. Usage Run the following
  in the container ./scripts/basecaller.sh <pod5dir> <out> # po...'
keywords:
- basecaller
- basecaller.sh
- 1. basecaller.sh
- '1. basecaller.sh:

  do simplex basecalling'
- 'Input : a file folder containing nanopore files in fast5'
- 'pod5 format

  Output : a bam file.

  Usage

  Run the following in the container

  '
- scripts
- 'basecaller.sh <pod5dir> <out>

  # pod5dir: Path of a file folder containing nanopore files in fast5'
- 'pod5 format.

  # out : name of output bam file'
path: .opencode/knowledge/tasks/task-0064-1-basecaller-sh.md
origin_source: basecaller.sh
origin_page: 65
source_entry_index: 60
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: basecaller
---

# 1. basecaller.sh:

## One-line description

1. basecaller.sh: do simplex basecalling. Input : a file folder containing nanopore files in fast5/pod5 format Output : a bam file. Usage Run the following in the container ./scripts/basecaller.sh <pod5dir> <out> # po...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `basecaller.sh`
- Origin page: `65`
- Source entry index: `60`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0064`
- Analysis/tool category: `basecaller`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
1. basecaller.sh:
do simplex basecalling. 
Input : a file folder containing nanopore files in fast5/pod5 format
Output : a bam file.
Usage
Run the following in the container
./scripts/basecaller.sh <pod5dir> <out>
# pod5dir: Path of a file folder containing nanopore files in fast5/pod5 format.
# out : name of output bam file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
