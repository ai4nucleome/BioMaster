---
id: wf-0044
title: 'Protein Expression Quantitative Analysis Workflow must include: Step 1: Data
  Preparation and Load...'
summary: 'Protein Expression Quantitative Analysis Workflow must include: Step 1:
  Data Preparation and Loading. Description: Read an Excel file containing protein
  quantification data and conduct an initial check on its structur...'
keywords:
- rnaseq-de
- workflow
- 'Protein Expression Quantitative Analysis Workflow must include: Step 1: Data Preparation
  and Load'
- 'Protein Expression Quantitative Analysis Workflow must include: Step 1: Data Preparation
  and Loading. Description: Read an Excel file containing protein quantification data
  and conduct an initial check on its structure'
- including column names
- distribution of missing values
- 'and content of the initial rows. Input Required: An Excel file (e.g'
- 'ms220042-dia-20220111.xls) containing columns such as PG.ProteinGroups and PG.Quantity.
  Expected Output: A preliminarily loaded DataFrame with columns for raw protein IDs'
- quantitative values
- etc
- 'and a console output preview of the data structure (df.head()). Tools Used: Pandas
  for data reading (pd.read_excel) and preliminary inspection. Step 2: Data Cleaning.
  Description: Rename complex column names to more readable ones'
- handle missing values by deleting rows with missing protein IDs
- 'and split rows containing multiple protein IDs into separate rows. Input Required:
  The preliminarily loaded DataFrame that may contain complex column names or missing
  values. Expected Output: A cleaned DataFrame with standardized column names and
  complete data without missing IDs. Tools Used: Pandas for column renaming (rename)'
- deleting rows with missing v
path: .opencode/knowledge/workflows/wf-0044-protein-expression-quantitative-analysis-workflow-must-include-step-1-data-preparation-and-load.md
origin_source: workflow
origin_page: 46
source_entry_index: 36
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: rnaseq-de
---

# Protein Expression Quantitative Analysis Workflow must include: Step 1: Data Preparation and Load...

## One-line description

Protein Expression Quantitative Analysis Workflow must include: Step 1: Data Preparation and Loading. Description: Read an Excel file containing protein quantification data and conduct an initial check on its structur...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `46`
- Source entry index: `36`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0044`
- Analysis/tool category: `rnaseq-de`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Protein Expression Quantitative Analysis Workflow must include: Step 1: Data Preparation and Loading. Description: Read an Excel file containing protein quantification data and conduct an initial check on its structure, including column names, distribution of missing values, and content of the initial rows. Input Required: An Excel file (e.g., ms220042-dia-20220111.xls) containing columns such as PG.ProteinGroups and PG.Quantity. Expected Output: A preliminarily loaded DataFrame with columns for raw protein IDs, quantitative values, etc., and a console output preview of the data structure (df.head()). Tools Used: Pandas for data reading (pd.read_excel) and preliminary inspection. Step 2: Data Cleaning. Description: Rename complex column names to more readable ones, handle missing values by deleting rows with missing protein IDs, and split rows containing multiple protein IDs into separate rows. Input Required: The preliminarily loaded DataFrame that may contain complex column names or missing values. Expected Output: A cleaned DataFrame with standardized column names and complete data without missing IDs. Tools Used: Pandas for column renaming (rename), deleting rows with missing values (dropna), and splitting multiple IDs (str.split + explode). Step 3: Data Preprocessing. Description: Perform log2(x + 1) transformation on quantitative values to address the skewed distribution of data and use quantile normalization to eliminate technical biases and make data distributions consistent across different samples. Input Required: The cleaned DataFrame with original quantitative values. Expected Output: A preprocessed DataFrame containing a quantitative matrix after log2 transformation and normalization. Tools Used: NumPy for numerical calculation (np.log2) and scikit-learn for quantile normalization (QuantileTransformer). Step 4: Differential Expression Analysis. Description: Conduct a t - test to calculate the significance difference (p - value) between the experimental group (Group2) and the control group (Group1) for each protein, use the Benjamini - Hochberg method for multiple test correction to generate adjusted p - values (adj_p_value), and calculate the log2(mean of experimental group / mean of control group) to obtain the fold change. Input Required: The preprocessed quantitative matrix with grouped data. Expected Output: A differential analysis results table with columns for log2FC, p_value, and adj_p_value, and a list of significantly differentially expressed proteins (filtered by adj_p_value < 0.05 and |log2FC| > 1). Tools Used: SciPy for the t - test (ttest_ind), statsmodels for multiple test correction (multipletests), and NumPy/Pandas for fold change calculation (mean + log2).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
