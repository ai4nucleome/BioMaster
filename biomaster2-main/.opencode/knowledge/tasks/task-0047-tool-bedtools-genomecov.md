---
id: task-0047
title: 'Tool: bedtools genomecov'
summary: 'Tool: bedtools genomecov Purpose: Generate base-level coverage profile from
  BAM file to infer PAS sites. Input: BAM file Output: Coverage profile Command Example:
  bedtools genomecov -ibam aligned.bam -d > coverage.txt'
keywords:
- bedtools
- task
- 'Tool: bedtools genomecov'
- 'Tool: bedtools genomecov

  Purpose: Generate base-level coverage profile from BAM file to infer PAS sites.

  Input: BAM file

  Output: Coverage profile

  Command Example'
- bedtools genomecov -ibam aligned.bam -d > coverage.txt
path: .opencode/knowledge/tasks/task-0047-tool-bedtools-genomecov.md
origin_source: task
origin_page: 48
source_entry_index: 43
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: bedtools
---

# Tool: bedtools genomecov

## One-line description

Tool: bedtools genomecov Purpose: Generate base-level coverage profile from BAM file to infer PAS sites. Input: BAM file Output: Coverage profile Command Example: bedtools genomecov -ibam aligned.bam -d > coverage.txt

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `task`
- Origin page: `48`
- Source entry index: `43`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0047`
- Analysis/tool category: `bedtools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Tool: bedtools genomecov
Purpose: Generate base-level coverage profile from BAM file to infer PAS sites.
Input: BAM file
Output: Coverage profile
Command Example:
  bedtools genomecov -ibam aligned.bam -d > coverage.txt
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
