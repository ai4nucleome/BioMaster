---
id: task-0006
title: 4. run-pairsam-markasdup.sh
summary: '4. run-pairsam-markasdup.sh Takes a pairsam file in and creates a pairsam
  file with duplicate reads marked * Input: a pairsam file * Output: a duplicate-marked
  pairsam file Usage Run the following in the container run...'
keywords:
- run-pairsam-parse-sort-sh-by-hic-workflow
- run-pairsam-parse-sort.sh by hic workflow
- 4. run-pairsam-markasdup.sh
- '4. run-pairsam-markasdup.sh

  Takes a pairsam file in and creates a pairsam file with duplicate reads marked

  * Input: a pairsam file

  * Output: a duplicate-marked pairsam file

  Usage

  Run the following in the container

  run-pairsam-markasdup.sh <input_pairsam>

  # input_pairsam : an input pairsam file.

  # outprefix : prefix of output files'
- 'Set parameters according to the example:

  Suppose the input file is'
- output
- '003'
- out.merged.sam.pairs.gz
- the target is
- out1
- Generate the following sample script
- bash
- scripts
- run-pairsam-markasdup.sh
- You can install the tool
- but do not do any additional operations.Please follow the example to generate rather
  than copy and paste completely
- especially for folder names
- file names
- etc.and 64 indicate the number of threads
path: .opencode/knowledge/tasks/task-0006-4-run-pairsam-markasdup-sh.md
origin_source: run-pairsam-parse-sort.sh by hic workflow
origin_page: 11
source_entry_index: 6
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-pairsam-parse-sort-sh-by-hic-workflow
---

# 4. run-pairsam-markasdup.sh

## One-line description

4. run-pairsam-markasdup.sh Takes a pairsam file in and creates a pairsam file with duplicate reads marked * Input: a pairsam file * Output: a duplicate-marked pairsam file Usage Run the following in the container run...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-pairsam-parse-sort.sh by hic workflow`
- Origin page: `11`
- Source entry index: `6`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0006`
- Analysis/tool category: `run-pairsam-parse-sort-sh-by-hic-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
4. run-pairsam-markasdup.sh
Takes a pairsam file in and creates a pairsam file with duplicate reads marked
* Input: a pairsam file
* Output: a duplicate-marked pairsam file
Usage
Run the following in the container
run-pairsam-markasdup.sh <input_pairsam>
# input_pairsam : an input pairsam file.
# outprefix : prefix of output files

Set parameters according to the example:
Suppose the input file is:  ./output/003/out.merged.sam.pairs.gz,the target is ./output/003/out1.  Generate the following sample script:

bash ./scripts/run-pairsam-markasdup.sh  ./output/003/out.merged.sam.pairs.gz  ./output/003/out1  

You can install the tool, but do not do any additional operations.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.and 64 indicate the number of threads.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
