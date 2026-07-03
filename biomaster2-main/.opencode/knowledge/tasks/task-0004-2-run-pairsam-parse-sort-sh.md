---
id: task-0004
title: 2. run-pairsam-parse-sort.sh
summary: '2. run-pairsam-parse-sort.sh Runs pairsam parse and sort on a bwa-produced
  bam file and produces a sorted pairsam file Input: a bam file Output: a pairsam
  file Usage Run the following in the container run-pairsam-pars...'
keywords:
- run-pairsam-parse-sort-sh-by-hic-workflow
- run-pairsam-parse-sort.sh by hic workflow
- 2. run-pairsam-parse-sort.sh
- '2. run-pairsam-parse-sort.sh

  Runs pairsam parse and sort on a bwa-produced bam file and produces a sorted pairsam
  file

  Input: a bam file

  Output: a pairsam file

  Usage

  Run the following in the container

  run-pairsam-parse-sort.sh <input_bam> <chromsizes> <outdir> <outprefix> <nthread>
  <compress_program>

  # input_bam : an input bam file.

  # chromsizes : a chromsize file

  # outdir : output directory

  # outprefix : prefix of output files

  # nthread : number of threads to use'
- 'Set parameters according to the example:

  Suppose the input file is'
- output
- aligned
- a1.bam
- and
- abc.bam
- the target is
- '003'
- pairsam_fix1.sam.pairs.gz and
- pairsam_fix2.sam.pairs.gz
- hg38.chrom.sizes
- is the a chromsize file. Generate the following sample script
- bash
- scripts
- run-pairsam-parse-sort.sh
- pairsam_fix1 64 lz4c
- pairsam_fix2 64 lz4c
- You can install the tool
- but do not do any additional operations.and 64 indicate the number of threads.Please
  follow the example to generate rather than copy and paste completely
- e
- BWA
path: .opencode/knowledge/tasks/task-0004-2-run-pairsam-parse-sort-sh.md
origin_source: run-pairsam-parse-sort.sh by hic workflow
origin_page: 9
source_entry_index: 4
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-pairsam-parse-sort-sh-by-hic-workflow
---

# 2. run-pairsam-parse-sort.sh

## One-line description

2. run-pairsam-parse-sort.sh Runs pairsam parse and sort on a bwa-produced bam file and produces a sorted pairsam file Input: a bam file Output: a pairsam file Usage Run the following in the container run-pairsam-pars...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-pairsam-parse-sort.sh by hic workflow`
- Origin page: `9`
- Source entry index: `4`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0004`
- Analysis/tool category: `run-pairsam-parse-sort-sh-by-hic-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
2. run-pairsam-parse-sort.sh
Runs pairsam parse and sort on a bwa-produced bam file and produces a sorted pairsam file
Input: a bam file
Output: a pairsam file
Usage
Run the following in the container
run-pairsam-parse-sort.sh <input_bam> <chromsizes> <outdir> <outprefix> <nthread> <compress_program>
# input_bam : an input bam file.
# chromsizes : a chromsize file
# outdir : output directory
# outprefix : prefix of output files
# nthread : number of threads to use

Set parameters according to the example:
Suppose the input file is: ./output/aligned/a1.bam  and ./output/aligned/abc.bam, the target is ./output/003/pairsam_fix1.sam.pairs.gz and ./output/003/pairsam_fix2.sam.pairs.gz . ./hg38.chrom.sizes  is the a chromsize file. Generate the following sample script:

bash ./scripts/run-pairsam-parse-sort.sh ./output/aligned/a1.bam ./hg38.chrom.sizes ./output/003/  pairsam_fix1 64 lz4c 
bash ./scripts/run-pairsam-parse-sort.sh ./output/aligned/abc.bam ./hg38.chrom.sizes ./output/003/  pairsam_fix2 64 lz4c

You can install the tool, but do not do any additional operations.and 64 indicate the number of threads.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
