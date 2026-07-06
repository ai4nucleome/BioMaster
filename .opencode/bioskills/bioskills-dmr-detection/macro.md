# Bioskills Dmr Detection

## Overview

This workflow identifies differentially methylated regions (DMRs) — contiguous genomic stretches with statistically significant methylation differences between conditions — and prepares them for biological interpretation. It accepts pre-called methylation data from whole-genome bisulfite sequencing (WGBS, e.g. Bismark coverage or CpG reports) or from methylation arrays (beta-value matrices) as input. The pipeline supports three complementary detection strategies: fixed-window tiling (methylKit), CpG-level smoothing (bsseq BSmooth), and kernel-based smoothing for arrays (DMRcate). After detection, DMRs are refined (merged and split into hyper/hypo subsets), annotated against genes, promoters, and CpG islands, visualized as genome-browser tracks, and exported to standard formats (BED/CSV/GFF). Use this skill when per-CpG or per-sample methylation calls already exist and region-level differential calls are needed; for upstream read-level calling see methylation-calling, and for per-CpG statistical testing see differential-cpg-testing. Expected outputs are a GRanges object of significant DMRs with statistics, an annotation table mapping DMRs to genomic features, genome-browser figures, and portable result files.

## Data Loading & Preprocessing

Read pre-called methylation data into R objects and apply coverage/quality filters. methylKit ingests Bismark coverage files via methRead and filters low- and high-coverage sites with filterByCoverage; bsseq reads Bismark CpG reports with read.bismark, collapsing strands and dropping zero-coverage sites. For array data, a beta-value matrix (CpGs x samples) plus a design matrix is prepared for DMRcate. This step produces filtered, sample-aware methylation objects ready for region-level testing.

## DMR Detection

Identify candidate DMRs using one of three complementary strategies. methylKit tiles the genome into fixed windows with tileMethylCounts, unites samples, and runs calculateDiffMeth to compute per-tile methylation differences and q-values, then extracts significant regions with getMethylDiff (optionally split into hyper/hypo). bsseq smooths CpG-level methylation with BSmooth, applies a coverage filter, and calls dmrFinder on the corrected t-statistic. DMRcate annotates CpGs with cpg.annotate and applies kernel smoothing via dmrcate to group significant CpGs into regions. Each method returns genomic ranges with associated statistics.

## DMR Refinement & Merging

Consolidate raw DMR calls into a clean set of non-overlapping regions. Adjacent or near-adjacent DMRs within a configurable gap (e.g. 500 bp) are merged with GenomicRanges::reduce, and hyper- versus hypo-methylated subsets are kept separate for downstream interpretation. This step yields a compact GRanges object of final DMRs suitable for annotation and export.

## Genomic Annotation

Map refined DMRs to functional genomic features for biological interpretation. annotatr builds a genome-wide annotation set (genes, promoters, CpG islands) and intersects DMRs with annotate_regions to produce a per-DMR feature table. genomation offers an alternative using BED12 gene models via annotateWithGeneParts, reporting promoter/exon/intron distributions with getTargetAnnotationStats. The output is a per-DMR table of overlapping features.

## Visualization & Export

Visualize DMRs in a genome-browser-style plot and export results in standard formats for sharing and downstream analysis. Gviz constructs methylation and gene-region tracks and renders them over a selected interval with plotTracks. rtracklayer exports DMRs to BED and GFF, and methylKit's getData combined with write.csv produces a tabular summary. This step produces publication-ready figures and portable result files.
