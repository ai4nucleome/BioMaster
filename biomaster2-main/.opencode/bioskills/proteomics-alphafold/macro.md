# Proteomics Alphafold

## Overview

This workflow validates protein designs using AlphaFold2 structure prediction. It covers selecting the appropriate prediction backend (AlphaFold2/ColabFold for complexes and highest accuracy, ESMFold for fast single-chain screening), running structure prediction on designed sequences or multi-chain complexes, extracting confidence metrics (pLDDT, pTM, ipTM, PAE) from result files, assessing output quality against established thresholds, and troubleshooting common runtime errors.

**Inputs:** FASTA files of designed sequences (monomer) or multi-chain complexes (multimer).

**Outputs:** Ranked PDB structure files (ranked_0.pdb is best), a ranking_debug.json with confidence scores, per-model result pickles (result_model_*.pkl) containing full metrics, MSA files, and input feature pickles.

**When to use:** Validating that designed sequences fold correctly, predicting binder-target complex structures, calculating confidence metrics, self-consistency validation of designs, and multi-chain complex prediction with AlphaFold-Multimer. For faster single-chain prediction, use the esm skill instead. For QC filtering and ranking of designs, follow this workflow with the protein-qc skill.

**Prerequisites:** Python 3.8+ (3.10 recommended), CUDA 11.0+ (12.0+ recommended), GPU with 32GB+ VRAM (40GB A100 recommended), 32GB+ RAM (64GB recommended), 100GB+ disk (500GB recommended for full databases).

## Backend Selection

Choose the right prediction backend based on the prediction target and accuracy/speed needs. For single proteins or fast screening, ESMFold is preferred (MSA-free, fast). For protein-protein complexes, highest accuracy, or batch prediction, AlphaFold2 or ColabFold is recommended. For protein-ligand prediction, Chai or Boltz should be used instead. Within AlphaFold2 options, local installation gives full control but slow setup, ColabFold is easier with an MSA server, and Modal is recommended for batch campaigns. This step also confirms that hardware and software prerequisites (Python, CUDA, GPU VRAM, RAM, disk) are met before proceeding.

## Structure Prediction

Run the structure prediction using the selected backend. ColabFold (via Modal) is the recommended option for multimer and batch prediction, running on an A100 (40GB) with a 3600s default timeout. Local AlphaFold2 installation provides full control via run_alphafold.py with configurable model preset (monomer or multimer), recycling iterations, template search, and template date cutoff. ESMFold (via Modal) provides fast single-chain prediction from a raw sequence string. Key parameters include model_preset (monomer/multimer), num_recycle (1-20, default 3), max_template_date (YYYY-MM-DD cutoff), and use_templates (True/False).

## Confidence Metric Extraction

Extract confidence metrics from the per-model result pickle files produced by AlphaFold2. The result_model_*.pkl files contain pLDDT (per-residue and mean local confidence on a 0-100 scale), pTM (predicted TM-score for global structure confidence), ipTM (interface pTM, multimer only, measures interface confidence), and PAE (predicted aligned error matrix). These metrics are the primary indicators of prediction quality and are used downstream for filtering and ranking designs.

## Quality Assessment & Verification

Assess prediction quality against established confidence thresholds and verify that all expected outputs were produced. Good-quality predictions should have mean pLDDT above 85 (or 0.85 normalized), pTM above 0.70, ipTM above 0.50 for complexes, and interface PAE below 10. Low pLDDT regions may indicate disorder or poor design; low ipTM suggests the interface is not confident and hotspots should be checked; high off-diagonal PAE indicates chains may not interact. Verification confirms the number of ranked_0.pdb files matches the input sequence count. Typical performance on an A100 is ~30-60s per complex with the MSA server.

## Troubleshooting

Diagnose and resolve common runtime errors encountered during AlphaFold2 prediction. The most frequent issues are CUDA out-of-memory errors (caused by sequences that are too long, fixed by using an A100 or splitting the prediction), missing iptm keys (caused by running the monomer preset on a complex, fixed by switching to the multimer preset), missing MSA databases (fixed by using the ColabFold MSA server), and timeout errors during slow MSA searches (fixed by reducing num_recycles). For OOM errors specifically, switching to ColabFold with the MSA server is recommended over local installation.
