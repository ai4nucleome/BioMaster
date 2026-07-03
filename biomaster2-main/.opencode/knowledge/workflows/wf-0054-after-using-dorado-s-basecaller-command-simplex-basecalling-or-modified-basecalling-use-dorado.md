---
id: wf-0054
title: After using dorado's basecaller command(simplex basecalling or modified basecalling),
  use dorado'...
summary: After using dorado's basecaller command(simplex basecalling or modified basecalling),
  use dorado's summary command to output a tab-separated file with read level sequencing
  information from the bam file generated duri...
keywords:
- nanopore
- workflow
- After using dorado's basecaller command(simplex basecalling or modified basecalling)
- use dorado'
- use dorado's summary command to output a tab-separated file with read level sequencing
  information from the bam file generated during basecalling
- 'Input : basecaller’s output bam file'
- 'Output : a summary tsv file.

  Usage

  Run the following in the container

  '
- dorado-0.9.1-linux-x64
- bin
- dorado summary <bam> > <out>
- '# bam : basecaller’s output bam file.

  # out : name of output tsv file'
- dorado
path: .opencode/knowledge/workflows/wf-0054-after-using-dorado-s-basecaller-command-simplex-basecalling-or-modified-basecalling-use-dorado.md
origin_source: workflow
origin_page: 54
source_entry_index: 44
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: nanopore
---

# After using dorado's basecaller command(simplex basecalling or modified basecalling), use dorado'...

## One-line description

After using dorado's basecaller command(simplex basecalling or modified basecalling), use dorado's summary command to output a tab-separated file with read level sequencing information from the bam file generated duri...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `54`
- Source entry index: `44`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0054`
- Analysis/tool category: `nanopore`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
After using dorado's basecaller command(simplex basecalling or modified basecalling), use dorado's summary command to output a tab-separated file with read level sequencing information from the bam file generated during basecalling. 
Input : basecaller’s output bam file 
Output : a summary tsv file.
Usage
Run the following in the container
../dorado-0.9.1-linux-x64/bin/dorado summary <bam> > <out>  
# bam : basecaller’s output bam file.
# out : name of output tsv file.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
