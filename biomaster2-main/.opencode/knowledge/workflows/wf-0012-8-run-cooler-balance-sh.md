---
id: wf-0012
title: '8. run-cooler-balance.sh:'
summary: '8. run-cooler-balance.sh: Runs cooler to create a normalized matrix file,
  taking in an unnormalized .cool file Input: a cool file (.cool) Output : a cool
  file (.cool) Usage Run the following in the container. run-cool...'
keywords:
- hic-matrix
- workflow
- 8. run-cooler-balance.sh
- '8. run-cooler-balance.sh:

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
- cooler
path: .opencode/knowledge/workflows/wf-0012-8-run-cooler-balance-sh.md
origin_source: workflow
origin_page: 15
source_entry_index: 5
source_subindex: 8
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: hic-matrix
---

# 8. run-cooler-balance.sh:

## One-line description

8. run-cooler-balance.sh: Runs cooler to create a normalized matrix file, taking in an unnormalized .cool file Input: a cool file (.cool) Output : a cool file (.cool) Usage Run the following in the container. run-cool...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `15`
- Source entry index: `5`
- Source subindex: `8`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0012`
- Analysis/tool category: `hic-matrix`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
8. run-cooler-balance.sh:
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
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
