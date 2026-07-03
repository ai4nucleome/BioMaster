---
id: wf-0028
title: This is a pipeline for rna splicing analysis of rna sequencing data from organisms
  with a referen...
summary: 'This is a pipeline for rna splicing analysis of rna sequencing data from
  organisms with a reference genome and annotation. Follow these steps in order, and
  adjust file paths and parameters as needed: 1. **Merge Re-seq...'
keywords:
- rnaseq-de
- workflow
- This is a pipeline for rna splicing analysis of rna sequencing data from organisms
  with a referen
- This is a pipeline for rna splicing analysis of rna sequencing data from organisms
  with a reference genome and annotation. Follow these steps in order
- and adjust file paths and parameters as needed
- 1. **Merge Re-sequenced FastQ Files**
- '**Tool:** Unix `cat`'
- '**Purpose:** Concatenate multiple FastQ files into a single file for further processing'
- '**Example:**'
- '```bash'
- cat sample_part1.fastq sample_part2.fastq > merged_sample.fastq
- '```'
- 2. **Read Quality Control**
- '**Tool:** FastQC'
- '**Purpose:** Assess the quality of raw sequencing reads and generate quality reports'
- fastqc merged_sample.fastq -o qc_reports
- 3. **Adapter and Quality Trimming**
- '**Tool:** TrimGalore'
- '**Purpose:** Remove adapter sequences and trim low-quality bases from the reads'
- trim_galore --quality 20 --fastqc merged_sample.fastq -o trimmed_reads
- 4. **Alignment with STAR**
- '**Tool:** STAR'
- '**Purpose:** Align trimmed reads to the reference genome'
- STAR --runThreadN 8 --genomeDir
- path
- to
- STAR_index --readFilesIn trimmed_reads
- merged_sam
- FastQC
- STAR
path: .opencode/knowledge/workflows/wf-0028-this-is-a-pipeline-for-rna-splicing-analysis-of-rna-sequencing-data-from-organisms-with-a-referen.md
origin_source: workflow
origin_page: 30
source_entry_index: 20
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: rnaseq-de
---

# This is a pipeline for rna splicing analysis of rna sequencing data from organisms with a referen...

## One-line description

This is a pipeline for rna splicing analysis of rna sequencing data from organisms with a reference genome and annotation. Follow these steps in order, and adjust file paths and parameters as needed: 1. **Merge Re-seq...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `30`
- Source entry index: `20`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0028`
- Analysis/tool category: `rnaseq-de`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
This is a pipeline for rna splicing analysis of rna sequencing data from organisms with a reference genome and annotation. Follow these steps in order, and adjust file paths and parameters as needed:

1. **Merge Re-sequenced FastQ Files**
   - **Tool:** Unix `cat`
   - **Purpose:** Concatenate multiple FastQ files into a single file for further processing.
   - **Example:**
     ~~~bash
     cat sample_part1.fastq sample_part2.fastq > merged_sample.fastq
     ~~~

2. **Read Quality Control**
   - **Tool:** FastQC
   - **Purpose:** Assess the quality of raw sequencing reads and generate quality reports.
   - **Example:**
     ~~~bash
     fastqc merged_sample.fastq -o qc_reports/
     ~~~

3. **Adapter and Quality Trimming**
   - **Tool:** TrimGalore
   - **Purpose:** Remove adapter sequences and trim low-quality bases from the reads.
   - **Example:**
     ~~~bash
     trim_galore --quality 20 --fastqc merged_sample.fastq -o trimmed_reads/
     ~~~

4. **Alignment with STAR**
   - **Tool:** STAR
   - **Purpose:** Align trimmed reads to the reference genome.
   - **Example:**
     ~~~bash
     STAR --runThreadN 8 --genomeDir /path/to/STAR_index --readFilesIn trimmed_reads/merged_sample_trimmed.fq --outFileNamePrefix alignments/sample_
     ~~~

5. **Quantification Options Depending on Analysis Type**
   - **Option A:** Quantification with Salmon using STAR alignments
     - **Example:**
       ~~~bash
       salmon quant -t transcripts.fa -l A -a alignments/sample_Aligned.out.sam -o quant_salmon/
       ~~~
   - **Option B:** Quantification with featureCounts using STAR alignments
     - **Example:**
       ~~~bash
       featureCounts -T 8 -a annotation.gtf -o counts_featureCounts.txt alignments/sample_Aligned.out.sam
       ~~~
   - **Option C:** Quantification with HTSeq for DEXSeq counts
     - **Example:**
       ~~~bash
       htseq-count -f sam -r pos -s no -t exon -i gene_id alignments/sample_Aligned.out.sam annotation.gtf > counts_htseq.txt
       ~~~

6. **Sort and Index Alignments**
   - **Tool:** SAMtools
   - **Purpose:** Convert SAM to BAM, sort, and index the alignments for efficient downstream analysis.
   - **Example:**
     ~~~bash
     samtools view -bS alignments/sample_Aligned.out.sam | samtools sort -o alignments/sample_sorted.bam
     samtools index alignments/sample_sorted.bam
     ~~~

7. **Create bigWig Coverage Files**
   - **Tools:** BEDTools and bedGraphToBigWig
   - **Purpose:** Generate bigWig files for visualization of read coverage across the genome.
   - **Example:**
     ~~~bash
     bedtools genomecov -ibam alignments/sample_sorted.bam -bg > coverage/sample.bedGraph
     bedGraphToBigWig coverage/sample.bedGraph /path/to/chrom.sizes coverage/sample.bw
     ~~~
 ~~~

9. **Summarize Quality Control**
   - **Tool:** MultiQC
   - **Purpose:** Aggregate and summarize QC reports from FastQC, TrimGalore, and other tools into a single report.
   - **Example:**
     ~~~bash
     multiqc qc_reports/ trimmed_reads/ alignments/ -o multiqc_report/
     ~~~

10. **Differential Exon Usage (DEU) Analysis**
    - **Using HTSeq:**
      - Quantify with HTSeq and perform DEU analysis with DEXSeq.
    - **Using featureCounts:**
      - Quantify with featureCounts and perform DEU analysis with edgeR.
    - **Example Commands:**
      (The quantification step is shown in step 5, and downstream DEU analysis is conducted using R packages such as DEXSeq or edgeR.)

11. **Differential Transcript Usage (DTU) Analysis**
    - **Workflow:**
      - Quantify with Salmon → Filter and analyze with DRIMSeq → Perform DTU analysis with DEXSeq.
    - **Example:**
      (DTU analysis is performed within an R environment using the output from Salmon and subsequent DRIMSeq filtering, followed by differential testing with DEXSeq.)

12. **Event-Based Splicing Analysis**
    - **Option A:** Use STAR alignments as input for rMATS to detect alternative splicing events.
      - **Example:**
        ~~~bash
        rmats.py --b1 sample1_bam_list.txt --b2 sample2_bam_list.txt --gtf annotation.gtf --od rmats_output/ --tmp rmats_tmp/ -t paired --readLength 100 --nthread 8
        ~~~
    - **Option B:** Use Salmon quantification as input for SUPPA2 to analyze splicing events.
      - **Example:**
        ~~~bash
        suppa.py generateEvents -i annotation.gtf -o suppa_events -f ioe -e SE SS MX RI
        suppa.py psiPerEvent -i suppa_events.ioe -e quant_salmon/quant.sf -o suppa_psi
        ~~~

This pipeline outlines the major steps and options available for alternative splicing analysis of RNA-seq data using a reference genome and annotation. Adjust each command and parameter to suit your specific data and analysis requirements.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
