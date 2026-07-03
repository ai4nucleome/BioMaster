---
id: task-0003
title: '1. run-bwa-mem.sh:'
summary: '1. run-bwa-mem.sh: Alignment module for Hi-C data, based on bwa-mem. Input
  : a pair of Hi-C fastq files Output : a bam file (Lossless, not sorted by coordinate)
  Usage Run the following in the container. run-bwa-mem.sh...'
keywords:
- run-bwa-mem-sh-by-hic-workflow
- run-bwa-mem.sh by hic workflow
- 1. run-bwa-mem.sh
- '1. run-bwa-mem.sh:

  Alignment module for Hi-C data'
- 'based on bwa-mem.

  Input : a pair of Hi-C fastq files

  Output : a bam file (Lossless'
- 'not sorted by coordinate)

  Usage

  Run the following in the container.

  run-bwa-mem.sh <fastq1> <fastq2> <bwaIndex> <outdir> <output_prefix> <nThreads>

  # fastq1'
- 'fastq2 : input fastq files'
- 'either gzipped or not

  # bwaIndex : tarball for bwa index'
- 'tgz.

  # outdir : output directory

  # output_prefix : prefix of the output bam file.

  # nThreads : number of threads'
- The script is invoked in the
- script
- path as bash
- run-bwa-mem.sh. Set parameters according to the example:I want to output under
- output
- '003'
- Reference file path for
- data
- hg38.bwaindex.tgz
- no need to extract the reference file
- and the first pair are
- 4DNFI15H1RVG.fastq.gz and
- 4DNFIZHUKESO.fastq.gz
- the second pair are for
- 4DNFIKVDGNJN.fastq.gz and
- 4DNFIEQ58J6G.fastq.gz
- the target is the first pair result is bwa_1.bam
- the second pair result is bwa.2.bam. the generated script is
- bash
- scripts
- run-bwa-mem.sh
- 4DNFI15H1RVG.fastq.gz
- bwa_1 64
- 4DN
- BWA
path: .opencode/knowledge/tasks/task-0003-1-run-bwa-mem-sh.md
origin_source: run-bwa-mem.sh by hic workflow
origin_page: 8
source_entry_index: 3
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-bwa-mem-sh-by-hic-workflow
---

# 1. run-bwa-mem.sh:

## One-line description

1. run-bwa-mem.sh: Alignment module for Hi-C data, based on bwa-mem. Input : a pair of Hi-C fastq files Output : a bam file (Lossless, not sorted by coordinate) Usage Run the following in the container. run-bwa-mem.sh...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-bwa-mem.sh by hic workflow`
- Origin page: `8`
- Source entry index: `3`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0003`
- Analysis/tool category: `run-bwa-mem-sh-by-hic-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
1. run-bwa-mem.sh:
Alignment module for Hi-C data, based on bwa-mem.
Input : a pair of Hi-C fastq files
Output : a bam file (Lossless, not sorted by coordinate)
Usage
Run the following in the container.
run-bwa-mem.sh <fastq1> <fastq2> <bwaIndex> <outdir> <output_prefix> <nThreads>
# fastq1, fastq2 : input fastq files, either gzipped or not
# bwaIndex : tarball for bwa index, .tgz.
# outdir : output directory
# output_prefix : prefix of the output bam file.
# nThreads : number of threads

The script is invoked in the./script/ path as bash./script/run-bwa-mem.sh. Set parameters according to the example:I want to output under./output/003/.Reference file path for: ./data/hg38.bwaindex.tgz,no need to extract the reference file, and the first pair are ./data/4DNFI15H1RVG.fastq.gz and ./data/4DNFIZHUKESO.fastq.gz, the second pair are for: ./data/4DNFIKVDGNJN.fastq.gz and ./data/4DNFIEQ58J6G.fastq.gz,  the target is the first pair result is bwa_1.bam,the second pair result is bwa.2.bam. the generated script is:

bash ./scripts/run-bwa-mem.sh ./data/4DNFI15H1RVG.fastq.gz ./data/4DNFIZHUKESO.fastq.gz  ./data/hg38.bwaindex.tgz ./output/003/  bwa_1 64

bash ./scripts/run-bwa-mem.sh ./data/4DNFIKVDGNJN.fastq.gz ./data/4DNFIEQ58J6G.fastq.gz  ./data/hg38.bwaindex.tgz ./output/003/ bwa_2 64

When the command is generated, the file name and the output path must require a space, otherwise the file name will be regarded as the folder name. bwa_1,bwa_2 indicate the generated file name, You should adjust according to the description of the desired destination file name. For example, the directive: bash ./scripts/run-bwa-mem.sh ./data/4DNFIKVDGNJN.fastq.gz ./data/4DNFIEQ58J6G.fastq.gz  ./data/hg38.bwaindex. tgz  In./output/003/ bwa_2 64, there is a space between /output/003/ and bwa_2, which must not be omitted. There is also a space between bwa_2 and 64 that cannot be omitted.and 64 indicate the number of threads. The number of threads is usually set to 16 or 32. You can install the tool, but do not do any additional operations.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
