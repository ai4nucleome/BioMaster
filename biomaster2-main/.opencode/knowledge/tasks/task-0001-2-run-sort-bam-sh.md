---
id: task-0001
title: '2. run-sort-bam.sh:'
summary: '2. run-sort-bam.sh: Data-type-independent, generic bam sorting module Input
  : any unsorted bam file (.bam) Output : a bam file sorted by coordinate (.sorted.bam)
  and its index (.sorted.bam.bai). Usage Run the followin...'
keywords:
- run-sort-bam
- run-sort-bam.sh
- 2. run-sort-bam.sh
- '2. run-sort-bam.sh:

  Data-type-independent'
- 'generic bam sorting module

  Input : any unsorted bam file (.bam)

  Output : a bam file sorted by coordinate (.sorted.bam) and its index (.sorted.bam.bai).

  Usage

  Run the following in the container.

  run-sort-bam.sh <input_bam> <output_prefix>

  # input_bam : any bam file to be sorted

  # output_prefix : prefix of the output bam file'
- 'Set parameters according to the example: Suppose the input file is'
- output
- GM12878_bwa_1.bam and
- GM12878_bwa_2.bam
- the target is
- GM12878_bwa_sorted.bam and
- GM12878_bwa_sorted
- 'Generate the following sample script:

  bash'
- scripts
- GM12878_bwa_1.bam
- bash
- You can install the tool
- but do not do any additional operations.You can install the tool
- but do not do any additional operations.Please follow the example to generate rather
  than copy and paste completely
- especially for folder names
- file names
- etc
path: .opencode/knowledge/tasks/task-0001-2-run-sort-bam-sh.md
origin_source: run-sort-bam.sh
origin_page: 6
source_entry_index: 1
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-sort-bam
---

# 2. run-sort-bam.sh:

## One-line description

2. run-sort-bam.sh: Data-type-independent, generic bam sorting module Input : any unsorted bam file (.bam) Output : a bam file sorted by coordinate (.sorted.bam) and its index (.sorted.bam.bai). Usage Run the followin...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-sort-bam.sh`
- Origin page: `6`
- Source entry index: `1`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0001`
- Analysis/tool category: `run-sort-bam`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
2. run-sort-bam.sh:
Data-type-independent, generic bam sorting module
Input : any unsorted bam file (.bam)
Output : a bam file sorted by coordinate (.sorted.bam) and its index (.sorted.bam.bai).
Usage
Run the following in the container.
run-sort-bam.sh <input_bam> <output_prefix>
# input_bam : any bam file to be sorted
# output_prefix : prefix of the output bam file.

Set parameters according to the example: Suppose the input file is: ./output/GM12878_bwa_1.bam and ./output/GM12878_bwa_2.bam, the target is./output/GM12878_bwa_sorted.bam and ./output/GM12878_bwa_sorted, Generate the following sample script:
bash ./scripts/run-sort-bam.sh ./output/GM12878_bwa_1.bam ./output/GM12878_bwa_sorted 

bash ./scripts/run-sort-bam.sh ./output/GM12878_bwa_2.bam ./output/GM12878_bwa_sorted

You can install the tool, but do not do any additional operations.You can install the tool, but do not do any additional operations.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
