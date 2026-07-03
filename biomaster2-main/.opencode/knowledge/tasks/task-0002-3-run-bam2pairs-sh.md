---
id: task-0002
title: '3. run-bam2pairs.sh:'
summary: '3. run-bam2pairs.sh: Bam to pairs conversion module for Hi-C data, based
  on samtools, bgzip and pairix. Input : any paired-end bam file Output : a chromosome-block-sorted
  and bgzipped pairs pairs file that contains al...'
keywords:
- run-bam2pairs
- run-bam2pairs.sh
- 3. run-bam2pairs.sh
- '3. run-bam2pairs.sh:

  Bam to pairs conversion module for Hi-C data'
- based on samtools
- 'bgzip and pairix.

  Input : any paired-end bam file

  Output : a chromosome-block-sorted and bgzipped pairs pairs file that contains all
  the mapped read pairs in the bam file'
- 'along with its index (.bsorted.pairs.gz and .bsorted.pairs.gz.px2)

  Usage

  Run the following in the container.

  run-bam2pairs.sh <input_bam> <output_prefix>

  # input_bam : input bam file.

  # output_prefix : prefix of the output pairs file.

  Set parameters according to the example:

  Suppose the input file is'
- output
- GM12878_bwa_sorted_1.bam and
- GM12878_bwa_sorted_2.bam
- the target is
- GM12878_bwa_sorted_pairs
- and
- 'Generate the following sample script:

  bash'
- scripts
- GM12878_bwa_sorted_1.bam
- bash
- You can install the tool
- but do not do any additional operations.You can install the tool
- but do not do any additional operations.Please follow the example to generate rather
  than copy and paste completely
- especially for folder names
- samtools
path: .opencode/knowledge/tasks/task-0002-3-run-bam2pairs-sh.md
origin_source: run-bam2pairs.sh
origin_page: 7
source_entry_index: 2
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: run-bam2pairs
---

# 3. run-bam2pairs.sh:

## One-line description

3. run-bam2pairs.sh: Bam to pairs conversion module for Hi-C data, based on samtools, bgzip and pairix. Input : any paired-end bam file Output : a chromosome-block-sorted and bgzipped pairs pairs file that contains al...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `run-bam2pairs.sh`
- Origin page: `7`
- Source entry index: `2`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0002`
- Analysis/tool category: `run-bam2pairs`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
3. run-bam2pairs.sh:
Bam to pairs conversion module for Hi-C data, based on samtools, bgzip and pairix.
Input : any paired-end bam file
Output : a chromosome-block-sorted and bgzipped pairs pairs file that contains all the mapped read pairs in the bam file, along with its index (.bsorted.pairs.gz and .bsorted.pairs.gz.px2)
Usage
Run the following in the container.
run-bam2pairs.sh <input_bam> <output_prefix>
# input_bam : input bam file.
# output_prefix : prefix of the output pairs file.
Set parameters according to the example:
Suppose the input file is: ./output/GM12878_bwa_sorted_1.bam and ./output/GM12878_bwa_sorted_2.bam, the target is./output/GM12878_bwa_sorted_pairs  and./output/GM12878_bwa_sorted_pairs , Generate the following sample script:
bash ./scripts/run-bam2pairs.sh ./output/GM12878_bwa_sorted_1.bam ./output/GM12878_bwa_sorted_pairs   
bash ./scripts/run-bam2pairs.sh ./output/GM12878_bwa_sorted_2.bam ./output/GM12878_bwa_sorted_pairs 

You can install the tool, but do not do any additional operations.You can install the tool, but do not do any additional operations.Please follow the example to generate rather than copy and paste completely, especially for folder names, file names, etc.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
