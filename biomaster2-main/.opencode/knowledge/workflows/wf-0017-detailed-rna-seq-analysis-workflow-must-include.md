---
id: wf-0017
title: 'Detailed RNA-seq Analysis Workflow must include:'
summary: 'Detailed RNA-seq Analysis Workflow must include: Step 1: Quality Control
  and Preprocessing Description: Perform quality control (QC) on the raw RNA-seq data.
  This includes checking the quality of raw reads, trimming a...'
keywords:
- rnaseq-de
- workflow
- Detailed RNA-seq Analysis Workflow must include
- 'Step 1: Quality Control and Preprocessing

  Description: Perform quality control (QC) on the raw RNA-seq data. This includes
  checking the quality of raw reads'
- trimming adapters
- and filtering low-quality sequences. FastQC is commonly used for assessing quality
- 'and Cutadapt can be used for trimming.

  Input Required: Raw FASTQ files'
- 'sample metadata.

  Expected Output: Cleaned and trimmed FASTQ files ready for alignment.

  Tools Used: FastQC'
- Cutadapt
- 'Step 2: Alignment to Reference Genome

  Description: Align the cleaned RNA-seq reads to a reference genome using a suitable
  aligner'
- such as STAR. The alignment process produces a SAM or BAM file
- 'which contains the mapped reads.

  Input Required: Trimmed FASTQ files from Step 1'
- 'reference genome (FASTA file).

  Expected Output: Aligned SAM'
- 'BAM files.

  Tools Used: STAR'
- 'Step 3: Quality Control of Aligned Reads

  Description: Perform a second round of quality control on the aligned reads to assess
  the alignment efficiency'
- the number of uniquely mapped reads
- 'and potential biases in the alignment. Tools like SAMtools can be used for this
  analysis.

  Input Required: Aligned SAM'
- 'BAM files from Step 2.

  E'
- FastQC
- STAR
- samtools
path: .opencode/knowledge/workflows/wf-0017-detailed-rna-seq-analysis-workflow-must-include.md
origin_source: workflow
origin_page: 19
source_entry_index: 9
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: rnaseq-de
---

# Detailed RNA-seq Analysis Workflow must include:

## One-line description

Detailed RNA-seq Analysis Workflow must include: Step 1: Quality Control and Preprocessing Description: Perform quality control (QC) on the raw RNA-seq data. This includes checking the quality of raw reads, trimming a...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `19`
- Source entry index: `9`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0017`
- Analysis/tool category: `rnaseq-de`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Detailed RNA-seq Analysis Workflow must include:

Step 1: Quality Control and Preprocessing
Description: Perform quality control (QC) on the raw RNA-seq data. This includes checking the quality of raw reads, trimming adapters, and filtering low-quality sequences. FastQC is commonly used for assessing quality, and Cutadapt can be used for trimming.
Input Required: Raw FASTQ files, sample metadata.
Expected Output: Cleaned and trimmed FASTQ files ready for alignment.
Tools Used: FastQC, Cutadapt.

Step 2: Alignment to Reference Genome
Description: Align the cleaned RNA-seq reads to a reference genome using a suitable aligner, such as STAR. The alignment process produces a SAM or BAM file, which contains the mapped reads.
Input Required: Trimmed FASTQ files from Step 1, reference genome (FASTA file).
Expected Output: Aligned SAM/BAM files.
Tools Used: STAR.

Step 3: Quality Control of Aligned Reads
Description: Perform a second round of quality control on the aligned reads to assess the alignment efficiency, the number of uniquely mapped reads, and potential biases in the alignment. Tools like SAMtools can be used for this analysis.
Input Required: Aligned SAM/BAM files from Step 2.
Expected Output: Alignment QC reports, such as mapping percentage, coverage distribution, and biases.
Tools Used: SAMtools.

Step 4: Gene Quantification
Description: Quantify gene expression levels by counting the number of reads mapped to each gene using tools like HTSeq. These tools output gene-level counts that are used for downstream differential expression analysis.
Input Required: Aligned BAM files from Step 3, gene annotation file (GTF or GFF).
Expected Output: Gene count matrix.
Tools Used: HTSeq.

Step 5: Differential Expression Analysis
Description: Perform differential gene expression analysis to identify genes that are significantly upregulated or downregulated between different conditions. This is typically done using DESeq2.
Input Required: Gene count matrix from Step 4, experimental design information.
Expected Output: Differentially expressed genes (DEGs), p-values, fold changes.
Tools Used: DESeq2.

Step 6: Data Normalization
Description: Normalize the raw gene counts to account for differences in sequencing depth and library size. This step is necessary to ensure accurate differential expression results. Methods like TMM (Trimmed Mean of M-values) or RPKM/FPKM (Reads/Fragments Per Kilobase of transcript per Million mapped reads) can be used.
Input Required: Gene count matrix from Step 4.
Expected Output: Normalized gene count matrix.
Tools Used: DESeq2, or custom scripts.

Step 7: Gene Ontology and Pathway Enrichment Analysis
Description: Conduct functional annotation and enrichment analysis to determine which biological processes, molecular functions, or pathways are enriched in the differentially expressed genes. Tools like DAVID, ClusterProfiler can be used for this analysis.
Input Required: List of differentially expressed genes (from Step 5), gene annotation information.
Expected Output: Enriched Gene Ontology terms and pathways, plots for visualization.
Tools Used: DAVID, ClusterProfiler.

Step 8: Clustering and Visualization
Description: Perform unsupervised clustering to group similar gene expression patterns and visualize the results using techniques like Principal Component Analysis (PCA), hierarchical clustering, or t-SNE.
Input Required: Normalized gene count matrix from Step 6.
Expected Output: Clustering results, visualizations (e.g., PCA plots, heatmaps).
Tools Used: Python (scikit-learn, Seaborn).

Step 9: Alternative Splicing Analysis
Description: Analyze alternative splicing events to identify differences in splicing patterns between conditions. Tools like rMATS or DEXSeq can be used for this analysis.
Input Required: Aligned BAM files from Step 3, gene annotation file (GTF or GFF).
Expected Output: Splicing event counts, significant splicing events.
Tools Used: rMATS, DEXSeq.

Step 10: Visualization and Reporting
Description: Generate publication-quality visualizations of the analysis results, such as volcano plots for differential expression, heatmaps for gene clustering, and pathway enrichment plots. Prepare a final report summarizing the RNA-seq analysis.
Input Required: Differential expression results, clustering results, pathway analysis results.
Expected Output: Final analysis report, visualizations for publication.
Tools Used: Python (matplotlib, Seaborn).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
