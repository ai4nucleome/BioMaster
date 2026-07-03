---
id: task-0029
title: 'MAFin Usage Instructions must include:Step1: Navigate to Output Directory.
  Description: Before ex...'
summary: 'MAFin Usage Instructions must include:Step1: Navigate to Output Directory.
  Description: Before executing the MAFin command, change the working directory to
  the expected output path using `cd`. MAFin will write output...'
keywords:
- mafin-execution
- MAFin_execution
- 'MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description:
  Before ex'
- 'MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description:
  Before executing the MAFin command'
- change the working directory to the expected output path using `cd`. MAFin will
  write output files to the current working directory. If your MAF input file is specified
  using a relative path (e.g
- '`'
- data
- xxx`)
- adjust it relative to your new working directory
- such as `
- 'xxx`. Step2: Run MAFin command. Description: Execute the MAFin tool with the desired
  parameters. The command-line must specify exactly one search type (`--regexes`'
- '`--kmers`'
- or `--jaspar_file`). Additional options include strand orientation
- number of processes
- and report format. Example Command
- '```bash

  MAFin'
- sample.maf \
- regexes "CTGCCCGCA" "AGT" \
- search_in reference \
- reverse_complement no \
- processes 4 \
- 'detailed_report

  ```'
- 'Expected Output: All result files will be written to the current directory'
- 'including:

  - `regex_search_motif_hits.bed`

  - `ref_genome_regex_search_AGT_motif_hits.json`

  - `ref_genome_regex_search_AGT_motif_hits.csv` (if `--detailed_report` is used)'
- 'Command-Line Arguments:

  - `maf_file` (Required): Path'
- MAFin
path: .opencode/knowledge/tasks/task-0029-mafin-usage-instructions-must-include-step1-navigate-to-output-directory-description-before-ex.md
origin_source: MAFin_execution
origin_page: 30
source_entry_index: 25
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: mafin-execution
---

# MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description: Before ex...

## One-line description

MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description: Before executing the MAFin command, change the working directory to the expected output path using `cd`. MAFin will write output...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `MAFin_execution`
- Origin page: `30`
- Source entry index: `25`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0029`
- Analysis/tool category: `mafin-execution`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
MAFin Usage Instructions must include:Step1: Navigate to Output Directory. Description: Before executing the MAFin command, change the working directory to the expected output path using `cd`. MAFin will write output files to the current working directory. If your MAF input file is specified using a relative path (e.g., `./data/xxx`), adjust it relative to your new working directory, such as `../../data/xxx`. Step2: Run MAFin command. Description: Execute the MAFin tool with the desired parameters. The command-line must specify exactly one search type (`--regexes`, `--kmers`, or `--jaspar_file`). Additional options include strand orientation, number of processes, and report format. Example Command: 

~~~bash
MAFin ../../data/sample.maf \
      --regexes "CTGCCCGCA" "AGT" \
      --search_in reference \
      --reverse_complement no \
      --processes 4 \
      --detailed_report
~~~

Expected Output: All result files will be written to the current directory, including:
- `regex_search_motif_hits.bed`
- `ref_genome_regex_search_AGT_motif_hits.json`
- `ref_genome_regex_search_AGT_motif_hits.csv` (if `--detailed_report` is used).

Command-Line Arguments:
- `maf_file` (Required): Path to the uncompressed MAF file.
- `--genome_ids`: Path to a genome IDs file (optional).
- `--search_in`: Genome to search motifs in ('reference' [default] or 'all').
- `--reverse_complement`: Search both strands if 'yes'. Choices: 'yes' or 'no' (default: 'no').
- `--pvalue_threshold`: P-value threshold for PWM matches (default: 1e-4).
- `--processes`: Number of parallel processes (default: 1).
- `--background_frequencies`: Four space-separated floats summing to 1 (e.g., 0.25 0.25 0.25 0.25).
- `--purge_results_dir`: Purge the 'tmp' directory before execution.
- `--verbose, -v`: Enable verbose logging to `debug.log`.
- `--detailed_report, -d`: Generate merged JSON and CSV analytical output.

Search Type Flags (Mutually Exclusive):
- `--regexes`: Provide one or more regex motifs as arguments.
- `--kmers`: Path to a text file containing K-mers (one per line).
- `--jaspar_file`: Path to a JASPAR-formatted PWM file.

Tools Used: MAFin command-line interface, with support for regular expression, k-mer, and PWM motif scanning, parallel computing, and flexible output formats.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
