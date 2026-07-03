---
id: wf-0009
title: '5. run-pairsam-filter.sh:'
summary: '5. run-pairsam-filter.sh: Takes in a pairsam file and creates a lossless,
  annotated bam file and a filtered pairs file. Input: a pairsam file Output: an annotated
  bam file and a filtered pairs file Usage Run the follo...'
keywords:
- hic-matrix
- workflow
- 5. run-pairsam-filter.sh
- '5. run-pairsam-filter.sh:

  Takes in a pairsam file and creates a lossless'
- 'annotated bam file and a filtered pairs file.

  Input: a pairsam file

  Output: an annotated bam file and a filtered pairs file

  Usage

  Run the following in the container

  run-pairsam-filter.sh <input_pairsam> <outprefix> <chromsizes>

  # input_pairsam : an input pairsam file.

  # outprefix : prefix of output files

  # chromsizes : a chromsize file'
path: .opencode/knowledge/workflows/wf-0009-5-run-pairsam-filter-sh.md
origin_source: workflow
origin_page: 15
source_entry_index: 5
source_subindex: 5
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: hic-matrix
---

# 5. run-pairsam-filter.sh:

## One-line description

5. run-pairsam-filter.sh: Takes in a pairsam file and creates a lossless, annotated bam file and a filtered pairs file. Input: a pairsam file Output: an annotated bam file and a filtered pairs file Usage Run the follo...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `15`
- Source entry index: `5`
- Source subindex: `5`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0009`
- Analysis/tool category: `hic-matrix`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
5. run-pairsam-filter.sh:
Takes in a pairsam file and creates a lossless, annotated bam file and a filtered pairs file.
Input: a pairsam file
Output: an annotated bam file and a filtered pairs file
Usage
Run the following in the container
run-pairsam-filter.sh <input_pairsam> <outprefix> <chromsizes>
# input_pairsam : an input pairsam file.
# outprefix : prefix of output files
# chromsizes : a chromsize file
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
