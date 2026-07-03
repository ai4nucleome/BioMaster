---
id: wf-0043
title: 'Protein Mass Spectrometry Analysis Workflow must include: Step 1: Read .mzML
  File. Description: P...'
summary: 'Protein Mass Spectrometry Analysis Workflow must include: Step 1: Read .mzML
  File. Description: Parse raw mass spectrometry data to extract MS1 spectrum information,
  including retention time, m/z values, and intensiti...'
keywords:
- workflow
- 'Protein Mass Spectrometry Analysis Workflow must include: Step 1: Read .mzML File.
  Description: P'
- 'Protein Mass Spectrometry Analysis Workflow must include: Step 1: Read .mzML File.
  Description: Parse raw mass spectrometry data to extract MS1 spectrum information'
- including retention time
- m
- z values
- 'and intensities. Input Required: Raw mass spectrometry file (sample.mzML). Expected
  Output: A list of Python dictionaries'
- each containing retention time (rt)
- z values (mz)
- 'and intensity values (intensity). Tools Used: pymzml for parsing .mzML files. Step
  2: Noise Filtering and Baseline Correction. Description: Remove noise peaks with
  low signal-to-noise ratio (SNR) through smoothing and baseline thresholding. Input
  Required: Processed dictionary list from Step 1. Expected Output: Updated dictionary
  list with only valid peaks (intensity > baseline threshold). Tools Used: scipy.signal
  for filtering. Step 3: Load Protein Database. Description: Read a FASTA file to
  generate a dictionary of protein sequences. Input Required: Protein database file
  (uniprot_human.fasta). Expected Output: Python dictionary {ProteinID: amino_acid_sequence}.
  Tools Used: pyteomics.fasta for FASTA file parsing. Step 4: Enzymatic Digestion
  to Generate Theoretical Peptides. Description: Simulate trypsin dig'
path: .opencode/knowledge/workflows/wf-0043-protein-mass-spectrometry-analysis-workflow-must-include-step-1-read-mzml-file-description-p.md
origin_source: workflow
origin_page: 45
source_entry_index: 35
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: workflow
---

# Protein Mass Spectrometry Analysis Workflow must include: Step 1: Read .mzML File. Description: P...

## One-line description

Protein Mass Spectrometry Analysis Workflow must include: Step 1: Read .mzML File. Description: Parse raw mass spectrometry data to extract MS1 spectrum information, including retention time, m/z values, and intensiti...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `45`
- Source entry index: `35`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0043`
- Analysis/tool category: `workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Protein Mass Spectrometry Analysis Workflow must include: Step 1: Read .mzML File. Description: Parse raw mass spectrometry data to extract MS1 spectrum information, including retention time, m/z values, and intensities. Input Required: Raw mass spectrometry file (sample.mzML). Expected Output: A list of Python dictionaries, each containing retention time (rt), m/z values (mz), and intensity values (intensity). Tools Used: pymzml for parsing .mzML files. Step 2: Noise Filtering and Baseline Correction. Description: Remove noise peaks with low signal-to-noise ratio (SNR) through smoothing and baseline thresholding. Input Required: Processed dictionary list from Step 1. Expected Output: Updated dictionary list with only valid peaks (intensity > baseline threshold). Tools Used: scipy.signal for filtering. Step 3: Load Protein Database. Description: Read a FASTA file to generate a dictionary of protein sequences. Input Required: Protein database file (uniprot_human.fasta). Expected Output: Python dictionary {ProteinID: amino_acid_sequence}. Tools Used: pyteomics.fasta for FASTA file parsing. Step 4: Enzymatic Digestion to Generate Theoretical Peptides. Description: Simulate trypsin digestion to generate theoretical peptides from protein sequences. Input Required: Protein sequence dictionary from Step 3. Expected Output: List of theoretical peptides. Tools Used: pyteomics.parser.cleave for enzymatic digestion. Step 5: Generate Theoretical Spectra. Description: Calculate fragment ion m/z values (b and y ions) for each theoretical peptide. Input Required: List of theoretical peptides. Expected Output: Dictionary mapping peptides to their fragment ion m/z values. Tools Used: pyteomics.mass.calculate_masses for mass spectrometry calculations. Step 6: Experimental Spectrum Matching. Description: Match experimental spectra to theoretical spectra to identify peptide sequences. Input Required: Preprocessed spectra from Step 2 and theoretical spectra from Step 5. Expected Output: CSV file (peptide_matches.csv) with spectrum IDs, peptides, and matching scores. Tools Used: numpy for array calculations. Step 7: Peptide-Protein Mapping. Description: Associate identified peptides with proteins and filter low-confidence proteins. Input Required: peptide_matches.csv and protein sequence dictionary from Step 3. Expected Output: CSV file (protein_list.csv) listing proteins and their supporting peptide counts. Tools Used: pandas for data aggregation. Step 8: Protein Quantification. Description: Calculate protein abundance using the top three highest-intensity peptides. Input Required: peptide_matches.csv and preprocessed spectra from Step 2. Expected Output: CSV file (protein_quant.csv) with protein abundances. Tools Used: pandas for data aggregation.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
