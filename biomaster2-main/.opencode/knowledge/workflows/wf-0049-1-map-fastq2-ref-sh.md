---
id: wf-0049
title: '1. map_fastq2_ref.sh:'
summary: '1. map_fastq2_ref.sh: Map basecalling file to reference genome(fa file).
  Generates sam file. Input : a basecalling file in format fastq and a reference genome
  fa file Output : a sam file Usage Run the following in the...'
keywords:
- workflow
- 1. map_fastq2_ref.sh
- '1. map_fastq2_ref.sh:

  Map basecalling file to reference genome(fa file). Generates sam file.

  Input : a basecalling file in format fastq and a reference genome fa file

  Output : a sam file'
- 'Usage

  Run the following in the container.

  '
- scripts
- 'map_fastq2_ref.sh <fq> <output_sam> <ref> <nThreads>

  # fq : basecalling fastq file.

  # output_sam : name of output sam file.

  # ref : reference genome fa file

  # nThreads : number of threads'
path: .opencode/knowledge/workflows/wf-0049-1-map-fastq2-ref-sh.md
origin_source: workflow
origin_page: 51
source_entry_index: 41
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: workflow
---

# 1. map_fastq2_ref.sh:

## One-line description

1. map_fastq2_ref.sh: Map basecalling file to reference genome(fa file). Generates sam file. Input : a basecalling file in format fastq and a reference genome fa file Output : a sam file Usage Run the following in the...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `51`
- Source entry index: `41`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0049`
- Analysis/tool category: `workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
1. map_fastq2_ref.sh:
Map basecalling file to reference genome(fa file). Generates sam file.
Input : a basecalling file in format fastq and a reference genome fa file
Output : a sam file 
Usage
Run the following in the container.
./scripts/map_fastq2_ref.sh <fq> <output_sam> <ref> <nThreads>
# fq : basecalling fastq file.
# output_sam : name of output sam file.
# ref : reference genome fa file
# nThreads : number of threads
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
