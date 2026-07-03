---
id: wf-0011
title: '7. run-cooler.sh:'
summary: '7. run-cooler.sh: Runs cooler to create an unnormalized matrix .cool file,
  taking in a (4dn-style) pairs file Input : a pairs file (.gz, along with .px2),
  chrom.size file Output : a contact matrix file (.cool) Usage R...'
keywords:
- hic-matrix
- workflow
- 7. run-cooler.sh
- '7. run-cooler.sh:

  Runs cooler to create an unnormalized matrix .cool file'
- 'taking in a (4dn-style) pairs file

  Input : a pairs file (.gz'
- along with .px2)
- 'chrom.size file

  Output : a contact matrix file (.cool)

  Usage

  Run the following in the container.

  run-cooler.sh <input_pairs> `<chromsize>` `<binsize>` `<ncores>` <output_prefix>
  <max_split>

  # input_pairs : a pairs file

  # chromsize : a chromsize file

  # binsize : binsize in bp

  # ncores : number of cores to use

  # output_prefix : prefix of the output cool file

  # max_split : max_split argument for cooler (e.g. 2 which is default for cooler)'
- cooler
path: .opencode/knowledge/workflows/wf-0011-7-run-cooler-sh.md
origin_source: workflow
origin_page: 15
source_entry_index: 5
source_subindex: 7
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: hic-matrix
---

# 7. run-cooler.sh:

## One-line description

7. run-cooler.sh: Runs cooler to create an unnormalized matrix .cool file, taking in a (4dn-style) pairs file Input : a pairs file (.gz, along with .px2), chrom.size file Output : a contact matrix file (.cool) Usage R...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `15`
- Source entry index: `5`
- Source subindex: `7`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0011`
- Analysis/tool category: `hic-matrix`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
7. run-cooler.sh:
Runs cooler to create an unnormalized matrix .cool file, taking in a (4dn-style) pairs file
Input : a pairs file (.gz, along with .px2), chrom.size file
Output : a contact matrix file (.cool)
Usage
Run the following in the container.
run-cooler.sh <input_pairs> `<chromsize>` `<binsize>` `<ncores>` <output_prefix> <max_split>
# input_pairs : a pairs file
# chromsize : a chromsize file
# binsize : binsize in bp
# ncores : number of cores to use
# output_prefix : prefix of the output cool file
# max_split : max_split argument for cooler (e.g. 2 which is default for cooler)
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
