---
id: task-0055
title: Before performing nanopore data process (except for modification identification,
  for example, ide...
summary: Before performing nanopore data process (except for modification identification,
  for example, identifying methylation) from nanopore files. If basecalling file (fastq/bam)
  is not supplied, firstly using basecaller.sh...
keywords:
- dorado
- Before performing nanopore data process (except for modification identification
- for example
- ide
- identifying methylation) from nanopore files. If basecalling file (fastq
- bam) is not supplied
- 'firstly using basecaller.sh command to do simplex basecalling to generate basecalling
  file before other steps.

  Input : a file folder containing nanopore files in fast5'
- 'pod5 format and a reference genome fa file

  Output : a bam file.

  Usage

  Run the following in the container

  '
- scripts
- 'basecaller.sh <pod5dir> <out>

  # pod5dir: Path of a file folder containing nanopore files in fast5'
- 'pod5 format.

  # out : name of output bam file'
path: .opencode/knowledge/tasks/task-0055-before-performing-nanopore-data-process-except-for-modification-identification-for-example-ide.md
origin_source: dorado
origin_page: 56
source_entry_index: 51
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: dorado
---

# Before performing nanopore data process (except for modification identification, for example, ide...

## One-line description

Before performing nanopore data process (except for modification identification, for example, identifying methylation) from nanopore files. If basecalling file (fastq/bam) is not supplied, firstly using basecaller.sh...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `dorado`
- Origin page: `56`
- Source entry index: `51`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0055`
- Analysis/tool category: `dorado`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Before performing nanopore data process (except for modification identification, for example, identifying methylation) from nanopore files. If basecalling file (fastq/bam) is not supplied, firstly using basecaller.sh command to do simplex basecalling to generate basecalling file before other steps.
Input : a file folder containing nanopore files in fast5/pod5 format and a reference genome fa file
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
