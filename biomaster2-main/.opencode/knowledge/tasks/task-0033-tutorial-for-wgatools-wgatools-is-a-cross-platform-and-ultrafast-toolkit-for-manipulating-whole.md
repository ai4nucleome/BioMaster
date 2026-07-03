---
id: task-0033
title: 'Tutorial for wgatools: wgatools is a cross-platform and ultrafast toolkit
  for manipulating Whole...'
summary: 'Tutorial for wgatools: wgatools is a cross-platform and ultrafast toolkit
  for manipulating Whole Genome Alignment files (MAF, PAF, CHAIN formats). Basic usage
  starts with ''wgatools <COMMAND>'' and each command supports...'
keywords:
- nichepca-tutorial
- NichePCA_tutorial
- 'Tutorial for wgatools: wgatools is a cross-platform and ultrafast toolkit for manipulating
  Whole'
- 'Tutorial for wgatools: wgatools is a cross-platform and ultrafast toolkit for manipulating
  Whole Genome Alignment files (MAF'
- PAF
- 'CHAIN formats). Basic usage starts with ''wgatools <COMMAND>'' and each command
  supports ''-h'' for help. Common conversions include: ''wgatools maf2paf test.maf
  > test.paf'''
- 'or reverse with ''wgatools paf2maf test.paf --target target.fa --query query.fa
  > test.maf''. Piping is supported: ''cat test.maf'
- wgatools maf2paf
- wgatools paf2maf -g target.fa -q query.fa > test.maf'. For visualizations
- '''wgatools dotplot -f paf test.paf > out.html'' generates base-level dotplots'
- 'or use ''-m overview'' for summary plots: ''wgatools dotplot test.maf -m overview
  > overview.html''. Extract specific genomic regions from MAF using indexed access:
  ''wgatools maf-index test.maf'' and ''wgatools maf-ext test.maf -r chr1:1-100''.
  To browse MAF interactively in terminal: ''wgatools tview test.maf''. Variant calling
  from MAF or PAF (with genome fasta) is supported: ''wgatools call test.maf -s -l0''
  or ''wgatools call test.paf -s -l0 --target target.fa --query query.fa -f paf''.
  Splitting large MAF blocks by length: ''wgatools chunk -l 100 test.maf -o chunked.maf''.
  Generate alignment statistics'
path: .opencode/knowledge/tasks/task-0033-tutorial-for-wgatools-wgatools-is-a-cross-platform-and-ultrafast-toolkit-for-manipulating-whole.md
origin_source: NichePCA_tutorial
origin_page: 34
source_entry_index: 29
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: nichepca-tutorial
---

# Tutorial for wgatools: wgatools is a cross-platform and ultrafast toolkit for manipulating Whole...

## One-line description

Tutorial for wgatools: wgatools is a cross-platform and ultrafast toolkit for manipulating Whole Genome Alignment files (MAF, PAF, CHAIN formats). Basic usage starts with 'wgatools <COMMAND>' and each command supports...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `NichePCA_tutorial`
- Origin page: `34`
- Source entry index: `29`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0033`
- Analysis/tool category: `nichepca-tutorial`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Tutorial for wgatools: wgatools is a cross-platform and ultrafast toolkit for manipulating Whole Genome Alignment files (MAF, PAF, CHAIN formats). Basic usage starts with 'wgatools <COMMAND>' and each command supports '-h' for help. Common conversions include: 'wgatools maf2paf test.maf > test.paf', or reverse with 'wgatools paf2maf test.paf --target target.fa --query query.fa > test.maf'. Piping is supported: 'cat test.maf | wgatools maf2paf | wgatools paf2maf -g target.fa -q query.fa > test.maf'. For visualizations, 'wgatools dotplot -f paf test.paf > out.html' generates base-level dotplots, or use '-m overview' for summary plots: 'wgatools dotplot test.maf -m overview > overview.html'. Extract specific genomic regions from MAF using indexed access: 'wgatools maf-index test.maf' and 'wgatools maf-ext test.maf -r chr1:1-100'. To browse MAF interactively in terminal: 'wgatools tview test.maf'. Variant calling from MAF or PAF (with genome fasta) is supported: 'wgatools call test.maf -s -l0' or 'wgatools call test.paf -s -l0 --target target.fa --query query.fa -f paf'. Splitting large MAF blocks by length: 'wgatools chunk -l 100 test.maf -o chunked.maf'. Generate alignment statistics: 'wgatools stat test.maf' or 'wgatools stat -f paf test.paf'. Validate or fix PAF inconsistencies: 'wgatools validate wrong.paf' and optionally output fixed version: 'wgatools validate wrong.paf -f happy.paf'. Filter alignment blocks by block length or query size: 'wgatools filter test.maf -q 1000000 > filt.maf' or filter all-to-all alignments: 'wgatools filter all2all.paf -a 1000000 > filt.paf'. Rename sequences to distinguish target/query: 'wgatools rename --prefixs REF.,QUERY. input.maf > rename.maf'. Compute coverage for all-to-all alignments: 'wgatools pafcov all.paf > all.cov.beds'. Generate pseudo-MAF for divergence analysis: 'wgatools pafpseudo -f all.fa.gz all.paf -o out_dir -t 10'. Enable auto-completion: 'wgatools gen-completion --shell fish > ~/.config/fish/completions/wgatools.fish'. Version: 0.1.0, Author: Wenjie Wei.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
