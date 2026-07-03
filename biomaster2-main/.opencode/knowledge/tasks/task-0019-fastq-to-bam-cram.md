---
id: task-0019
title: FASTQ to BAM/CRAM
summary: '## FASTQ to BAM/CRAM Modern sequencing instruments typically produce *unaligned*
  data in FASTQ format. We can store unaligned data in BAM or CRAM to include valuable
  metadata (e.g., headers, auxiliary tags), but the f...'
keywords:
- samtools
- FASTQ to BAM
- CRAM
- '## FASTQ to BAM'
- 'CRAM

  Modern sequencing instruments typically produce *unaligned* data in FASTQ format.
  We can store unaligned data in BAM or CRAM to include valuable metadata (e.g'
- headers
- auxiliary tags)
- but the focus here is on producing a **sorted
- aligned** BAM or CRAM file
- '## Two Main Approaches

  1. **Alignment'
- 'mapping** to a known reference.

  2. **De-novo assembly** (not covered in detail here)'
- '## Example Workflow for Alignment'
- This pipeline takes paired FASTQ reads
- aligns them to a reference using Minimap2
- and produces a sorted
- duplicate-marked BAM or CRAM
- '### Steps Overview

  1. **Map'
- 'align**

  2. **Fix mate-pair issues** (e.g'
- 'with `samtools fixmate`)

  3. **Mark duplicates (part 1)** – add tags needed for later duplication marking

  4. **Sort** to positional order

  5. **Mark duplicates (part 2)** – final marking of duplicates

  6. **Convert** to final file format (BAM or CRAM)'
- '### Step 1: Mapping

  ```bash

  minimap2 -t 8 -a -x sr C.Elegans.fa \'
- 'SRR065390_1.fastq SRR065390_2.fastq -o CE.sam

  ```

  - `-t 8`: uses 8 threads.

  - `-a`: output in SAM.

  - `-x sr`: sets Minimap2 presets for paired-end short reads.

  - Output is name-collated (read pairs are together)'
- whi
path: .opencode/knowledge/tasks/task-0019-fastq-to-bam-cram.md
origin_source: samtools
origin_page: 20
source_entry_index: 15
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: samtools
---

# FASTQ to BAM/CRAM

## One-line description

## FASTQ to BAM/CRAM Modern sequencing instruments typically produce *unaligned* data in FASTQ format. We can store unaligned data in BAM or CRAM to include valuable metadata (e.g., headers, auxiliary tags), but the f...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `samtools`
- Origin page: `20`
- Source entry index: `15`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0019`
- Analysis/tool category: `samtools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
## FASTQ to BAM/CRAM
Modern sequencing instruments typically produce *unaligned* data in FASTQ format. We can store unaligned data in BAM or CRAM to include valuable metadata (e.g., headers, auxiliary tags), but the focus here is on producing a **sorted, aligned** BAM or CRAM file.

---

## Two Main Approaches
1. **Alignment / mapping** to a known reference.
2. **De-novo assembly** (not covered in detail here).

---

## Example Workflow for Alignment

This pipeline takes paired FASTQ reads, aligns them to a reference using Minimap2, and produces a sorted, duplicate-marked BAM or CRAM.

### Steps Overview
1. **Map / align**
2. **Fix mate-pair issues** (e.g., with `samtools fixmate`)
3. **Mark duplicates (part 1)** – add tags needed for later duplication marking
4. **Sort** to positional order
5. **Mark duplicates (part 2)** – final marking of duplicates
6. **Convert** to final file format (BAM or CRAM)

### Step 1: Mapping
~~~bash
minimap2 -t 8 -a -x sr C.Elegans.fa \
  SRR065390_1.fastq SRR065390_2.fastq -o CE.sam
~~~
- `-t 8`: uses 8 threads.
- `-a`: output in SAM.
- `-x sr`: sets Minimap2 presets for paired-end short reads.
- Output is name-collated (read pairs are together), which is needed for the next step.

### Step 2: Fixing Mate-Pair Issues
~~~bash
samtools fixmate -O bam,level=1 CE.sam fixmate.bam
~~~
- `samtools fixmate` checks and corrects mate information (FLAG, RNEXT, PNEXT, TLEN).
- `-O bam,level=1` outputs BAM with minimal compression for speed.
- Add `-m` if you want to populate mate CIGAR (`MC`) and mate score (`ms`) tags:

  ~~~bash
  samtools fixmate -O bam,level=1 -m CE.sam fixmate.bam
  ~~~

### Step 3 & 4: Sorting to Positional Order
~~~bash
samtools sort -l 1 -@8 -o pos.srt.bam -T /tmp/example_prefix fixmate.bam
~~~
- Sort reads by genomic coordinate.
- `-@8`: uses 8 threads.
- `-l 1`: minimal compression (optional).
- `-T /tmp/example_prefix`: prefix for temporary sorting files.

### Step 5: Marking Duplicates
~~~bash
samtools markdup -O bam,level=1 pos.srt.bam markdup.bam
~~~
- Uses the MC/ms tags from the `-m` fixmate step.

### Step 6: Converting to Final Format
~~~bash
samtools view -@8 markdup.bam -o final.bam
~~~
or, to produce CRAM:
~~~bash
samtools view -T C.Elegans.fa -@8 markdup.bam -o final.cram
~~~

---

## Pipelining for Efficiency
Instead of writing each intermediate file to disk, we can **pipe** the commands:
~~~bash
minimap2 -t 8 -a -x sr C.Elegans.fa SRR065390_[12].fastq | \
samtools fixmate -u -m - - | \
samtools sort -u -@2 -T /tmp/example_prefix - | \
samtools markdup -@8 --reference C.Elegans.fa - final.cram
~~~
- `-u` or `-O bam,level=0` keeps data uncompressed in the pipeline for speed.
- `set -o pipefail` helps detect errors in earlier commands.

---

## Converting Back to FASTQ
If the unmapped reads were retained, you can revert your final BAM/CRAM to FASTQ:
~~~bash
samtools sort -n -@8 final.cram | \
samtools fastq - -1 dat_1.fq -2 dat_2.fq > /dev/null
~~~
- Sorting by read name (`-n`) is required before producing paired FASTQ.
- The original exact FASTQ order is not preserved but is generally unimportant for reanalysis.

---

## De-novo Assembly
- Assemblers produce a consensus FASTA or FASTQ rather than individual alignments.
- If you need per-read alignments to the newly assembled consensus, just build an index on the assembly and follow the same **Mapping** steps as above.
- For CRAM, ensure you have access to the same consensus reference or embed it:
  ~~~bash
  samtools view -O CRAM,embed_ref in.sam -o out.cram
  ~~~

---

## Key Takeaways
- **Name-collated** BAM is essential for certain steps (e.g., `fixmate`, partial duplication marking).
- **Coordinate-sorted** BAM is needed for final duplicate marking and most downstream analyses.
- **Pipelines** avoid intermediate files, are faster, and use uncompressed or minimal-compression data in memory.
- **CRAM** can reduce storage size but requires consistent references.
- Always verify each step with basic stats (`samtools flagstat`, etc.) to ensure no unexpected data loss.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
