## Pre-Filtering

_modules: pre-filtering, filterbyexpr, gene-filtering_

```r
library(edgeR)

# Design-aware filtering: requires CPM above threshold in >= n samples,
# where n = smallest group size; min.count=10, min.total.count=15 by default
keep <- filterByExpr(y, design=model.matrix(~condition, data=metadata))
y <- y[keep, , keep.lib.sizes=FALSE]
```

```r
# DESeq2: speed/memory only; independent filtering at results() handles stats
keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep, ]

# alpha in results() should match the planned FDR cutoff,
# because independent filtering is optimized at this threshold
res <- results(dds, alpha=0.05)
```

## Between-Sample Normalization

_modules: size-factors, rle, tmm, composition-bias_

```r
library(DESeq2)

dds <- DESeqDataSetFromMatrix(countData=counts, colData=coldata, design=~condition)
dds <- estimateSizeFactors(dds)
sizeFactors(dds)

# Normalized counts for export/visualization
norm_counts <- counts(dds, normalized=TRUE)

# Special cases:
# estimateSizeFactors(dds, type='poscounts')        # high zero-inflation (single-cell)
# estimateSizeFactors(dds, type='iterate')          # very small libraries
# estimateSizeFactors(dds, controlGenes=stable_idx) # known stable genes / mostly-DE genome
```

```r
library(edgeR)

y <- DGEList(counts=counts, group=metadata$condition)
y <- calcNormFactors(y, method='TMM')
# Trims 30% of M-values, 5% of A-values by default.
# Effective library size = lib.size * norm.factors (stored in y$samples$norm.factors).

# Upper quartile alternative (mild composition bias)
y <- calcNormFactors(y, method='upperquartile')
```

```python
# Simplified TMM normalization factors (Python)
import numpy as np
import pandas as pd

def tmm_norm_factors(counts):
    lib_sizes = counts.sum(axis=0)
    ref_idx = np.argmin(np.abs(np.log(lib_sizes) - np.mean(np.log(lib_sizes))))
    ref = counts.iloc[:, ref_idx]
    factors = np.ones(counts.shape[1])
    for i in range(counts.shape[1]):
        if i == ref_idx:
            continue
        sample = counts.iloc[:, i]
        keep = (ref > 0) & (sample > 0)
        m = np.log2(sample[keep] / lib_sizes[i]) - np.log2(ref[keep] / lib_sizes[ref_idx])
        a = 0.5 * (np.log2(sample[keep] / lib_sizes[i]) + np.log2(ref[keep] / lib_sizes[ref_idx]))
        m_lo, m_hi = np.percentile(m, [15, 85])
        a_lo, a_hi = np.percentile(a, [2.5, 97.5])
        keep2 = (m >= m_lo) & (m <= m_hi) & (a >= a_lo) & (a <= a_hi)
        factors[i] = 2 ** np.average(m[keep2])
    return factors / np.exp(np.mean(np.log(factors)))
```

## Within-Sample Normalization (TPM/FPKM)

_modules: tpm, fpkm, within-sample, gene-length_

```python
import pandas as pd
import numpy as np

def counts_to_tpm(counts, gene_lengths):
    '''Convert raw counts to TPM. gene_lengths in bp.'''
    rate = counts.div(gene_lengths / 1000, axis=0)  # RPK
    tpm = rate.div(rate.sum(axis=0), axis=1) * 1e6
    return tpm
```

```r
counts_to_tpm <- function(counts, gene_lengths) {
    rate <- counts / (gene_lengths / 1000)  # RPK
    tpm <- t(t(rate) / colSums(rate)) * 1e6
    return(tpm)
}
```

## Variance-Stabilizing Transformations

_modules: vst, rlog, log-cpm, variance-stabilization_

```r
library(DESeq2)

# blind=TRUE: re-estimates dispersions ignoring design; for unbiased QC
vsd <- vst(dds, blind=TRUE)

# blind=FALSE: uses dispersions from full model; recommended for downstream use
vsd <- vst(dds, blind=FALSE)
vst_matrix <- assay(vsd)

# rlog: better when library sizes vary >10-fold; slow, impractical for >100 samples
rld <- rlog(dds, blind=FALSE)
rlog_matrix <- assay(rld)
```

```r
library(edgeR)

# Default prior.count=0.25 for stats; use >=2 for heatmaps/PCA to dampen low-count noise
log_cpm <- cpm(y, log=TRUE, prior.count=2)
```

```python
import numpy as np

def log_cpm(counts, prior_count=2):
    '''Log2 CPM with prior count for noise dampening.'''
    lib_sizes = counts.sum(axis=0)
    # Scale prior proportional to library size (edgeR convention)
    cpm_vals = (counts + prior_count) / (lib_sizes + 2 * prior_count) * 1e6
    return np.log2(cpm_vals)
```

## GC Content and Gene Length Bias Correction

_modules: gc-bias, gene-length-bias, edaseq, cqn_

```r
library(EDASeq)

# Requires gene-level GC content
feature_data <- data.frame(gc=gene_gc_content, length=gene_lengths, row.names=rownames(counts))
data <- newSeqExpressionSet(counts=as.matrix(counts), featureData=feature_data, phenoData=coldata)

# Within-lane GC normalization, then between-lane normalization
data_norm <- withinLaneNormalization(data, 'gc', which='full')
data_norm <- betweenLaneNormalization(data_norm, which='full')
normalized_counts <- counts(data_norm)
```

```r
library(cqn)

# Combines GC and length correction with quantile normalization
cqn_result <- cqn(counts, x=gene_gc_content, lengths=gene_lengths)

# Use offset in edgeR
y$offset <- cqn_result$glm.offset
```

## Single-Cell Normalization

_modules: single-cell, scran, scanpy, deconvolution_

```r
library(scran)
library(scater)

# Pre-cluster to avoid mixing cell types with different transcriptome sizes
clusters <- quickCluster(sce)

# Deconvolution-based size factors
sce <- computeSumFactors(sce, clusters=clusters)

# Apply normalization
sce <- logNormCounts(sce)
```

```python
import scanpy as sc

# Simpler CPM-like normalization; less robust to composition bias than scran.
# For rigorous analysis, use scran via rpy2 or anndata2ri.
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
```
