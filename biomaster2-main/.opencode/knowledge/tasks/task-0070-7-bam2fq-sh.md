---
id: task-0070
title: '7. bam2fq.sh:'
summary: '7. bam2fq.sh: transfer bam file to fastq format. Input : host-gene-removal
  bam file Output : a fastq file. Usage Run the following in the container ./scripts/bam2fq.sh
  <numcore> <bam> <out> # numcore : number of threa...'
keywords:
- bam2fq
- bam2fq.sh
- 7. bam2fq.sh
- 'transfer bam file to fastq format.

  Input : host-gene-removal bam file'
- 'Output : a fastq file.

  Usage

  Run the following in the container

  '
- scripts
- bam2fq.sh <numcore> <bam> <out>
- '# numcore : number of threads

  # bam : host-gene-removal bam file.

  # out : name of output fastq file'
path: .opencode/knowledge/tasks/task-0070-7-bam2fq-sh.md
origin_source: bam2fq.sh
origin_page: 70
source_entry_index: 66
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: bam2fq
---

# 7. bam2fq.sh:

## One-line description

7. bam2fq.sh: transfer bam file to fastq format. Input : host-gene-removal bam file Output : a fastq file. Usage Run the following in the container ./scripts/bam2fq.sh <numcore> <bam> <out> # numcore : number of threa...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `bam2fq.sh`
- Origin page: `70`
- Source entry index: `66`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0070`
- Analysis/tool category: `bam2fq`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
7. bam2fq.sh:
 transfer bam file to fastq format.
Input : host-gene-removal bam file 
Output : a fastq file.
Usage
Run the following in the container
./scripts/bam2fq.sh <numcore> <bam> <out>  
# numcore : number of threads
# bam : host-gene-removal bam file.
# out : name of output fastq file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
