---
id: task-0076
title: '13. result_sum.sh:'
summary: '13. result_sum.sh: make a new diroctory to store all the readable result.
  Input : path to raw_plot dir, filterd_plot dir, alignment_stats report txt file,
  gene_abundance tsv file and basecall summary tsv file, a new d...'
keywords:
- result-sum
- result_sum.sh
- 13. result_sum.sh
- make a new diroctory to store all the readable result
- 'Input : path to raw_plot dir'
- filterd_plot dir
- alignment_stats report txt file
- gene_abundance tsv file and basecall summary tsv file
- a new diroctory path
- 'Usage

  Run the following in the container.

  '
- scripts
- 'result_sum.sh <dir1> <dir2> <alignment_stats> <gene_abundance> <basecall> <report_dir>

  # dir1 : path to raw_plot QC imformation dir'
- '# dir2 : path to filtered_plot QC imformation dir

  # alignment_stats : path to alignment_stats report txt file.

  # gene_abundance : path to gene_abundance tsv file.

  # basecall : path to'
- 'basecall summary tsv file. .

  # report_dir : path of new diroctory to store the results'
path: .opencode/knowledge/tasks/task-0076-13-result-sum-sh.md
origin_source: result_sum.sh
origin_page: 76
source_entry_index: 72
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: result-sum
---

# 13. result_sum.sh:

## One-line description

13. result_sum.sh: make a new diroctory to store all the readable result. Input : path to raw_plot dir, filterd_plot dir, alignment_stats report txt file, gene_abundance tsv file and basecall summary tsv file, a new d...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `result_sum.sh`
- Origin page: `76`
- Source entry index: `72`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0076`
- Analysis/tool category: `result-sum`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
13. result_sum.sh:
 make a new diroctory to store all the readable result. 
Input : path to raw_plot dir, filterd_plot dir, alignment_stats report txt file, gene_abundance tsv file and basecall summary tsv file, a new diroctory path.  
Usage
Run the following in the container.
./scripts/result_sum.sh <dir1> <dir2> <alignment_stats> <gene_abundance> <basecall> <report_dir>
# dir1 : path to raw_plot QC imformation dir 
# dir2 : path to filtered_plot QC imformation dir
# alignment_stats : path to alignment_stats report txt file.
# gene_abundance : path to gene_abundance tsv file.
# basecall : path to  basecall summary tsv file. .
# report_dir : path of new diroctory to store the results.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
