---
id: wf-0004
title: 'Detailed Metagenomic Analysis Workflow must include:Step1: load main function:
  source(''00.func_v2...'
summary: 'Detailed Metagenomic Analysis Workflow must include:Step1: load main function:
  source(''00.func_v2.R''). Description: The document ''00.func_v2.R'' contains necessary
  R packages along with their installation commands, and...'
keywords:
- metagenomics
- workflow
- 'Detailed Metagenomic Analysis Workflow must include:Step1: load main function:
  source(''00.func_v2'
- 'Detailed Metagenomic Analysis Workflow must include:Step1: load main function:
  source(''00.func_v2.R''). Description: The document ''00.func_v2.R'' contains necessary
  R packages along with their installation commands'
- 'and a pre-written main function. Subsequent use only requires sourcing the file
  with `source("00.func_v2.R")`.Step2: create_phyloseq function: Description: create
  phyloseq-class object'
- specify group (g1
- g2) variables and subset specified levels (g1.level
- g2.level)
- 'filter taxonomy by detection and prevalence cutoff. Parameters: otu_table (OTU
  table)'
- tax_table (taxonomy table)
- sam_data (samples metadata)
- tax_level (select specified taxonomy level)
- g1 (group1 in sample metadata)
- g1.level (subgroups level included in group1)
- g2 (group2 in sample metadata)
- g2.level (subgroups level included in group2)
- detection (detection cutoff)
- prevalence (prevalence cutoff)
- 'rel (Transformation to apply. The options include: ''compositional'' (ie relative
  abundance)'
- '''Z'''
- '''log10'''
- '''log10p'''
- '''hellinger'''
- '''pageentity'''
- '''clr'''
- '''alr'')'
- 'tpagey_taxonomy (Clean up the taxonomic table to make taxonomic assignments consistent).
  Expected Output: phyloseq-class object. Tools Used: create_ph'
path: .opencode/knowledge/workflows/wf-0004-detailed-metagenomic-analysis-workflow-must-include-step1-load-main-function-source-00-func-v2.md
origin_source: workflow
origin_page: 13
source_entry_index: 4
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: metagenomics
---

# Detailed Metagenomic Analysis Workflow must include:Step1: load main function: source('00.func_v2...

## One-line description

Detailed Metagenomic Analysis Workflow must include:Step1: load main function: source('00.func_v2.R'). Description: The document '00.func_v2.R' contains necessary R packages along with their installation commands, and...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `13`
- Source entry index: `4`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0004`
- Analysis/tool category: `metagenomics`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Detailed Metagenomic Analysis Workflow must include:Step1: load main function: source('00.func_v2.R'). Description: The document '00.func_v2.R' contains necessary R packages along with their installation commands, and a pre-written main function. Subsequent use only requires sourcing the file with `source("00.func_v2.R")`.Step2: create_phyloseq function: Description: create phyloseq-class object; specify group (g1, g2) variables and subset specified levels (g1.level, g2.level); filter taxonomy by detection and prevalence cutoff. Parameters: otu_table (OTU table), tax_table (taxonomy table), sam_data (samples metadata), tax_level (select specified taxonomy level), g1 (group1 in sample metadata), g1.level (subgroups level included in group1), g2 (group2 in sample metadata), g2.level (subgroups level included in group2), detection (detection cutoff), prevalence (prevalence cutoff), rel (Transformation to apply. The options include: 'compositional' (ie relative abundance), 'Z', 'log10', 'log10p', 'hellinger', 'pageentity', 'clr', 'alr'), tpagey_taxonomy (Clean up the taxonomic table to make taxonomic assignments consistent). Expected Output: phyloseq-class object. Tools Used: create_phyloseq function.Step3: plot_detection_prevalence function: Description: Calculates the community core microbita and visualization. Determine members of the core microbiota with given abundance and prevalences. Parameters:   ps (phyloseq object), min_prevalence (minimum prevalence cutoff), step_detection (Set the number of steps for detection). Expected Output: filtered phyloseq object and core microbita figure plot. Tools Used: plot_detection_prevalence function.Step4: plot_comp function: Description: Plot taxon abundance for microbiome composition. Parameters: ps (phyloseq object), tax_level (select specified taxonomy level), strata (Specifies a faceted variable), groupmean (calculate mean abundance for each group), ntaxa (how many taxa are selected to show), sort_bacteria (Select the number of bacteria to arrange the sample), clustering (whether order samples by the clustering), clustering_plot (whether add clustering plot), use_alluvium (whether add alluvium plot). Expected Output: Composition figure plot. Tools Used: plot_comp function.Step5: cal_alpha function: Description: analyzing alpha diversity in ecosystems, including the calculation of various richness, evenness, diversity, dominance, and rarity indices, along with methods for visualizing these measures and testing differences in alpha diversity between groups. Parameters: ps (phyloseq object), group (A string indicating the variable for group pageentifiers), strata (A string indicating the variable for strata pageentifiers), method_test (the name of the statistical test (e.g. t.test, wilcox.test etc.)), signif_label (whether show the p-value as labels: c('***'=0.001, '**'=0.01, '*'=0.05)), adj.vars (Specify adjust variables of sample metadata). Expected Output: Alpha diversity index table (res_alpha$table) and figure plots (res_alpha$observed, res_alpha$chao1, res_alpha$diversity_shannon, res_alpha$diversity_gini_simpson, etc.). Tools Used: cal_alpha function.Step6: cal_pca function: Description: Performs a principal components analysis (PCA). Parameters: ps (phyloseq object), group (A string indicating the variable for group pageentifiers), center (whether the variables should be shifted to be zero centered), scale (whether the variables should be scaled to have unit variance). Expected Output: PCA  components table (res_pca$table) and figure plots (res_pca$pca_biplot, res_pca$pca_ind, res_pca$pca_contrib1, res_pca$pca_contrib2). Tools Used: cal_pca function.Step7: cal_dist function: Description: Calculate dissimilarity matrix, anosim and PERMANOVA analysis. Parameters: ps (phyloseq object), method (Dissimilarity index, one of c('manhattan', 'euclpageean', 'canberra', 'clark', 'bray', 'kulczynski', 'jaccard', 'gower', 'altGower', 'morisita', 'horn', 'mountford', 'raup', 'binomial', 'chao', 'cao', 'mahalanobis', 'chisq', 'chord', 'hellinger', 'aitchison','robust.aitchison')), group (A string indicating the variable for group pageentifiers for anosim and PERMANOVA analysis), adj.vars (adjust variables of sample metadata. Note: This feature is yet to be verified). Expected Output: A list contains Dissimilarity matrix (res_dist$dist), anosim result (res_dist$anosim) and PERMANOVA RESULT (res_dist$PERMANOVA). Tools Used: cal_dist function.Step8: cal_ordination function: Description: Perform an ordination on phyloseq data. Parameters: ps (phyloseq object), dist (a pre-computed dist-class object), method (several commonly-used ordination methods. Currently supported method options are: c('DCA', 'CCA', 'RDA', 'NMDS', 'MDS', 'PCoA')), type (The plot type. Default is 'samples'. The currently supported options are c('samples', 'taxa', 'biplot', 'split', 'scree')), group (The name of the variable to map to colors in the plot), shape (The name of the variable to map to different shapes on the plot), label (The name of the variable to map to text labels on the plot). Expected Output: An ordination object (res_ord$ordination) and figure plot (res_ord$fig_ord). Tools Used: cal_ordination function.Step9: cal_marker function: Description: This function is only a wrapper of all differential analysis functions, We recommend to use the corresponding function, since it has a better default arguments setting. Parameters: ps (phyloseq object), group (A string indicating the variable for group pageentifiers), da_method (character to specify the differential analysis method. The options include:c('lefse','simple_t','simple_welch','simple_white','simple_kruskal','simple_anova','edger','deseq2','metagenomeseq','ancom','ancombc','aldex','limma_voom','sl_lr','sl_rf','sl_svm')), tax_rank (character to specify taxonomic rank to perform differential analysis on), transform (the methods used to transform the microbial abundance, default is pageentity), norm (the methods used to normalize the microbial abundance data), norm_para (arguments passed to specific normalization methods), p_adjust (method for multiple test correction, default none), pvalue_cutoff (p value cutoff, default 0.05). Expected Output: a microbiomeMarker table (mm@marker_table), in which the slot of marker_table contains four variables (feature, enrich_group, lda, pvalue), `microbiomeMarker::plot_ef_bar(mm)` plot bar of markers, `microbiomeMarker::plot_abundance(mm,group = iGroup)` plot abundance of markers. Tools Used: R packages microbiomeMarker, run_lefse function.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
