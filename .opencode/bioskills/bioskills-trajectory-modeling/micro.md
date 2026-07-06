## Data Preparation

_modules: data-preparation, metadata_

```r
# R: long-format data frame per gene for mgcv/segmented
gene_df <- data.frame(
    expression = as.numeric(expr_mat[gene, ]),
    time = timepoints,
    condition = conditions
)

# Binary indicator for difference-smooth condition comparisons
gene_df$is_treated <- as.numeric(gene_df$condition == "treated")
```

```python
# Python: numpy arrays for ruptures changepoint detection
import numpy as np
signal = np.array(expression_values)        # 1D array for one gene
expr_mat = np.array(expression_matrix)      # genes x timepoints
```

## GAM Fitting

_modules: gam, mgcv, smooth-fitting, condition-comparison, fdr_

```r
library(mgcv)

# Basic GAM: s(time, k=6); k < number of unique timepoints
# edf near 1 = linear; edf near k-1 = highly non-linear
fit <- gam(expression ~ s(time, k = 6), data = gene_df, method = 'REML')
summary(fit)

# Condition comparison: separate smooths per condition via 'by'
fit_cond <- gam(
    expression ~ condition + s(time, k = 6, by = condition),
    data = gene_df, method = 'REML'
)

# Difference smooth: second smooth models deviation from baseline
fit_diff <- gam(
    expression ~ s(time, k = 6) + s(time, k = 6, by = is_treated),
    data = gene_df, method = 'REML'
)
summary(fit_diff)

# Genome-wide: loop over genes, collect stats, BH FDR correction
results <- data.frame()
for (gene in rownames(expr_mat)) {
    gene_df <- data.frame(expression = as.numeric(expr_mat[gene, ]), time = timepoints)
    fit <- gam(expression ~ s(time, k = 6), data = gene_df, method = 'REML')
    s_table <- summary(fit)$s.table
    results <- rbind(results, data.frame(
        gene = gene, edf = s_table[, 'edf'],
        F_stat = s_table[, 'F'], p_value = s_table[, 'p-value']
    ))
}
results$q_value <- p.adjust(results$p_value, method = 'BH')
temporal_genes <- results[results$q_value < 0.05, ]
```

## Statistical Testing & Diagnostics

_modules: diagnostics, tradeSeq, hypothesis-testing, concurvity_

```r
library(mgcv)
library(tradeSeq)

# Model diagnostics: gam.check() residual plots + basis dimension check
# k-index < 1.0 => increase k (smooth too rigid)
gam.check(fit)

# Concurvity: > 0.8 indicates redundancy between smooth terms
concurvity(fit_cond, full = TRUE)

# tradeSeq: fitGAM for pseudobulk/aggregated time-course data
# nKnots < number of unique timepoints
sce <- fitGAM(counts = count_mat, pseudotime = time_mat,
              cellWeights = weight_mat, nKnots = 6)

# associationTest: tests whether expression changes over time
assoc_res <- associationTest(sce)

# conditionTest: tests trajectory differences between conditions
cond_res <- conditionTest(sce)
```

## Changepoint Detection

_modules: changepoint-detection, segmented, ruptures, breakpoint_

```r
library(segmented)

# Fit linear model, then search for a breakpoint
lm_fit <- lm(expression ~ time, data = gene_df)

# psi=NA lets segmented estimate the breakpoint location
seg_fit <- segmented(lm_fit, seg.Z = ~time, psi = NA)

# davies.test: H0 = no breakpoint; p < 0.05 => changepoint exists
davies.test(lm_fit, seg.Z = ~time)

# Extract breakpoint estimate and confidence interval
summary(seg_fit)$psi
```

```python
import numpy as np
import pandas as pd
import ruptures as rpt

# Pelt: exact penalized algorithm; model='rbf' detects mean+variance changes
# min_size=2: at least 2 timepoints per segment
signal = np.array(expression_values)
algo = rpt.Pelt(model='rbf', min_size=2).fit(signal)

# BIC penalty: np.log(n) * sigma**2; higher = fewer changepoints (more conservative)
n = len(signal)
penalty = np.log(n) * np.var(signal)
changepoints = algo.predict(pen=penalty)

# BinSeg: faster approximate; n_bkps = max changepoints (use as sanity check)
algo_binseg = rpt.Binseg(model='rbf', min_size=2).fit(signal)
changepoints_binseg = algo_binseg.predict(n_bkps=3)

# Genome-wide: loop over genes; bkps[-1] is always n (end of signal)
results = []
for gene_idx in range(expr_mat.shape[0]):
    signal = expr_mat[gene_idx, :]
    algo = rpt.Pelt(model='rbf', min_size=2).fit(signal)
    penalty = np.log(len(signal)) * np.var(signal)
    bkps = algo.predict(pen=penalty)
    results.append({'gene': f'gene_{gene_idx}', 'n_changepoints': len(bkps) - 1,
                    'changepoint_indices': bkps[:-1]})
results_df = pd.DataFrame(results)
```

## Prediction & Visualization

_modules: prediction, visualization, confidence-intervals, model-comparison_

```r
library(mgcv)

# Predict on fine time grid with confidence intervals
new_data <- data.frame(time = seq(min(gene_df$time), max(gene_df$time),
                                  length.out = 200))
pred <- predict(fit, newdata = new_data, se.fit = TRUE)

new_data$fitted <- pred$fit
# 1.96 * SE: 95% CI assuming approximate normality
new_data$lower <- pred$fit - 1.96 * pred$se.fit
new_data$upper <- pred$fit + 1.96 * pred$se.fit

# Model comparison: AIC/BIC linear vs GAM (lower AIC = better fit/complexity trade-off)
lm_fit <- lm(expression ~ time, data = gene_df)
AIC(lm_fit, fit)
```
