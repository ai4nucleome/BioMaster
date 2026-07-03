---
id: task-0027
title: SortMeRNA Usage Documentation
summary: '# SortMeRNA Usage Documentation SortMeRNA is a tool designed for detecting
  and filtering out rRNA reads from sequencing libraries. It supports both single-end
  and paired-end data, and automatically recognizes file for...'
keywords:
- star
- SortMeRNA
- SortMeRNA Usage Documentation
- '# SortMeRNA Usage Documentation'
- SortMeRNA is a tool designed for detecting and filtering out rRNA reads from sequencing
  libraries. It supports both single-end and paired-end data
- and automatically recognizes file formats and compression (e.g. plain fasta
- fastq or gzipped files)
- '## 1. Installation'
- '### Using conda'
- Install SortMeRNA with the following command
- '```bash

  conda install sortmerna

  ```'
- Verify the installation by checking the version
- '```bash

  $ sortmerna --version

  SortMeRNA version 4.3.2

  Build Date: Apr'
- '2 2021

  ```'
- '## 2. Basic Usage'
- The only required options are `--ref` and `--reads`. Options can be specified using
  a single dash (e.g. `-ref` and `-reads`). File extensions are optional because the
  format and compression are automatically recognized
- '### Example Commands'
- '**Single Reference and Single Reads File**'
- '```bash

  sortmerna --ref REF_PATH --reads READS_PATH

  ```'
- '**Multiple References**'
- '```bash

  sortmerna --ref REF_PATH_1 --ref REF_PATH_2 --ref REF_PATH_3 --reads READS_PATH

  ```'
- '**Paired-End Reads**'
- '```bash

  sortmerna --ref REF_PATH_1 --ref REF_PATH_2 --ref REF_PATH_3 --reads READS_PATH_1
  --reads READS_PATH_2

  ```'
- '## 3. Example: Identifying'
- STAR
path: .opencode/knowledge/tasks/task-0027-sortmerna-usage-documentation.md
origin_source: SortMeRNA
origin_page: 28
source_entry_index: 23
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-conda
tool: star
---

# SortMeRNA Usage Documentation

## One-line description

# SortMeRNA Usage Documentation SortMeRNA is a tool designed for detecting and filtering out rRNA reads from sequencing libraries. It supports both single-end and paired-end data, and automatically recognizes file for...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `SortMeRNA`
- Origin page: `28`
- Source entry index: `23`
- Source subindex: `1`
- Canonical skill: `exec-conda`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-conda`
- Registry ID: `task-0027`
- Analysis/tool category: `star`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
# SortMeRNA Usage Documentation

SortMeRNA is a tool designed for detecting and filtering out rRNA reads from sequencing libraries. It supports both single-end and paired-end data, and automatically recognizes file formats and compression (e.g. plain fasta/fastq or gzipped files).

---

## 1. Installation

### Using conda

Install SortMeRNA with the following command:

~~~bash
conda install sortmerna
~~~

Verify the installation by checking the version:

~~~bash
$ sortmerna --version
SortMeRNA version 4.3.2
Build Date: Apr  2 2021
~~~

---

## 2. Basic Usage

The only required options are `--ref` and `--reads`. Options can be specified using a single dash (e.g. `-ref` and `-reads`). File extensions are optional because the format and compression are automatically recognized.

### Example Commands

**Single Reference and Single Reads File**:

~~~bash
sortmerna --ref REF_PATH --reads READS_PATH
~~~

**Multiple References**:

~~~bash
sortmerna --ref REF_PATH_1 --ref REF_PATH_2 --ref REF_PATH_3 --reads READS_PATH
~~~

**Paired-End Reads**:

~~~bash
sortmerna --ref REF_PATH_1 --ref REF_PATH_2 --ref REF_PATH_3 --reads READS_PATH_1 --reads READS_PATH_2
~~~

---

## 3. Example: Identifying Bacterial 16S rRNA

The following command identifies rRNA in the file `DRR110568_1.fastq` using the bacterial 16S rRNA database. rRNA-matched sequences are saved to `DRR110568.1.16s` while non-matched sequences are saved to `DRR110568.1.non.16s`.

~~~bash
./sortmerna \
  --ref rRNA_databases/silva-bac-16s-id90.fasta,/index/silva-bac-16s-db: \
  --reads DRR110568_1.fastq \
  --aligned DRR110568.1.16s \    # rRNA-matched sequences
  --sam --num_alignments 1 --fastx \
  --other DRR110568.1.non.16s \   # non-rRNA sequences
  --log -v
~~~

---

## 4. Indexing rRNA Databases

To avoid re-indexing at every run, pre-build the index for your rRNA databases. Once the index is built, copy the generated `idx/` directory to your working directory.

### Indexing Command Example:

~~~bash
sortmerna --index 1 --threads 32 \
  --ref ~/sortmerna4.3/rRNA_databases/silva-bac-16s-id90.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-bac-23s-id98.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-arc-16s-id95.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-arc-23s-id98.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-euk-18s-id95.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-euk-28s-id98.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/rfam-5s-database-id98.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/rfam-5.8s-database-id98.fasta \
  --workdir ./
~~~

After indexing, the working directory will include the following folders:

~~~
WORKDIR/
  idx/    (index files)
  kvdb/   (key-value alignment results)
  out/    (output files)
  readb/  (preprocessed reads index)
~~~

> **Note:** Ensure the `kvdb/` directory is empty before each run to avoid errors.

---

## 5. Removing rRNA Reads from Paired-End Data

The following command removes rRNA reads from paired-end sequencing data. The output files will retain the input format (e.g. `.fq.gz`).

~~~bash
sortmerna --index 0 --threads 48 \
  --ref ~/sortmerna4.3/rRNA_databases/silva-bac-16s-id90.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-bac-23s-id98.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-arc-16s-id95.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-arc-23s-id98.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-euk-18s-id95.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/silva-euk-28s-id98.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/rfam-5s-database-id98.fasta \
  --ref ~/sortmerna4.3/rRNA_databases/rfam-5.8s-database-id98.fasta \
  --workdir ./ \
  --reads NR1.fq.gz \
  --reads NR2.fq.gz \
  --aligned "NR/N_rRNA" --other "NR/N_clean" --paired_in --fastx --out2
~~~

### Expected Output

After running, the output directory (e.g. `NR/`) should contain files such as:

~~~
N_clean_fwd.fq.gz  N_clean_rev.fq.gz
N_rRNA_fwd.fq.gz   N_rRNA_rev.fq.gz
N_rRNA.log
~~~

The log file provides statistics on the total reads classified as rRNA versus non-rRNA, along with coverage by each reference database.

---

## 6. Key Parameters and Options

- **--ref**: Specify the reference fasta file. Use multiple times for multiple databases.
- **--reads**: Input reads file. For paired-end data, provide this option twice.
- **--aligned**: Output for reads that match the rRNA database. Can include a path and prefix for the output file.
- **--other**: Output for reads that do not match the rRNA database.
- **--index**: Controls indexing behavior:
  - `--index 1`: Only build the index.
  - `--index 0`: Skip indexing (requires an existing index in the `idx/` directory).
  - Default (or `--index 2`): Automatically detect or build the index if not found.
- **--sam**: Output alignments in SAM format.
- **--fastx**: Output in fasta/fastq format, matching the input format.
- **--num_alignments INT**: Specifies the number of alignments to output. Use `1` for faster filtering; higher values increase runtime.
- **--paired_in / --paired_out**: Control output handling for paired-end reads.
  - `--paired_in`: Outputs non-rRNA reads to the `other` file (although a few rRNA reads might be included).
  - `--paired_out`: Ensures rRNA reads appear only in the aligned file (with a chance of non-rRNA reads also appearing in the other file).

---

## 7. Advanced Options

SortMeRNA includes additional parameters for fine-tuning alignment sensitivity and speed:

- **--num_seeds INT**: Minimum number of seed matches required (default: 2).
- **passes INT,INT,INT**: Adjusts seed search passes using decreasing intervals (default: L, L/2, L/3).
- **--edges INT(%)**: Extends the alignment region on the reference by a set number of nucleotides (default: 4).
- **--full_search**: Disables early termination upon finding 0-error seed matches, which can increase sensitivity but decrease speed up to four-fold.
- **--pid**: Appends the process ID to output filenames to avoid overwriting files from concurrent runs.

---

## 8. Summary

SortMeRNA is a powerful tool for rRNA detection and removal from sequencing libraries. It offers:

- Automatic recognition of input file formats and compression.
- Support for both single-end and paired-end data.
- Flexible parameter settings for balancing speed and sensitivity.
- Compatibility with standard rRNA databases such as SILVA and Rfam.

While SortMeRNA is highly sensitive, for quick rRNA estimation some users might prefer aligners like STAR or Bowtie2. However, for comprehensive rRNA filtering, SortMeRNA remains an effective solution.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
