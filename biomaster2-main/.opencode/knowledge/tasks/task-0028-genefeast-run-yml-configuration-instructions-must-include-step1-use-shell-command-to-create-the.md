---
id: task-0028
title: 'GeneFEAST run.yml Configuration Instructions must include:Step1: Use shell
  command to create the...'
summary: 'GeneFEAST run.yml Configuration Instructions must include:Step1: Use shell
  command to create the run.yml file. Description: You can create the configuration
  file using shell redirection with `cat << ''EOF'' > run.yml`,...'
keywords:
- genefeast-run-yml-config
- GeneFEAST_run.yml_config
- 'GeneFEAST run.yml Configuration Instructions must include:Step1: Use shell command
  to create the'
- 'GeneFEAST run.yml Configuration Instructions must include:Step1: Use shell command
  to create the run.yml file. Description: You can create the configuration file using
  shell redirection with `cat << ''EOF'' > run.yml`'
- followed by the structured YAML content
- 'and then closed with `EOF`. This approach allows easy inline editing in terminal
  or scripts. Step2: Fill in configuration content. Description: The configuration
  consists of FEA result references'
- gene-of-interest (GOI) files
- optional keyword annotations
- and tooltips options. The following fields must be specified
- FEAs
- 'id: "mmc2_3h"'
- 'goi_file: "'
- GeneFEAST
- mmc2_goi_3h.csv"
- 'fea_file: "'
- GO_BP_3h_0.0001_4GF_basic.csv"
- 'id: "mmc2_24h"'
- mmc2_goi_24h.csv"
- GO_BP_24h_0.0001_4GF_basic.csv"
- 'SEARCH_WORDS:

  - Covid 19

  - sars-cov-2'
- EA_FILE
- mmc2_3h_24h_extra_annotations.txt
- 'TOOLTIPS: True'
- Description of Fields
- 'id: A unique identifier for each FEA dataset'
- 'such as "mmc2_3h" or "mmc2_24h".

  - goi_file: Path to the CSV file containing the gene-of-interest list.

  - fea_file: Path to the functional enrichment analysis result CSV file'
path: .opencode/knowledge/tasks/task-0028-genefeast-run-yml-configuration-instructions-must-include-step1-use-shell-command-to-create-the.md
origin_source: GeneFEAST_run.yml_config
origin_page: 29
source_entry_index: 24
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: genefeast-run-yml-config
---

# GeneFEAST run.yml Configuration Instructions must include:Step1: Use shell command to create the...

## One-line description

GeneFEAST run.yml Configuration Instructions must include:Step1: Use shell command to create the run.yml file. Description: You can create the configuration file using shell redirection with `cat << 'EOF' > run.yml`,...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `GeneFEAST_run.yml_config`
- Origin page: `29`
- Source entry index: `24`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0028`
- Analysis/tool category: `genefeast-run-yml-config`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
GeneFEAST run.yml Configuration Instructions must include:Step1: Use shell command to create the run.yml file. Description: You can create the configuration file using shell redirection with `cat << 'EOF' > run.yml`, followed by the structured YAML content, and then closed with `EOF`. This approach allows easy inline editing in terminal or scripts. Step2: Fill in configuration content. Description: The configuration consists of FEA result references, gene-of-interest (GOI) files, optional keyword annotations, and tooltips options. The following fields must be specified: 

FEAs:
    - id: "mmc2_3h"
      goi_file: "./GeneFEAST/mmc2_goi_3h.csv"
      fea_file: "./GeneFEAST/GO_BP_3h_0.0001_4GF_basic.csv"

    - id: "mmc2_24h"
      goi_file: "./GeneFEAST/mmc2_goi_24h.csv"
      fea_file: "./GeneFEAST/GO_BP_24h_0.0001_4GF_basic.csv"

SEARCH_WORDS:
- Covid 19
- sars-cov-2

EA_FILE: ./GeneFEAST/mmc2_3h_24h_extra_annotations.txt

TOOLTIPS: True

Description of Fields: 
- id: A unique identifier for each FEA dataset, such as "mmc2_3h" or "mmc2_24h".
- goi_file: Path to the CSV file containing the gene-of-interest list.
- fea_file: Path to the functional enrichment analysis result CSV file.
- SEARCH_WORDS: List of keywords used to highlight or search annotations (e.g., disease-related terms).
- EA_FILE: Path to an additional annotations file linking gene-level metadata across datasets.
- TOOLTIPS: Boolean to enable or disable additional visual tooltips in the final report.

Tools Used: Bash command line with heredoc syntax, manual editing of YAML fields.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
