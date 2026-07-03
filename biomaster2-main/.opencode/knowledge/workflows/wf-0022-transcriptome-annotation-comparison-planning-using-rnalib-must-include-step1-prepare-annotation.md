---
id: wf-0022
title: 'Transcriptome Annotation Comparison Planning using rnalib must include:Step1:
  Prepare Annotation...'
summary: 'Transcriptome Annotation Comparison Planning using rnalib must include:Step1:
  Prepare Annotation Resources. Description: Gather annotation files (e.g., Gencode,
  Chess, FlyBase, MirGeneDB) and define filters for target...'
keywords:
- annotation-comparison
- rnalib_analysis_planning
- 'Transcriptome Annotation Comparison Planning using rnalib must include:Step1: Prepare
  Annotation'
- 'Transcriptome Annotation Comparison Planning using rnalib must include:Step1: Prepare
  Annotation Resources. Description: Gather annotation files (e.g'
- Gencode
- Chess
- FlyBase
- 'MirGeneDB) and define filters for target gene types or genomic regions. Expected
  Input: Gene annotation files (.gff'
- gtf)
- reference genome sequences
- 'optional alias mapping files. Expected Output: Configured transcriptome datasets
  ready for comparative analysis. Step2: Perform Comparative Analysis. Description:
  Compare gene sets or transcript structures across annotations'
- assessing differences in gene naming
- genomic coordinates
- splice junction motifs
- 'and CDS lengths. Expected Input: Prepared transcriptome datasets from Step1. Expected
  Output: Statistical summaries'
- comparative plots
- lists of unique
- shared annotations
- and optionally visualizations (e.g
- IGV tracks)
path: .opencode/knowledge/workflows/wf-0022-transcriptome-annotation-comparison-planning-using-rnalib-must-include-step1-prepare-annotation.md
origin_source: rnalib_analysis_planning
origin_page: 24
source_entry_index: 14
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: annotation-comparison
---

# Transcriptome Annotation Comparison Planning using rnalib must include:Step1: Prepare Annotation...

## One-line description

Transcriptome Annotation Comparison Planning using rnalib must include:Step1: Prepare Annotation Resources. Description: Gather annotation files (e.g., Gencode, Chess, FlyBase, MirGeneDB) and define filters for target...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `rnalib_analysis_planning`
- Origin page: `24`
- Source entry index: `14`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0022`
- Analysis/tool category: `annotation-comparison`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Transcriptome Annotation Comparison Planning using rnalib must include:Step1: Prepare Annotation Resources. Description: Gather annotation files (e.g., Gencode, Chess, FlyBase, MirGeneDB) and define filters for target gene types or genomic regions. Expected Input: Gene annotation files (.gff/.gtf), reference genome sequences, optional alias mapping files. Expected Output: Configured transcriptome datasets ready for comparative analysis. Step2: Perform Comparative Analysis. Description: Compare gene sets or transcript structures across annotations, assessing differences in gene naming, genomic coordinates, splice junction motifs, and CDS lengths. Expected Input: Prepared transcriptome datasets from Step1. Expected Output: Statistical summaries, comparative plots, lists of unique/shared annotations, and optionally visualizations (e.g., IGV tracks).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
