---
id: task-0008
title: 6. run-merge-pairs.sh
summary: '6. run-merge-pairs.sh Alignment module for Hi-C data, based on merge-pairs.
  Input : a set of pairs files, with their associated indices Output : a merged pairs
  file and its index Usage Run the following in the contain...'
keywords:
- run-pairsam-parse-sort-sh-by-hic-workflow
- run-pairsam-parse-sort.sh by hic workflow
- 6. run-merge-pairs.sh
- '6. run-merge-pairs.sh

  Alignment module for Hi-C data'
- based on merge-pairs
- 'Input : a set of pairs files'
- 'with their associated indices

  Output : a merged pairs file and its index

  Usage

  Run the following in the container.

  run-merge-pairs.sh <output_prefix> <pairs1> <pairs2> [<pairs3> [...]]'
- '# output_prefix : prefix of the output pairs file.

  # pairs1'
- pairs2
- input pairs files
- 'Set parameters according to the example:

  Suppose the input file is'
- out
- out12345.dedup.pairs.gz
- the target is
- out321.pairs.gz. Generate the following sample script
- bash
- scripts
- run-merge-pairs.sh
- out321
- You can install the tool
- but do not do any additional operations. Please follow the example to generate rather
  than copy and paste completely
- especially for folder names
- file names
- etc
path: .opencode/knowledge/tasks/task-0008-6-run-merge-pairs-sh.md
origin_source: run-pairsam-parse-sort.sh by hic workflow
origin_page: 13
source_entry_index: 8
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-pairsam-parse-sort-sh-by-hic-workflow
---

# 6. run-merge-pairs.sh

## One-line description

6. run-merge-pairs.sh Alignment module for Hi-C data, based on merge-pairs. Input : a set of pairs files, with their associated indices Output : a merged pairs file and its index Usage Run the following in the contain...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-pairsam-parse-sort.sh by hic workflow`
- Origin page: `13`
- Source entry index: `8`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0008`
- Analysis/tool category: `run-pairsam-parse-sort-sh-by-hic-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
6. run-merge-pairs.sh
Alignment module for Hi-C data, based on merge-pairs.

Input : a set of pairs files, with their associated indices
Output : a merged pairs file and its index
Usage
Run the following in the container.
run-merge-pairs.sh <output_prefix> <pairs1> <pairs2> [<pairs3> [...]]  
# output_prefix : prefix of the output pairs file.
# pairs1, pairs2, ... : input pairs files

Set parameters according to the example:
Suppose the input file is: ./out/out12345.dedup.pairs.gz, the target is ./out/out321.pairs.gz. Generate the following sample script:

bash ./scripts/run-merge-pairs.sh ./out/out321 ./out/out12345.dedup.pairs.gz

You can install the tool, but do not do any additional operations. Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
