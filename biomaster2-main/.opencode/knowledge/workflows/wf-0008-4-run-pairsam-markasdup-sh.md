---
id: wf-0008
title: '4. run-pairsam-markasdup.sh:'
summary: '4. run-pairsam-markasdup.sh: Takes a pairsam file in and creates a pairsam
  file with duplicate reads marked Input: a pairsam file Output: a duplicate-marked
  pairsam file Usage Run the following in the container run-pa...'
keywords:
- hic-matrix
- workflow
- 4. run-pairsam-markasdup.sh
- '4. run-pairsam-markasdup.sh:

  Takes a pairsam file in and creates a pairsam file with duplicate reads marked

  Input: a pairsam file

  Output: a duplicate-marked pairsam file

  Usage

  Run the following in the container

  run-pairsam-markasdup.sh <input_pairsam>

  # input_pairsam : an input pairsam file.

  # outprefix : prefix of output files'
path: .opencode/knowledge/workflows/wf-0008-4-run-pairsam-markasdup-sh.md
origin_source: workflow
origin_page: 15
source_entry_index: 5
source_subindex: 4
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: hic-matrix
---

# 4. run-pairsam-markasdup.sh:

## One-line description

4. run-pairsam-markasdup.sh: Takes a pairsam file in and creates a pairsam file with duplicate reads marked Input: a pairsam file Output: a duplicate-marked pairsam file Usage Run the following in the container run-pa...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `15`
- Source entry index: `5`
- Source subindex: `4`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0008`
- Analysis/tool category: `hic-matrix`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
4. run-pairsam-markasdup.sh:
Takes a pairsam file in and creates a pairsam file with duplicate reads marked
Input: a pairsam file
Output: a duplicate-marked pairsam file
Usage
Run the following in the container
run-pairsam-markasdup.sh <input_pairsam>
# input_pairsam : an input pairsam file.
# outprefix : prefix of output files
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
