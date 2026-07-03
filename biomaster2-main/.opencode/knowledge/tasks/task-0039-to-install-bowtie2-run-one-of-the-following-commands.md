---
id: task-0039
title: 'To install Bowtie2, run one of the following commands:'
summary: 'To install Bowtie2, run one of the following commands: ### Installation
  Instructions: ```bash # Install Bowtie2 using conda conda install -c bioconda bowtie2
  # Or install via package manager on Linux sudo apt-get inst...'
keywords:
- bowtie2
- Bowtie2
- To install Bowtie2
- run one of the following commands
- '### Installation Instructions:

  ```bash

  # Install Bowtie2 using conda

  conda install -c bioconda bowtie2'
- '# Or install via package manager on Linux

  sudo apt-get install bowtie2

  ```'
- '### Bowtie2 Overview:

  Bowtie2 is a fast and efficient aligner that aligns short reads to a reference genome.
  It can handle paired-end and single-end read files in FASTQ format'
- and produces output in the widely used SAM format. It is optimized for aligning
  short DNA reads with high accuracy
- '### Supported Features:

  - **Single-End Read Alignment**: Aligns single-end reads to a reference genome.

  - **Paired-End Read Alignment**: Aligns paired-end reads to a reference genome.

  - **Output in SAM format**: SAM format is widely used for storing sequence alignments.

  - **Multithreading support**: Bowtie2 supports multithreading to speed up the alignment
  process'
- '### Installation & Setup:

  ```bash

  # Install Bowtie2 using conda

  conda install -c bioconda bowtie2

  ```'
- '### Basic Usage:

  #### **Aligning single-end reads**

  ```bash

  bowtie2 -x reference_genome -U reads.fastq -S output.sam

  ```

  #### **Aligning paired-end reads**

  ```bash

  bowtie2 -x reference_genome -1 rea'
path: .opencode/knowledge/tasks/task-0039-to-install-bowtie2-run-one-of-the-following-commands.md
origin_source: Bowtie2
origin_page: 40
source_entry_index: 35
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-conda
tool: bowtie2
---

# To install Bowtie2, run one of the following commands:

## One-line description

To install Bowtie2, run one of the following commands: ### Installation Instructions: ```bash # Install Bowtie2 using conda conda install -c bioconda bowtie2 # Or install via package manager on Linux sudo apt-get inst...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `Bowtie2`
- Origin page: `40`
- Source entry index: `35`
- Source subindex: `1`
- Canonical skill: `exec-conda`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-conda`
- Registry ID: `task-0039`
- Analysis/tool category: `bowtie2`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
To install Bowtie2, run one of the following commands:

### Installation Instructions:
~~~bash
# Install Bowtie2 using conda
conda install -c bioconda bowtie2

# Or install via package manager on Linux
sudo apt-get install bowtie2
~~~

### Bowtie2 Overview:
Bowtie2 is a fast and efficient aligner that aligns short reads to a reference genome. It can handle paired-end and single-end read files in FASTQ format, and produces output in the widely used SAM format. It is optimized for aligning short DNA reads with high accuracy.

### Supported Features:
- **Single-End Read Alignment**: Aligns single-end reads to a reference genome.
- **Paired-End Read Alignment**: Aligns paired-end reads to a reference genome.
- **Output in SAM format**: SAM format is widely used for storing sequence alignments.
- **Multithreading support**: Bowtie2 supports multithreading to speed up the alignment process.

### Installation & Setup:
~~~bash
# Install Bowtie2 using conda
conda install -c bioconda bowtie2
~~~

### Basic Usage:
#### **Aligning single-end reads**
~~~bash
bowtie2 -x reference_genome -U reads.fastq -S output.sam
~~~
#### **Aligning paired-end reads**
~~~bash
bowtie2 -x reference_genome -1 reads_1.fastq -2 reads_2.fastq -S output.sam
~~~

#### **Aligning with multithreading (using 4 threads)**
~~~bash
bowtie2 -x reference_genome -U reads.fastq -S output.sam -p 4
~~~

### Output Files:
- **output.sam**: The resulting alignment file in SAM format. It contains the aligned reads and their respective positions in the reference genome.

### **Advanced Features:**
- **Bowtie2 Indexing**: Before aligning, you need to index the reference genome with the following command:
  ~~~bash
  bowtie2-build reference_genome.fa reference_genome
  ~~~
- **Handling Large Datasets**: Bowtie2 is optimized for large datasets, and its multithreading support helps improve performance on large genome alignments.

### **Reference Documentation:**
For more details on Bowtie2, refer to the official documentation and help command:
~~~bash
bowtie2 --help
~~~
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
