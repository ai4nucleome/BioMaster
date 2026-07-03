---
id: task-0037
title: To install this package run one of the following:conda install bioconda::rmats
  conda install bioc...
summary: 'To install this package run one of the following:conda install bioconda::rmats
  conda install bioconda/label/cf201901::rmats ,rMATS: rMATS (replicate Multivariate
  Analysis of Transcript Splicing) is a computational too...'
keywords:
- samtools
- rMATS
- To install this package run one of the following:conda install bioconda::rmats conda
  install bioc
- To install this package run one of the following:conda install bioconda::rmats conda
  install bioconda
- label
- cf201901::rmats
- 'rMATS: rMATS (replicate Multivariate Analysis of Transcript Splicing) is a computational
  tool designed for detecting differential alternative splicing events from RNA-Seq
  data with biological replicates. It quantifies splicing variations by computing
  inclusion levels and applying a likelihood-ratio test for statistical significance'
- '### Supported Alternative Splicing Events:

  - **Skipped exon (SE)** - Exon skipping events.

  - **Alternative 5'' splice site (A5SS)** - Variable splice site at the 5'' end.

  - **Alternative 3'' splice site (A3SS)** - Variable splice site at the 3'' end.

  - **Mutually exclusive exons (MXE)** - Selection between two alternative exons.

  - **Retained intron (RI)** - Intron retention events'
- '### Dependencies:

  - Python (>=3.6.12 or 2.7.15)

  - Cython (0.29.21 or 0.29.15 for Python 2)

  - numpy (>=1.16.6)

  - BLAS'
- 'LAPACK

  - GNU Scientific Library (GSL 2.5)

  - GCC (>=5.4.0)

  - gfortran (Fortran 77)

  - CMake (3.15.4)

  - PAIRADISE (optional)

  - Samtools (optional)

  - STAR (optional)'
- '### Installation & Setup:

  ```bash

  # Build rMATS with required dependencies

  '
- STAR
path: .opencode/knowledge/tasks/task-0037-to-install-this-package-run-one-of-the-following-conda-install-bioconda-rmats-conda-install-bioc.md
origin_source: rMATS
origin_page: 38
source_entry_index: 33
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-conda
tool: samtools
---

# To install this package run one of the following:conda install bioconda::rmats conda install bioc...

## One-line description

To install this package run one of the following:conda install bioconda::rmats conda install bioconda/label/cf201901::rmats ,rMATS: rMATS (replicate Multivariate Analysis of Transcript Splicing) is a computational too...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `rMATS`
- Origin page: `38`
- Source entry index: `33`
- Source subindex: `1`
- Canonical skill: `exec-conda`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-conda`
- Registry ID: `task-0037`
- Analysis/tool category: `samtools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
To install this package run one of the following:conda install bioconda::rmats conda install bioconda/label/cf201901::rmats ,rMATS: rMATS (replicate Multivariate Analysis of Transcript Splicing) is a computational tool designed for detecting differential alternative splicing events from RNA-Seq data with biological replicates. It quantifies splicing variations by computing inclusion levels and applying a likelihood-ratio test for statistical significance. 

### Supported Alternative Splicing Events:
- **Skipped exon (SE)** - Exon skipping events.
- **Alternative 5' splice site (A5SS)** - Variable splice site at the 5' end.
- **Alternative 3' splice site (A3SS)** - Variable splice site at the 3' end.
- **Mutually exclusive exons (MXE)** - Selection between two alternative exons.
- **Retained intron (RI)** - Intron retention events.

### Dependencies:
- Python (>=3.6.12 or 2.7.15)
- Cython (0.29.21 or 0.29.15 for Python 2)
- numpy (>=1.16.6)
- BLAS, LAPACK
- GNU Scientific Library (GSL 2.5)
- GCC (>=5.4.0)
- gfortran (Fortran 77)
- CMake (3.15.4)
- PAIRADISE (optional)
- Samtools (optional)
- STAR (optional)

### Installation & Setup:
~~~bash
# Build rMATS with required dependencies
./build_rmats --conda

# Running rMATS with conda environment
./run_rmats {arguments}
~~~

### Usage:
#### **Running with FASTQ files**
1. Prepare sample lists in a text file:
~~~bash
# Sample 1 FASTQ list (paired-end reads separated by ':', replicates by ',')
echo '/path/to/1_1.R1.fastq:/path/to/1_1.R2.fastq,/path/to/1_2.R1.fastq:/path/to/1_2.R2.fastq' > s1.txt

echo '/path/to/2_1.R1.fastq:/path/to/2_1.R2.fastq,/path/to/2_2.R1.fastq:/path/to/2_2.R2.fastq' > s2.txt
~~~
2. Run rMATS with FASTQ input:
~~~bash
python rmats.py --s1 s1.txt --s2 s2.txt --gtf annotation.gtf --bi STAR_index/ -t paired --readLength 50 --nthread 4 --od results/ --tmp temp/
~~~

#### **Running with BAM files**
1. Prepare BAM file lists:
~~~bash
echo '/path/to/1_1.bam,/path/to/1_2.bam' > b1.txt
echo '/path/to/2_1.bam,/path/to/2_2.bam' > b2.txt
~~~
2. Run rMATS with BAM input:
~~~bash
python rmats.py --b1 b1.txt --b2 b2.txt --gtf annotation.gtf -t paired --readLength 50 --nthread 4 --od results/ --tmp temp/
~~~

### **Running rMATS in Steps:**
- **Prep phase** (extract and process alignments):
~~~bash
python rmats.py --b1 b1.txt --gtf annotation.gtf -t paired --readLength 50 --nthread 4 --od output/ --tmp tmp_prep --task prep
~~~
- **Post phase** (calculate statistical significance):
~~~bash
python rmats.py --b1 b1.txt --b2 b2.txt --gtf annotation.gtf -t paired --readLength 50 --nthread 4 --od output/ --tmp tmp_post --task post
~~~

### **Statistical Model Options:**
- **Enable paired statistics model**:
~~~bash
python rmats.py --b1 b1.txt --b2 b2.txt --gtf annotation.gtf -t paired --readLength 50 --nthread 4 --od output/ --tmp tmp_post --paired-stats
~~~
- **Skip statistical testing (only generate raw splicing events):**
~~~bash
python rmats.py --b1 b1.txt --b2 b2.txt --gtf annotation.gtf -t paired --readLength 50 --nthread 4 --od output/ --tmp tmp_post --statoff
~~~

### **Output Files:**
- `[AS_Event].MATS.JC.txt` - Results including only junction-spanning reads.
- `[AS_Event].MATS.JCEC.txt` - Results including junction and exon-spanning reads.
- `fromGTF.[AS_Event].txt` - Identified alternative splicing events from annotation.
- `JC.raw.input.[AS_Event].txt` - Raw count data for junction counts.
- `JCEC.raw.input.[AS_Event].txt` - Raw count data including exon counts.

### **Additional Features:**
- **Detect novel splice sites:**
~~~bash
python rmats.py --b1 b1.txt --b2 b2.txt --gtf annotation.gtf -t paired --readLength 50 --nthread 4 --od output/ --tmp tmp_post --novelSS
~~~
- **Use predefined event set:**
~~~bash
python rmats.py --b1 b1.txt --b2 b2.txt --gtf annotation.gtf -t paired --readLength 50 --nthread 4 --od output/ --tmp tmp_post --fixed-event-set events_dir/
~~~

### **Reference Documentation:**
For more details, refer to the rMATS official documentation and command-line help:
~~~bash
python rmats.py -h
~~~
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
