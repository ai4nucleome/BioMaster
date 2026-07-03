---
id: task-0058
title: '2. indexbam.sh:'
summary: '2. indexbam.sh: index bam and generate statistics - coverage, error rate,
  number of reads. Input: a sam file Output: a sorted bam file Usage Run the following
  in the container ./scripts/indexbam.sh <nthread> <input_sa...'
keywords:
- indexbam
- indexbam.sh
- 2. indexbam.sh
- '2. indexbam.sh:

  index bam and generate statistics - coverage'
- error rate
- 'number of reads.

  Input: a sam file

  Output: a sorted bam file

  Usage

  Run the following in the container

  '
- scripts
- 'indexbam.sh <nthread> <input_sam> <outputbam>

  # nthread : number of threads to use

  # input_sam : an input sam file

  # outputbam : name of output bam file'
path: .opencode/knowledge/tasks/task-0058-2-indexbam-sh.md
origin_source: indexbam.sh
origin_page: 59
source_entry_index: 54
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: indexbam
---

# 2. indexbam.sh:

## One-line description

2. indexbam.sh: index bam and generate statistics - coverage, error rate, number of reads. Input: a sam file Output: a sorted bam file Usage Run the following in the container ./scripts/indexbam.sh <nthread> <input_sa...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `indexbam.sh`
- Origin page: `59`
- Source entry index: `54`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0058`
- Analysis/tool category: `indexbam`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
2. indexbam.sh:
index bam and generate statistics - coverage, error rate, number of reads.
Input: a sam file
Output: a sorted bam file
Usage
Run the following in the container
./scripts/indexbam.sh <nthread> <input_sam> <outputbam>
# nthread : number of threads to use
# input_sam : an input sam file
# outputbam : name of output bam file
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
