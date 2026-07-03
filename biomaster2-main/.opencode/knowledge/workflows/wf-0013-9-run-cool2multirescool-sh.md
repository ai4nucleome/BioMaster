---
id: wf-0013
title: '9. run-cool2multirescool.sh:'
summary: '9. run-cool2multirescool.sh: Runs cooler coarsegrain to create multi-res
  cool file from a .cool file. Input : a cool file (.cool) Output : a multires.cool
  file (.multires.cool) Usage Run the following in the container...'
keywords:
- hic-matrix
- workflow
- 9. run-cool2multirescool.sh
- '9. run-cool2multirescool.sh:

  Runs cooler coarsegrain to create multi-res cool file from a .cool file.

  Input : a cool file (.cool)

  Output : a multires.cool file (.multires.cool)

  Usage

  Run the following in the container.

  run-cool2multirescool.sh -i <input_cool> [-p <ncores>] [-o <output_prefix>] [-c
  <chunksize>] [-j] [-u custom_res] [-B]

  # input_cool : a (single-res) cool file with the highest resolution you want in
  the multi-res cool file

  # -p ncores: number of cores to use (default: 1)

  # -o output_prefix: prefix of the output multires.cool file (default: out)

  # -c chunksize : chunksize argument of cooler (e.g. default: 10000000)

  # -j : juicer resolutions (default: use HiGlass resolutions)

  # -u custom_res : custom resolutions separated by commas (e.g. 100000'
- '200000'
- '500000). The minimum of this set must match min_res (-r).

  # -B : no balancing'
- normalizations
- cooler
path: .opencode/knowledge/workflows/wf-0013-9-run-cool2multirescool-sh.md
origin_source: workflow
origin_page: 15
source_entry_index: 5
source_subindex: 9
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: hic-matrix
---

# 9. run-cool2multirescool.sh:

## One-line description

9. run-cool2multirescool.sh: Runs cooler coarsegrain to create multi-res cool file from a .cool file. Input : a cool file (.cool) Output : a multires.cool file (.multires.cool) Usage Run the following in the container...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `15`
- Source entry index: `5`
- Source subindex: `9`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0013`
- Analysis/tool category: `hic-matrix`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
9. run-cool2multirescool.sh:
Runs cooler coarsegrain to create multi-res cool file from a .cool file.
Input : a cool file (.cool)
Output : a multires.cool file (.multires.cool)
Usage
Run the following in the container.
run-cool2multirescool.sh -i <input_cool> [-p <ncores>] [-o <output_prefix>] [-c <chunksize>] [-j] [-u custom_res] [-B]
# input_cool : a (single-res) cool file with the highest resolution you want in the multi-res cool file
# -p ncores: number of cores to use (default: 1)
# -o output_prefix: prefix of the output multires.cool file (default: out)
# -c chunksize : chunksize argument of cooler (e.g. default: 10000000)
# -j : juicer resolutions (default: use HiGlass resolutions)
# -u custom_res : custom resolutions separated by commas (e.g. 100000,200000,500000). The minimum of this set must match min_res (-r).
# -B : no balancing/normalizations
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
