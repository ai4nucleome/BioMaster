---
id: wf-0016
title: Predict Fusion genes using STAR-Fusion workflow :Below is a detailed, step-by-step
  workflow for R...
summary: 'Predict Fusion genes using STAR-Fusion workflow :Below is a detailed, step-by-step
  workflow for RNA-Seq Fusion Gene Detection using STAR and STAR-Fusion, formatted
  similarly to the example provided. ## Detailed RNA-Se...'
keywords:
- rnaseq-de
- workflow
- Predict Fusion genes using STAR-Fusion workflow :Below is a detailed
- step-by-step workflow for R
- step-by-step workflow for RNA-Seq Fusion Gene Detection using STAR and STAR-Fusion
- formatted similarly to the example provided
- '## Detailed RNA-Seq Fusion Gene Detection Workflow'
- 'Step 1: RNA-Seq Data QC and Read Mapping

  **Description:**

  1. (Conduct quality control (QC) on raw FASTQ files using tools like FastQC and
  Trimmomatic to remove low-quality reads and adapter contaminants'
- Step 2. Use STAR to align the (cleaned) RNA-Seq reads to the reference genome. Ensure
  you enable chimeric (fusion) detection by setting parameters such as --chimOutType
  Junctions so that STAR outputs Chimeric.out.junction files
- '**Input Required:**

  - Raw or cleaned RNA-Seq FASTQ files

  - STAR genome index'
- '**Expected Output:**

  - Alignment files: Aligned.out.sam or Aligned.sortedByCoord.out.bam

  - Chimeric junction file: Chimeric.out.junction (key for fusion detection)'
- '**Tools Used:**

  - FastQC'
- 'Trimmomatic (or equivalent) for QC

  - STAR for alignment'
- '### Step3: Fusion Gene Prediction with STAR-Fusion

  **Description:**

  1. Run STAR-Fusion on the resulting STAR alignments (specifically the Chimeric.out.junction
  file) using the pre'
- FastQC
- Trimmomatic
- STAR-Fusion
- STAR
path: .opencode/knowledge/workflows/wf-0016-predict-fusion-genes-using-star-fusion-workflow-below-is-a-detailed-step-by-step-workflow-for-r.md
origin_source: workflow
origin_page: 18
source_entry_index: 8
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: rnaseq-de
---

# Predict Fusion genes using STAR-Fusion workflow :Below is a detailed, step-by-step workflow for R...

## One-line description

Predict Fusion genes using STAR-Fusion workflow :Below is a detailed, step-by-step workflow for RNA-Seq Fusion Gene Detection using STAR and STAR-Fusion, formatted similarly to the example provided. ## Detailed RNA-Se...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `18`
- Source entry index: `8`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0016`
- Analysis/tool category: `rnaseq-de`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Predict Fusion genes using STAR-Fusion workflow :Below is a detailed, step-by-step workflow for RNA-Seq Fusion Gene Detection using STAR and STAR-Fusion, formatted similarly to the example provided.

## Detailed RNA-Seq Fusion Gene Detection Workflow

 Step 1: RNA-Seq Data QC and Read Mapping
**Description:**
1. (Conduct quality control (QC) on raw FASTQ files using tools like FastQC and Trimmomatic to remove low-quality reads and adapter contaminants.
  Step 2. Use STAR to align the (cleaned) RNA-Seq reads to the reference genome. Ensure you enable chimeric (fusion) detection by setting parameters such as --chimOutType Junctions so that STAR outputs Chimeric.out.junction files.

**Input Required:**
- Raw or cleaned RNA-Seq FASTQ files
- STAR genome index 

**Expected Output:**
- Alignment files: Aligned.out.sam or Aligned.sortedByCoord.out.bam
- Chimeric junction file: Chimeric.out.junction (key for fusion detection)

**Tools Used:**
- FastQC, Trimmomatic (or equivalent) for QC
- STAR for alignment

---

### Step3: Fusion Gene Prediction with STAR-Fusion
**Description:**
1. Run STAR-Fusion on the resulting STAR alignments (specifically the Chimeric.out.junction file) using the prepared STAR-Fusion genome library.
2. (Optional) Enable FusionInspector (e.g., --FusionInspector validate) for deeper validation and to generate more comprehensive information about candidate fusion genes.

**Input Required:**
- Chimeric.out.junction from STAR alignment
- STAR-Fusion genome library directory
- (Optionally) the BAM alignment file for additional context

**Expected Output:**
- A main results file (e.g., star-fusion.fusion_predictions.tsv) containing predicted fusions
- Additional FusionInspector files and visualization outputs (if used)

**Tools Used:**
- STAR-Fusion (core tool)
- (Optionally) FusionInspector (bundled with STAR-Fusion)

---

.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
