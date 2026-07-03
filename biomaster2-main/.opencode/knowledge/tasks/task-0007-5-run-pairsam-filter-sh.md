---
id: task-0007
title: 5. run-pairsam-filter.sh
summary: '5. run-pairsam-filter.sh Takes in a pairsam file and creates a lossless,
  annotated bam file and a filtered pairs file. Input: a pairsam file Output: an annotated
  bam file and a filtered pairs file Usage Run the follow...'
keywords:
- run-pairsam-parse-sort-sh-by-hic-workflow
- run-pairsam-parse-sort.sh by hic workflow
- 5. run-pairsam-filter.sh
- '5. run-pairsam-filter.sh

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
- 'Set parameters according to the example:

  Suppose the input file is'
- sample_data
- outlala.merged.sam.pairs.gz
- the target is
- out
- out12345.dedup.pairs.gz and
- out12345.lossless.bam
- home
- agent
- POPGENAGENT
- data
- hg38.chrom.sizes is the a chromsize file. Generate the following sample script
- bash
- scripts
- run-pairsam-filter.sh
- out12345
- hg38.chrom.sizes
- You can install the tool
- but do not do any additional operations.Please follow the example to generate rather
  than copy and paste completely
- especially for folder names
- file names
- etc
path: .opencode/knowledge/tasks/task-0007-5-run-pairsam-filter-sh.md
origin_source: run-pairsam-parse-sort.sh by hic workflow
origin_page: 12
source_entry_index: 7
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-pairsam-parse-sort-sh-by-hic-workflow
---

# 5. run-pairsam-filter.sh

## One-line description

5. run-pairsam-filter.sh Takes in a pairsam file and creates a lossless, annotated bam file and a filtered pairs file. Input: a pairsam file Output: an annotated bam file and a filtered pairs file Usage Run the follow...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-pairsam-parse-sort.sh by hic workflow`
- Origin page: `12`
- Source entry index: `7`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0007`
- Analysis/tool category: `run-pairsam-parse-sort-sh-by-hic-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
5. run-pairsam-filter.sh
Takes in a pairsam file and creates a lossless, annotated bam file and a filtered pairs file.
Input: a pairsam file
Output: an annotated bam file and a filtered pairs file
Usage
Run the following in the container
run-pairsam-filter.sh <input_pairsam> <outprefix> <chromsizes>
# input_pairsam : an input pairsam file.
# outprefix : prefix of output files
# chromsizes : a chromsize file

Set parameters according to the example:
Suppose the input file is: ../sample_data/outlala.merged.sam.pairs.gz, the target is  ./out/out12345.dedup.pairs.gz and ./out/out12345.lossless.bam ,/home/agent/POPGENAGENT/data/hg38.chrom.sizes is the a chromsize file. Generate the following sample script:

bash ./scripts/run-pairsam-filter.sh  ./sample_data/outlala.merged.sam.pairs.gz ./out/out12345  /home/agent/POPGENAGENT/data/hg38.chrom.sizes

You can install the tool, but do not do any additional operations.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
