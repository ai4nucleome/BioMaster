---
id: wf-0002
title: GATK:The GATK is the industry standard for pageentifying SNPs and indels in
  germline DNA and RNAs...
summary: GATK:The GATK is the industry standard for pageentifying SNPs and indels
  in germline DNA and RNAseq data. Its scope is now expanding to include somatic short
  variant calling, and to tackle copy number (CNV) and struct...
keywords:
- rnaseq-de
- tools
- GATK:The GATK is the industry standard for pageentifying SNPs and indels in germline
  DNA and RNAs
- GATK:The GATK is the industry standard for pageentifying SNPs and indels in germline
  DNA and RNAseq data. Its scope is now expanding to include somatic short variant
  calling
- and to tackle copy number (CNV) and structural variation (SV). In addition to the
  variant callers themselves
- the GATK also includes many utilities to perform related tasks such as processing
  and quality control of high-throughput sequencing data
- and bundles the popular Picard toolkit
path: .opencode/knowledge/workflows/wf-0002-gatk-the-gatk-is-the-industry-standard-for-pageentifying-snps-and-indels-in-germline-dna-and-rnas.md
origin_source: tools
origin_page: 9
source_entry_index: 2
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: rnaseq-de
---

# GATK:The GATK is the industry standard for pageentifying SNPs and indels in germline DNA and RNAs...

## One-line description

GATK:The GATK is the industry standard for pageentifying SNPs and indels in germline DNA and RNAseq data. Its scope is now expanding to include somatic short variant calling, and to tackle copy number (CNV) and struct...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `tools`
- Origin page: `9`
- Source entry index: `2`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0002`
- Analysis/tool category: `rnaseq-de`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
GATK:The GATK is the industry standard for pageentifying SNPs and indels in germline DNA and RNAseq data. Its scope is now expanding to include somatic short variant calling, and to tackle copy number (CNV) and structural variation (SV). In addition to the variant callers themselves, the GATK also includes many utilities to perform related tasks such as processing and quality control of high-throughput sequencing data, and bundles the popular Picard toolkit.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
