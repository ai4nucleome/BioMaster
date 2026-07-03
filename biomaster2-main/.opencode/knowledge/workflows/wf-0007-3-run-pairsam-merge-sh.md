---
id: wf-0007
title: '3. run-pairsam-merge.sh:'
summary: '3. run-pairsam-merge.sh: Merges a list of pairsam files Input: a list of
  pairsam files Output: a merged pairsam file Usage Run the following in the container
  run-pairsam-merge.sh <outprefix> <nthreads> <input_pairsam1...'
keywords:
- hic-matrix
- workflow
- 3. run-pairsam-merge.sh
- '3. run-pairsam-merge.sh:

  Merges a list of pairsam files

  Input: a list of pairsam files

  Output: a merged pairsam file

  Usage

  Run the following in the container

  run-pairsam-merge.sh <outprefix> <nthreads> <input_pairsam1> [<input_pairsam2> [<input_pairsam3>
  [...]]]

  # outprefix : prefix of output files

  # nthreads : number of threads to use

  # input_pairsam : an input pairsam file'
path: .opencode/knowledge/workflows/wf-0007-3-run-pairsam-merge-sh.md
origin_source: workflow
origin_page: 15
source_entry_index: 5
source_subindex: 3
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: hic-matrix
---

# 3. run-pairsam-merge.sh:

## One-line description

3. run-pairsam-merge.sh: Merges a list of pairsam files Input: a list of pairsam files Output: a merged pairsam file Usage Run the following in the container run-pairsam-merge.sh <outprefix> <nthreads> <input_pairsam1...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `15`
- Source entry index: `5`
- Source subindex: `3`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0007`
- Analysis/tool category: `hic-matrix`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
3. run-pairsam-merge.sh:
Merges a list of pairsam files
Input: a list of pairsam files
Output: a merged pairsam file
Usage
Run the following in the container
run-pairsam-merge.sh <outprefix> <nthreads> <input_pairsam1> [<input_pairsam2> [<input_pairsam3> [...]]]
# outprefix : prefix of output files
# nthreads : number of threads to use
# input_pairsam : an input pairsam file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
