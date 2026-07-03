---
id: wf-0021
title: 'MAFin Usage Instructions must include:Step1: Navigate to Output Directory.
  Description: Before ru...'
summary: 'MAFin Usage Instructions must include:Step1: Navigate to Output Directory.
  Description: Before running MAFin, use `cd` to enter the target directory where
  output files are expected to be saved. This directory should b...'
keywords:
- motif-analysis
- MAFin_usage
- 'MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description:
  Before ru'
- 'MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description:
  Before running MAFin'
- 'use `cd` to enter the target directory where output files are expected to be saved.
  This directory should be empty or cleaned as necessary. Step2: Adjust Input Path
  If Needed. Description: If the input MAF file is referenced with a relative path
  (e.g'
- '`'
- data
- file.maf`)
- ensure to update it according to the current working directory (e.g
- 'file.maf`) to guarantee correct file access. Step3: Run MAFin Command. Description:
  Use the `MAFin` command-line interface with specified arguments. You must choose
  exactly one motif search type: `--regexes`'
- '`--kmers`'
- or `--jaspar_file`. Other options include target genome
- strand orientation
- parallel processing
- and reporting format
- 'Example Command (Regex):

  MAFin path'
- to
- file.maf \
- regexes "CTGCCCGCA" "AGT" \
- search_in reference \
- reverse_complement no \
- processes 4 \
- detailed_report
- 'Command-Line Arguments:

  - maf_file: (Required) Path to the uncompressed MAF file.

  - --genome_ids: Path to the genome IDs file (optional).

  - --search_in: Genome to search motifs in. Options: ''reference'' (defaul'
- MAFin
path: .opencode/knowledge/workflows/wf-0021-mafin-usage-instructions-must-include-step1-navigate-to-output-directory-description-before-ru.md
origin_source: MAFin_usage
origin_page: 23
source_entry_index: 13
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: motif-analysis
---

# MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description: Before ru...

## One-line description

MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description: Before running MAFin, use `cd` to enter the target directory where output files are expected to be saved. This directory should b...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `MAFin_usage`
- Origin page: `23`
- Source entry index: `13`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0021`
- Analysis/tool category: `motif-analysis`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description: Before running MAFin, use `cd` to enter the target directory where output files are expected to be saved. This directory should be empty or cleaned as necessary. Step2: Adjust Input Path If Needed. Description: If the input MAF file is referenced with a relative path (e.g., `./data/file.maf`), ensure to update it according to the current working directory (e.g., `../../data/file.maf`) to guarantee correct file access. Step3: Run MAFin Command. Description: Use the `MAFin` command-line interface with specified arguments. You must choose exactly one motif search type: `--regexes`, `--kmers`, or `--jaspar_file`. Other options include target genome, strand orientation, parallel processing, and reporting format.

Example Command (Regex):
MAFin path/to/file.maf \
    --regexes "CTGCCCGCA" "AGT" \
    --search_in reference \
    --reverse_complement no \
    --processes 4 \
    --detailed_report

Command-Line Arguments:
- maf_file: (Required) Path to the uncompressed MAF file.
- --genome_ids: Path to the genome IDs file (optional).
- --search_in: Genome to search motifs in. Options: 'reference' (default) or 'all'.
- --reverse_complement: Search both strands if 'yes'. Default is 'no'.
- --pvalue_threshold: P-value threshold for PWM matches. Default: 1e-4.
- --processes: Number of parallel processes. Default: 1.
- --background_frequencies: Four space-separated floats for A, C, G, T frequencies. Must sum to 1.
- --purge_results_dir: Remove temporary result directories before running.
- --verbose, -v: Enable detailed logging to `debug.log`.
- --detailed_report, -d: Generate additional CSV and JSON reports.

Search Types (choose one only):
- --regexes: Provide inline regex patterns (e.g., "AGT", "CTG[CC]+CGCA").
- --kmers: Path to file with K-mers, one per line.
- --jaspar_file: Path to a motif file in JASPAR PWM format.

Additional Examples:
• Regex search across all genomes and both strands:
MAFin path/to/file.maf \
    --regexes "CTG[CC]+CGCA" "AGT" \
    --search_in all \
    --verbose \
    --reverse_complement yes \
    --processes 8 \
    --purge_results_dir

• K-mer search:
MAFin path/to/file.maf \
    --kmers data/kmers.txt \
    --search_in reference \
    --processes 2 \
    --detailed_report

• PWM motif search:
MAFin path/to/file.maf \
    --jaspar_file data/motif.jaspar \
    --search_in all \
    --pvalue_threshold 1e-5 \
    --background_frequencies 0.25 0.15 0.35 0.25 \
    --processes 4
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
