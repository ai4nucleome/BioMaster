# Bioskills Tcr Pipeline

## Overview

End-to-end TCR/BCR repertoire analysis pipeline that takes paired-end FASTQ files from immune repertoire sequencing (bulk or single-cell) and produces clonotype tables, diversity metrics, sample-overlap distances, and repertoire visualizations. The pipeline orchestrates MiXCR for V(D)J alignment and clonotype assembly, VDJtools for diversity and overlap analysis, and generates spectratype and V/J gene usage plots. Inputs: paired FASTQ files (R1/R2) from TCR/BCR sequencing. Outputs: an aligned VDJCA file, an assembled clonotype CLNS file, an exported clonotype TXT table, diversity statistics, pairwise overlap distance matrices, and publication-ready repertoire plots. Use this workflow when analyzing TCR/BCR repertoire sequencing data end-to-end, e.g. to compare clonal composition across conditions, time points, or donors. Prerequisite: verify that MiXCR 4.6+ and VDJtools 1.2.1+ are installed and that CLI flags match the installed versions (run `mixcr --version` and `vdjtools --version`); if a command throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to the actual API rather than retrying.

## MiXCR Processing

Align paired-end sequencing reads to V(D)J reference segments using MiXCR, assemble the aligned reads into clonotypes, and export the resulting clonotype table. This is the foundational step that converts raw FASTQ into structured clonotype calls, using the rna-seq preset for human samples. It produces an aligned VDJCA file, an assembled clonotype CLNS file, and an exported TXT clonotype table that all downstream steps consume.

## VDJtools Analysis

Convert the MiXCR clonotype export into VDJtools format, compute repertoire diversity statistics, and calculate pairwise distances between samples to quantify repertoire overlap. This step quantifies clonal diversity (e.g. Shannon, Simpson, Gini indices) and inter-sample similarity, enabling comparison of repertoire composition across conditions, time points, or donors.

## Visualization

Generate repertoire visualizations from the VDJtools-format clonotype data, including fancy spectratype plots (CDR3 length distribution) and fancy V/J gene usage plots. These plots summarize the repertoire structure for quality assessment and publication figures, making clonal expansion and V/J gene biases immediately visible.

## QC and Validation

Run quality-control checkpoints at each stage of the pipeline to validate results before drawing biological conclusions. After alignment, verify the V/J assignment rate (typically greater than 70%). After assembly, confirm that the clonotype count and read coverage fall within expected ranges. After diversity analysis, compare the computed diversity metrics against expected ranges for the sample type. These checkpoints catch low-quality libraries, failed alignments, or anomalous diversity early.
