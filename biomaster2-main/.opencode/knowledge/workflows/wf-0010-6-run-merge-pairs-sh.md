---
id: wf-0010
title: '6. run-merge-pairs.sh:'
summary: '6. run-merge-pairs.sh: Alignment module for Hi-C data, based on merge-pairs.
  Input : a set of pairs files, with their associated indices Output : a merged pairs
  file and its index Usage Run the following in the contai...'
keywords:
- hic-matrix
- workflow
- 6. run-merge-pairs.sh
- '6. run-merge-pairs.sh:

  Alignment module for Hi-C data'
- 'based on merge-pairs.

  Input : a set of pairs files'
- 'with their associated indices

  Output : a merged pairs file and its index

  Usage

  Run the following in the container.

  run-merge-pairs.sh <output_prefix> <pairs1> <pairs2> [<pairs3> [...]]

  # output_prefix : prefix of the output pairs file.

  # pairs1'
- pairs2
- input pairs files
path: .opencode/knowledge/workflows/wf-0010-6-run-merge-pairs-sh.md
origin_source: workflow
origin_page: 15
source_entry_index: 5
source_subindex: 6
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: hic-matrix
---

# 6. run-merge-pairs.sh:

## One-line description

6. run-merge-pairs.sh: Alignment module for Hi-C data, based on merge-pairs. Input : a set of pairs files, with their associated indices Output : a merged pairs file and its index Usage Run the following in the contai...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `15`
- Source entry index: `5`
- Source subindex: `6`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0010`
- Analysis/tool category: `hic-matrix`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
6. run-merge-pairs.sh:
Alignment module for Hi-C data, based on merge-pairs.
Input : a set of pairs files, with their associated indices
Output : a merged pairs file and its index
Usage
Run the following in the container.
run-merge-pairs.sh <output_prefix> <pairs1> <pairs2> [<pairs3> [...]]
# output_prefix : prefix of the output pairs file.
# pairs1, pairs2, ... : input pairs files
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
