---
id: wf-0025
title: Squidpy is a tool for the analysis and visualization of spatial molecular data.
  It builds on top...
summary: Squidpy is a tool for the analysis and visualization of spatial molecular
  data. It builds on top of scanpy and anndata, from which it inherits modularity
  and scalability. It provides analysis tools that leverages the...
keywords:
- scrnaseq-cluster
- tools
- Squidpy is a tool for the analysis and visualization of spatial molecular data.
  It builds on top
- Squidpy is a tool for the analysis and visualization of spatial molecular data.
  It builds on top of scanpy and anndata
- from which it inherits modularity and scalability. It provides analysis tools that
  leverages the spatial coordinates of the data
- as well as tissue images if available
- Scanpy
path: .opencode/knowledge/workflows/wf-0025-squidpy-is-a-tool-for-the-analysis-and-visualization-of-spatial-molecular-data-it-builds-on-top.md
origin_source: tools
origin_page: 27
source_entry_index: 17
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: scrnaseq-cluster
---

# Squidpy is a tool for the analysis and visualization of spatial molecular data. It builds on top...

## One-line description

Squidpy is a tool for the analysis and visualization of spatial molecular data. It builds on top of scanpy and anndata, from which it inherits modularity and scalability. It provides analysis tools that leverages the...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `tools`
- Origin page: `27`
- Source entry index: `17`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0025`
- Analysis/tool category: `scrnaseq-cluster`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Squidpy is a tool for the analysis and visualization of spatial molecular data. It builds on top of scanpy and anndata, from which it inherits modularity and scalability. It provides analysis tools that leverages the spatial coordinates of the data, as well as tissue images if available.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
