---
id: task-0065
title: '2. basecall_sum.sh:'
summary: '2. basecall_sum.sh: output a tab-separated file with read level sequencing
  information from the bam file generated during basecalling. Input : basecaller’s
  output bam file Output : a summary tsv file. Usage Run the fo...'
keywords:
- basecall-sum
- basecall_sum.sh
- 2. basecall_sum.sh
- '2. basecall_sum.sh:

  output a tab-separated file with read level sequencing information from the bam
  file generated during basecalling'
- 'Input : basecaller’s output bam file'
- 'Output : a summary tsv file.

  Usage

  Run the following in the container

  '
- scripts
- basecall_sum.sh <bam> <out>
- '# bam : basecaller’s output bam file.

  # out : name of output tsv file'
path: .opencode/knowledge/tasks/task-0065-2-basecall-sum-sh.md
origin_source: basecall_sum.sh
origin_page: 66
source_entry_index: 61
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: basecall-sum
---

# 2. basecall_sum.sh:

## One-line description

2. basecall_sum.sh: output a tab-separated file with read level sequencing information from the bam file generated during basecalling. Input : basecaller’s output bam file Output : a summary tsv file. Usage Run the fo...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `basecall_sum.sh`
- Origin page: `66`
- Source entry index: `61`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0065`
- Analysis/tool category: `basecall-sum`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
2. basecall_sum.sh:
output a tab-separated file with read level sequencing information from the bam file generated during basecalling. 
Input : basecaller’s output bam file 
Output : a summary tsv file.
Usage
Run the following in the container
./scripts/basecall_sum.sh <bam> <out>  
# bam : basecaller’s output bam file.
# out : name of output tsv file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
