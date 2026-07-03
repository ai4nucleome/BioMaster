---
id: task-0009
title: 7. run-cooler.sh
summary: '7. run-cooler.sh Runs cooler to create an unnormalized matrix .cool file,
  taking in a (4dn-style) pairs file Input : a pairs file (.gz, along with .px2),
  chrom.size file Output : a contact matrix file (.cool) Usage Ru...'
keywords:
- run-pairsam-parse-sort-sh-by-hic-workflow
- run-pairsam-parse-sort.sh by hic workflow
- 7. run-cooler.sh
- '7. run-cooler.sh

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

  run-cooler.sh <input_pairs> <chromsize> <binsize> <ncores> <output_prefix> <max_split>

  # input_pairs : a pairs file

  # chromsize : a chromsize file

  # binsize : binsize in bp

  # ncores : number of cores to use

  # output_prefix : prefix of the output cool file

  # max_split : max_split argument for cooler (e.g. 2 which is default for cooler)'
- 'Set parameters according to the example:

  Suppose the input file is'
- home
- agent
- POPGENAGENT
- sample_data
- outlala.ff.pairs.gz
- the target is
- out
- out3
- data
- hg38.chrom.sizes is the a chromsize file. Generate the following sample script
- bash
- scripts
- run-cooler.sh
- hg38.chrom.sizes
- '1000'
- '32'
- '2'
- You can install the tool
- but do not do any additional operations.Please
- cooler
path: .opencode/knowledge/tasks/task-0009-7-run-cooler-sh.md
origin_source: run-pairsam-parse-sort.sh by hic workflow
origin_page: 14
source_entry_index: 9
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-pairsam-parse-sort-sh-by-hic-workflow
---

# 7. run-cooler.sh

## One-line description

7. run-cooler.sh Runs cooler to create an unnormalized matrix .cool file, taking in a (4dn-style) pairs file Input : a pairs file (.gz, along with .px2), chrom.size file Output : a contact matrix file (.cool) Usage Ru...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-pairsam-parse-sort.sh by hic workflow`
- Origin page: `14`
- Source entry index: `9`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0009`
- Analysis/tool category: `run-pairsam-parse-sort-sh-by-hic-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
7. run-cooler.sh
Runs cooler to create an unnormalized matrix .cool file, taking in a (4dn-style) pairs file
Input : a pairs file (.gz, along with .px2), chrom.size file
Output : a contact matrix file (.cool)
Usage
Run the following in the container.
run-cooler.sh <input_pairs> `<chromsize>` `<binsize>` `<ncores>` <output_prefix> <max_split>
run-cooler.sh <input_pairs> <chromsize> <binsize> <ncores> <output_prefix> <max_split>
# input_pairs : a pairs file
# chromsize : a chromsize file
# binsize : binsize in bp
# ncores : number of cores to use
# output_prefix : prefix of the output cool file
# max_split : max_split argument for cooler (e.g. 2 which is default for cooler) 

Set parameters according to the example:
Suppose the input file is:/home/agent/POPGENAGENT/sample_data/outlala.ff.pairs.gz , the target is  ./out/out3 ,/home/agent/POPGENAGENT/data/hg38.chrom.sizes is the a chromsize file. Generate the following sample script:

bash ./scripts/run-cooler.sh      /home/agent/POPGENAGENT/sample_data/outlala.ff.pairs.gz      /home/agent/POPGENAGENT/data/hg38.chrom.sizes      1000      32      ./out/out3      2

You can install the tool, but do not do any additional operations.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.and 32 indicate the number of threads.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
