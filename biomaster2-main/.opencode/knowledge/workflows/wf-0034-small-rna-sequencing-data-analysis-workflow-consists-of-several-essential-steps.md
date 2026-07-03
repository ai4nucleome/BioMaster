---
id: wf-0034
title: 'Small RNA sequencing data analysis workflow consists of several essential
  steps:'
summary: 'Small RNA sequencing data analysis workflow consists of several essential
  steps: Step 1: Quality Control and Trimming Description: Perform quality control
  and adapter trimming on raw sequencing reads. Input Required:...'
keywords:
- annotation-comparison
- workflow
- Small RNA sequencing data analysis workflow consists of several essential steps
- 'Step 1: Quality Control and Trimming

  Description: Perform quality control and adapter trimming on raw sequencing reads.

  Input Required: Raw FASTQ files.

  Expected Output: Trimmed and filtered FASTQ files.

  Tools Used: FastQC'
- 'fastp.

  Commands'
- '```bash'
- '# Run FastQC to assess raw reads quality'
- fastqc
- data
- '*.fastq.gz -o'
- output
- 008
- '# Trim adapters and filter low-quality reads using fastp'
- fastp -i
- C1-N1-R1_S4_L001_R1_001.fastq.gz -o
- trimmed_C1-N1-R1_S4_L001_R1_001.fastq.gz
- C9-N1-R1_S7_L001_R1_001.fastq.gz -o
- trimmed_C9-N1-R1_S7_L001_R1_001.fastq.gz
- Ctl-N1-R1_S1_L001_R1_001.fastq.gz -o
- trimmed_Ctl-N1-R1_S1_L001_R1_001.fastq.gz
- '```'
- 'Step 2: Prepare miRBase Reference and Convert Annotation Format

  Description: Download miRBase reference sequences and convert GFF3 annotation to
  GTF format for downstream analysis.

  Input Required: hsa.gff3 and miRBase_hairpin.fasta from miRBase.

  Expected Output: miRNA annotation in GTF format and reference sequences for alignment.

  Tools Used: wget'
- 'gffread.

  Commands'
- '# D'
- FastQC
path: .opencode/knowledge/workflows/wf-0034-small-rna-sequencing-data-analysis-workflow-consists-of-several-essential-steps.md
origin_source: workflow
origin_page: 36
source_entry_index: 26
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: annotation-comparison
---

# Small RNA sequencing data analysis workflow consists of several essential steps:

## One-line description

Small RNA sequencing data analysis workflow consists of several essential steps: Step 1: Quality Control and Trimming Description: Perform quality control and adapter trimming on raw sequencing reads. Input Required:...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `36`
- Source entry index: `26`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0034`
- Analysis/tool category: `annotation-comparison`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Small RNA sequencing data analysis workflow consists of several essential steps:

Step 1: Quality Control and Trimming
Description: Perform quality control and adapter trimming on raw sequencing reads.
Input Required: Raw FASTQ files.
Expected Output: Trimmed and filtered FASTQ files.
Tools Used: FastQC, fastp.
Commands:
  ~~~bash
  # Run FastQC to assess raw reads quality
  fastqc ./data/*.fastq.gz -o ./output/008/
  
  # Trim adapters and filter low-quality reads using fastp
  fastp -i ./data/C1-N1-R1_S4_L001_R1_001.fastq.gz -o ./output/008/trimmed_C1-N1-R1_S4_L001_R1_001.fastq.gz
  fastp -i ./data/C9-N1-R1_S7_L001_R1_001.fastq.gz -o ./output/008/trimmed_C9-N1-R1_S7_L001_R1_001.fastq.gz
  fastp -i ./data/Ctl-N1-R1_S1_L001_R1_001.fastq.gz -o ./output/008/trimmed_Ctl-N1-R1_S1_L001_R1_001.fastq.gz
  ~~~

Step 2: Prepare miRBase Reference and Convert Annotation Format
Description: Download miRBase reference sequences and convert GFF3 annotation to GTF format for downstream analysis.
Input Required: hsa.gff3 and miRBase_hairpin.fasta from miRBase.
Expected Output: miRNA annotation in GTF format and reference sequences for alignment.
Tools Used: wget, gffread.
Commands:
  ~~~bash
  # Download miRBase annotation for human miRNAs (GFF3)
  wget -O ./data/hsa.gff3 https://www.mirbase.org/download/CURRENT/genomes/hsa.gff3
  
  # Download miRNA reference sequences (FASTA)
  wget -O ./data/miRBase_hairpin.fasta https://www.mirbase.org/download/CURRENT/hairpin.fa
  
  # Convert GFF3 to GTF format for featureCounts and downstream analysis
  gffread ./data/hsa.gff3 -T -o ./data/miRNA_annotation.gtf
  
  # Verify output
  ls -lh ./data/miRNA_annotation.gtf
  ~~~

Step 3: Build Bowtie Index for miRBase
Description: Build Bowtie1 index for miRBase reference to enable efficient read alignment.
Input Required: `miRBase_hairpin.fasta`.
Expected Output: Bowtie index files.
Tools Used: bowtie-build.
Commands:
  ~~~bash
  # Build Bowtie index for miRBase hairpin sequences
  bowtie-build ./data/miRBase_hairpin.fasta ./data/miRBase_index
  
  # Verify index files
  ls -lh ./data/miRBase_index*
  ~~~
  **Checkpoint:** If `ls ./data/miRBase_index*` returns empty, the indexing step failed.

Step 4: Read Alignment
Description: Align reads to the miRNA reference database (miRBase).
Input Required: Filtered FASTQ files, miRBase Bowtie index.
Expected Output: Aligned BAM files.
Tools Used: Bowtie1, SAMtools.
Commands:
  ~~~bash
  # Align reads to miRBase using Bowtie1
  bowtie -v 1 -p 16 -x ./data/miRBase_index -U ./output/008/trimmed_C1-N1-R1_S4_L001_R1_001.fastq.gz -S ./output/008/aligned_C1-N1-R1_S4_L001_R1_001.sam
  bowtie -v 1 -p 16 -x ./data/miRBase_index -U ./output/008/trimmed_C9-N1-R1_S7_L001_R1_001.fastq.gz -S ./output/008/aligned_C9-N1-R1_S7_L001_R1_001.sam
  bowtie -v 1 -p 16 -x ./data/miRBase_index -U ./output/008/trimmed_Ctl-N1-R1_S1_L001_R1_001.fastq.gz -S ./output/008/aligned_Ctl-N1-R1_S1_L001_R1_001.sam
  
  # Convert SAM to BAM, sort, and index
  samtools view -bS ./output/008/aligned_C1-N1-R1_S4_L001_R1_001.sam | samtools sort -o ./output/008/aligned_C1-N1-R1_S4_L001_R1_001.bam
  samtools index ./output/008/aligned_C1-N1-R1_S4_L001_R1_001.bam
  ~~~
  **Checkpoint:** Run `samtools flagstat ./output/008/aligned_C1-N1-R1_S4_L001_R1_001.bam`. If `0 + 0 mapped`, alignment failed.

Step 5: miRNA Quantification
Description: Quantify miRNA expression levels.
Input Required: Aligned BAM files and miRNA annotation in GTF format.
Expected Output: Expression matrix.
Tools Used: featureCounts, HTSeq.
Commands:
  ~~~bash
  # Run featureCounts to quantify miRNA expression levels
  featureCounts -a ./data/miRNA_annotation.gtf -o ./output/008/mirna_quantification_results.txt ./output/008/aligned_C1-N1-R1_S4_L001_R1_001.bam ./output/008/aligned_C9-N1-R1_S7_L001_R1_001.bam ./output/008/aligned_Ctl-N1-R1_S1_L001_R1_001.bam
  ~~~
  **Checkpoint:** If `featureCounts` output has all `0` counts, check BAM files.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
