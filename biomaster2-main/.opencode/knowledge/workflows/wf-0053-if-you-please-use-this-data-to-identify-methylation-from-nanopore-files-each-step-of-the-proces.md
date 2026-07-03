---
id: wf-0053
title: 'IF you: Please use this data to identify methylation from nanopore files.
  Each step of the proces...'
summary: 'IF you: Please use this data to identify methylation from nanopore files.
  Each step of the process has been organized into specific executable scripts(2 steps).
  The bash tool is used. All the scripts are in the folder...'
keywords:
- nanopore
- workflow
- 'IF you: Please use this data to identify methylation from nanopore files. Each
  step of the proces'
- 'IF you: Please use this data to identify methylation from nanopore files. Each
  step of the process has been organized into specific executable scripts(2 steps).
  The bash tool is used. All the scripts are in the folder'
- scripts
- The steps must be generated in strict order
- '1. methy_iden.sh:

  do modified basecalling from nanopore pod5 files'
- 'Input : a file folder containing nanopore files in fast5'
- 'pod5 format and a reference genome fa file

  Output : a bam file.

  Usage

  Run the following in the container

  '
- 'methy_iden.sh <pod5dir> <ref> <out>

  # pod5dir: Path of a file folder containing nanopore files in fast5'
- 'pod5 format.

  # ref : reference genome fa file

  # out : name of output bam file'
- 2. basecall_sum.sh
- output a tab-separated file with read level sequencing information from the bam
  file generated during basecalling
- 'Input : basecaller’s output bam file'
- 'Output : a summary tsv file.

  Usage

  Run the following in the container

  '
- basecall_sum.sh <bam> <out>
- '# bam : basecaller’s output bam file.

  # out : name of output tsv file'
path: .opencode/knowledge/workflows/wf-0053-if-you-please-use-this-data-to-identify-methylation-from-nanopore-files-each-step-of-the-proces.md
origin_source: workflow
origin_page: 53
source_entry_index: 43
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: nanopore
---

# IF you: Please use this data to identify methylation from nanopore files. Each step of the proces...

## One-line description

IF you: Please use this data to identify methylation from nanopore files. Each step of the process has been organized into specific executable scripts(2 steps). The bash tool is used. All the scripts are in the folder...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `53`
- Source entry index: `43`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0053`
- Analysis/tool category: `nanopore`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
IF you: Please use this data to identify methylation from nanopore files. Each step of the process has been organized into specific executable scripts(2 steps). The bash tool is used. All the scripts are in the folder ./scripts/. The steps must be generated in strict order. 

1. methy_iden.sh:
do modified basecalling from nanopore pod5 files. 
Input : a file folder containing nanopore files in fast5/pod5 format and a reference genome fa file
Output : a bam file.
Usage
Run the following in the container
./scripts/methy_iden.sh <pod5dir> <ref> <out>
# pod5dir: Path of a file folder containing nanopore files in fast5/pod5 format.
# ref : reference genome fa file
# out : name of output bam file.
 2. basecall_sum.sh:
 output a tab-separated file with read level sequencing information from the bam file generated during basecalling. 
Input : basecaller’s output bam file 
Output : a summary tsv file.
Usage
Run the following in the container
./scripts/basecall_sum.sh <bam> <out>  
# bam : basecaller’s output bam file.
# out : name of output tsv file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
