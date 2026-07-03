---
id: wf-0041
title: 'Simplified WGS Bioinformatics Analysis Pipeline (SV Detection) must include:
  Step 1: Raw Data Qua...'
summary: 'Simplified WGS Bioinformatics Analysis Pipeline (SV Detection) must include:
  Step 1: Raw Data Quality Control. Description: Remove low-quality sequences and
  adapter contamination to ensure the reliability of subsequen...'
keywords:
- variant-calling
- workflow
- 'Simplified WGS Bioinformatics Analysis Pipeline (SV Detection) must include: Step
  1: Raw Data Qua'
- 'Simplified WGS Bioinformatics Analysis Pipeline (SV Detection) must include: Step
  1: Raw Data Quality Control. Description: Remove low-quality sequences and adapter
  contamination to ensure the reliability of subsequent analyses. Input Required:
  Raw sequencing files (*.fq.gz). Expected Output: Cleaned high-quality sequencing
  files (clean_*.fq.gz). Tools Used: fastp'
- 'a multi-threaded tool that performs quality control and generates statistical reports
  in one step. Step 2: Sequence Alignment. Description: Align quality-controlled sequencing
  reads to the reference genome and generate a sorted BAM file. Input Required: Quality-controlled
  sequencing files (clean_*.fq.gz)'
- 'reference genome file. Expected Output: Sorted alignment file (sample.sorted.bam).
  Tools Used: BWA-MEM. Step 3: Post-alignment Processing. Description: Remove PCR
  duplicates and calibrate base quality to enhance SV detection accuracy. Input Required:
  Sorted BAM file (sample.sorted.bam). Expected Output: Deduplicated and recalibrated
  BAM file (sample.dedup.recal.bam). Tools Used: GATK MarkDuplicates for PCR duplicate
  removal and GATK BaseRecalibrator for base quality score recalibration (BQSR). Step
  4: SV Detection (Core'
- BWA
path: .opencode/knowledge/workflows/wf-0041-simplified-wgs-bioinformatics-analysis-pipeline-sv-detection-must-include-step-1-raw-data-qua.md
origin_source: workflow
origin_page: 43
source_entry_index: 33
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: variant-calling
---

# Simplified WGS Bioinformatics Analysis Pipeline (SV Detection) must include: Step 1: Raw Data Qua...

## One-line description

Simplified WGS Bioinformatics Analysis Pipeline (SV Detection) must include: Step 1: Raw Data Quality Control. Description: Remove low-quality sequences and adapter contamination to ensure the reliability of subsequen...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `43`
- Source entry index: `33`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0041`
- Analysis/tool category: `variant-calling`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Simplified WGS Bioinformatics Analysis Pipeline (SV Detection) must include: Step 1: Raw Data Quality Control. Description: Remove low-quality sequences and adapter contamination to ensure the reliability of subsequent analyses. Input Required: Raw sequencing files (*.fq.gz). Expected Output: Cleaned high-quality sequencing files (clean_*.fq.gz). Tools Used: fastp, a multi-threaded tool that performs quality control and generates statistical reports in one step. Step 2: Sequence Alignment. Description: Align quality-controlled sequencing reads to the reference genome and generate a sorted BAM file. Input Required: Quality-controlled sequencing files (clean_*.fq.gz), reference genome file. Expected Output: Sorted alignment file (sample.sorted.bam). Tools Used: BWA-MEM. Step 3: Post-alignment Processing. Description: Remove PCR duplicates and calibrate base quality to enhance SV detection accuracy. Input Required: Sorted BAM file (sample.sorted.bam). Expected Output: Deduplicated and recalibrated BAM file (sample.dedup.recal.bam). Tools Used: GATK MarkDuplicates for PCR duplicate removal and GATK BaseRecalibrator for base quality score recalibration (BQSR). Step 4: SV Detection (Core Step). Description: Detect structural variations (SVs) and generate raw VCF results. Input Required: Processed BAM file (sample.dedup.recal.bam). Expected Output: VCF file containing SV loci (e.g., cutesv.vcf). Recommended Tools: cuteSV.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
