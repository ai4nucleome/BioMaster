---
id: task-0016
title: '2. **Compile and install**: Typically, you will use a C compiler (e.g., GCC).
  The official docume...'
summary: '2. **Compile and install**: Typically, you will use a C compiler (e.g.,
  GCC). The official documentation provides detailed build instructions. 3. **Finalize
  installation**: Make sure your environment variables or syst...'
keywords:
- samtools
- BWA-MEM
- '2. **Compile and install**: Typically'
- you will use a C compiler (e.g
- GCC). The official docume
- 'GCC). The official documentation provides detailed build instructions.

  3. **Finalize installation**: Make sure your environment variables or system PATH
  are set correctly so you can call `bwa` directly'
- '## Quick Start'
- 1. **Indexing the reference genome**
- '```bash

  bwa index reference.fa

  ```'
- This command builds the required FM-index for the reference genome `reference.fa`
- 2. **Running the alignment**
- '```bash

  bwa mem reference.fa reads.fq > alignment.sam

  ```'
- Aligns the reads in `reads.fq` to the reference `reference.fa` and writes the alignment
  in SAM format to `alignment.sam`
- '## Examples of Popular Commands'
- Below are five common BWA-MEM usage examples
- 1. **Indexing a reference genome with a custom prefix**
- '```bash

  bwa index -p ref_index reference.fa

  ```'
- Generates an index for `reference.fa` with the prefix `ref_index`
- 2. **Single-end read alignment**
- '```bash

  bwa mem ref_index reads.fq > aligned_reads.sam

  ```'
- Aligns single-end reads in `reads.fq` to the reference indexed by `ref_index` and
  outputs the result to `aligned_reads.sam`
- 3. **Paired-end read alignment**
- '```bash

  bwa mem'
- BWA
path: .opencode/knowledge/tasks/task-0016-2-compile-and-install-typically-you-will-use-a-c-compiler-e-g-gcc-the-official-docume.md
origin_source: BWA-MEM
origin_page: 17
source_entry_index: 12
source_subindex: 5
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: samtools
---

# 2. **Compile and install**: Typically, you will use a C compiler (e.g., GCC). The official docume...

## One-line description

2. **Compile and install**: Typically, you will use a C compiler (e.g., GCC). The official documentation provides detailed build instructions. 3. **Finalize installation**: Make sure your environment variables or syst...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `BWA-MEM`
- Origin page: `17`
- Source entry index: `12`
- Source subindex: `5`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0016`
- Analysis/tool category: `samtools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
2. **Compile and install**: Typically, you will use a C compiler (e.g., GCC). The official documentation provides detailed build instructions.
3. **Finalize installation**: Make sure your environment variables or system PATH are set correctly so you can call `bwa` directly.

---

## Quick Start

1. **Indexing the reference genome**:

~~~bash
bwa index reference.fa
~~~

This command builds the required FM-index for the reference genome `reference.fa`.

2. **Running the alignment**:

~~~bash
bwa mem reference.fa reads.fq > alignment.sam
~~~

Aligns the reads in `reads.fq` to the reference `reference.fa` and writes the alignment in SAM format to `alignment.sam`.

---

## Examples of Popular Commands

Below are five common BWA-MEM usage examples:

1. **Indexing a reference genome with a custom prefix**:

~~~bash
bwa index -p ref_index reference.fa
~~~

Generates an index for `reference.fa` with the prefix `ref_index`.

2. **Single-end read alignment**:

~~~bash
bwa mem ref_index reads.fq > aligned_reads.sam
~~~

Aligns single-end reads in `reads.fq` to the reference indexed by `ref_index` and outputs the result to `aligned_reads.sam`.

3. **Paired-end read alignment**:

~~~bash
bwa mem ref_index reads_1.fq reads_2.fq > aligned_pair.sam
~~~

Aligns paired-end reads in `reads_1.fq` and `reads_2.fq` and saves them to `aligned_pair.sam`.

4. **Generating a sorted BAM file directly**:

~~~bash
bwa mem ref_index reads.fq | samtools sort -o sorted_reads.bam
~~~

Pipes the alignment output from BWA to samtools and sorts it before writing to `sorted_reads.bam`.

5. **Using extra options for speed or marking secondary alignments**:

~~~bash
bwa mem -t 4 -M ref_index reads.fq > aligned_reads.sam
~~~

- `-t 4`: Use 4 threads for faster alignment.
- `-M`: Mark shorter split alignments as secondary, which helps compatibility with certain downstream tools (e.g., Picard).

---

## Learning Objectives (Variant Calling Workflow)

- Exploring the variant calling workflow
- Choosing suitable BWA parameters for your dataset
- Understanding alignment clean-up steps

---

## Variant Calling Workflow

A typical variant calling workflow includes:

1. Quality control (QC)
2. Alignment (e.g., using BWA)
3. Alignment clean-up (e.g., marking duplicates, sorting)
4. Variant calling
5. Variant filtering and annotation

After obtaining raw sequencing data, you typically use tools like FastQC to check read quality. Next, you align the reads to a reference genome and clean up the alignments before applying variant-calling tools (e.g., GATK or samtools/bcftools) and then filter/annotate the resulting variants.

---

## Environment and Directory Setup

In a cluster environment (e.g., Harvard’s O2), the process might be as follows:

1. **Request an interactive session** (example command):

~~~bash
srun --pty -p interactive -t 0-6:00 --mem 8G -c 2 --reservation=HBC bash
~~~

2. **Create project directories**:

~~~bash
mkdir ~/var-calling
cd ~/var-calling

mkdir -p raw_data reference_data scripts logs meta results/bwa
~~~

3. **Copy required data**:

~~~bash
cp /n/groups/hbctraining/ngs-data-analysis-longcourse/var-calling/raw_fastq/*fq raw_data/
cp /n/groups/hbctraining/ngs-data-analysis-longcourse/var-calling/reference_data/chr20.fa reference_data/
~~~

In this tutorial, we use a subset of the Genome in a Bottle (GIAB) NA12878 data (human genome reads restricted to chromosome 20), consisting of ~4 million paired-end reads.

---

## QC and Alignment

1. **Skipping QC**: Typically you would use FastQC, but for demonstration we skip that step.
2. **Aligner choice**: BWA is often preferred in variant calling for its high accuracy. Minimal misalignment can help avoid false positives in variant detection.
3. **BWA modes**:
   - BWA-backtrack: Up to 100-bp reads
   - BWA-SW: Longer reads (70 bp ~ 1 Mbps) with split alignment
   - BWA-MEM: Newest, recommended for most use cases, supports long reads and high accuracy

In most variant-calling workflows, **BWA-MEM** is used.

---

## Using BWA-MEM for Alignment

### 1. Creating a BWA-MEM Index

~~~bash
cd ~/var-calling/reference_data
module load gcc/6.2.0 bwa/0.7.8

bwa index -p chr20 chr20.fa
~~~

- `-p chr20`: Uses `chr20` as the prefix for all index files.
- `chr20.fa`: Reference genome file (only chromosome 20 here).

### 2. Aligning Reads

~~~bash
cd ~/var-calling

bwa mem -M -t 2 \
  reference_data/chr20 \
  raw_data/na12878_1.fq raw_data/na12878_2.fq \
  2> logs/bwa.err \
  > results/bwa/na12878.sam
~~~

- `-M`: Marks shorter split hits as secondary, helpful for some downstream tools.
- `-t 2`: Uses 2 threads.
- `2> logs/bwa.err`: Redirects standard error to a log file.
- `> results/bwa/na12878.sam`: Writes output to `na12878.sam`.

---

## Alignment Clean-up

For variant calling, marking duplicates is crucial to avoid PCR artifact errors.

### 1. Installing/Loading Picard

~~~bash
module spider picard
module load picard/2.8.0
~~~

Usage:

~~~bash
java -jar $PICARD/picard-2.8.0.jar [ToolName] [options]
~~~

### 2. Sorting by Coordinate (SortSam)

Picard’s `SortSam` tool sorts SAM/BAM files by coordinate. Key options:
- `INPUT`: Input file (SAM/BAM)
- `OUTPUT`: Output file (SAM/BAM)
- `SORT_ORDER`: Sort order (e.g., coordinate, queryname)
- `VALIDATION_STRINGENCY`: Level of validation (set to `SILENT` to avoid errors from BWA’s unmapped flags)

Example:

~~~bash
cd results/bwa

java -Xmx8G -jar $PICARD/picard-2.8.0.jar SortSam \
  INPUT=na12878.sam \
  OUTPUT=na12878_sorted.sam \
  SORT_ORDER=coordinate \
  VALIDATION_STRINGENCY=SILENT
~~~

### 3. Marking Duplicates (MarkDuplicates)

Picard’s `MarkDuplicates` identifies and tags duplicate reads (PCR or optical) in BAM/SAM files. Key options:
- `INPUT`: Sorted input file
- `OUTPUT`: Output file
- `METRICS_FILE`: File to write duplication metrics
- `ASSUME_SORTED`: Set to true if the input is coordinate-sorted
- `VALIDATION_STRINGENCY`: Similar to above

Example:

~~~bash
java -Xmx8G -jar $PICARD/picard-2.8.0.jar MarkDuplicates \
  INPUT=na12878_sorted.sam \
  OUTPUT=na12878_sorted_marked.bam \
  METRICS_FILE=metrics.txt \
  ASSUME_SORTED=true \
  VALIDATION_STRINGENCY=SILENT
~~~

`-Xmx8G` ensures Java uses no more than 8 GB of memory (adjust if needed for larger data).

### 4. Creating an Index for the BAM File

Use samtools to index the marked BAM file for visualization or downstream steps:

~~~bash
module load gcc/6.2.0 samtools/1.9

samtools index na12878_sorted_marked.bam
~~~

---

## Summary

Following these steps, you have:
1. Used **BWA-MEM** to align reads to a reference genome
2. Sorted the alignment results
3. Marked duplicates
4. Created an index for the final BAM file

The resulting file can now be used in subsequent variant-calling pipelines (e.g., GATK or bcftools), followed by variant filtering and annotation. These materials are adapted from open-access teaching materials by the Harvard Chan Bioinformatics Core (HBC).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
