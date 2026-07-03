---
id: task-0074
title: '11. alignment_stats.sh:'
summary: '11. alignment_stats.sh: Get the alignment_stats report. Input : the sorted
  bam file Output : a alignment_stats txt file Usage Run the following in the container.
  ./scripts/alignment_stats.sh <bam> <out> # bam : the so...'
keywords:
- alignment-stats
- alignment_stats.sh
- 11. alignment_stats.sh
- '11. alignment_stats.sh:

  Get the alignment_stats report.

  Input : the sorted bam file

  Output : a alignment_stats txt file'
- 'Usage

  Run the following in the container.

  '
- scripts
- alignment_stats.sh <bam> <out>
- '# bam'
- 'the sorted bam file.

  # out : name of alignment_stats report txt file.

  # ref : reference genome fa file

  # nThreads : number of threads'
path: .opencode/knowledge/tasks/task-0074-11-alignment-stats-sh.md
origin_source: alignment_stats.sh
origin_page: 74
source_entry_index: 70
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: alignment-stats
---

# 11. alignment_stats.sh:

## One-line description

11. alignment_stats.sh: Get the alignment_stats report. Input : the sorted bam file Output : a alignment_stats txt file Usage Run the following in the container. ./scripts/alignment_stats.sh <bam> <out> # bam : the so...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `alignment_stats.sh`
- Origin page: `74`
- Source entry index: `70`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0074`
- Analysis/tool category: `alignment-stats`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
11. alignment_stats.sh:
Get the alignment_stats report.
Input : the sorted bam file
Output : a alignment_stats txt file 
Usage
Run the following in the container.
./scripts/alignment_stats.sh <bam> <out> 
# bam :  the sorted bam file.
# out : name of alignment_stats report txt file.
# ref : reference genome fa file
# nThreads : number of threads
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
