---
id: wf-0018
title: This is a workflow for Comprehensive Cancer DNA/RNA Analysis using nf-core/oncoanalyser
summary: 'This is a workflow for Comprehensive Cancer DNA/RNA Analysis using nf-core/oncoanalyser
  Step 1: Create Sample Sheet (Input Preparation) Description: Prepare a tab‐delimited
  sample sheet listing each sample’s identifie...'
keywords:
- variant-calling
- workflow
- This is a workflow for Comprehensive Cancer DNA
- RNA Analysis using nf-core
- oncoanalyser
- 'Step 1: Create Sample Sheet (Input Preparation)

  Description: Prepare a tab‐delimited sample sheet listing each sample’s identifiers
  and file paths. This file informs the pipeline about the type of sequencing data
  (e.g. WGS'
- WTS) and associated metadata
- 'Input Required: Sequencing data file paths (FASTQ or BAM) and metadata details
  (group_id'
- subject_id
- sample_id
- sample_type
- sequence_type
- filetype
- info
- filepath)
- 'Expected Output: A well-formatted CSV file (e.g. samplesheet.csv) for pipeline
  input'
- 'Tool Used: Text editor (or spreadsheet software)'
- 'Step 2: DNA Alignment with bwa‐mem2'
- 'Description: Align DNA FASTQ reads to the reference genome using an efficient short-read
  mapper'
- 'Input Required: DNA FASTQ files and reference genome (e.g. GRCh38_hmf)'
- 'Expected Output: Aligned DNA BAM files with mapped reads'
- 'Tool Used: bwa‐mem2'
- 'Step 3: RNA Alignment with STAR'
- 'Description: Align RNA FASTQ reads to the reference genome'
- transcriptome to capture spliced transcripts
- 'Input Required: RNA FASTQ files and corresponding reference genome'
- transcriptome index
- 'Expected Output: RNA'
- STAR
- BWA
path: .opencode/knowledge/workflows/wf-0018-this-is-a-workflow-for-comprehensive-cancer-dna-rna-analysis-using-nf-core-oncoanalyser.md
origin_source: workflow
origin_page: 20
source_entry_index: 10
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: variant-calling
---

# This is a workflow for Comprehensive Cancer DNA/RNA Analysis using nf-core/oncoanalyser

## One-line description

This is a workflow for Comprehensive Cancer DNA/RNA Analysis using nf-core/oncoanalyser Step 1: Create Sample Sheet (Input Preparation) Description: Prepare a tab‐delimited sample sheet listing each sample’s identifie...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `20`
- Source entry index: `10`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0018`
- Analysis/tool category: `variant-calling`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
This is a workflow for Comprehensive Cancer DNA/RNA Analysis using nf-core/oncoanalyser

Step 1: Create Sample Sheet (Input Preparation)
Description: Prepare a tab‐delimited sample sheet listing each sample’s identifiers and file paths. This file informs the pipeline about the type of sequencing data (e.g. WGS, WTS) and associated metadata.  
Input Required: Sequencing data file paths (FASTQ or BAM) and metadata details (group_id, subject_id, sample_id, sample_type, sequence_type, filetype, info, filepath).  
Expected Output: A well-formatted CSV file (e.g. samplesheet.csv) for pipeline input.  
Tool Used: Text editor (or spreadsheet software)  

Step 2: DNA Alignment with bwa‐mem2  
Description: Align DNA FASTQ reads to the reference genome using an efficient short-read mapper.  
Input Required: DNA FASTQ files and reference genome (e.g. GRCh38_hmf).  
Expected Output: Aligned DNA BAM files with mapped reads.  
Tool Used: bwa‐mem2  

Step 3: RNA Alignment with STAR  
Description: Align RNA FASTQ reads to the reference genome/transcriptome to capture spliced transcripts.  
Input Required: RNA FASTQ files and corresponding reference genome/transcriptome index.  
Expected Output: RNA alignment files (BAM) with spliced alignments.  
Tool Used: STAR  

Step 4: Duplicate Marking with MarkDups  
Description: Identify and mark duplicate reads in the aligned BAM files to reduce PCR artifacts.  
Input Required: Aligned BAM files (from DNA and/or RNA alignments).  
Expected Output: BAM files with duplicate reads marked (typically flagged in the header).  
Tool Used: MarkDups  

Step 5: Duplicate Marking with Picard MarkDuplicates  
Description: Alternatively, mark duplicate reads using a widely adopted toolkit to eliminate PCR artifacts.  
Input Required: Aligned BAM files resulting from DNA or RNA read mapping.  
Expected Output: Processed BAM files with duplicates flagged for downstream analysis.  
Tool Used: Picard MarkDuplicates  

Step 6: SNV, MNV, and INDEL Calling with SAGE  
Description: Detect single nucleotide variants (SNVs), multi-nucleotide variants (MNVs), and small insertions/deletions (INDELs) from processed alignments.  
Input Required: Processed BAM files from duplicate marking.  
Expected Output: Variant call files (VCFs) with SNVs, MNVs, and INDELs.  
Tool Used: SAGE  

Step 7: SNV, MNV, and INDEL Calling with PAVE  
Description: Optionally, perform variant calling for SNVs, MNVs, and INDELs with an alternative algorithm to validate or complement the SAGE output.  
Input Required: Processed BAM files from duplication marking.  
Expected Output: VCF files with detected SNVs, MNVs, and INDELs.  
Tool Used: PAVE  

Step 8: CNV Calling with AMBER  
Description: Initiate copy-number variation (CNV) analysis by quantifying allele-specific copy numbers across the genome.  
Input Required: Aligned and duplicate-marked BAM files.  
Expected Output: CNV segmentation files indicating allele-specific copy number estimates.  
Tool Used: AMBER  

Step 9: CNV Calling with COBALT  
Description: Complement the CNV analysis by measuring read depth based on binning strategies across the genome.  
Input Required: Aligned BAM files along with a binning reference for read depth calculation.  
Expected Output: Binned read-depth profiles for copy-number estimation.  
Tool Used: COBALT  

Step 10: CNV Integration with PURPLE  
Description: Integrate allele-specific CNV data (from AMBER and COBALT) with variant allele frequencies and tumor purity estimates to infer final copy-number calls.  
Input Required: Outputs from AMBER (allele-specific segmentation) and COBALT (read-depth profiles), and variant calls.  
Expected Output: Final CNV calls with integrated information about copy numbers and purity estimates.  
Tool Used: PURPLE  

Step 11: SV Preprocessing with SvPrep  
Description: Preprocess alignments for structural variant (SV) detection by reformatting and quality filtering the data.  
Input Required: Aligned and duplicate-marked BAM files from earlier steps.  
Expected Output: Reformatted files prepared for input into SV detection tools.  
Tool Used: SvPrep  

Step 12: SV Calling with GRIDSS  
Description: Identify structural variants (SVs) such as insertions, deletions, and rearrangements in the genomic data.  
Input Required: Processed BAM files or output from SvPrep.  
Expected Output: Raw SV call files indicating breakpoints or rearrangements in the genome.  
Tool Used: GRIDSS  

Step 13: SV Calling with GRIPSS  
Description: Alternatively, run a complementary method for SV detection to capture additional variants or refine the breakpoints.  
Input Required: Preprocessed alignment files from SvPrep.  
Expected Output: SV call files detailing candidate structural variants.  
Tool Used: GRIPSS  

Step 14: SV Event Interpretation with LINX  
Description: Interpret and cluster structural variant events in the context of cancer genomes to deduce genomic rearrangements and complex events.  
Input Required: SV call files generated from GRIDSS and/or GRIPSS.  
Expected Output: Interpreted and annotated SV event files with biological context.  
Tool Used: LINX  

Step 15: Transcript Analysis with Isofox  
Description: Analyze transcriptome data to quantify gene expression and detect transcript isoforms relevant for cancer profiling.  
Input Required: RNA alignment files (BAM) from STAR.  
Expected Output: Expression matrices or transcript isoform reports for downstream analysis.  
Tool Used: Isofox  

Step 16: Oncoviral Detection with VIRUSBreakend  
Description: Detect oncoviral integration events by scanning for breakends that could indicate viral insertions in the host genome.  
Input Required: Processed BAM files from the alignment steps.  
Expected Output: Viral integration candidate lists with genomic coordinates.  
Tool Used: VIRUSBreakend  

Step 17: Viral Interpretation with Virus Interpreter  
Description: Annotate and interpret the detected viral integration events, providing clinical and biological insights.  
Input Required: Oncoviral candidate events generated by VIRUSBreakend.  
Expected Output: Detailed viral event reports with annotated significance.  
Tool Used: Virus Interpreter  

Step 18: HLA Calling with LILAC  
Description: Infer HLA alleles from the sequencing data to assess potential immunogenomic markers.  
Input Required: Aligned BAM files (typically from DNA data) along with reference HLA allele databases.  
Expected Output: HLA allele calls and reports.  
Tool Used: LILAC  

Step 19: HRD Status Prediction with CHORD  
Description: Assess homologous recombination deficiency (HRD) status in cancer samples by leveraging genomic scar signatures and mutational patterns.  
Input Required: Variant call files (from SAGE/PAVE) and CNV profiles (from PURPLE).  
Expected Output: HRD status prediction reports for each sample.  
Tool Used: CHORD  

Step 20: Mutational Signature Fitting with Sigs  
Description: Decompose the mutational profile of the tumor into known mutational signatures to infer underlying mutagenic processes.  
Input Required: Catalog of detected SNVs/MNVs/INDELs from earlier variant calling.  
Expected Output: Fitted mutational signature profiles with quantitative contributions.  
Tool Used: Sigs  

Step 21: Tissue of Origin Prediction with CUPPA  
Description: Predict the tissue of origin for cancer samples based on genomic and transcriptomic signatures.  
Input Required: Combined genomic features (e.g. mutational signatures, CNVs) and transcriptome profiles.  
Expected Output: Predicted tissue of origin report per sample.  
Tool Used: CUPPA  

Step 22: Report Generation with ORANGE  
Description: Generate a comprehensive clinical report summarizing key findings (variants, CNVs, SVs, HRD status, oncogenic drivers, etc.) for each sample.  
Input Required: Integrated results from individual analyses (variant calls, CNV integration, SV interpretation, transcript analysis, etc.).  
Expected Output: A visually formatted report (PDF/HTML) summarizing the cancer genomic profile (e.g. ORANGE_report.pdf).  
Tool Used: ORANGE  

Step 23: Report Generation with linxreport  
Description: Alternatively, compile a report focused on structural variant events and their interpretation in the clinical context.  
Input Required: Output from the LINX SV interpretation step and other supporting annotation data.  
Expected Output: A detailed report providing insights into rearrangement events and clinical annotations.  
Tool Used: linxreport
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
