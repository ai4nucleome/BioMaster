---
id: wf-0019
title: 'Gene-Centric Functional Enrichment Analysis Workflow using GeneFEAST must
  include:Step1: Prepare...'
summary: 'Gene-Centric Functional Enrichment Analysis Workflow using GeneFEAST must
  include:Step1: Prepare Configuration File. Description: Based on the available gene-level
  quantitative data, a configuration file run.yml shoul...'
keywords:
- functional-enrichment
- GeneFEAST_workflow
- 'Gene-Centric Functional Enrichment Analysis Workflow using GeneFEAST must include:Step1:
  Prepare'
- 'Gene-Centric Functional Enrichment Analysis Workflow using GeneFEAST must include:Step1:
  Prepare Configuration File. Description: Based on the available gene-level quantitative
  data'
- a configuration file run.yml should be created and edited. This file specifies the
  input gene list
- expression matrices
- 'and analysis parameters for GeneFEAST. Expected Output: A completed configuration
  file named run.yml. Tools Used: Manual editing or script-based generation of run.yml.
  Step2: Run GeneFEAST Analysis. Description: Invoke GeneFEAST with the run.yml configuration
  file. GeneFEAST will perform gene-centric functional enrichment analysis (FEA) and
  generate a series of visualizations and a navigable HTML report. Expected Output:
  A result directory containing: Multiple visualization outputs (e.g'
- expression heatmaps
- enrichment summaries)
- 'A system-organized and navigable HTML report summarizing the analysis. Key Features
  of GeneFEAST: Gene-Centric Enrichment Interpretation: Enables easy identification
  of gene sets driving repeated enrichment signals'
- 'with direct reference to the gene-level quantitative data used to define the input.
  Cross-Study FEA Integration: Supports the comparison of FE'
- GeneFEAST
path: .opencode/knowledge/workflows/wf-0019-gene-centric-functional-enrichment-analysis-workflow-using-genefeast-must-include-step1-prepare.md
origin_source: GeneFEAST_workflow
origin_page: 21
source_entry_index: 11
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: functional-enrichment
---

# Gene-Centric Functional Enrichment Analysis Workflow using GeneFEAST must include:Step1: Prepare...

## One-line description

Gene-Centric Functional Enrichment Analysis Workflow using GeneFEAST must include:Step1: Prepare Configuration File. Description: Based on the available gene-level quantitative data, a configuration file run.yml shoul...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `GeneFEAST_workflow`
- Origin page: `21`
- Source entry index: `11`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0019`
- Analysis/tool category: `functional-enrichment`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Gene-Centric Functional Enrichment Analysis Workflow using GeneFEAST must include:Step1: Prepare Configuration File. Description: Based on the available gene-level quantitative data, a configuration file run.yml should be created and edited. This file specifies the input gene list, expression matrices, and analysis parameters for GeneFEAST. Expected Output: A completed configuration file named run.yml. Tools Used: Manual editing or script-based generation of run.yml. Step2: Run GeneFEAST Analysis. Description: Invoke GeneFEAST with the run.yml configuration file. GeneFEAST will perform gene-centric functional enrichment analysis (FEA) and generate a series of visualizations and a navigable HTML report. Expected Output: A result directory containing: Multiple visualization outputs (e.g., expression heatmaps, enrichment summaries); A system-organized and navigable HTML report summarizing the analysis. Key Features of GeneFEAST: Gene-Centric Enrichment Interpretation: Enables easy identification of gene sets driving repeated enrichment signals, with direct reference to the gene-level quantitative data used to define the input. Cross-Study FEA Integration: Supports the comparison of FEA results from multiple studies, highlighting expression patterns of genes that are differentially expressed under at least one condition, and identifying shared enriched terms across conditions. HTML Report Generation: Produces an interactive and systematized report for exploration and hypothesis generation. Advancement of Gene-Centric Hypotheses: Helps connect overlapping enrichment results with their underlying genes and datasets, facilitating hypothesis development and providing key insights for downstream experimental validation.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
