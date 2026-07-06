# Bioskills Umi Processing

## Overview

This workflow processes UMI-tagged sequencing reads from raw FASTQ through to a deduplicated BAM and per-gene/per-cell UMI count matrix. UMIs (Unique Molecular Identifiers) are short random sequences added during library preparation to tag individual molecules before PCR amplification, enabling accurate PCR duplicate removal and molecule counting. The pipeline uses UMI-tools (with optional fastp for simple extraction) plus a standard aligner (STAR for RNA-seq, bwa/bowtie2 for DNA). Inputs: paired-end FASTQ files carrying UMI sequences (in the read sequence, a separate index read, or both reads). Outputs: a deduplicated, indexed BAM file and/or a gene-by-cell UMI count table (TSV, long or wide format). Use this workflow for UMI-based bulk RNA-seq, single-cell RNA-seq post-CellRanger deduplication, or any library prep that incorporates UMIs. The ordered stages are: extract UMIs to read headers, align to a reference, collapse PCR duplicates by UMI+position, count molecules per gene/cell, and assess deduplication statistics.

## UMI Extraction

Extract UMI sequences from raw FASTQ reads and move them into the read header so they survive alignment. UMI-tools `extract` supports UMIs located at the start of R1, R2, both reads, or in a separate index read, specified via pattern strings where `N` denotes a UMI base, `C` a cell barcode, and `X` a discarded base. Complex patterns support cell-barcode + UMI combinations (e.g. 10X 3' v3: 16bp barcode + 12bp UMI), fixed anchor sequences, and skipped bases between barcode and UMI. Quality filtering can discard reads with low-quality UMI bases (Phred threshold) or N-containing UMIs. For simple cases, fastp can extract UMIs during QC, but it does not deduplicate and must be followed by `umi_tools dedup` after alignment.

## Alignment

Align UMI-tagged reads to a reference genome using a standard splice-aware or short-read aligner (STAR for RNA-seq, bwa/bowtie2 for DNA). The UMI is preserved in the read name and carried through to the BAM. The resulting BAM must be coordinate-sorted and indexed before deduplication, since `umi_tools dedup` requires a sorted, indexed BAM as input.

## Deduplication

Collapse PCR duplicates by grouping reads that share the same UMI and mapping position, retaining one representative read per original molecule. UMI-tools `dedup` offers multiple methods: `directional` (default, recommended for most RNA-seq), `unique` (exact UMI matches only, most stringent), `cluster` (network-based, for low-diversity/high-error data), `adjacency` (balanced accuracy/speed), and `percentile` (for extremely high duplication). It supports paired-end mode, per-gene deduplication using a gene tag (GX/XT), and per-cell deduplication using a cell barcode tag (CB) for single-cell data. As an alternative to collapsing, `umi_tools group` tags reads with their UMI group (BX tag) without removing duplicates.

## UMI Counting

Produce a molecule count table from a deduplicated (or grouped) BAM. UMI-tools `count` generates a gene-by-cell matrix using gene tags (GX) and cell barcode tags (CB). Output is available in long format (gene, cell, count columns) or wide matrix format suitable for downstream expression analysis. This is the final count matrix used as input for single-cell or bulk RNA-seq quantification pipelines.

## Statistics & QC

Generate and interpret deduplication statistics to assess library complexity and the PCR duplication rate. UMI-tools `dedup --output-stats` produces per-UMI-per-position, per-UMI, and edit-distance TSV files. The dedup log can be parsed with pandas to compute the deduplication rate (fraction of reads removed as PCR duplicates). Performance options tune speed and memory for large files: `--parallel` uses multiple cores, `--buffer-whole-contig` reduces memory, and `--no-sort-output` skips re-sorting for speed.
