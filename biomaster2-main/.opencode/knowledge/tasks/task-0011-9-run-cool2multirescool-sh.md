---
id: task-0011
title: 9. run-cool2multirescool.sh
summary: '9. run-cool2multirescool.sh Runs cooler coarsegrain to create multi-res
  cool file from a .cool file. Input : a cool file (.cool) Output : a multires.cool
  file (.multires.cool) Usage Run the following in the container....'
keywords:
- run-pairsam-parse-sort-sh-by-hic-workflow
- run-pairsam-parse-sort.sh by hic workflow
- 9. run-cool2multirescool.sh
- '9. run-cool2multirescool.sh

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
- 'Set parameters according to the example:

  Suppose the input file is'
- output
- '003'
- cool_prefix_normalized.cool
- the target is
- multirescool_prefix.mcool. Generate the following sample script
- bash
- scripts
- run-cool2multirescool.sh -i
- cool_prefix_normalized.cool -p 8 -o
- multirescool_prefix -c
- cooler
path: .opencode/knowledge/tasks/task-0011-9-run-cool2multirescool-sh.md
origin_source: run-pairsam-parse-sort.sh by hic workflow
origin_page: 16
source_entry_index: 11
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-pairsam-parse-sort-sh-by-hic-workflow
---

# 9. run-cool2multirescool.sh

## One-line description

9. run-cool2multirescool.sh Runs cooler coarsegrain to create multi-res cool file from a .cool file. Input : a cool file (.cool) Output : a multires.cool file (.multires.cool) Usage Run the following in the container....

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-pairsam-parse-sort.sh by hic workflow`
- Origin page: `16`
- Source entry index: `11`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0011`
- Analysis/tool category: `run-pairsam-parse-sort-sh-by-hic-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
9. run-cool2multirescool.sh
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

Set parameters according to the example:
Suppose the input file is: ./output/003/cool_prefix_normalized.cool , the target is ./output/003/multirescool_prefix.mcool. Generate the following sample script:

bash ./scripts/run-cool2multirescool.sh -i ./output/003/cool_prefix_normalized.cool -p 8 -o ./output/003/multirescool_prefix -c 10000000 -j -u 100000,200000,500000

You can install the tool, but do not do any additional operations.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.and 64 indicate the number of threads.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
