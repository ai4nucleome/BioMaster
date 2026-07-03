---
id: wf-0050
title: '2. indexbam.sh:'
summary: '2. indexbam.sh: index bam and generate statistics - coverage, error rate,
  number of reads. Input: a sam file Output: a sorted bam file Usage Run the following
  in the container ./scripts/indexbam.sh <nthread> <input_sa...'
keywords:
- workflow
- 2. indexbam.sh
- '2. indexbam.sh:

  index bam and generate statistics - coverage'
- error rate
- 'number of reads.

  Input: a sam file

  Output: a sorted bam file

  Usage

  Run the following in the container

  '
- scripts
- 'indexbam.sh <nthread> <input_sam> <outputbam>

  # nthread : number of threads to use

  # input_sam : an input sam file

  # outputbam : name of output bam file'
path: .opencode/knowledge/workflows/wf-0050-2-indexbam-sh.md
origin_source: workflow
origin_page: 51
source_entry_index: 41
source_subindex: 2
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: workflow
---

# 2. indexbam.sh:

## One-line description

2. indexbam.sh: index bam and generate statistics - coverage, error rate, number of reads. Input: a sam file Output: a sorted bam file Usage Run the following in the container ./scripts/indexbam.sh <nthread> <input_sa...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `51`
- Source entry index: `41`
- Source subindex: `2`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0050`
- Analysis/tool category: `workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
2. indexbam.sh:
index bam and generate statistics - coverage, error rate, number of reads.
Input: a sam file
Output: a sorted bam file
Usage
Run the following in the container
./scripts/indexbam.sh <nthread> <input_sam> <outputbam>
# nthread : number of threads to use
# input_sam : an input sam file
# outputbam : name of output bam file
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
