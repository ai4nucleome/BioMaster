# Bioskills Crispr Screen Pipeline

## Overview

This end-to-end CRISPR screen pipeline takes raw pooled or single-cell CRISPR screening data from FASTQ files through to a tiered consensus of high-confidence hit genes. It covers library design validation, guide counting with MAGeCK, six-stage quality control, copy-number and batch correction for cancer cell lines and multi-batch designs, design-matched hit calling (MAGeCK RRA/MLE, BAGEL2, drugZ, JACKS, or Chronos), and cross-method tier-based consensus with visualization.

**Inputs:** FASTQ files, a library annotation CSV (guide sequences and gene mappings), a sample sheet with labels, and optionally a copy-number profile and a batch design matrix.

**Outputs:** a raw count matrix, per-sample QC metrics, CN-corrected counts (cancer lines), per-method gene-level score tables (RRA, MLE, Bayes factors, drugZ FDR, JACKS effects, Chronos effects), and a tiered consensus hit table with volcano-plot figures.

**When to use:** Use this workflow for pooled CRISPR essentiality, drug-modifier, time-course, or multi-screen joint analyses. For single-cell Perturb-seq/CROP-seq, combinatorial paralog screens, base/prime-editing variant screens, or in vivo tumor/immune screens, follow the specialized branches referenced within the hit-calling step.

**Version compatibility note:** Reference examples were tested with MAGeCK 0.5.9+, BAGEL2 1.0.5+, drugZ Aug 2019+, JACKS 0.2.0+, Chronos 2.0+, CRISPRcleanR 3.0+ (R), Pertpy 0.6+, CRISPResso2 2.2.14+, MAGeCKFlute 2.0+, pandas 2.2+, numpy 1.26+, matplotlib 3.8+. Before running, verify installed versions (e.g. `mageck --version`, `BAGEL.py fc --help`, `drugz -h`, `pip show pertpy jacks chronos-cn`, `packageVersion('CRISPRcleanR')`). If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to the actual API rather than retrying.

## Library Design and Pre-Screen Validation

Validate the sgRNA library composition before sequencing to ensure the screen is fit for purpose. Confirm that the plasmid pool Gini coefficient is below 0.1 (Joung 2017 Nat Protoc 12:828), at least 99% of guides are detected at more than 25 reads per guide, the skew ratio (p90/p10) is below 2, and that non-targeting controls comprise approximately 1% of the library. Include the CEGv2 reference essential gene set and the NEGv1 non-essential gene set as benchmarking references. This step gates whether the library should proceed to sequencing.

## Guide Counting

Count sgRNA abundances from FASTQ files using MAGeCK count to produce a raw count matrix and a per-sample count summary. Provide a library CSV listing guide sequences and gene mappings, sample labels matching the FASTQ order, and the 5' protospacer adapter to trim (e.g. CACCG for SpCas9). Use median normalization. For Cas12a libraries (Inzolia, in4mer) or combinatorial designs, follow the combinatorial-screens workflow. For 10X single-cell direct capture, use cellranger-arc or pertpy-aware counting instead of MAGeCK count.

## Quality Control

Run the six-stage quality control audit on the count matrix. Compute per-sample metrics: percent zero-count guides, Gini coefficient, reads per sgRNA, and replicate Pearson correlation on log10-transformed counts. Apply hard gates: plasmid Gini below 0.1 and endpoint Gini below 0.3 (or below 0.55 for heavy drug screens), replicate Pearson above 0.85, CEGv2 precision-recall AUC above 0.7 against the Hart 2017 reference essential gene set, and at least 300 reads per sgRNA per sample (DepMap convention). Flag or exclude samples failing these gates before proceeding to correction and hit calling.

## Copy-Number and Batch Correction

For cancer cell line screens, apply copy-number correction to remove the amplicon artifact (Aguirre 2016 / Munoz 2016) using CRISPRcleanR (unsupervised, no CN profile required) or Chronos (joint model with a matched CN profile). Feed the corrected counts into all downstream hit-calling methods. For multi-batch screens, add batch as a covariate in the MAGeCK MLE design matrix rather than pre-correcting with ComBat. For DepMap-scale panels with longitudinal data and matched CN, use Chronos as the joint standard that handles CN bias, screen quality, and time jointly.

## Hit Calling

Select and run the hit-calling method matched to the screen design. For two-condition essentiality screens, use MAGeCK RRA (treatment vs control) or BAGEL2 (Bayes factor against the CEGv2 essential and NEGv1 non-essential reference sets). For time-course or multi-condition designs, use MAGeCK MLE with a design matrix. For drug-modifier chemogenomic screens, use drugZ with vehicle (not Day-0) as the control. For multi-screen joint analysis, use JACKS to model shared sgRNA efficacy across screens. For cancer cell-line panels, use Chronos as the DepMap quarterly standard that jointly handles CN bias, screen quality, and longitudinal data.

## Consensus and Visualization

Aggregate per-method gene-level results into a tier-based consensus table of high-confidence hits. Merge MAGeCK FDR, BAGEL Bayes factor, and drugZ synthetic-lethal FDR by gene; classify each gene as a hit per method using thresholds (MAGeCK FDR below 0.05, BAGEL Bayes factor above 6, drugZ FDR below 0.05); and assign tiers by the number of methods calling a hit (tier 1 = all methods agree, tier 2 = two of three). Visualize the essentiality results as a volcano plot of log2 fold change versus negative log10 FDR. Use the MAGeCKFlute R package (FluteRRA / FluteMLE) for one-shot dashboards with KEGG/Reactome pathway enrichment of the hit lists.
