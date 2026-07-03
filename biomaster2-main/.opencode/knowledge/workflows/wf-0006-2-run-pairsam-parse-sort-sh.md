---
id: wf-0006
title: '2. run-pairsam-parse-sort.sh:'
summary: '2. run-pairsam-parse-sort.sh: Runs pairsam parse and sort on a bwa-produced
  bam file and produces a sorted pairsam file Input: a bam file Output: a pairsam
  file Usage Run the following in the container run-pairsam-par...'
keywords:
- hic-matrix
- workflow
- 2. run-pairsam-parse-sort.sh
- '2. run-pairsam-parse-sort.sh:

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
- BWA
path: .opencode/knowledge/workflows/wf-0006-2-run-pairsam-parse-sort-sh.md
origin_source: workflow
origin_page: 15
source_entry_index: 5
source_subindex: 2
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: hic-matrix
---

# 2. run-pairsam-parse-sort.sh:

## One-line description

2. run-pairsam-parse-sort.sh: Runs pairsam parse and sort on a bwa-produced bam file and produces a sorted pairsam file Input: a bam file Output: a pairsam file Usage Run the following in the container run-pairsam-par...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `15`
- Source entry index: `5`
- Source subindex: `2`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0006`
- Analysis/tool category: `hic-matrix`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
2. run-pairsam-parse-sort.sh:
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
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
