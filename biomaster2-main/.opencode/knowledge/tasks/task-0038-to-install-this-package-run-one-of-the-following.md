---
id: task-0038
title: 'To install this package run one of the following:'
summary: 'To install this package run one of the following: conda install -c bioconda
  bedtools BEDTools: BEDTools is a powerful suite of utilities for comparing, manipulating,
  and analyzing genomic intervals in the popular BED,...'
keywords:
- bedtools
- BEDTools
- To install this package run one of the following
- 'To install this package run one of the following:

  conda install -c bioconda bedtools'
- 'BEDTools: BEDTools is a powerful suite of utilities for comparing'
- manipulating
- and analyzing genomic intervals in the popular BED
- GFF
- and VCF formats. It is widely used for a variety of tasks including interval manipulation
- intersection analysis
- and genomic file format conversion. BEDTools supports many types of genomic file
  formats
- allowing users to easily perform complex analyses on genomic data
- '### Supported Operations:

  - **Intersect**: Find common regions between multiple files.

  - **Merge**: Combine overlapping or adjacent intervals into a single interval.

  - **Closest**: Find the closest feature from a set of intervals.

  - **Subtract**: Subtract one set of intervals from another.

  - **Shuffle**: Randomly shuffle intervals while preserving their length.

  - **Map**: Map a set of intervals to another file to extract values.

  - **Split**: Split intervals into smaller chunks based on specific criteria'
- '### Dependencies:

  - Python (>=3.6)

  - GCC (>=5.4.0)

  - CMake (>=3.10.2)'
- '### Installation & Setup:

  ```bash

  # Install BEDTools using conda

  conda install -c bioconda bedtools

  ```'
- '### Usage:

  #### *'
path: .opencode/knowledge/tasks/task-0038-to-install-this-package-run-one-of-the-following.md
origin_source: BEDTools
origin_page: 39
source_entry_index: 34
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-conda
tool: bedtools
---

# To install this package run one of the following:

## One-line description

To install this package run one of the following: conda install -c bioconda bedtools BEDTools: BEDTools is a powerful suite of utilities for comparing, manipulating, and analyzing genomic intervals in the popular BED,...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `BEDTools`
- Origin page: `39`
- Source entry index: `34`
- Source subindex: `1`
- Canonical skill: `exec-conda`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-conda`
- Registry ID: `task-0038`
- Analysis/tool category: `bedtools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
To install this package run one of the following:
conda install -c bioconda bedtools

BEDTools: BEDTools is a powerful suite of utilities for comparing, manipulating, and analyzing genomic intervals in the popular BED, GFF, and VCF formats. It is widely used for a variety of tasks including interval manipulation, intersection analysis, and genomic file format conversion. BEDTools supports many types of genomic file formats, allowing users to easily perform complex analyses on genomic data.

### Supported Operations:
- **Intersect**: Find common regions between multiple files.
- **Merge**: Combine overlapping or adjacent intervals into a single interval.
- **Closest**: Find the closest feature from a set of intervals.
- **Subtract**: Subtract one set of intervals from another.
- **Shuffle**: Randomly shuffle intervals while preserving their length.
- **Map**: Map a set of intervals to another file to extract values.
- **Split**: Split intervals into smaller chunks based on specific criteria.

### Dependencies:
- Python (>=3.6)
- GCC (>=5.4.0)
- CMake (>=3.10.2)

### Installation & Setup:
~~~bash
# Install BEDTools using conda
conda install -c bioconda bedtools
~~~

### Usage:
#### **Intersecting two BED files**
~~~bash
bedtools intersect -a file1.bed -b file2.bed > output.bed
~~~

#### **Merging overlapping intervals**
~~~bash
bedtools merge -i input.bed > merged.bed
~~~

#### **Find the closest feature**
~~~bash
bedtools closest -a file1.bed -b file2.bed > closest.bed
~~~

#### **Subtract one set of intervals from another**
~~~bash
bedtools subtract -a file1.bed -b file2.bed > result.bed
~~~

#### **Shuffle intervals randomly**
~~~bash
bedtools shuffle -i input.bed -g genome.txt > shuffled.bed
~~~

#### **Map intervals to another file**
~~~bash
bedtools map -a input.bed -b values.bed > mapped.bed
~~~

### **Advanced Features:**
- **Multi-threading support**: BEDTools allows parallel processing for large genomic datasets.
- **Custom genome definitions**: Users can specify custom genome definitions for operations like shuffling or calculating closest distances.

### **Output Files:**
- **output.bed**: The resulting file after performing an operation, typically in BED format.
- **merged.bed**: The output file containing merged intervals from the input file.

### **Reference Documentation:**
For more details, refer to the official BEDTools documentation and command-line help:
~~~bash
bedtools --help
~~~
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
