---
id: task-0059
title: '3. eventalign.sh:'
summary: '3. eventalign.sh: index fast5 to fastq with nanopolish index tool and run
  nanopolish for fastq files to compute an improved consensus sequence from the draft
  genome assembly produced by minimap2, thus, get the signal....'
keywords:
- eventalign
- eventalign.sh
- 3. eventalign.sh
- '3. eventalign.sh:

  index fast5 to fastq with nanopolish index tool and run nanopolish for fastq files
  to compute an improved consensus sequence from the draft genome assembly produced
  by minimap2'
- thus
- 'get the signal.

  Input: a combined nanopore fastq file'
- 'a file folder containing nanopore files in fast5 format and a reference genome
  fa file

  Output: a summary file in format sum and a output txt file

  Usage

  Run the following in the container

  '
- scripts
- 'eventalign.sh <fq> <fast5dir> <sortedBam> <ref> <npsummary> <nThreads> <np_out>

  # fq: a combined fastq file.

  # fast5dir: Path of a file folder containing nanopore files in fast5 format.

  # sortedBam: a sorted bam file.

  # ref : reference genome fa file

  # nThreads : number of threads.

  # npsummary : name of merged summary file .

  # np_out : name of output txt file'
path: .opencode/knowledge/tasks/task-0059-3-eventalign-sh.md
origin_source: eventalign.sh
origin_page: 60
source_entry_index: 55
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: eventalign
---

# 3. eventalign.sh:

## One-line description

3. eventalign.sh: index fast5 to fastq with nanopolish index tool and run nanopolish for fastq files to compute an improved consensus sequence from the draft genome assembly produced by minimap2, thus, get the signal....

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `eventalign.sh`
- Origin page: `60`
- Source entry index: `55`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0059`
- Analysis/tool category: `eventalign`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
3. eventalign.sh:
index fast5 to fastq with nanopolish index tool and run nanopolish for fastq files to compute an improved consensus sequence from the draft genome assembly produced by minimap2, thus, get the signal.
Input: a combined nanopore fastq file , a file folder containing nanopore files in fast5 format and a reference genome fa file
Output: a summary file in format sum and a output txt file
Usage
Run the following in the container
./scripts/eventalign.sh <fq> <fast5dir> <sortedBam> <ref> <npsummary> <nThreads> <np_out>
# fq: a combined fastq file.
# fast5dir: Path of a file folder containing nanopore files in fast5 format.
# sortedBam: a sorted bam file.
# ref : reference genome fa file
# nThreads : number of threads.
# npsummary : name of merged summary file .
# np_out : name of output txt file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
