# Bioskills Lineage Tracing

## Overview

This workflow reconstructs cell lineage trees from heritable barcode mutations and links them to clonal dynamics and transcriptomic state. It supports three barcode modalities — engineered CRISPR editing sites (Cassiopeia), lentiviral LARRY barcodes, and natural mitochondrial DNA variants (MitoTracing) — and combines phylogenetic reconstruction (Cassiopeia solvers) with fate-map inference (CoSpar) and scRNA-seq integration (scanpy).

**Inputs:** raw barcode sequencing (BAM/FASTQ) or a pre-built cells-by-sites integer character matrix (values: -1 missing, 0 unedited/reference, 1+ mutation states); optionally a paired scRNA-seq AnnData with clone annotations and cell-type labels.

**Outputs:** a cleaned character matrix, a reconstructed lineage tree (CassiopeiaTree), tree quality metrics and visualizations, CoSpar transition/fate maps and clone-size dynamics, and clonal-expansion differential-expression results integrated with transcriptomic state.

**When to use:** studying clonal relationships, cell fate decisions, clonal expansion, or transition dynamics in lineage-traced single-cell experiments. Not a substitute for pseudotime-only trajectory inference when no heritable barcode is available.

**Version note:** reference examples target Cassiopeia 2.0+, matplotlib 3.8+, numpy 1.26+, scanpy 1.10+. Verify installed versions before running; if code raises ImportError/AttributeError/TypeError, introspect the installed package (`pip show <package>`, `help(module.function)`) and adapt the call to the actual API rather than retrying.

## Barcode Processing & Character Matrix Construction

Parse lineage barcodes from raw sequencing data and convert them into a numeric character matrix suitable for tree inference. Three input modalities are supported. (1) CRISPR editing barcodes: call alleles from a BAM alignment against a barcode reference, filter low-quality cells and alleles, then convert to a character matrix with -1 as the missing-state indicator. (2) Lentiviral LARRY barcodes: parse paired FASTQ reads against a cell whitelist and assign clone IDs that can be joined into an AnnData obs column. (3) Mitochondrial (MitoTracing) barcodes: call mtDNA variants directly from an scRNA-seq BAM as natural barcodes requiring no engineering, filter variants by cell count and allele frequency, then compute a Jaccard distance matrix and build a neighbor-joining tree. Each modality applies quality filters and yields an integer cells-by-sites matrix (or distance matrix) where -1 indicates missing data, 0 the unedited/reference state, and positive integers index distinct mutation states.

## Character Matrix QC

Assess and clean the character matrix before tree reconstruction. Quantify barcode diversity as the number of mutation states per site, identify and drop uninformative characters (sites mutated in only one cell), and profile missing data per cell and per site. Remove cells whose missing-data fraction exceeds a threshold (e.g. 0.5) to reduce noise and improve downstream parsimony solutions.

## Lineage Tree Reconstruction

Reconstruct a cell lineage tree from the cleaned character matrix using maximum parsimony. Build a CassiopeiaTree object holding the character matrix and cell metadata, inspect basic data-quality statistics (cell count, character count, missing fraction), then solve with an appropriate solver. VanillaGreedySolver is fast for large trees; ILPSolver gives optimal parsimony on smaller subsets (set a convergence time limit); HybridSolver combines a greedy top solver with an ILP bottom solver below a cell cutoff for scalability with quality; NeighborJoiningSolver with weighted Hamming dissimilarity provides a distance-based comparison.

## Tree Quality Assessment & Visualization

Evaluate reconstructed tree quality and visualize results. Compare two trees with Robinson-Foulds distance and assess topological accuracy via triplet correctness against a ground-truth tree. Estimate branch support by bootstrapping the solver across replicates and summarizing support per clade. Report summary statistics — tree depth, Colless balance, Sackin index, and the gamma statistic — to characterize tree shape and diversification tempo. Render trees annotated with cell-type metadata using matplotlib, ETE3, or export to iTOL for interactive viewing.

## Clonal Dynamics with CoSpar

Infer cell fate transition maps and clonal dynamics from time-series lineage-tracing data using CoSpar. Load a lineage-traced AnnData carrying a clone-id or barcode column in obs, infer a transition map with intraclone smoothing over a multi-scale neighborhood, then estimate fate probabilities from a source population to a sink population. Extend the analysis with fate coupling between cell types, time-resolved transition probabilities, and clone-size dynamics across time points, visualizing clonal embedding, fate maps, fate coupling, transition maps, and clone-size distributions.

## Integration with scRNA-seq & Clonal Expansion

Connect lineage trees to transcriptomic state. Match tree leaves to scRNA-seq cells via their shared cell barcodes, subset both the tree and the AnnData to the common cells, and compute pairwise tree distances to store in adata.obsp for correlation with transcriptomic similarity. Identify expanded clones by a size threshold, run differential expression between expanded and non-expanded clones with scanpy, and score clone-specific gene signatures to link clonal relatedness to functional cell states.
