---
id: task-0017
title: samtools – Utilities for the Sequence Alignment/Map (SAM) format
summary: '# samtools – Utilities for the Sequence Alignment/Map (SAM) format ## NAME
  **samtools** – A suite of programs for manipulating alignments in the SAM (Sequence
  Alignment/Map), BAM, and CRAM formats. ## SYNOPSIS (Select...'
keywords:
- samtools
- samtools – Utilities for the Sequence Alignment
- Map (SAM) format
- '# samtools – Utilities for the Sequence Alignment'
- '## NAME

  **samtools** – A suite of programs for manipulating alignments in the SAM (Sequence
  Alignment'
- Map)
- BAM
- and CRAM formats
- '## SYNOPSIS (Selected Examples)'
- '```bash

  samtools addreplacerg -r ''ID:fish'' -r ''LB:1334'' -r ''SM:alpha'' -o output.bam
  input.bam

  samtools ampliconclip -b bed.file input.bam

  samtools ampliconstats primers.bed in.bam

  samtools bedcov aln.sorted.bam

  samtools calmd in.sorted.bam ref.fasta

  samtools cat out.bam in1.bam in2.bam in3.bam

  samtools collate -o aln.name_collated.bam aln.sorted.bam

  samtools consensus -o out.fasta in.bam

  samtools coverage aln.sorted.bam

  samtools cram-size -v -o out.size in.cram

  samtools depad input.bam

  samtools depth aln.sorted.bam

  samtools dict -a GRCh38 -s "Homo sapiens" ref.fasta

  samtools faidx ref.fasta

  samtools fasta input.bam > output.fasta

  samtools fastq input.bam > output.fastq

  samtools fixmate in.namesorted.sam out.bam

  samtools flags PAIRED'
- UNMAP
- 'MUNMAP

  samtools flagstat aln.sorted.bam

  samtools fqidx ref.fastq

  samtools head in.bam

  samtools idxstats aln.sorted.bam

  samtools import input.fastq > output.bam

  samtools index aln.sorted.bam

  samtools markdup in.algnsort'
path: .opencode/knowledge/tasks/task-0017-samtools-utilities-for-the-sequence-alignment-map-sam-format.md
origin_source: samtools
origin_page: 18
source_entry_index: 13
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: samtools
---

# samtools – Utilities for the Sequence Alignment/Map (SAM) format

## One-line description

# samtools – Utilities for the Sequence Alignment/Map (SAM) format ## NAME **samtools** – A suite of programs for manipulating alignments in the SAM (Sequence Alignment/Map), BAM, and CRAM formats. ## SYNOPSIS (Select...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `samtools`
- Origin page: `18`
- Source entry index: `13`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0017`
- Analysis/tool category: `samtools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
# samtools – Utilities for the Sequence Alignment/Map (SAM) format

## NAME
**samtools** – A suite of programs for manipulating alignments in the SAM (Sequence Alignment/Map), BAM, and CRAM formats.

## SYNOPSIS (Selected Examples)

~~~bash
samtools addreplacerg -r 'ID:fish' -r 'LB:1334' -r 'SM:alpha' -o output.bam input.bam
samtools ampliconclip -b bed.file input.bam
samtools ampliconstats primers.bed in.bam
samtools bedcov aln.sorted.bam
samtools calmd in.sorted.bam ref.fasta
samtools cat out.bam in1.bam in2.bam in3.bam
samtools collate -o aln.name_collated.bam aln.sorted.bam
samtools consensus -o out.fasta in.bam
samtools coverage aln.sorted.bam
samtools cram-size -v -o out.size in.cram
samtools depad input.bam
samtools depth aln.sorted.bam
samtools dict -a GRCh38 -s "Homo sapiens" ref.fasta
samtools faidx ref.fasta
samtools fasta input.bam > output.fasta
samtools fastq input.bam > output.fastq
samtools fixmate in.namesorted.sam out.bam
samtools flags PAIRED,UNMAP,MUNMAP
samtools flagstat aln.sorted.bam
samtools fqidx ref.fastq
samtools head in.bam
samtools idxstats aln.sorted.bam
samtools import input.fastq > output.bam
samtools index aln.sorted.bam
samtools markdup in.algnsorted.bam out.bam
samtools merge out.bam in1.bam in2.bam in3.bam
samtools mpileup -f ref.fasta -r chr3:1,000-2,000 in1.bam in2.bam
samtools phase input.bam
samtools quickcheck in1.bam in2.cram
samtools reference -o ref.fa in.cram
samtools reheader in.header.sam in.bam > out.bam
samtools reset -o /tmp/reset.bam processed.bam
samtools samples input.bam
samtools sort -T /tmp/aln.sorted -o aln.sorted.bam aln.bam
samtools split merged.bam
samtools stats aln.sorted.bam
samtools targetcut input.bam
samtools tview aln.sorted.bam ref.fasta
samtools view -bt ref_list.txt -o aln.bam aln.sam.gz
~~~

## BRIEF DESCRIPTION
Samtools converts between SAM/BAM/CRAM formats, sorts and merges alignments, indexes them for fast random access, and retrieves reads within specific genomic regions. It can read/write compressed data, works well in pipelines, and supports remote file access.

## SELECTED COMMANDS

### samtools view
~~~bash
samtools view [options] in.bam [region...]
~~~
- Converts input to SAM/BAM/CRAM.
- If indexed and region(s) are specified, outputs only alignments overlapping those regions.

### samtools tview
~~~bash
samtools tview in.sorted.bam [ref.fasta]
~~~
- Text-based viewer for alignments. Press `?` for help.

### samtools quickcheck
~~~bash
samtools quickcheck in.bam in.cram
~~~
- Quickly checks if files are intact (e.g., valid header, EOF block in BAM).

### samtools head
~~~bash
samtools head in.bam
~~~
- Prints file headers and optionally the first few alignments.

### samtools index
~~~bash
samtools index aln.bam
~~~
- Indexes a coordinate-sorted BAM or CRAM file for fast region queries.

### samtools sort
~~~bash
samtools sort -o aln.sorted.bam aln.bam
~~~
- Sorts alignments by coordinate (default) or by name (`-n`).

### samtools collate
~~~bash
samtools collate -o aln.name_collated.bam aln.sorted.bam
~~~
- Groups reads by name, without full sorting.

### samtools idxstats
~~~bash
samtools idxstats aln.sorted.bam
~~~
- Reports reference sequence length, mapped reads, and unmapped reads.

### samtools flagstat
~~~bash
samtools flagstat aln.sorted.bam
~~~
- Gives overall alignment statistics (number of mapped/unmapped reads, duplicates, etc.).

### samtools mpileup
~~~bash
samtools mpileup -f ref.fasta in1.bam in2.bam
~~~
- Generates textual pileup of reads.

### samtools consensus
~~~bash
samtools consensus -o out.fasta in.bam
~~~
- Creates consensus sequence from alignment data.

### samtools coverage
~~~bash
samtools coverage aln.sorted.bam
~~~
- Produces coverage stats per chromosome or region.

### samtools merge
~~~bash
samtools merge out.bam in1.bam in2.bam
~~~
- Merges multiple sorted BAM/CRAM files into one.

### samtools split
~~~bash
samtools split merged.bam
~~~
- Splits one file into separate files by read group.

### samtools cat
~~~bash
samtools cat out.bam in1.bam in2.bam
~~~
- Concatenates BAM/CRAM files of the same format.

### samtools fastq/fasta
~~~bash
samtools fastq in.bam > out.fastq
samtools fasta in.bam > out.fasta
~~~
- Converts BAM/CRAM to FASTQ or FASTA.

### samtools faidx
~~~bash
samtools faidx ref.fasta
~~~
- Indexes a FASTA file or extracts subsequences if regions are given.

### samtools fqidx
~~~bash
samtools fqidx ref.fastq
~~~
- Similar to faidx but for FASTQ (small files only).

### samtools calmd
~~~bash
samtools calmd aln.bam ref.fasta
~~~
- Adds or updates the MD tag.

### samtools fixmate
~~~bash
samtools fixmate in.nameSrt.bam out.bam
~~~
- Fills in mate coordinates, ISIZE, and flags from a name-sorted file.

### samtools markdup
~~~bash
samtools markdup in.algnsorted.bam out.bam
~~~
- Marks duplicate reads after fixmate.

### samtools reheader
~~~bash
samtools reheader in.header.sam in.bam > out.bam
~~~
- Replaces the header without re-converting the entire file.

### samtools stats
~~~bash
samtools stats aln.sorted.bam
~~~
- Collects alignment statistics, output can be plotted with plot-bamstats.

---

## AUTHOR & LINKS
- Original author: Heng Li (Sanger Institute).
- Project page: [http://www.htslib.org/](http://www.htslib.org/)
- Code repositories:
  - [Samtools GitHub](https://github.com/samtools/samtools)
  - [HTSlib GitHub](https://github.com/samtools/htslib)
  - [Bcftools GitHub](http://samtools.github.io/bcftools)
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
