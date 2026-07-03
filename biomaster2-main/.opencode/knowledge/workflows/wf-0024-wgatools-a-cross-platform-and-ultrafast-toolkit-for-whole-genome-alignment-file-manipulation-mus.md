---
id: wf-0024
title: 'WGATools: A Cross-Platform and Ultrafast Toolkit for Whole Genome Alignment
  File Manipulation mus...'
summary: 'WGATools: A Cross-Platform and Ultrafast Toolkit for Whole Genome Alignment
  File Manipulation must include: Step1: Select Command Based on Task. Description:
  WGATools provides a suite of high-performance subcommands f...'
keywords:
- variant-calling
- wgatools_manual
- 'WGATools: A Cross-Platform and Ultrafast Toolkit for Whole Genome Alignment File
  Manipulation mus'
- 'WGATools: A Cross-Platform and Ultrafast Toolkit for Whole Genome Alignment File
  Manipulation must include: Step1: Select Command Based on Task. Description: WGATools
  provides a suite of high-performance subcommands for converting'
- analyzing
- and visualizing alignment files in MAF
- PAF
- and CHAIN formats. Users can convert between formats (e.g
- '`maf2paf`'
- '`paf2chain`)'
- extract and view MAF content (`maf-ext`
- '`tview`)'
- perform dotplot visualizations (`dotplot`)
- call variants (`call`)
- compute statistics (`stat`)
- filter or rename records
- and calculate alignment coverage (`pafcov`). WGATools also supports chaining commands
  with stdin
- stdout
- indexing MAF files
- generating shell completions
- 'and fixing invalid PAF files. Expected Input: A variety of alignment files in MAF'
- 'or CHAIN format. Optional inputs include reference and query FASTA files when required
  by format conversion. Expected Output: Converted alignment files'
- filtered or renamed alignments
- interactive HTML dotplots
- statistical summaries
- extracted region outputs
- 'and VCF variant calls. Tools Used: WGATools command-line interface with multi-threading
  support'
- compatible with Linux
- macOS
- and Windows. Example C
path: .opencode/knowledge/workflows/wf-0024-wgatools-a-cross-platform-and-ultrafast-toolkit-for-whole-genome-alignment-file-manipulation-mus.md
origin_source: wgatools_manual
origin_page: 26
source_entry_index: 16
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: variant-calling
---

# WGATools: A Cross-Platform and Ultrafast Toolkit for Whole Genome Alignment File Manipulation mus...

## One-line description

WGATools: A Cross-Platform and Ultrafast Toolkit for Whole Genome Alignment File Manipulation must include: Step1: Select Command Based on Task. Description: WGATools provides a suite of high-performance subcommands f...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `wgatools_manual`
- Origin page: `26`
- Source entry index: `16`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0024`
- Analysis/tool category: `variant-calling`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
WGATools: A Cross-Platform and Ultrafast Toolkit for Whole Genome Alignment File Manipulation must include: Step1: Select Command Based on Task. Description: WGATools provides a suite of high-performance subcommands for converting, analyzing, and visualizing alignment files in MAF, PAF, and CHAIN formats. Users can convert between formats (e.g., `maf2paf`, `paf2chain`), extract and view MAF content (`maf-ext`, `tview`), perform dotplot visualizations (`dotplot`), call variants (`call`), compute statistics (`stat`), filter or rename records, and calculate alignment coverage (`pafcov`). WGATools also supports chaining commands with stdin/stdout, indexing MAF files, generating shell completions, and fixing invalid PAF files. Expected Input: A variety of alignment files in MAF, PAF, or CHAIN format. Optional inputs include reference and query FASTA files when required by format conversion. Expected Output: Converted alignment files, filtered or renamed alignments, interactive HTML dotplots, statistical summaries, extracted region outputs, and VCF variant calls. Tools Used: WGATools command-line interface with multi-threading support, compatible with Linux, macOS, and Windows. Example Commands: `wgatools maf2paf test.maf > test.paf` for format conversion; `wgatools dotplot test.maf -m overview > out.html` for visualization; `wgatools call test.paf -s -l0 --target target.fa --query query.fa -f paf` for variant calling. Advanced Features: Soft-filtering, navigation-based terminal viewing, and output compression support.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
