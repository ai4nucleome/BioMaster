---
id: task-0045
title: If miRBase_mature.fasta is available, convert it to SAF format using the provided
  script. Command...
summary: 'If miRBase_mature.fasta is available, convert it to SAF format using the
  provided script. Command: `python ./scripts/convert_fasta_to_saf.py -i ./data/miRBase_mature.fasta
  -o ./data/miRBase_mature.saf`. Alternatively,...'
keywords:
- featurecounts
- task
- If miRBase_mature.fasta is available
- convert it to SAF format using the provided script. Command
- 'convert it to SAF format using the provided script. Command: `python'
- scripts
- convert_fasta_to_saf.py -i
- data
- miRBase_mature.fasta -o
- miRBase_mature.saf`. Alternatively
- 'the user may prepare SAF manually before running featureCounts. Required SAF fields
  are: GeneID'
- Chr
- Start
- End
- Strand
- featureCounts
path: .opencode/knowledge/tasks/task-0045-if-mirbase-mature-fasta-is-available-convert-it-to-saf-format-using-the-provided-script-command.md
origin_source: task
origin_page: 46
source_entry_index: 41
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: featurecounts
---

# If miRBase_mature.fasta is available, convert it to SAF format using the provided script. Command...

## One-line description

If miRBase_mature.fasta is available, convert it to SAF format using the provided script. Command: `python ./scripts/convert_fasta_to_saf.py -i ./data/miRBase_mature.fasta -o ./data/miRBase_mature.saf`. Alternatively,...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `task`
- Origin page: `46`
- Source entry index: `41`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0045`
- Analysis/tool category: `featurecounts`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
If miRBase_mature.fasta is available, convert it to SAF format using the provided script. Command: `python ./scripts/convert_fasta_to_saf.py -i ./data/miRBase_mature.fasta -o ./data/miRBase_mature.saf`. Alternatively, the user may prepare SAF manually before running featureCounts. Required SAF fields are: GeneID, Chr, Start, End, Strand.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
