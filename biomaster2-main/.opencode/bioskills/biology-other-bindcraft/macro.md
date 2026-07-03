# Biology Other Bindcraft

## Overview

BindCraft is an end-to-end protein binder design pipeline that uses AlphaFold2-based hallucination to jointly optimize binder backbone and sequence, with built-in AF2 validation of each candidate. Given a target protein structure (PDB), target chain(s), hotspot residues, and a binder length range, it generates a specified number of candidate binders and reports per-design quality metrics (pLDDT, pTM, ipTM, PAE, RMSD, sequence).

Use this skill for production-quality binder design campaigns where experimental success rate is the priority. For backbone-only generation use rfdiffusion; for QC threshold guidance use protein-qc; for tool-selection guidance use binder-design.

Inputs: target PDB, target chain(s), hotspot residues, binder length range, number of designs, protocol (fast/default/slow). Outputs: per-design directory containing binder.pdb, complex.pdb, metrics.json, and an optimization trajectory; plus a campaign-level summary.csv aggregating all metrics.

The pipeline runs on Modal (recommended, L40S 48GB GPU, no local hardware needed) or locally (requires 32GB+ VRAM, 48GB L40S/A100 recommended). Expected pass rate is 30-70% with ipTM > 0.5, target-dependent. Typical campaign: 50 designs in 2-4h (~$15 on Modal).

## Environment Setup

Verify hardware and software prerequisites and install BindCraft. Requirements: Python 3.9+ (3.10 recommended), CUDA 11.7+ (12.0+ recommended), 32GB+ GPU VRAM (48GB L40S recommended), 32GB+ RAM (64GB recommended). Two installation paths are supported: Modal (recommended for most users, no local GPU required) or a local clone of the BindCraft repository with its Python dependencies. First-time Modal users must complete the Modal/biomodals installation guide before running.

## Input Preparation & Protocol Selection

Prepare the target structure and choose design parameters. Required inputs: a target PDB file, target chain identifier(s), hotspot residues on the target (e.g. A45,A67,A89), and a binder length range (default 70-100, range 40-150). Set the number of designs based on campaign size and budget (default 50, range 1-500). Select the design protocol based on use case: fast for initial screening (lower quality, higher speed), default for standard campaigns, slow for final production-quality designs. Hotspot residue numbering must match the target PDB or a 'no hotspots' error will occur.

## Campaign Execution

Run the binder design campaign. On Modal, invoke modal_bindcraft.py with the prepared parameters (L40S 48GB GPU, 3600s default timeout). Locally, run bindcraft.py directly. The pipeline jointly optimizes binder backbone and sequence via AF2-based hallucination and validates each design with built-in AF2 prediction. Progress is logged per design, reporting length, pLDDT, and ipTM as each design completes.

## Output & Metrics QC

Interpret the per-design and campaign-level output. Each design directory contains binder.pdb (final design), complex.pdb (binder + target), metrics.json (QC scores), and a trajectory/ folder (optimization trajectory). A campaign-level summary.csv aggregates all metrics. Key quality indicators: pLDDT > 0.85 indicates a well-folded design, ipTM > 0.5 indicates a passing design. Expected pass rate is 30-70% with ipTM > 0.5 depending on the target. Rank passing designs by ipTM/ipSAE for downstream experimental validation.

## Verification & Troubleshooting

Verify that the number of output binder.pdb files matches the requested num_designs. Diagnose common issues: low ipTM scores (check hotspot selection, increase number of designs), slow convergence (use fast protocol for screening), OOM errors (reduce num_models or use L40S/A100 GPU), poor diversity (lower sampling_temp, run multiple seeds). Handle specific runtime errors including CUDA out-of-memory, hotspot-not-found, and timeout errors.
