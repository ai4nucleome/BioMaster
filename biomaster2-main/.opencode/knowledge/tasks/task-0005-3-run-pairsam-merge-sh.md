---
id: task-0005
title: 3. run-pairsam-merge.sh
summary: '3. run-pairsam-merge.sh Merges a list of pairsam files Input: a list of
  pairsam files Output: a merged pairsam file Usage Run the following in the container
  run-pairsam-merge.sh <outprefix> <nthreads> <input_pairsam1>...'
keywords:
- run-pairsam-parse-sort-sh-by-hic-workflow
- run-pairsam-parse-sort.sh by hic workflow
- 3. run-pairsam-merge.sh
- '3. run-pairsam-merge.sh

  Merges a list of pairsam files

  Input: a list of pairsam files

  Output: a merged pairsam file

  Usage

  Run the following in the container

  run-pairsam-merge.sh <outprefix> <nthreads> <input_pairsam1> [<input_pairsam2> [<input_pairsam3>
  [...]]]

  # outprefix : prefix of output files

  # nthreads : number of threads to use'
- '# input_pairsam : an input pairsam file'
- 'Set parameters according to the example:

  Suppose the input file is'
- output
- '003'
- pairsam_fix1.sam.pairs.gz
- and
- pairsam_fix2.sam.pairs.gz
- the target is
- out.merged.sam.pairs.gz . Generate the following sample script
- bash
- scripts
- run-pairsam-merge.sh
- out 64 '
- pairsam_fix2.sam.pairs.gz'
- You can install the tool
- but do not do any additional operations.Please follow the example to generate rather
  than copy and paste completely
- especially for folder names
- file names
- etc.and 64 indicate the number of threads
path: .opencode/knowledge/tasks/task-0005-3-run-pairsam-merge-sh.md
origin_source: run-pairsam-parse-sort.sh by hic workflow
origin_page: 10
source_entry_index: 5
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-pairsam-parse-sort-sh-by-hic-workflow
---

# 3. run-pairsam-merge.sh

## One-line description

3. run-pairsam-merge.sh Merges a list of pairsam files Input: a list of pairsam files Output: a merged pairsam file Usage Run the following in the container run-pairsam-merge.sh <outprefix> <nthreads> <input_pairsam1>...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-pairsam-parse-sort.sh by hic workflow`
- Origin page: `10`
- Source entry index: `5`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0005`
- Analysis/tool category: `run-pairsam-parse-sort-sh-by-hic-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
3. run-pairsam-merge.sh
Merges a list of pairsam files
Input: a list of pairsam files
Output: a merged pairsam file
Usage
Run the following in the container
run-pairsam-merge.sh <outprefix> <nthreads> <input_pairsam1> [<input_pairsam2> [<input_pairsam3> [...]]]
# outprefix : prefix of output files
# nthreads : number of threads to use   
# input_pairsam : an input pairsam file.

Set parameters according to the example:
Suppose the input file is: ./output/003/pairsam_fix1.sam.pairs.gz  and ./output/003/pairsam_fix2.sam.pairs.gz, the target is ./output/003/out.merged.sam.pairs.gz . Generate the following sample script:

bash ./scripts/run-pairsam-merge.sh ./output/003/out 64 './output/003/pairsam_fix1.sam.pairs.gz ./output/003/pairsam_fix2.sam.pairs.gz' 

You can install the tool, but do not do any additional operations.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.and 64 indicate the number of threads.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
