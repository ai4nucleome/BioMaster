---
id: task-0044
title: 'Step 3: miRNA Quantification'
summary: 'Step 3: miRNA Quantification Description: Quantify miRNA expression using
  featureCounts and SAF-format annotation derived from known miRNA sequences. Input
  Required: Aligned BAM files, miRNA annotation in SAF format....'
keywords:
- featurecounts
- workflow
- 'Step 3: miRNA Quantification'
- 'Step 3: miRNA Quantification

  Description: Quantify miRNA expression using featureCounts and SAF-format annotation
  derived from known miRNA sequences.

  Input Required: Aligned BAM files'
- 'miRNA annotation in SAF format.

  Expected Output: Expression matrix (miRNA counts).

  Tools Used: featureCounts.

  Commands'
- '```bash'
- '# Convert FASTA to SAF'
- python
- scripts
- convert_fasta_to_saf.py -i
- data
- miRBase_mature.fasta -o
- miRBase_mature.saf
- '# Run featureCounts'
- featureCounts -F SAF -T 4 -a
- miRBase_mature.saf -o
- output
- '010'
- miRNA_expression_matrix.txt
- aligned_C1.bam
- '```

  **Checkpoint:** Check that `miRNA_expression_matrix.txt` has non-zero counts'
- featureCounts
path: .opencode/knowledge/tasks/task-0044-step-3-mirna-quantification.md
origin_source: workflow
origin_page: 45
source_entry_index: 40
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: featurecounts
---

# Step 3: miRNA Quantification

## One-line description

Step 3: miRNA Quantification Description: Quantify miRNA expression using featureCounts and SAF-format annotation derived from known miRNA sequences. Input Required: Aligned BAM files, miRNA annotation in SAF format....

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `workflow`
- Origin page: `45`
- Source entry index: `40`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0044`
- Analysis/tool category: `featurecounts`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Step 3: miRNA Quantification
Description: Quantify miRNA expression using featureCounts and SAF-format annotation derived from known miRNA sequences.
Input Required: Aligned BAM files, miRNA annotation in SAF format.
Expected Output: Expression matrix (miRNA counts).
Tools Used: featureCounts.
Commands:
  ~~~bash
  # Convert FASTA to SAF
  python ./scripts/convert_fasta_to_saf.py -i ./data/miRBase_mature.fasta -o ./data/miRBase_mature.saf
  
  # Run featureCounts
  featureCounts -F SAF -T 4 -a ./data/miRBase_mature.saf -o ./output/010/miRNA_expression_matrix.txt ./output/010/aligned_C1.bam
  ~~~
**Checkpoint:** Check that `miRNA_expression_matrix.txt` has non-zero counts.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
