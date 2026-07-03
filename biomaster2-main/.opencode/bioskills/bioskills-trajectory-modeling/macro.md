# Bioskills Trajectory Modeling

## Overview

This workflow models continuous temporal trajectories from gene expression time-series data. It fits smooth non-linear curves using generalized additive models (GAMs) via mgcv (R), tests for significant temporal trends and condition differences, detects abrupt changepoints where dynamics shift (segmented in R, ruptures in Python), and predicts fitted trajectories with confidence intervals for visualization.

**Inputs:** a gene expression matrix (genes × samples/timepoints), timepoint values for each sample, and optional condition labels for between-group comparisons. For tradeSeq, count matrices with pseudotime and cell-weight matrices are expected.

**Outputs:** fitted GAM objects, per-gene significance tables (edf, F-statistics, p-values, BH-adjusted q-values), changepoint locations and counts, and predicted trajectories with 95% confidence intervals on a fine time grid.

**When to use:** time-course RNA-seq, pseudobulk aggregated trajectories, single-cell pseudotime data, or any experiment where you need to model non-linear temporal dynamics, compare trajectory shapes between conditions, or locate abrupt shifts in expression dynamics. Prefer REML estimation over GCV for smooth parameter selection (less prone to overfitting). GAMs capture smooth trends while changepoint methods complement them by locating abrupt shifts. Verify installed package versions (mgcv, numpy, pandas, scanpy) before use: in Python run `pip show <package>` then `help(module.function)`; in R run `packageVersion('<pkg>')` then `?function_name`. If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to the actual API rather than retrying.

## Data Preparation

Prepare gene expression data with associated timepoint and condition metadata for trajectory modeling. The input is an expression matrix (genes × samples/timepoints) together with metadata describing the time value and experimental condition for each sample. For mgcv and segmented fitting, reshape each gene into a long-format data frame with columns for expression, time, and condition. For tradeSeq, provide count, pseudotime, and cell-weight matrices. For ruptures, extract each gene's expression as a 1D numpy array. Create a binary condition indicator (e.g. is_treated) when planning condition comparisons via difference smooths.

## GAM Fitting

Fit generalized additive models (GAMs) with penalized smooth terms to capture non-linear temporal dynamics per gene. Use mgcv::gam() with s(time) smooth terms where the basis dimension k controls smoothness: k should be less than the number of unique timepoints, and k=6 is a good default for 8-12 timepoints (too low underfits, too high overfits). The effective degrees of freedom (edf) from summary() indicates linearity: edf near 1 is linear, edf near k-1 is highly non-linear. For condition comparisons, use the 'by' argument to fit separate smooths per condition, or use a difference smooth (by=is_treated) whose second term directly models the deviation from baseline and whose p-value tests trajectory divergence. For genome-wide analysis, loop over all genes, collect edf, F-statistics, and p-values from the s.table, then apply Benjamini-Hochberg FDR correction (q < 0.05 threshold).

## Statistical Testing & Diagnostics

Assess model adequacy and test for significant temporal trends and condition differences. Run gam.check() to inspect residual plots and verify the basis dimension is sufficient: the k-index should be >= 1.0, and if it falls below 1.0 the smooth is too rigid and k should be increased. Check concurvity (analogous to collinearity for smooth terms); values > 0.8 indicate redundancy between smooth terms. For trajectory-focused analysis, use tradeSeq, a Bioconductor wrapper around mgcv designed for trajectory analysis with built-in statistical tests: fitGAM fits the model (nKnots plays the same role as k and should be less than the number of unique timepoints), associationTest tests whether expression changes over time, and conditionTest tests trajectory differences between conditions.

## Changepoint Detection

Detect abrupt shifts in temporal dynamics where the trajectory changes direction or level, complementing the smooth GAM trends. In R, use segmented for piecewise linear regression with automatic breakpoint detection: fit a linear model first, then call segmented() with psi=NA to estimate the breakpoint, and use davies.test() to test whether a breakpoint exists (p < 0.05 indicates a changepoint). Extract the breakpoint estimate and confidence interval from summary(seg_fit)$psi. In Python, use ruptures for changepoint detection: Pelt with model='rbf' and a BIC-based penalty (np.log(n) * variance) performs exact detection, while Binseg with n_bkps offers a faster approximate alternative. Run genome-wide by looping over genes and counting changepoints per gene (note bkps[-1] is always n, the end of the signal).

## Prediction & Visualization

Predict fitted trajectories on a fine time grid and compute confidence intervals for visualization. Use predict() on the GAM fit with newdata over a dense sequence of time values (e.g. 200 points spanning the observed range) and request se.fit=TRUE to obtain standard errors. Construct 95% confidence intervals as fitted ± 1.96 * SE assuming approximate normality. Compare model choices (linear vs GAM) via AIC/BIC to determine whether non-linear modeling is warranted: lower AIC indicates a better trade-off of fit versus complexity. Use GAMs for smooth trends alongside changepoint methods for abrupt shifts to obtain a complete picture of temporal dynamics.
