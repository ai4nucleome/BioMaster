# Bioskills Context Specific Models

## Overview

This workflow builds a context-specific metabolic model by constraining a generic genome-scale model (e.g., Recon3D, iJO1366, E. coli core) with transcriptomics or proteomics expression data, so that the resulting model reflects the active metabolism of a particular tissue, cell type, or condition. Inputs are a generic COBRApy model and a gene-expression table (RNA-seq TPM/FPKM, microarray intensities, or proteomics abundances). Outputs are a pruned/constrained context-specific model plus a validation report comparing growth capability and reaction activity against the original model. Use this workflow when you need to simulate tissue- or condition-specific metabolism, for example as a precursor to flux balance analysis of a particular cell type. Three integration strategies are supported: GIMME (penalize flux through lowly-expressed reactions while maintaining a minimum biomass flux), iMAT (maximize agreement between flux activity and expression via MILP-style constraints), and a tissue-specific wrapper around GIMME driven by GTEx median TPM. The workflow is implemented in Python with COBRApy (tested with COBRApy 0.29+, numpy 1.26+, pandas 2.2+); before running, verify installed versions match and introspect the API if ImportErrors or AttributeErrors arise.

## Expression Data Integration

Load expression data from a tabular file (RNA-seq TPM/FPKM, microarray intensities, or proteomics abundances), log-transform it when the dynamic range is large, and min-max normalize values to a 0-1 range. Then map gene-level expression onto model reactions through the gene-protein-reaction (GPR) associations: aggregate expression across the genes of each reaction using max for OR relationships, min for AND (complex) relationships, or mean; non-enzymatic reactions without GPR rules default to a neutral 0.5. The output is a reaction-to-expression mapping consumed by the downstream GIMME and iMAT steps.

## GIMME Context Model

Build a context-specific model with the GIMME algorithm (Gene Inactivity Moderated by Metabolism and Expression). Compute an expression cutoff at a configurable percentile (default bottom 25%), flag genes below the cutoff as lowly expressed, copy the generic model, enforce a minimum biomass/growth flux, and constrain reactions whose entire gene set is low-expressed to near-zero bounds. The result retains metabolically active reactions required for growth while suppressing inactive ones.

## iMAT Context Model

Build a context-specific model with the iMAT algorithm (Integrative Metabolic Analysis Tool), which maximizes agreement between flux activity and expression. Classify each reaction as highly or lowly expressed using high/low percentile thresholds (aggregating gene expression with max for OR logic), then force a minimum flux through highly expressed reactions and tightly bound lowly expressed reactions. This is a simplified MILP-style formulation; a full implementation would add binary consistency variables to formally maximize the number of consistent reactions.

## Tissue-Specific Model Construction

Apply the GIMME-based pipeline to public tissue expression atlases such as GTEx, which provides median TPM across 54 human tissues. Load the GTEx median expression table, select the column matching the target tissue (e.g., liver), build a gene-to-expression dictionary, and pass it to GIMME to obtain a tissue-specific human metabolic model. GTEx median expression can be downloaded from https://gtexportal.org/home/datasets.

## Model Validation

Compare the context-specific model against the original generic model to confirm the integration was sound. Run flux balance analysis on both models and compare objective (growth) values, count how many reactions had their upper bounds tightened relative to the original, and report the growth ratio and fraction of constrained reactions. A valid context model should retain reasonable growth capability while substantially reducing the number of active reactions.
