---
id: task-0048
title: 'Tool: filter_pas_peaks.py'
summary: 'Tool: filter_pas_peaks.py Purpose: Custom Python script to detect PAS peaks
  from coverage profile. Automatically selects regions with local maxima at 3′ ends.
  Input: Coverage profile (text) Output: PAS_sites.bed Comma...'
keywords:
- task
- 'Tool: filter_pas_peaks.py'
- 'Tool: filter_pas_peaks.py

  Purpose: Custom Python script to detect PAS peaks from coverage profile. Automatically
  selects regions with local maxima at 3′ ends.

  Input: Coverage profile (text)

  Output: PAS_sites.bed

  Command Example'
- python filter_pas_peaks.py --input coverage.txt --output PAS_sites.bed
path: .opencode/knowledge/tasks/task-0048-tool-filter-pas-peaks-py.md
origin_source: task
origin_page: 49
source_entry_index: 44
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: task
---

# Tool: filter_pas_peaks.py

## One-line description

Tool: filter_pas_peaks.py Purpose: Custom Python script to detect PAS peaks from coverage profile. Automatically selects regions with local maxima at 3′ ends. Input: Coverage profile (text) Output: PAS_sites.bed Comma...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `task`
- Origin page: `49`
- Source entry index: `44`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0048`
- Analysis/tool category: `task`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Tool: filter_pas_peaks.py
Purpose: Custom Python script to detect PAS peaks from coverage profile. Automatically selects regions with local maxima at 3′ ends.
Input: Coverage profile (text)
Output: PAS_sites.bed
Command Example:
  python filter_pas_peaks.py --input coverage.txt --output PAS_sites.bed
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
