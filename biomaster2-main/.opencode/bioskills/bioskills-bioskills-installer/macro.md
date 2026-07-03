# Bioskills Bioskills Installer

## Overview

The bioSkills Installer is a meta-skill that downloads and installs the full bioSkills collection — 425 curated bioinformatics skills spanning 62 categories — into a BioMaster project's `.opencode/bioskills/` library. It is used when setting up a fresh project or when extending an existing one with new analysis capabilities. Inputs are the user's desired scope: a full install of every skill, or a selective install limited to specific categories (e.g. single-cell, variant-calling, differential-expression, chip-seq, atac-seq, metagenomics, proteomics). Outputs are a populated bioskills directory whose skills are then automatically triggered by BioMaster based on the task at hand. Use this skill at project initialization, or before running an analysis whose required methods are not yet installed. The installed collection covers sequence and alignment, read processing, RNA-seq and expression, single-cell and spatial, variant analysis, epigenomics, metagenomics, genomics and assembly, regulatory and causal networks, immunology and clinical, specialized omics, RNA biology, phylogenetics, structural and systems biology, screens and cytometry, pathway and multi-omics integration, infrastructure, and end-to-end workflows.

## Pre-installation Check

Verify the environment meets prerequisites before installing the bioSkills collection. Confirm that the working directory is a BioMaster project with the expected `.opencode/` structure, check that the bundled install script is present, and decide whether a full or category-selective install is needed based on the user's analysis goals. This step prevents failed or partial installs by catching missing prerequisites early.

## Installation

Run the bundled install script to download and install bioSkills. The script supports two modes: a full install that populates the entire 425-skill collection across all 62 categories, and a selective install limited to specific categories passed via the `--categories` flag. Choose selective mode when only a subset of methods is needed, to keep the library lean; choose full mode for a general-purpose project.

## Verification

Confirm that the bioSkills were installed correctly by listing the installed skill directories and counting them against the expected total. This catches partial or failed downloads before the user relies on the skills for an analysis. For selective installs, spot-check that each requested category landed in the library.

## Post-installation Usage

After installation, skills are automatically triggered by BioMaster based on the task at hand — no manual invocation command is required. This step documents how to discover installed skills and provides example natural-language requests that map to installed categories, so the user knows how to kick off analyses such as differential expression, variant calling, single-cell clustering, protein structure prediction, or metagenomics classification.
