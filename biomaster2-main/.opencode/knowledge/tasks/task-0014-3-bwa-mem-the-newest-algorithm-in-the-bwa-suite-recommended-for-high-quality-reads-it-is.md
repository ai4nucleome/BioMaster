---
id: task-0014
title: '3. **BWA-MEM**: The newest algorithm in the BWA suite, recommended for high-quality
  reads. It is...'
summary: '3. **BWA-MEM**: The newest algorithm in the BWA suite, recommended for high-quality
  reads. It is both fast and accurate, with support for read lengths from 70 bp to
  1 Mbps. BWA-MEM also performs well for reads between...'
keywords:
- samtools
- BWA-MEM
- '3. **BWA-MEM**: The newest algorithm in the BWA suite'
- recommended for high-quality reads. It is
- recommended for high-quality reads. It is both fast and accurate
- with support for read lengths from 70 bp to 1 Mbps. BWA-MEM also performs well for
  reads between 70 and 100 bp
- Among these
- '**BWA-MEM** is widely used due to its balance of speed and accuracy'
- making it suitable for various downstream applications
- such as whole-genome variant calling. It supports long reads
- split alignment
- and chimeric reads
- and outputs standard SAM files that are compatible with tools like samtools and
  GATK
- Before running BWA-MEM
- you must build an FM-index of the reference genome using the `bwa index` command.
  Once the index is created
- you can align reads to the reference genome with the `bwa mem` sub-command
- '## Installation'
- BWA
path: .opencode/knowledge/tasks/task-0014-3-bwa-mem-the-newest-algorithm-in-the-bwa-suite-recommended-for-high-quality-reads-it-is.md
origin_source: BWA-MEM
origin_page: 17
source_entry_index: 12
source_subindex: 3
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: samtools
---

# 3. **BWA-MEM**: The newest algorithm in the BWA suite, recommended for high-quality reads. It is...

## One-line description

3. **BWA-MEM**: The newest algorithm in the BWA suite, recommended for high-quality reads. It is both fast and accurate, with support for read lengths from 70 bp to 1 Mbps. BWA-MEM also performs well for reads between...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `BWA-MEM`
- Origin page: `17`
- Source entry index: `12`
- Source subindex: `3`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0014`
- Analysis/tool category: `samtools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
3. **BWA-MEM**: The newest algorithm in the BWA suite, recommended for high-quality reads. It is both fast and accurate, with support for read lengths from 70 bp to 1 Mbps. BWA-MEM also performs well for reads between 70 and 100 bp.

Among these, **BWA-MEM** is widely used due to its balance of speed and accuracy, making it suitable for various downstream applications, such as whole-genome variant calling. It supports long reads, split alignment, and chimeric reads, and outputs standard SAM files that are compatible with tools like samtools and GATK.

Before running BWA-MEM, you must build an FM-index of the reference genome using the `bwa index` command. Once the index is created, you can align reads to the reference genome with the `bwa mem` sub-command.

---

## Installation
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
