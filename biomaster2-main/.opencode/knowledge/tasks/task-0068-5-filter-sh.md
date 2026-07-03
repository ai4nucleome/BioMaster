---
id: task-0068
title: '5. filter.sh:'
summary: '5. filter.sh: filter low_quality reads in basecall fastq file. Input : basecall
  fastq file Output : a filtered fastq file. Usage Run the following in the container
  ./scripts/filter.sh <fastq> <out> # fastq : basecall...'
keywords:
- filter
- filter.sh
- 5. filter.sh
- 'filter low_quality reads in basecall fastq file.

  Input : basecall fastq file'
- 'Output : a filtered fastq file.

  Usage

  Run the following in the container

  '
- scripts
- filter.sh <fastq> <out>
- '# fastq : basecall fastq file.

  # out : name of filtered fastq file'
path: .opencode/knowledge/tasks/task-0068-5-filter-sh.md
origin_source: filter.sh
origin_page: 68
source_entry_index: 64
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: filter
---

# 5. filter.sh:

## One-line description

5. filter.sh: filter low_quality reads in basecall fastq file. Input : basecall fastq file Output : a filtered fastq file. Usage Run the following in the container ./scripts/filter.sh <fastq> <out> # fastq : basecall...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `filter.sh`
- Origin page: `68`
- Source entry index: `64`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0068`
- Analysis/tool category: `filter`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
5. filter.sh:
 filter low_quality reads in basecall fastq file.
Input : basecall fastq file 
Output : a filtered fastq file.
Usage
Run the following in the container
./scripts/filter.sh <fastq> <out>  
# fastq : basecall fastq file.
# out : name of filtered fastq file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
