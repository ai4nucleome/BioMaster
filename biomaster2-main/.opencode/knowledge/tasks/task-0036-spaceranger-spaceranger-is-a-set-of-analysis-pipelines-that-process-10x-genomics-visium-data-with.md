---
id: task-0036
title: spaceranger:spaceranger is a set of analysis pipelines that process 10x Genomics
  Visium data with...
summary: spaceranger:spaceranger is a set of analysis pipelines that process 10x Genomics
  Visium data with brightfield or fluorescence microscope images, allowing users to
  map the whole transcriptome in a variety of tissues. T...
keywords:
- spaceranger
- spaceranger:spaceranger is a set of analysis pipelines that process 10x Genomics
  Visium data with
- spaceranger:spaceranger is a set of analysis pipelines that process 10x Genomics
  Visium data with brightfield or fluorescence microscope images
- allowing users to map the whole transcriptome in a variety of tissues. This tool
  has been installed
- just use spaceranger command dierectly
- do not download spaceranger repeatly.e.g
- spaceranger count --id=Visium_FFPE_Mouse_Brain_RUN1
- create-bam=false
- transcriptome=
- path
- to
- refdata-gex-mm10-2020-A
- —-probe-set=
- adult_mouse_brain_FFPE
- Visium_FFPE_Mouse_Brain_probe_set.csv
- fastqs=
- Visium_FFPE_Mouse_Brain_fastqs
- image=
- Visium_FFPE_Mouse_Brain_image.jpg
- slide=V11J26-127
- area=B1
path: .opencode/knowledge/tasks/task-0036-spaceranger-spaceranger-is-a-set-of-analysis-pipelines-that-process-10x-genomics-visium-data-with.md
origin_source: spaceranger
origin_page: 37
source_entry_index: 32
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: spaceranger
---

# spaceranger:spaceranger is a set of analysis pipelines that process 10x Genomics Visium data with...

## One-line description

spaceranger:spaceranger is a set of analysis pipelines that process 10x Genomics Visium data with brightfield or fluorescence microscope images, allowing users to map the whole transcriptome in a variety of tissues. T...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `spaceranger`
- Origin page: `37`
- Source entry index: `32`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0036`
- Analysis/tool category: `spaceranger`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
spaceranger:spaceranger is a set of analysis pipelines that process 10x Genomics Visium data with brightfield or fluorescence microscope images, allowing users to map the whole transcriptome in a variety of tissues. This tool has been installed,just use spaceranger command dierectly,do not download spaceranger repeatly.e.g., spaceranger count --id=Visium_FFPE_Mouse_Brain_RUN1 
--create-bam=false 
 --transcriptome=/path/to/refdata-gex-mm10-2020-A 
—-probe-set=/path/to/adult_mouse_brain_FFPE/Visium_FFPE_Mouse_Brain_probe_set.csv 
 --fastqs=/path/to/adult_mouse_brain_FFPE/Visium_FFPE_Mouse_Brain_fastqs 
--image=/path/to/adult_mouse_brain_FFPE/Visium_FFPE_Mouse_Brain_image.jpg 
--slide=V11J26-127 
--area=B1
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
