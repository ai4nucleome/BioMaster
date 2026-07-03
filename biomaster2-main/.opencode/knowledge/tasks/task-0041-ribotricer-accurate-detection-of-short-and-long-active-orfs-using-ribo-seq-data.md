---
id: task-0041
title: 'ribotricer: Accurate detection of short and long active ORFs using Ribo-seq
  data'
summary: 'ribotricer: Accurate detection of short and long active ORFs using Ribo-seq
  data ribotricer is a tool that helps in detecting actively translating open reading
  frames (ORFs) from Ribo-seq data. It works by assessing t...'
keywords:
- ribotricer
- 'ribotricer: Accurate detection of short and long active ORFs using Ribo-seq data'
- ribotricer is a tool that helps in detecting actively translating open reading frames
  (ORFs) from Ribo-seq data. It works by assessing the periodicity of candidate ORFs.
  To run ribotricer
- the following files are required
- '1. **Genome annotation file** in GTF format (handles variations of GTFs including
  GENCODE and Ensembl)

  2. **Reference genome file** in FASTA format

  3. **Alignment file** in BAM format'
- '### Installation

  To install ribotricer using conda'
- execute
- '```bash

  conda create -n ribotricer_env -c bioconda ribotricer

  conda activate ribotricer_env

  ribotricer --help

  ```'
- Alternatively
- to install locally
- download the source code and run
- '```bash

  make install

  ```'
- '### Workflow

  1. **Preparing candidate ORFs**'
- Run ribotricer to find all candidate ORFs from the GTF and FASTA files
- '```bash'
- ribotricer prepare-orfs --gtf {GTF} --fasta {FASTA} --prefix {RIBOTRICER_INDEX_PREFIX}
- '```'
- 'This generates a file with candidate ORFs: `{PREFIX}_candidate_orfs.tsv`'
- 2. **Detecting translating ORFs**
- Detect active translation from BAM file
- ribotricer detect-orfs --bam {BAM}
path: .opencode/knowledge/tasks/task-0041-ribotricer-accurate-detection-of-short-and-long-active-orfs-using-ribo-seq-data.md
origin_source: ribotricer
origin_page: 42
source_entry_index: 37
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-conda
tool: ribotricer
---

# ribotricer: Accurate detection of short and long active ORFs using Ribo-seq data

## One-line description

ribotricer: Accurate detection of short and long active ORFs using Ribo-seq data ribotricer is a tool that helps in detecting actively translating open reading frames (ORFs) from Ribo-seq data. It works by assessing t...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `ribotricer`
- Origin page: `42`
- Source entry index: `37`
- Source subindex: `1`
- Canonical skill: `exec-conda`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-conda`
- Registry ID: `task-0041`
- Analysis/tool category: `ribotricer`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
ribotricer: Accurate detection of short and long active ORFs using Ribo-seq data

ribotricer is a tool that helps in detecting actively translating open reading frames (ORFs) from Ribo-seq data. It works by assessing the periodicity of candidate ORFs. To run ribotricer, the following files are required:

1. **Genome annotation file** in GTF format (handles variations of GTFs including GENCODE and Ensembl)
2. **Reference genome file** in FASTA format
3. **Alignment file** in BAM format

### Installation
To install ribotricer using conda, execute:

~~~bash
conda create -n ribotricer_env -c bioconda ribotricer
conda activate ribotricer_env
ribotricer --help
~~~

Alternatively, to install locally, download the source code and run:

~~~bash
make install
~~~

### Workflow
1. **Preparing candidate ORFs**

   Run ribotricer to find all candidate ORFs from the GTF and FASTA files:
   ~~~bash
   ribotricer prepare-orfs --gtf {GTF} --fasta {FASTA} --prefix {RIBOTRICER_INDEX_PREFIX}
   ~~~
   This generates a file with candidate ORFs: `{PREFIX}_candidate_orfs.tsv`.

2. **Detecting translating ORFs**

   Detect active translation from BAM file:
   ~~~bash
   ribotricer detect-orfs --bam {BAM} --ribotricer_index {RIBOTRICER_INDEX_PREFIX}_candidate_ORFs.tsv --prefix {OUTPUT_PREFIX}
   ~~~
   This will generate output such as `{OUTPUT_PREFIX}_translating_ORFs.tsv`.

### Additional Features
- **Learn cutoff empirically from data** using both Ribo-seq and RNA-seq BAM files.
- **Visualization** of ribotricer output available in the provided notebooks.

For more details and troubleshooting, refer to the [documentation](https://github.com/smithlabcode/ribotricer/issues).

### Dependencies
- pyfaidx>=0.5.0
- pysam>=0.11.2.2
- numpy>=1.11.0
- pandas>=0.20.3
- scipy>=0.19.1
- matplotlib>=2.1.0
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
