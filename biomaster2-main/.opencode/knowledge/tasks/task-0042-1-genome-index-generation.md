---
id: task-0042
title: 1. Genome Index Generation
summary: '### 1. Genome Index Generation To use STAR, you first need to generate genome
  indexes from reference genome FASTA and annotation GTF files: ```bash STAR --runThreadN
  8 \ --runMode genomeGenerate \ --genomeDir /path/to...'
keywords:
- star
- STAR
- 1. Genome Index Generation
- '### 1. Genome Index Generation

  To use STAR'
- you first need to generate genome indexes from reference genome FASTA and annotation
  GTF files
- '```bash

  STAR --runThreadN 8 \'
- runMode genomeGenerate \
- genomeDir
- path
- to
- genomeDir \
- genomeFastaFiles
- genome.fa \
- sjdbGTFfile
- annotations.gtf \
- 'sjdbOverhang 99

  ```'
- '**Option explanations:**

  - `--runThreadN`: Number of threads to use. Should match the available CPU cores.

  - `--runMode genomeGenerate`: Tells STAR to generate genome indices.

  - `--genomeDir`: Directory where the genome index will be saved. Must be created
  beforehand and have write permission.

  - `--genomeFastaFiles`: Reference genome file(s) in FASTA format.

  - `--sjdbGTFfile`: Gene annotations in GTF format (optional but highly recommended).

  - `--sjdbOverhang`: ReadLength - 1. For example'
- for 100 bp reads
- use 99
- Make sure the chromosome names in the GTF and FASTA files match exactly (e.g. both
  use `chr1`
- '`chr2`'
- etc.)
- '### 2. Read Mapping

  After index generation'
- map reads using the following command
- readFilesIn
- read1.fq
- read2.fq
path: .opencode/knowledge/tasks/task-0042-1-genome-index-generation.md
origin_source: STAR
origin_page: 43
source_entry_index: 38
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: star
---

# 1. Genome Index Generation

## One-line description

### 1. Genome Index Generation To use STAR, you first need to generate genome indexes from reference genome FASTA and annotation GTF files: ```bash STAR --runThreadN 8 \ --runMode genomeGenerate \ --genomeDir /path/to...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `STAR`
- Origin page: `43`
- Source entry index: `38`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0042`
- Analysis/tool category: `star`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
### 1. Genome Index Generation
To use STAR, you first need to generate genome indexes from reference genome FASTA and annotation GTF files:

~~~bash
STAR --runThreadN 8 \
     --runMode genomeGenerate \
     --genomeDir /path/to/genomeDir \
     --genomeFastaFiles /path/to/genome.fa \
     --sjdbGTFfile /path/to/annotations.gtf \
     --sjdbOverhang 99
~~~

**Option explanations:**
- `--runThreadN`: Number of threads to use. Should match the available CPU cores.
- `--runMode genomeGenerate`: Tells STAR to generate genome indices.
- `--genomeDir`: Directory where the genome index will be saved. Must be created beforehand and have write permission.
- `--genomeFastaFiles`: Reference genome file(s) in FASTA format.
- `--sjdbGTFfile`: Gene annotations in GTF format (optional but highly recommended).
- `--sjdbOverhang`: ReadLength - 1. For example, for 100 bp reads, use 99.

Make sure the chromosome names in the GTF and FASTA files match exactly (e.g. both use `chr1`, `chr2`, etc.).

### 2. Read Mapping
After index generation, map reads using the following command:

~~~bash
STAR --runThreadN 8 \
     --genomeDir /path/to/genomeDir \
     --readFilesIn /path/to/read1.fq /path/to/read2.fq \
     --outFileNamePrefix /path/to/output/sample_
~~~

**Optional flags:**
- `--readFilesCommand zcat`: For gzipped files.
- `--outSAMtype BAM SortedByCoordinate`: Direct output to sorted BAM file.
- `--outSAMunmapped Within`: Include unmapped reads in BAM.
- `--quantMode GeneCounts`: Count reads per gene.

### 3. Output Files
- `Aligned.out.sam`: default alignment in SAM format.
- `Aligned.sortedByCoord.out.bam`: coordinate-sorted BAM output (if specified).
- `ReadsPerGene.out.tab`: gene-level read count (if `--quantMode GeneCounts` used).
- `SJ.out.tab`: detected splice junctions.
- `Log.out`, `Log.progress.out`, `Log.final.out`: run logs and summary statistics.

### 4. Example Workflow (Paired-End gzipped FASTQ):
~~~bash
STAR --runThreadN 12 \
     --genomeDir ./GenomeDir \
     --readFilesIn sample_R1.fastq.gz sample_R2.fastq.gz \
     --readFilesCommand zcat \
     --outFileNamePrefix ./output/sample_ \
     --outSAMtype BAM SortedByCoordinate \
     --quantMode GeneCounts
~~~

This will map reads to genome, output a sorted BAM file, and generate gene count summary.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
