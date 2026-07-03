# Bioskills Enhancer Gene Linking

## Overview

Predicts which gene a distal accessible (enhancer) region regulates by combining accessibility activity, 3D contact frequency, and (optionally) sequence-based chromatin features into a per-(enhancer, gene) score that can be thresholded for high-confidence calls. Inputs: ATAC-seq BAM/peaks, H3K27ac ChIP-seq BAM, a Hi-C/Micro-C contact matrix (optional but recommended), and gene annotation. Outputs: per-pair ABC or ENCODE-rE2G scores, plus an intersected high-confidence set when multiple methods agree. Use this workflow for cell-type-specific enhancer-target assignment; ABC and ENCODE-rE2G are the canonical predictors when Hi-C/Micro-C is available, Cicero is the ATAC-only fallback, and CRISPRi-FlowFISH is the experimental gold-standard for validation. ABC computes Activity (geometric mean of ATAC and H3K27ac) times Hi-C contact, normalized over a +/- 5 Mb cis window, with ABC.Score >= 0.02 as the standard high-confidence threshold. ENCODE-rE2G reformulates this as a logistic regression trained on CRISPRi-FlowFISH ground truth and generally outperforms ABC at CRISPRi recall, especially at 50-500 kb distances. For therapeutic target nomination, require consistency across two methods plus experimental validation; single-method high-score predictions remain exploratory hypotheses.

## Signal Track Preparation

Generate RPGC-normalized ATAC and H3K27ac signal tracks from aligned BAM files. Both tracks must share the same scale because ABC's Activity metric is the geometric mean of accessibility and H3K27ac signals; mismatched sequencing depths skew activity scores. Use bamCoverage with reads-per-genomic-content (RPGC) normalization and a 50 bp bin size. When H3K27ac depth differs from ATAC, additionally apply ABC's quantile normalization (--qnorm) against a reference file (e.g. src/EnhancersQNormRef.K562.txt from the ABC repo) so both signals are on a comparable scale before they are combined downstream.

## Candidate Enhancer Definition

Define non-promoter candidate enhancers from ATAC peaks, typically MACS narrowPeak output. Filter out promoter regions with bedtools so that ABC predictions do not concentrate at transcription start sites. The resulting candidate set is the input to ABC neighborhoods. Using a peak set that is too narrow can cause HiChIP loops to fall below the ABC threshold, so ensure the candidate enhancers span the accessible regions adequately.

## ABC Scoring Pipeline

Run the ABC pipeline in two coupled stages. First, run.neighborhoods.py computes per-candidate Activity as the geometric mean of ATAC accessibility and H3K27ac signal over each candidate enhancer. Second, predict.py multiplies Activity by Hi-C/Micro-C contact frequency to the gene's TSS and normalizes over the cis window (default +/- 5 Mb), producing a per-(enhancer, gene) ABC.Score. Threshold ABC.Score >= 0.02 for high-confidence calls (Fulco 2019 calibration against CRISPRi-FlowFISH); >= 0.04 is a stricter precision cut. When Hi-C is unavailable, ABC falls back to an average contact map pooled from five ENCODE cell types with acknowledged performance degradation; document this proxy in methods. Use 5 kb or 10 kb Hi-C resolution when Micro-C is available, since default 25 kb resolution masks fine ABC structure.

## ENCODE-rE2G Alternative

Run ENCODE-rE2G as an alternative or complementary predictor. It reformulates ABC as a logistic regression trained on CRISPRi-FlowFISH ground truth, combining ABC features with sequence features and distance. Choose a cell-type-matched pre-trained model; for novel cell types pick the closest ENCODE lineage (myeloid -> K562, lymphoid -> GM12878, hepatic -> HepG2) and document the proxy. Use the no-hic feature configuration when 3D contact data is unavailable. ENCODE-rE2G generally outperforms ABC at CRISPRi recall, especially at 50-500 kb distances; for ENCODE cell types prefer ENCODE-rE2G, while ABC remains the default for novel cell types. Retraining requires CRISPRi-FlowFISH data.

## Multi-Method Integration

Build a high-confidence enhancer-gene set by intersecting evidence across methods. Merge ABC and ENCODE-rE2G predictions on the enhancer-gene pair above per-method thresholds (ABC >= 0.02, ENCODE-rE2G >= 0.5), then flag pairs supported by HiChIP loops for triple-method evidence. When ABC and ENCODE-rE2G disagree, both are valid; report the intersection as high-confidence. When ABC is strong but Cicero is weak, trust ABC if Hi-C is matched. For therapeutic target nomination, require consistency across two methods (ABC + ENCODE-rE2G, or ABC + HiChIP) plus experimental validation; single-method high-score predictions remain exploratory hypotheses.

## Experimental Validation

Validate predictions experimentally with CRISPRi-FlowFISH, the gold-standard assay. Tile each candidate enhancer with sgRNAs, transduce CRISPRi-expressing cells, sort by gene expression via FlowFISH (endogenous) or a reporter (ectopic), and sequence sgRNAs across low- and high-expression bins. Compute log2 enrichment per sgRNA and meta-test across sgRNAs within the same enhancer; a 2-fold expression decrease at p < 0.05 confirms the enhancer regulates the gene. For publication-grade reporting, benchmark predictions against published CRISPRi catalogs (Fulco 2019 K562, Gasperini 2019, Schraivogel 2020), check effect-size correlation between predicted score and observed expression effect, and verify no distance-ranking bias.
