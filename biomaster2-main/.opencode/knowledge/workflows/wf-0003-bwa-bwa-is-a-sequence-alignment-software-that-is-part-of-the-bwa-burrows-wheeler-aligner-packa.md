---
id: wf-0003
title: 'bwa: bwa is a sequence alignment software that is part of the BWA (Burrows-Wheeler
  Aligner) packa...'
summary: 'bwa: bwa is a sequence alignment software that is part of the BWA (Burrows-Wheeler
  Aligner) package. It is designed for mapping low-divergent sequences against a large
  reference genome, such as the human genome. BWA i...'
keywords:
- tools
- 'bwa: bwa is a sequence alignment software that is part of the BWA (Burrows-Wheeler
  Aligner) packa'
- 'bwa: bwa is a sequence alignment software that is part of the BWA (Burrows-Wheeler
  Aligner) package. It is designed for mapping low-divergent sequences against a large
  reference genome'
- 'such as the human genome. BWA includes three algorithms: BWA-backtrack'
- BWA-SW
- and bwa. BWA-backtrack is optimized for short reads up to 100bp
- while BWA-SW and bwa are intended for longer reads ranging from 70bp to 1Mbp
- BWA
path: .opencode/knowledge/workflows/wf-0003-bwa-bwa-is-a-sequence-alignment-software-that-is-part-of-the-bwa-burrows-wheeler-aligner-packa.md
origin_source: tools
origin_page: 12
source_entry_index: 3
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: tools
---

# bwa: bwa is a sequence alignment software that is part of the BWA (Burrows-Wheeler Aligner) packa...

## One-line description

bwa: bwa is a sequence alignment software that is part of the BWA (Burrows-Wheeler Aligner) package. It is designed for mapping low-divergent sequences against a large reference genome, such as the human genome. BWA i...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `tools`
- Origin page: `12`
- Source entry index: `3`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0003`
- Analysis/tool category: `tools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
bwa: bwa is a sequence alignment software that is part of the BWA (Burrows-Wheeler Aligner) package. It is designed for mapping low-divergent sequences against a large reference genome, such as the human genome. BWA includes three algorithms: BWA-backtrack, BWA-SW, and bwa. BWA-backtrack is optimized for short reads up to 100bp, while BWA-SW and bwa are intended for longer reads ranging from 70bp to 1Mbp.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
