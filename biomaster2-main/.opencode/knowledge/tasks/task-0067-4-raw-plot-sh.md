---
id: task-0067
title: '4. raw_plot.sh:'
summary: '4. raw_plot.sh: plot QC imformation from the basecall fastq file(raw_plot).
  Input : basecall fastq file Output : sevaral png file and a report html file containing
  QC imformation. Usage Run the following in the contai...'
keywords:
- raw-plot
- raw_plot.sh
- 4. raw_plot.sh
- 'plot QC imformation from the basecall fastq file(raw_plot).

  Input : basecall fastq file'
- 'Output : sevaral png file and a report html file containing QC imformation.

  Usage

  Run the following in the container

  '
- scripts
- raw_plot.sh <fastq> <outdir>
- '# fastq : basecall fastq file.

  # outdir : directory to store QC imformation files'
path: .opencode/knowledge/tasks/task-0067-4-raw-plot-sh.md
origin_source: raw_plot.sh
origin_page: 68
source_entry_index: 63
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: raw-plot
---

# 4. raw_plot.sh:

## One-line description

4. raw_plot.sh: plot QC imformation from the basecall fastq file(raw_plot). Input : basecall fastq file Output : sevaral png file and a report html file containing QC imformation. Usage Run the following in the contai...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `raw_plot.sh`
- Origin page: `68`
- Source entry index: `63`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0067`
- Analysis/tool category: `raw-plot`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
4. raw_plot.sh:
 plot QC imformation from the basecall fastq file(raw_plot).
Input : basecall fastq file 
Output : sevaral png file and a report html file containing QC imformation.
Usage
Run the following in the container
./scripts/raw_plot.sh <fastq> <outdir>  
# fastq : basecall fastq file.
# outdir : directory to store QC imformation files.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
