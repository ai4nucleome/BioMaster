# Genomics Metagenomics

## Overview

Shotgun metagenomics workflow covering host-depletion-aware QC, taxonomic profiling, functional pathway profiling, AMR follow-up, and reproducible cohort-ready output tables.

**Inputs:** paired or single-end metagenomic FASTQ files, sample metadata, and taxonomy / function databases (Kraken2/Bracken DB, HUMAnN ChocoPhlAn + UniRef, optional AMR DB).

**Outputs:** per-sample and merged taxonomy abundance tables (bracken_species.tsv, bracken_genus.tsv), functional pathway profiles (pathabundance.tsv), AMR summaries (amr_summary.tsv), and QC summaries (read_processing_summary.tsv, fastp HTML/JSON reports).

**When to use:** shotgun metagenomics data (NOT amplicon 16S/ITS) when the user needs species or genus abundances, functional pathway profiles, AMR/resistance summaries, or cohort-level multi-sample comparison. For host-associated samples (human, plant), perform host depletion before community interpretation. For taxonomy-only needs, kraken2 + bracken is a pragmatic route; add humann for functional profiling; strain-level claims require more evidence than top-level taxonomy calls.

**Reference tool versions:** fastp 0.23+, kraken2 2.1+, bracken 2.8+, metaphlan 4+, humann 3.9+. Verify the environment before running (kraken2 --version, bracken -v, metaphlan --version, humann --version).

**Key caveats:** abundance results depend strongly on the reference database and version — always document which DB was used. Do not compare outputs from different databases as if directly interchangeable. Avoid over-interpreting taxa with extremely low abundance. State whether abundance values are relative abundance, counts, or normalized function estimates.

## Read QC and optional host depletion

Inspect read quality, adapter content, and retained reads using fastp, which produces HTML/JSON quality reports and cleaned FASTQ output. For host-associated samples (human gut, plant rhizosphere, etc.), remove host reads by aligning against the host reference genome and retaining only unmapped reads before any community interpretation. Document the host reference and version used. Report retained read counts explicitly after QC and host depletion, as downstream abundance estimates depend on read retention.

## Taxonomic profiling

Classify reads taxonomically using a k-mer-based profiler (Kraken2) or a marker-based profiler (MetaPhlAn). Document the database and version because abundance results depend strongly on the reference. Kraken2 with a confidence threshold of 0.1 is a common pragmatic choice. The output is a per-sample Kraken report file used as input for abundance refinement.

## Abundance refinement

Convert raw Kraken2 classification reports into species- and genus-level abundance tables using Bracken, which re-estimates abundance at a chosen taxonomic level by redistributing reads. Produce both species-level (S) and genus-level (G) tables. These tables are the primary taxonomy outputs suitable for cohort comparison.

## Functional and AMR profiling

Run pathway and AMR profiling only after confirming that taxonomic QC and read retention are reasonable. Use HUMAnN for functional profiling, which maps reads to gene families and reconstructs pathway abundance. For AMR follow-up, run a resistance-gene detection tool against cleaned reads or assembled contigs. Clarify whether function estimates are normalized (RPKM/CPM) and keep taxonomy-only and pathway outputs clearly separated.

## Cohort-ready output export

Save per-sample tables and merged cohort matrices with clear metadata joins so that downstream comparison and statistics are reproducible. Ensure every merged table carries sample identifiers that map to the metadata file. Verify that abundance values are labeled as relative abundance, counts, or normalized estimates. The final output tree contains taxonomy, function, AMR, and QC subdirectories.
