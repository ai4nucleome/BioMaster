---
id: wf-0023
title: 'NichePCA: PCA-based Spatial Domain Identification for Single-Cell Spatial
  Transcriptomics Data mu...'
summary: 'NichePCA: PCA-based Spatial Domain Identification for Single-Cell Spatial
  Transcriptomics Data must include: Step1: Run NichePCA Analysis. Description: NichePCA
  is designed for identifying spatial domains in single-ce...'
keywords:
- scrnaseq-cluster
- NichePCA_workflow
- 'NichePCA: PCA-based Spatial Domain Identification for Single-Cell Spatial Transcriptomics
  Data mu'
- 'NichePCA: PCA-based Spatial Domain Identification for Single-Cell Spatial Transcriptomics
  Data must include: Step1: Run NichePCA Analysis. Description: NichePCA is designed
  for identifying spatial domains in single-cell spatial transcriptomics data through
  Principal Component Analysis (PCA). It performs dimensionality reduction on spatially
  resolved gene expression profiles and identifies distinct spatial niches or domains.
  Expected Input: A single `.h5ad` file containing spatial transcriptomics data'
- 'including gene expression matrices and spatial coordinates. Expected Output: Visualization
  results'
- 'typically as spatial plots highlighting domain structures inferred from PCA. Tools
  Used: NichePCA module or script'
- typically integrated within a Python analysis pipeline (e.g
- using Scanpy or custom scripts)
- Scanpy
path: .opencode/knowledge/workflows/wf-0023-nichepca-pca-based-spatial-domain-identification-for-single-cell-spatial-transcriptomics-data-mu.md
origin_source: NichePCA_workflow
origin_page: 25
source_entry_index: 15
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: scrnaseq-cluster
---

# NichePCA: PCA-based Spatial Domain Identification for Single-Cell Spatial Transcriptomics Data mu...

## One-line description

NichePCA: PCA-based Spatial Domain Identification for Single-Cell Spatial Transcriptomics Data must include: Step1: Run NichePCA Analysis. Description: NichePCA is designed for identifying spatial domains in single-ce...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `NichePCA_workflow`
- Origin page: `25`
- Source entry index: `15`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0023`
- Analysis/tool category: `scrnaseq-cluster`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
NichePCA: PCA-based Spatial Domain Identification for Single-Cell Spatial Transcriptomics Data must include: Step1: Run NichePCA Analysis. Description: NichePCA is designed for identifying spatial domains in single-cell spatial transcriptomics data through Principal Component Analysis (PCA). It performs dimensionality reduction on spatially resolved gene expression profiles and identifies distinct spatial niches or domains. Expected Input: A single `.h5ad` file containing spatial transcriptomics data, including gene expression matrices and spatial coordinates. Expected Output: Visualization results, typically as spatial plots highlighting domain structures inferred from PCA. Tools Used: NichePCA module or script, typically integrated within a Python analysis pipeline (e.g., using Scanpy or custom scripts).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
