---
id: task-0050
title: 'Tool: extract_3p_end'
summary: 'Tool: extract_3p_end Purpose: Extract the last 20 bases (3′ end) from each
  read in a trimmed FASTQ file without using a reference genome. Input: Trimmed FASTQ
  file Output: FASTA file containing 3′ end sequences Note:...'
keywords:
- extract-3p-end
- extract_3p_end
- 'Tool: extract_3p_end'
- 'Tool: extract_3p_end

  Purpose: Extract the last 20 bases (3′ end) from each read in a trimmed FASTQ file
  without using a reference genome.

  Input: Trimmed FASTQ file

  Output: FASTA file containing 3′ end sequences

  Note: This is an internal logic operation for extracting sequence tails'
- not a script call
path: .opencode/knowledge/tasks/task-0050-tool-extract-3p-end.md
origin_source: extract_3p_end
origin_page: 51
source_entry_index: 46
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: extract-3p-end
---

# Tool: extract_3p_end

## One-line description

Tool: extract_3p_end Purpose: Extract the last 20 bases (3′ end) from each read in a trimmed FASTQ file without using a reference genome. Input: Trimmed FASTQ file Output: FASTA file containing 3′ end sequences Note:...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `extract_3p_end`
- Origin page: `51`
- Source entry index: `46`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0050`
- Analysis/tool category: `extract-3p-end`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Tool: extract_3p_end
Purpose: Extract the last 20 bases (3′ end) from each read in a trimmed FASTQ file without using a reference genome.
Input: Trimmed FASTQ file
Output: FASTA file containing 3′ end sequences
Note: This is an internal logic operation for extracting sequence tails, not a script call.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
