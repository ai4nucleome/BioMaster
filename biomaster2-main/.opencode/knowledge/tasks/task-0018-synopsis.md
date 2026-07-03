---
id: task-0018
title: Synopsis
summary: '## Synopsis This tutorial demonstrates how to explore, process, and manipulate
  SAM/BAM files using **samtools**. We will walk through installing samtools, creating
  a demo directory, converting between SAM and BAM form...'
keywords:
- samtools
- Synopsis
- '## Synopsis

  This tutorial demonstrates how to explore'
- process
- and manipulate SAM
- BAM files using **samtools**. We will walk through installing samtools
- creating a demo directory
- converting between SAM and BAM formats
- sorting
- indexing
- and selectively viewing alignments
- '## Installing samtools

  ```bash

  cd ~

  mkdir src'
- '# optional if you do not already have a src directory

  cd ~'
- src
- git clone https
- github.com
- 'htslib

  git clone https'
- 'cd samtools

  make

  cp samtools ~'
- bin
- '# move the samtools binary to your PATH

  ```'
- '## Setup

  1. **Create** a new directory from your home directory'
- '```bash'
- cd ~
- mkdir samtools-demo
- cd samtools-demo
- '```

  2. **Download** the sample SAM file and decompress'
- curl https
- s3.amazonaws.com
- samtools-tutorial
- sample.sam.gz > sample.sam.gz
- gzip -d sample.sam.gz
- '```'
- '## samtools help

  Typing `samtools` alone displays the available subcommands. Examples:

  ```bash

  samtools view

  samtools sort

  samtools depth

  ```'
- '## Converting SAM to BAM (`samtools view`)

  1. **Convert** the SAM file to BAM'
- samtools view -S -b sample.sam > sample.bam
- 'Here:

  '
path: .opencode/knowledge/tasks/task-0018-synopsis.md
origin_source: samtools
origin_page: 19
source_entry_index: 14
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: samtools
---

# Synopsis

## One-line description

## Synopsis This tutorial demonstrates how to explore, process, and manipulate SAM/BAM files using **samtools**. We will walk through installing samtools, creating a demo directory, converting between SAM and BAM form...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `samtools`
- Origin page: `19`
- Source entry index: `14`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0018`
- Analysis/tool category: `samtools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
## Synopsis
This tutorial demonstrates how to explore, process, and manipulate SAM/BAM files using **samtools**. We will walk through installing samtools, creating a demo directory, converting between SAM and BAM formats, sorting, indexing, and selectively viewing alignments.

---

## Installing samtools
~~~bash
cd ~
mkdir src          # optional if you do not already have a src directory
cd ~/src

git clone https://github.com/samtools/htslib
git clone https://github.com/samtools/samtools

cd samtools
make
cp samtools ~/bin  # move the samtools binary to your PATH
~~~

---

## Setup
1. **Create** a new directory from your home directory:

   ~~~bash
   cd ~
   mkdir samtools-demo
   cd samtools-demo
   ~~~
2. **Download** the sample SAM file and decompress:

   ~~~bash
   curl https://s3.amazonaws.com/samtools-tutorial/sample.sam.gz > sample.sam.gz
   gzip -d sample.sam.gz
   ~~~

---

## samtools help
Typing `samtools` alone displays the available subcommands. Examples:
~~~bash
samtools view
samtools sort
samtools depth
~~~

---

## Converting SAM to BAM (`samtools view`)
1. **Convert** the SAM file to BAM:
   ~~~bash
   samtools view -S -b sample.sam > sample.bam
   ~~~
   Here:
   - `-S` specifies the input is SAM.
   - `-b` specifies to output BAM.
   - The `>` redirect writes to `sample.bam`.
2. **Check** the BAM contents (by converting back to SAM and showing only the first few lines):
   ~~~bash
   samtools view sample.bam | head
   ~~~

---

## Sorting alignments (`samtools sort`)
1. **Sort** the BAM so alignments are in order by genomic position:
   ~~~bash
   samtools sort sample.bam -o sample.sorted.bam
   ~~~
2. **Inspect** a few lines:
   ~~~bash
   samtools view sample.sorted.bam | head
   ~~~
   Now the coordinates should appear in ascending order.

---

## Indexing a sorted BAM (`samtools index`)
1. **Index** the sorted BAM:
   ~~~bash
   samtools index sample.sorted.bam
   ~~~
2. **Check** for the newly created index file (`.bai` extension):
   ~~~bash
   ls
   ~~~
3. **Use** the index to extract alignments from chromosome 1, positions `33,000,000–34,000,000`:
   ~~~bash
   samtools view sample.sorted.bam 1:33000000-34000000
   ~~~
   And count how many alignments are in that region:
   ~~~bash
   samtools view sample.sorted.bam 1:33000000-34000000 | wc -l
   ~~~

---

## More on `samtools view`
### Viewing a subset of alignments

- **Print** the first five lines:
  ~~~bash
  samtools view sample.sorted.bam | head -n 5
  ~~~
- **Make FLAG more readable** with `-X`:
  ~~~bash
  samtools view -X sample.sorted.bam | head -n 5
  ~~~
  (Try `samtools view -?` for help on all options.)

### Counting alignments
~~~bash
samtools view sample.sorted.bam | wc -l
~~~

### Inspecting the header
~~~bash
samtools view -H sample.sorted.bam
~~~

### Filtering by FLAG
- **Proper pairs** only (`-f 0x2`):
  ~~~bash
  samtools view -f 0x2 sample.sorted.bam | wc -l
  ~~~
- **NOT properly paired** (`-F 0x2`):
  ~~~bash
  samtools view -F 0x2 sample.sorted.bam | wc -l
  ~~~
  `-F` indicates **exclude** flags. The counts of `-f 0x2` plus `-F 0x2` should sum to the total number of alignments.

---

## Summary
1. **Install** samtools.
2. **Convert** SAM→BAM.
3. **Sort** by genomic position.
4. **Index** to enable region queries.
5. **View** subsets of data based on coordinates or specific flags.
6. **Inspect** headers and other metadata.

This workflow covers basic operations required for many downstream applications (e.g., variant calling or visualization in IGV). For more details, consult the [samtools documentation](https://www.htslib.org/).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
