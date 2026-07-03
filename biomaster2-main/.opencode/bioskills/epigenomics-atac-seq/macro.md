# Epigenomics Atac Seq

## Overview

Bulk ATAC-seq processing pipeline for paired-end data, from raw BAM/FASTQ through peak calling to downstream accessibility analysis. Inputs: paired-end ATAC BAM or FASTQ, a reference genome, and sample groups for comparisons. Outputs: per-sample narrowPeak calls and summits, a consensus peak-by-sample count matrix, a differential accessibility table, and QC figures (TSS enrichment, fragment size distribution). Use this skill when the task is bulk ATAC-seq (not ChIP-seq) and the user needs assay QC review (TSS enrichment, fragment periodicity, FRiP), peak calling, accessibility counting, differential accessibility testing, or motif deviation / footprint follow-up. For paired-end bulk ATAC, use fragment-aware (BAMPE) mode and ATAC-specific Tn5 shifting rather than generic ChIP defaults. If TSS enrichment is poor, stop and flag data quality before interpretation. Expected runtime versions: macs3 3.0+, samtools 1.18+, deepTools 3.5+.

## Validate assay QC

Review assay quality before any interpretation. Inspect TSS enrichment, fragment size periodicity (nucleosome ladder), duplication rate, and mapped read depth. Acceptance gates: uniquely mapped reads >= 20M preferred for strong bulk ATAC; TSS enrichment > 7 acceptable, > 10 strong; FRiP > 0.2 typically strong, while FRiP < 0.1 is weak and needs scrutiny. Strong nucleosome periodicity supports a good library. If TSS enrichment falls below 7, stop and flag data quality rather than proceeding. Do not merge peaks from mixed reference builds. Verify the runtime tool versions first.

## Call peaks with ATAC-specific settings

Call peaks per sample using fragment-aware paired-end mode (BAMPE) with Tn5-aware shifting. Do not use generic ChIP peak-calling defaults for ATAC. Call peaks without a control using ATAC-specific settings: nomodel, shift -100, extsize 200, FDR q 0.01 as a starting threshold. Produce per-sample narrowPeak and summits files.

## Build a consensus peak matrix

Merge peaks across samples into a consensus set of intervals, then count fragments from each sample into those consensus intervals to produce a peak-by-sample count matrix. Ensure all peaks come from the same reference build before merging.

## Test differential accessibility

Test for differential accessibility between sample groups using replicate-aware statistics. Report both effect size (log2 fold change) and adjusted significance. Use a model that accounts for biological replicates; do not interpret single-replicate comparisons as differential.

## Run motif or footprint follow-up

Run motif deviation or footprinting analysis only after peak quality and read depth support it. Do not trust footprinting on low-depth or poor-quality libraries. This is an optional downstream step contingent on the QC gates from step 1 passing.
