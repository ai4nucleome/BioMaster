---
id: task-0010
title: 8. run-cooler-balance.sh
summary: '8. run-cooler-balance.sh Runs cooler to create a normalized matrix file,
  taking in an unnormalized .cool file Input: a cool file (.cool) Output : a cool
  file (.cool) Usage Run the following in the container. run-coole...'
keywords:
- run-pairsam-parse-sort-sh-by-hic-workflow
- run-pairsam-parse-sort.sh by hic workflow
- 8. run-cooler-balance.sh
- '8. run-cooler-balance.sh

  Runs cooler to create a normalized matrix file'
- 'taking in an unnormalized .cool file

  Input: a cool file (.cool)

  Output : a cool file (.cool)

  Usage

  Run the following in the container.

  run-cooler-balance.sh <input_cool> <max_iter> <output_prefix> <chunksize>

  # input_cool : a cool file (without normalization vector)

  # max_iter : maximum number of iterations

  # output_prefix : prefix of the output cool file

  # chunksize : chunksize argument for cooler (e.g. 10000000 which is default for
  cooler)'
- 'Set parameters according to the example:

  Suppose the input file is'
- output
- '003'
- cool_prefix.cool
- the target is
- cool_prefix_normalized.cool
- home
- agent
- POPGENAGENT
- data
- hg38.chrom.sizes is the a chromsize file. Generate the following sample script
- bash
- scripts
- run-cooler-balance.sh
- cool_prefix.cool 1000
- cool_prefix_normalized 10000000
- You can install the tool
- but do not do any additional operations.Please follow the example to generate rather
  than copy and paste completely
- especially for folder names
- file names
- etc.and 64 indicate the number of threads
- cooler
path: .opencode/knowledge/tasks/task-0010-8-run-cooler-balance-sh.md
origin_source: run-pairsam-parse-sort.sh by hic workflow
origin_page: 15
source_entry_index: 10
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-pairsam-parse-sort-sh-by-hic-workflow
---

# 8. run-cooler-balance.sh

## One-line description

8. run-cooler-balance.sh Runs cooler to create a normalized matrix file, taking in an unnormalized .cool file Input: a cool file (.cool) Output : a cool file (.cool) Usage Run the following in the container. run-coole...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-pairsam-parse-sort.sh by hic workflow`
- Origin page: `15`
- Source entry index: `10`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0010`
- Analysis/tool category: `run-pairsam-parse-sort-sh-by-hic-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
8. run-cooler-balance.sh
Runs cooler to create a normalized matrix file, taking in an unnormalized .cool file
Input: a cool file (.cool)
Output : a cool file (.cool)
Usage
Run the following in the container.
run-cooler-balance.sh <input_cool> <max_iter> <output_prefix> <chunksize>
# input_cool : a cool file (without normalization vector)
# max_iter : maximum number of iterations
# output_prefix : prefix of the output cool file
# chunksize : chunksize argument for cooler (e.g. 10000000 which is default for cooler)

Set parameters according to the example:
Suppose the input file is: ./output/003/cool_prefix.cool , the target is ./output/003/cool_prefix_normalized.cool,/home/agent/POPGENAGENT/data/hg38.chrom.sizes is the a chromsize file. Generate the following sample script:

bash ./scripts/run-cooler-balance.sh ./output/003/cool_prefix.cool 1000 ./output/003/cool_prefix_normalized 10000000

You can install the tool, but do not do any additional operations.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.and 64 indicate the number of threads.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
