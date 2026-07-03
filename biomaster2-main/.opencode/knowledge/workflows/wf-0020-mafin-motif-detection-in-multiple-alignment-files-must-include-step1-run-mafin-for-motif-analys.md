---
id: wf-0020
title: 'MAFin: Motif Detection in Multiple Alignment Files must include:Step1: Run
  MAFin for motif analys...'
summary: 'MAFin: Motif Detection in Multiple Alignment Files must include:Step1: Run
  MAFin for motif analysis. Description: This CLI tool allows motif detection within
  MAF (Multiple Alignment Format) files using one of the foll...'
keywords:
- motif-analysis
- MAFin_workflow
- 'MAFin: Motif Detection in Multiple Alignment Files must include:Step1: Run MAFin
  for motif analys'
- 'MAFin: Motif Detection in Multiple Alignment Files must include:Step1: Run MAFin
  for motif analysis. Description: This CLI tool allows motif detection within MAF
  (Multiple Alignment Format) files using one of the following search methods: regular
  expression (regex)'
- K-mers
- 'or Position Weight Matrices (PWMs) in JASPAR format. Users can configure the tool
  to search within only the reference genome or across all aligned genomes. It also
  supports scanning both forward and reverse strands. The tool is optimized with parallel
  processing to accelerate large-scale searches. Expected Input: One or more `.maf`
  files containing multiple sequence alignments. Expected Output: Default output includes
  a BED-formatted file named `regex_search_motif_hits.bed`. If `--detailed_report`
  is specified'
- 'the tool additionally produces a JSON file (`ref_genome_regex_search_AGT_motif_hits.json`)
  and a CSV file (`ref_genome_regex_search_AGT_motif_hits.csv`) that provide an analytical
  summary of motif hits. Tools Used: MAFin command-line interface'
- supporting parallel processing and flexible motif formats
- MAFin
path: .opencode/knowledge/workflows/wf-0020-mafin-motif-detection-in-multiple-alignment-files-must-include-step1-run-mafin-for-motif-analys.md
origin_source: MAFin_workflow
origin_page: 22
source_entry_index: 12
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: motif-analysis
---

# MAFin: Motif Detection in Multiple Alignment Files must include:Step1: Run MAFin for motif analys...

## One-line description

MAFin: Motif Detection in Multiple Alignment Files must include:Step1: Run MAFin for motif analysis. Description: This CLI tool allows motif detection within MAF (Multiple Alignment Format) files using one of the foll...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `MAFin_workflow`
- Origin page: `22`
- Source entry index: `12`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0020`
- Analysis/tool category: `motif-analysis`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
MAFin: Motif Detection in Multiple Alignment Files must include:Step1: Run MAFin for motif analysis. Description: This CLI tool allows motif detection within MAF (Multiple Alignment Format) files using one of the following search methods: regular expression (regex), K-mers, or Position Weight Matrices (PWMs) in JASPAR format. Users can configure the tool to search within only the reference genome or across all aligned genomes. It also supports scanning both forward and reverse strands. The tool is optimized with parallel processing to accelerate large-scale searches. Expected Input: One or more `.maf` files containing multiple sequence alignments. Expected Output: Default output includes a BED-formatted file named `regex_search_motif_hits.bed`. If `--detailed_report` is specified, the tool additionally produces a JSON file (`ref_genome_regex_search_AGT_motif_hits.json`) and a CSV file (`ref_genome_regex_search_AGT_motif_hits.csv`) that provide an analytical summary of motif hits. Tools Used: MAFin command-line interface, supporting parallel processing and flexible motif formats.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
