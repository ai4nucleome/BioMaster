---
id: wf-0051
title: '3. eventalign.sh:'
summary: '3. eventalign.sh: index fast5 to basecalling fastq with nanopolish index
  tool and then run nanopolish for basecalling fastq file to compute an improved consensus
  sequence from the draft genome assembly produced by min...'
keywords:
- nanopore
- workflow
- 3. eventalign.sh
- '3. eventalign.sh:

  index fast5 to basecalling fastq with nanopolish index tool and then run nanopolish
  for basecalling fastq file to compute an improved consensus sequence from the draft
  genome assembly produced by minimap2'
- thus
- 'get the signal.

  Input: a basecalling nanopore fastq file'
- 'a file folder containing nanopore files in fast5 format and a reference genome
  fa file

  Output: a summary file in format sum and a output txt file

  Usage

  Run the following in the container

  '
- scripts
- 'eventalign.sh <fq> <fast5dir> <sortedBam> <ref> <npsummary> <nThreads> <np_out>

  # fq: a basecalling fastq file.

  # fast5dir: Path of a file folder containing nanopore files in fast5 format.

  # sortedBam: a sorted bam file.

  # ref : reference genome fa file

  # nThreads : number of threads.

  # npsummary : name of merged summary file .

  # np_out : name of output txt file'
- eventalign
path: .opencode/knowledge/workflows/wf-0051-3-eventalign-sh.md
origin_source: workflow
origin_page: 51
source_entry_index: 41
source_subindex: 3
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: nanopore
---

# 3. eventalign.sh:

## One-line description

3. eventalign.sh: index fast5 to basecalling fastq with nanopolish index tool and then run nanopolish for basecalling fastq file to compute an improved consensus sequence from the draft genome assembly produced by min...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `51`
- Source entry index: `41`
- Source subindex: `3`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0051`
- Analysis/tool category: `nanopore`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
3. eventalign.sh:
index fast5 to basecalling fastq with nanopolish index tool and then run nanopolish for basecalling fastq file to compute an improved consensus sequence from the draft genome assembly produced by minimap2, thus, get the signal.
Input: a basecalling nanopore fastq file , a file folder containing nanopore files in fast5 format and a reference genome fa file
Output: a summary file in format sum and a output txt file
Usage
Run the following in the container
./scripts/eventalign.sh <fq> <fast5dir> <sortedBam> <ref> <npsummary> <nThreads> <np_out>
# fq: a basecalling fastq file.
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
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
