# Bioskills Doublet Detection

## Overview

Detect and remove cell doublets (aggregates) from flow cytometry or CyTOF data before clustering or quantitative analysis. Inputs: a flowSet of FCS files read with flowCore, or a SingleCellExperiment built with CATALYST, carrying scatter (FSC/SSC) and/or DNA channels. Outputs: a filtered flowSet or SCE of singlets, per-sample doublet rates, and diagnostic scatter plots. Use this skill after initial cytometry QC and before bead normalization, clustering, or phenotyping. The workflow covers standard FSC-A/FSC-H (and FSC-W) gating, automated flowDensity gating, ratio-based detection, SSC-based gating, CyTOF DNA/event-length methods, and a regression-residual approach, with batch processing via fsApply and flowAI QC, plus visualization for reporting.

## Data Loading & Channel Verification

Load FCS files into a flowSet with flowCore and inspect the available scatter channels (FSC-A, FSC-H, FSC-W, SSC-A, SSC-H) to decide which doublet-detection methods are applicable. Also verify that installed package versions match the reference examples (flowCore 2.14+, ggplot2 3.5+); if versions differ, introspect the API before adapting the code. This is the entry point that all downstream gating steps depend on.

## Scatter-Based Singlet Gating

Apply standard singlet discrimination on the scatter pulse geometry. Singlets fall along the FSC-A vs FSC-H diagonal while doublets carry elevated FSC-A for a given FSC-H, so they are removed with rectangular or polygon gates. This step also covers the FSC-A/FSC-W width variant for instruments that report width, SSC-A/SSC-H gating for cell types where FSC discriminates poorly (combined with the FSC gate), automated flowDensity gating, and a ratio-based approach that adds an FSC-A/FSC-H derived parameter and thresholds it at the 95th percentile.

## CyTOF Doublet Detection

For mass cytometry (CyTOF) data, scatter pulse geometry is unavailable, so doublets are detected from DNA content or event length instead. Doublets carry roughly twice the DNA intercalator signal and longer event lengths than singlets. Using a CATALYST SingleCellExperiment, this step thresholds the Event_length channel or the summed DNA1/DNA2 channels at the 95th percentile and subsets to singlets.

## Regression-Based Doublet Detection

Model the expected FSC-A vs FSC-H relationship for singlets with linear regression and flag events whose absolute residuals exceed the 95th percentile as doublets. Built on a CATALYST SingleCellExperiment (with arcsinh transformation), this step can also leverage CATALYST's marker-based is_doublet call and reports the overall doublet rate. It is the recommended computational approach when manual gating is impractical.

## Batch Processing & Quality Control

Scale doublet detection across an entire experiment. First run flowAI for comprehensive quality control (flow rate, signal acquisition, and dynamic range anomalies), then apply a reusable detect_doublets function over every sample in the flowSet with fsApply. The function supports both the FSC-regression and ratio methods, and per-sample doublet rates are summarized to flag problematic tubes.

## Visualization & Reporting

Visualize and report doublet-detection outcomes. Plot FSC-A against FSC-H with doublets (identified by regression residuals above the 95th percentile) highlighted in a contrasting color, and save the figure for QC records. Diagnostic plots complement the per-sample doublet-rate reports from the batch step and feed into downstream workflow decisions.
