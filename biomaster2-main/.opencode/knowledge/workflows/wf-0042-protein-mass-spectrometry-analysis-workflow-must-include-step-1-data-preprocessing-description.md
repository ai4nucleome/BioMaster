---
id: wf-0042
title: 'Protein Mass Spectrometry Analysis Workflow must include:Step 1: Data Preprocessing.
  Description:...'
summary: 'Protein Mass Spectrometry Analysis Workflow must include:Step 1: Data Preprocessing.
  Description: Perform denoising, peak alignment, normalization, and quality control
  (QC) on raw mzML files. Input Required: Raw mass...'
keywords:
- functional-enrichment
- workflow
- 'Protein Mass Spectrometry Analysis Workflow must include:Step 1: Data Preprocessing.
  Description'
- 'Protein Mass Spectrometry Analysis Workflow must include:Step 1: Data Preprocessing.
  Description: Perform denoising'
- peak alignment
- normalization
- 'and quality control (QC) on raw mzML files. Input Required: Raw mass spectrometry
  file (input.mzML). Expected Output: Preprocessed mass spectrometry file (processed.mzML)'
- Quality control report (QC_report.pdf
- 'including peak intensity distribution and missing value ratio). Tools Used: pyOpenMS
  (for peak detection and alignment)'
- 'pandas (for data cleaning). Step 2: Peptide Identification & Quantification. Description:
  Identify peptides from preprocessed mzML files and perform quantification (e.g'
- 'Label-free or TMT labeling). Input Required: Preprocessed mass spectrometry file
  (processed.mzML)'
- Protein sequence database (e.g
- 'human.fasta). Expected Output: Peptide list file (peptides.tsv'
- 'containing peptide sequences and quantitative values). Tools Used: MSFragger (for
  database searching)'
- 'pyteomics (for result parsing). Step 3: Protein Identification. Description: Infer
  proteins from peptides and control false discovery rate (FDR < 1%). Input Required:
  Peptide list file (peptides.tsv). Expected Output: Identified protein list (protein'
path: .opencode/knowledge/workflows/wf-0042-protein-mass-spectrometry-analysis-workflow-must-include-step-1-data-preprocessing-description.md
origin_source: workflow
origin_page: 44
source_entry_index: 34
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: functional-enrichment
---

# Protein Mass Spectrometry Analysis Workflow must include:Step 1: Data Preprocessing. Description:...

## One-line description

Protein Mass Spectrometry Analysis Workflow must include:Step 1: Data Preprocessing. Description: Perform denoising, peak alignment, normalization, and quality control (QC) on raw mzML files. Input Required: Raw mass...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `44`
- Source entry index: `34`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0042`
- Analysis/tool category: `functional-enrichment`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Protein Mass Spectrometry Analysis Workflow must include:Step 1: Data Preprocessing. Description: Perform denoising, peak alignment, normalization, and quality control (QC) on raw mzML files. Input Required: Raw mass spectrometry file (input.mzML). Expected Output: Preprocessed mass spectrometry file (processed.mzML), Quality control report (QC_report.pdf, including peak intensity distribution and missing value ratio). Tools Used: pyOpenMS (for peak detection and alignment), pandas (for data cleaning). Step 2: Peptide Identification & Quantification. Description: Identify peptides from preprocessed mzML files and perform quantification (e.g., Label-free or TMT labeling). Input Required: Preprocessed mass spectrometry file (processed.mzML), Protein sequence database (e.g., human.fasta). Expected Output: Peptide list file (peptides.tsv, containing peptide sequences and quantitative values). Tools Used: MSFragger (for database searching), pyteomics (for result parsing). Step 3: Protein Identification. Description: Infer proteins from peptides and control false discovery rate (FDR < 1%). Input Required: Peptide list file (peptides.tsv). Expected Output: Identified protein list (protein_ids.csv, with unique protein IDs). Tools Used: Percolator (for FDR validation), pyteomics (for data parsing). Step 4: Protein Quantification. Description: Calculate protein abundances based on peptide-level quantitative results (e.g., Top3 method or intensity summation). Input Required: Identified protein list (protein_ids.csv), Peptide quantification file (peptides.tsv). Expected Output: Protein abundance matrix (protein_quant.csv, rows = proteins, columns = samples). Tools Used: pandas (for data integration), numpy (for abundance calculation). Step 5: Differential Analysis. Description: Identify differentially expressed proteins using statistical tests and correct for multiple hypothesis testing. Input Required: Protein abundance matrix (protein_quant.csv), Sample group information (group_info.csv). Expected Output: List of differentially expressed proteins (diff_proteins.csv, containing log2FC and FDR-corrected p-values). Tools Used: scipy.stats.ttest_ind (for t-tests), statsmodels.stats.multitest (for FDR correction). Step 6: Functional Annotation. Description: Map differentially expressed proteins to Gene Ontology (GO) terms and KEGG pathways. Input Required: List of differentially expressed proteins (diff_proteins.csv), Functional annotation databases (e.g., GO.csv, KEGG_terms.csv). Expected Output: Annotated protein table (annotated_proteins.csv). Tools Used: gseapy (for functional mapping), pandas (for data merging). Step 7: Pathway Enrichment Analysis. Description: Perform pathway enrichment analysis on annotated proteins using hypergeometric or Fisher's exact tests. Input Required: Annotated protein table (annotated_proteins.csv), Pathway database (e.g., KEGG_pathways.gmt). Expected Output: Pathway enrichment results table (pathway_enrichment.csv, including p-values and enriched gene counts). Tools Used: gseapy.enrichr (for enrichment analysis), statsmodels (for statistical testing). Step 8: Protein-Protein Interaction (PPI) Network Analysis. Description: Construct PPI networks for differentially expressed proteins and identify hub proteins. Input Required: List of differentially expressed proteins (diff_proteins.csv), PPI database (e.g., STRING_interactions.tsv). Expected Output: PPI network file (PPI_network.graphml), List of hub proteins (hub_proteins.csv). Tools Used: NetworkX (for network analysis), Cytoscape (for visualization).
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
