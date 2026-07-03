---
id: wf-0005
title: '1. run-bwa-mem.sh:'
summary: '1. run-bwa-mem.sh: Alignment module for Hi-C data, based on bwa-mem. Input
  : a pair of Hi-C fastq files Output : a bam file (Lossless, not sorted by coordinate)
  Usage Run the following in the container. run-bwa-mem.sh...'
keywords:
- hic-matrix
- workflow
- 1. run-bwa-mem.sh
- '1. run-bwa-mem.sh:

  Alignment module for Hi-C data'
- 'based on bwa-mem.

  Input : a pair of Hi-C fastq files

  Output : a bam file (Lossless'
- 'not sorted by coordinate)

  Usage

  Run the following in the container.

  run-bwa-mem.sh <fastq1> <fastq2> <bwaIndex> <output_prefix> <nThreads>

  # fastq1'
- 'fastq2 : input fastq files'
- 'either gzipped or not

  # bwaIndex : tarball for bwa index'
- 'tgz.

  # outdir : output directory

  # output_prefix : prefix of the output bam file.

  # nThreads : number of threads. Also for the first step run-bwa-mem'
- if there are two pairs of data
- one set of data should be output. If there are four pairs data
- two pairs of data should be generated. Six makes three.Example 4DNFI15H1RVG.fastq.gz
- 4DNFIZHUKESO.fastq.gz
- 4DNFIEQ58J6G.fastq.gz
- 4DNFIKVDGNJN.fastq.gz should generate two of 4DNFI95DH3QJ.fastq.gz and 4DNFIHMY7KMH.fastq.gz
  output
- for reference only
- BWA
path: .opencode/knowledge/workflows/wf-0005-1-run-bwa-mem-sh.md
origin_source: workflow
origin_page: 15
source_entry_index: 5
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: hic-matrix
---

# 1. run-bwa-mem.sh:

## One-line description

1. run-bwa-mem.sh: Alignment module for Hi-C data, based on bwa-mem. Input : a pair of Hi-C fastq files Output : a bam file (Lossless, not sorted by coordinate) Usage Run the following in the container. run-bwa-mem.sh...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `15`
- Source entry index: `5`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0005`
- Analysis/tool category: `hic-matrix`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
1. run-bwa-mem.sh:
Alignment module for Hi-C data, based on bwa-mem.
Input : a pair of Hi-C fastq files
Output : a bam file (Lossless, not sorted by coordinate)
Usage
Run the following in the container.
run-bwa-mem.sh <fastq1> <fastq2> <bwaIndex> <output_prefix> <nThreads>
# fastq1, fastq2 : input fastq files, either gzipped or not
# bwaIndex : tarball for bwa index, .tgz.
# outdir : output directory
# output_prefix : prefix of the output bam file.
# nThreads : number of threads. Also for the first step run-bwa-mem, if there are two pairs of data, one set of data should be output. If there are four pairs data, two pairs of data should be generated. Six makes three.Example 4DNFI15H1RVG.fastq.gz,4DNFIZHUKESO.fastq.gz,4DNFIEQ58J6G.fastq.gz,4DNFIKVDGNJN.fastq.gz should generate two of 4DNFI95DH3QJ.fastq.gz and 4DNFIHMY7KMH.fastq.gz output, for reference only
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
