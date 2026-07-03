---
id: task-0066
title: '3. bam2fq.sh:'
summary: '3. bam2fq.sh: transfer bam file to fastq format. Input : basecaller’s output
  bam file Output : a fastq file. Usage Run the following in the container ./scripts/bam2fq.sh
  <numcore> <bam> <out> # numcore : number of thr...'
keywords:
- bam2fq
- bam2fq.sh
- 3. bam2fq.sh
- 'transfer bam file to fastq format.

  Input : basecaller’s output bam file'
- 'Output : a fastq file.

  Usage

  Run the following in the container

  '
- scripts
- bam2fq.sh <numcore> <bam> <out>
- '# numcore : number of threads

  # bam : basecaller’s output bam file.

  # out : name of output fastq file'
path: .opencode/knowledge/tasks/task-0066-3-bam2fq-sh.md
origin_source: bam2fq.sh
origin_page: 67
source_entry_index: 62
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: bam2fq
---

# 3. bam2fq.sh:

## One-line description

3. bam2fq.sh: transfer bam file to fastq format. Input : basecaller’s output bam file Output : a fastq file. Usage Run the following in the container ./scripts/bam2fq.sh <numcore> <bam> <out> # numcore : number of thr...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `bam2fq.sh`
- Origin page: `67`
- Source entry index: `62`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0066`
- Analysis/tool category: `bam2fq`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
3. bam2fq.sh:
 transfer bam file to fastq format.
Input : basecaller’s output bam file 
Output : a fastq file.
Usage
Run the following in the container
./scripts/bam2fq.sh <numcore> <bam> <out>  
# numcore : number of threads
# bam : basecaller’s output bam file.
# out : name of output fastq file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
