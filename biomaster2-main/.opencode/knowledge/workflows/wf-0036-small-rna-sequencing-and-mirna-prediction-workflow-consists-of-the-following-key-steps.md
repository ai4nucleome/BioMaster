---
id: wf-0036
title: 'Small RNA sequencing and miRNA prediction workflow consists of the following
  key steps:'
summary: 'Small RNA sequencing and miRNA prediction workflow consists of the following
  key steps: Step 1: Quality Control and Trimming Description: Perform quality control
  on raw sequencing reads, remove low-quality reads, and...'
keywords:
- annotation-comparison
- workflow
- Small RNA sequencing and miRNA prediction workflow consists of the following key
  steps
- 'Step 1: Quality Control and Trimming

  Description: Perform quality control on raw sequencing reads'
- remove low-quality reads
- 'and trim sequencing adapters.

  Commands'
- fastqc
- data
- '*.fastq.gz -o'
- output
- '010'
- qc_reports
- fastp -i
- C1.fastq.gz -o
- trimmed_C1.fastq.gz
- 'Step 2: Genome Alignment

  Description: Build index from genome and align reads with Bowtie1. Convert to sorted
  BAM.

  Commands'
- bowtie-build
- genome.fa
- genome_index
- bowtie -S -p 16
- trimmed_C1.fastq.gz >
- C1.sam
- samtools view -bS
- samtools sort -o
- aligned_C1.bam
- samtools index
- 'aligned_C1.bam

  Checkpoint: Use `samtools flagstat` to verify alignments are not empty'
- 'Step 3: miRNA Quantification

  Description: Use featureCounts with a SAF annotation file. If the SAF file does
  not exist'
- 'generate it from the miRBase mature FASTA using the provided Python script.

  Commands'
- python convert_fasta_to_saf.py -i
- miRBase_mature.fasta -o
- miRBase_mature.saf
- featureCounts -T 4 -F SAF -a
- FastQC
- samtools
- featureCounts
path: .opencode/knowledge/workflows/wf-0036-small-rna-sequencing-and-mirna-prediction-workflow-consists-of-the-following-key-steps.md
origin_source: workflow
origin_page: 38
source_entry_index: 28
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: annotation-comparison
---

# Small RNA sequencing and miRNA prediction workflow consists of the following key steps:

## One-line description

Small RNA sequencing and miRNA prediction workflow consists of the following key steps: Step 1: Quality Control and Trimming Description: Perform quality control on raw sequencing reads, remove low-quality reads, and...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `38`
- Source entry index: `28`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0036`
- Analysis/tool category: `annotation-comparison`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Small RNA sequencing and miRNA prediction workflow consists of the following key steps:

Step 1: Quality Control and Trimming
Description: Perform quality control on raw sequencing reads, remove low-quality reads, and trim sequencing adapters.
Commands:
  fastqc ./data/*.fastq.gz -o ./output/010/qc_reports/
  fastp -i ./data/C1.fastq.gz -o ./output/010/trimmed_C1.fastq.gz

Step 2: Genome Alignment
Description: Build index from genome and align reads with Bowtie1. Convert to sorted BAM.
Commands:
  bowtie-build ./data/genome.fa ./output/010/genome_index
  bowtie -S -p 16 ./output/010/genome_index ./output/010/trimmed_C1.fastq.gz > ./output/010/C1.sam
  samtools view -bS ./output/010/C1.sam | samtools sort -o ./output/010/aligned_C1.bam
  samtools index ./output/010/aligned_C1.bam
Checkpoint: Use `samtools flagstat` to verify alignments are not empty.

Step 3: miRNA Quantification
Description: Use featureCounts with a SAF annotation file. If the SAF file does not exist, generate it from the miRBase mature FASTA using the provided Python script.
Commands:
  python convert_fasta_to_saf.py -i ./data/miRBase_mature.fasta -o ./data/miRBase_mature.saf
  featureCounts -T 4 -F SAF -a ./data/miRBase_mature.saf -o ./output/010/miRNA_expression_matrix.txt ./output/010/aligned_C1.bam
Checkpoint: Ensure expression matrix has non-zero counts.

Step 4: Novel miRNA Discovery
Description: Collapse reads and predict novel miRNAs with miRDeep2.
Commands:
  mapper.pl ./output/010/trimmed_C1.fastq.gz -e -h -m -l 18 -s ./output/010/reads_collapsed.fa -t ./output/010/reads.arf -r ./data/genome.fa
  miRDeep2.pl ./output/010/reads_collapsed.fa ./data/genome.fa ./output/010/reads.arf ./data/miRBase_mature.fasta ./data/miRBase_hairpin.fasta -t Human > ./output/010/miRDeep2_results.txt
Checkpoint: Ensure result file contains predicted miRNAs.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
