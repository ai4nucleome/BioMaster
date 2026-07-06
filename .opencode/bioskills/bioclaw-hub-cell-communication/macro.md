# Bioclaw Hub Cell Communication

## Overview

Workflow for ligand-receptor (L-R) communication inference in single-cell or spatial transcriptomics data. The pipeline takes an annotated single-cell or spatial object (e.g., AnnData with validated cell type labels), a ligand-receptor resource, and optional condition or group metadata. It produces interaction tables, sender-receiver summaries, and communication visualizations. Use this workflow when cell type annotations or spatial domains are robust and the goal is to infer potential intercellular signaling. All results are hypothesis-generating and must be interpreted with appropriate caveats unless validated experimentally.

## Validate Annotations

Confirm that cell type labels or spatial domain annotations are robust before any communication inference. Communication analysis is highly sensitive to annotation quality — unstable or weak labels produce misleading interaction results. Check cluster stability, marker gene coherence, and ensure metadata joins correctly.

## Load Ligand-Receptor Resource

Load and prepare the ligand-receptor interaction database. Choose a resource appropriate for the organism (human, mouse) and context. Common resources include CellChatDB, OmniPath, or CellPhoneDB. Filter to keep only interactions where both ligand and receptor are expressed in the dataset.

## Run Interaction Scoring

Compute ligand-receptor interaction scores between all pairs of cell types or spatial neighborhoods. Use a permutation-based or product-based method (e.g., LIANA's aggregate method, CellPhoneDB-style mean expression, or CellChat's communication probability). Apply filtering for expression support and redundancy to reduce false positives.

## Aggregate and Summarize

Summarize interaction signals by sender cell type, receiver cell type, pathway, or condition. Produce sender-receiver summary tables showing the number and strength of outgoing and incoming signals per cell type. Optionally compare across conditions (e.g., healthy vs. disease) to identify differential communication.

## Visualize and Report Caveats

Generate communication visualizations including heatmaps, chord diagrams, and network plots. Always accompany visual results with a clear statement that inferred communication is hypothesis-generating unless validated experimentally. Save outputs to organized directories.
