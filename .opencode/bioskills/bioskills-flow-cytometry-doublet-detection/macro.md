# Bioskills Flow Cytometry Doublet Detection

## Overview

This workflow detects and removes cell doublets (aggregates) from flow cytometry or CyTOF data before clustering, phenotyping, or quantitative analysis. Inputs are FCS files loaded as a flowSet (flowCore) or a CATALYST SingleCellExperiment; outputs are a singlet-filterated flowSet/SCE, per-sample doublet rates, and diagnostic scatter plots. The pipeline covers manual scatter gating (FSC-A/FSC-H, FSC-W width, SSC-A/SSC-H), automated gating (flowDensity), QC-based detection (flowAI), computational regression and ratio-based scoring, CyTOF-specific DNA/event-length detection, and batch processing with visualization. Use this skill after initial cytometry QC and before bead normalization, clustering, or phenotyping. Reference versions tested: flowCore 2.14+, ggplot2 3.5+.

## Data Loading & Channel Verification

Load FCS files into a flowSet with flowCore and confirm that the scatter channels required for doublet discrimination (FSC-A and FSC-H at minimum) are present. Optionally check for FSC-W, SSC-A/SSC-H, and CyTOF-specific channels (Event_length, DNA1, DNA2) so later steps can select the appropriate method. Verify installed package versions match the tested references before running code patterns, and introspect the package API if versions differ.

## Manual Scatter Gating

Apply manual gates on the FSC-A vs FSC-H scatter pair to retain singlets, which fall along the diagonal, and exclude doublets, which show elevated FSC-A for a given FSC-H. Use rectangular gates for simple bounds or polygon gates to follow the diagonal more closely. For instruments that provide FSC-W (width), gate on low width since doublets have larger pulse widths (FSC-A = FSC-H x FSC-W). When FSC discriminates poorly for a cell type, add an SSC-A vs SSC-H gate and combine it with the FSC gate to improve singlet purity. Visualize gates on the scatter plot to confirm placement.

## Automated & QC-Based Singlet Gating

Use automated methods to place singlet gates without manual threshold tuning. flowDensity fits an automated gate on FSC-A vs FSC-H and returns the singlet population along with a singlet percentage. flowAI performs comprehensive quality control — flow rate anomalies, signal acquisition anomalies, and dynamic range anomalies — and produces high-quality filtered FCS files that complement singlet detection based on flow rate stability.

## Regression & Ratio-Based Detection

Use computational approaches that model the expected singlet scatter relationship rather than relying on fixed gates. Linear regression of FSC-A on FSC-H models the singlet line; events with residuals above the 95th percentile are flagged as doublets. Alternatively, compute the FSC-A/FSC-H ratio (near-constant for singlets based on pulse geometry) and gate on its upper quantile. The ratio can be added as a derived parameter to each flowFrame for downstream gating.

## CyTOF Doublet Detection

For mass cytometry (CyTOF) data, which lacks traditional FSC/SSC pulse-height pairs, detect doublets using event-level features. Event_length is longer for doublets; DNA intercalator channels (DNA1, DNA2) show roughly doubled DNA content in doublets. Build a SingleCellExperiment with CATALYST's prepData, then filter events above the 95th percentile of Event_length or total DNA. CATALYST also provides a built-in is_doublet marker-based filter that can be applied via filterSCE.

## Batch Processing, Reporting & Visualization

Scale the chosen detection method across all samples in the flowSet using fsApply, then summarize results with per-sample and mean doublet rates. Visualize FSC-A vs FSC-H with events colored by doublet status (regression residuals) using ggplot2 to verify that flagged events lie off the singlet diagonal, and save the diagnostic plot to disk.
