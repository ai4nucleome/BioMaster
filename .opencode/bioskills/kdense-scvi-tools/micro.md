## differential-expression.md

# Differential Expression Analysis in scvi-tools

This document provides detailed information about differential expression (DE) analysis using scvi-tools' probabilistic framework.

## Overview

scvi-tools implements Bayesian differential expression testing that leverages the learned generative models to estimate expression differences between groups. This approach provides several advantages over traditional methods:

- **Batch correction**: DE testing on batch-corrected representations
- **Uncertainty quantification**: Probabilistic estimates of effect sizes
- **Zero-inflation handling**: Proper modeling of dropout and zeros
- **Flexible comparisons**: Between any groups or cell types
- **Multiple modalities**: Works for RNA, proteins (totalVI), and accessibility (PeakVI)

## Core Statistical Framework

### Problem Definition

The goal is to estimate the log fold-change in expression between two conditions:

```
log fold-change = log(μ_B) - log(μ_A)
```

Where μ_A and μ_B are the mean expression levels in conditions A and B.

### Three-Stage Process

**Stage 1: Estimating Expression Levels**
- Sample from posterior distribution of cellular states
- Generate expression values from the learned generative model
- Aggregate across cells to get population-level estimates

**Stage 2: Detecting Relevant Features (Hypothesis Testing)**
- Test for differential expression using Bayesian framework
- Two testing modes available:
  - **"vanilla" mode**: Point null hypothesis (β = 0)
  - **"change" mode**: Composite hypothesis (|β| ≤ δ)

**Stage 3: Controlling False Discovery**
- Posterior expected False Discovery Proportion (FDP) control
- Selects maximum number of discoveries ensuring E[FDP] ≤ α

## Basic Usage

### Simple Two-Group Comparison

```python
import scvi

# After training a model
model = scvi.model.SCVI(adata)
model.train()

# Compare two cell types
de_results = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells"
)

# View top DE genes
top_genes = de_results.sort_values("lfc_mean", ascending=False).head(20)
print(top_genes[["lfc_mean", "lfc_std", "bayes_factor", "is_de_fdr_0.05"]])
```

### One vs. Rest Comparison

```python
# Compare one group against all others
de_results = model.differential_expression(
    groupby="cell_type",
    group1="T cells"  # No group2 = compare to rest
)
```

### All Pairwise Comparisons

```python
# Compare all cell types pairwise
all_comparisons = {}

cell_types = adata.obs["cell_type"].unique()

for ct1 in cell_types:
    for ct2 in cell_types:
        if ct1 != ct2:
            key = f"{ct1}_vs_{ct2}"
            all_comparisons[key] = model.differential_expression(
                groupby="cell_type",
                group1=ct1,
                group2=ct2
            )
```

## Key Parameters

### `groupby` (required)
Column in `adata.obs` defining groups to compare.

```python
# Must be a categorical variable
de_results = model.differential_expression(groupby="cell_type")
```

### `group1` and `group2`
Groups to compare. If `group2` is None, compares `group1` to all others.

```python
# Specific comparison
de = model.differential_expression(groupby="condition", group1="treated", group2="control")

# One vs rest
de = model.differential_expression(groupby="cell_type", group1="T cells")
```

### `mode` (Hypothesis Testing Mode)

**"vanilla" mode** (default): Point null hypothesis
- Tests if β = 0 exactly
- More sensitive, but may find trivially small effects

**"change" mode**: Composite null hypothesis
- Tests if |β| ≤ δ
- Requires biologically meaningful change
- Reduces false discoveries of tiny effects

```python
# Change mode with minimum effect size
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells",
    mode="change",
    delta=0.25  # Minimum log fold-change
)
```

### `delta`
Minimum effect size threshold for "change" mode.
- Typical values: 0.25, 0.5, 0.7 (log scale)
- log2(1.5) ≈ 0.58 (1.5-fold change)
- log2(2) = 1.0 (2-fold change)

```python
# Require at least 1.5-fold change
de = model.differential_expression(
    groupby="condition",
    group1="disease",
    group2="healthy",
    mode="change",
    delta=0.58  # log2(1.5)
)
```

### `fdr_target`
False discovery rate threshold (default: 0.05)

```python
# More stringent FDR control
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    fdr_target=0.01
)
```

### `batch_correction`
Whether to perform batch correction during DE testing (default: True)

```python
# Test within a specific batch
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells",
    batch_correction=False
)
```

### `n_samples`
Number of posterior samples for estimation (default: 5000)
- More samples = more accurate but slower
- Reduce for speed, increase for precision

```python
# High precision analysis
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    n_samples=10000
)
```

## Interpreting Results

### Output Columns

The results DataFrame contains several important columns:

**Effect Size Estimates**:
- `lfc_mean`: Mean log fold-change
- `lfc_median`: Median log fold-change
- `lfc_std`: Standard deviation of log fold-change
- `lfc_min`: Lower bound of effect size
- `lfc_max`: Upper bound of effect size

**Statistical Significance**:
- `bayes_factor`: Bayes factor for differential expression
  - Higher values = stronger evidence
  - >3 often considered meaningful
- `is_de_fdr_0.05`: Boolean indicating if gene is DE at FDR 0.05
- `is_de_fdr_0.1`: Boolean indicating if gene is DE at FDR 0.1

**Expression Levels**:
- `mean1`: Mean expression in group 1
- `mean2`: Mean expression in group 2
- `non_zeros_proportion1`: Proportion of non-zero cells in group 1
- `non_zeros_proportion2`: Proportion of non-zero cells in group 2

### Example Interpretation

```python
de_results = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells"
)

# Find significantly upregulated genes in T cells
upreg_tcells = de_results[
    (de_results["is_de_fdr_0.05"]) &
    (de_results["lfc_mean"] > 0)
].sort_values("lfc_mean", ascending=False)

print(f"Upregulated genes in T cells: {len(upreg_tcells)}")
print(upreg_tcells.head(10))

# Find genes with large effect sizes
large_effect = de_results[
    (de_results["is_de_fdr_0.05"]) &
    (abs(de_results["lfc_mean"]) > 1)  # 2-fold change
]
```

## Advanced Usage

### DE Within Specific Cells

```python
# Test DE only within a subset of cells
subset_indices = adata.obs["tissue"] == "lung"

de = model.differential_expression(
    idx1=adata.obs["cell_type"] == "T cells" & subset_indices,
    idx2=adata.obs["cell_type"] == "B cells" & subset_indices
)
```

### Batch-Specific DE

```python
# Test DE within each batch separately
batches = adata.obs["batch"].unique()

batch_de_results = {}
for batch in batches:
    batch_idx = adata.obs["batch"] == batch
    batch_de_results[batch] = model.differential_expression(
        idx1=(adata.obs["condition"] == "treated") & batch_idx,
        idx2=(adata.obs["condition"] == "control") & batch_idx
    )
```

### Pseudo-bulk DE

```python
# Aggregate cells before DE testing
# Useful for low cell counts per group

de = model.differential_expression(
    groupby="cell_type",
    group1="rare_cell_type",
    group2="common_cell_type",
    n_samples=10000,  # More samples for stability
    batch_correction=True
)
```

## Visualization

### Volcano Plot

```python
import matplotlib.pyplot as plt
import numpy as np

de = model.differential_expression(
    groupby="condition",
    group1="treated",
    group2="control"
)

# Volcano plot
plt.figure(figsize=(10, 6))
plt.scatter(
    de["lfc_mean"],
    -np.log10(1 / (de["bayes_factor"] + 1)),
    c=de["is_de_fdr_0.05"],
    cmap="coolwarm",
    alpha=0.5
)
plt.xlabel("Log Fold Change")
plt.ylabel("-log10(1/Bayes Factor)")
plt.title("Volcano Plot: Treated vs Control")
plt.axvline(x=0, color='k', linestyle='--', linewidth=0.5)
plt.show()
```

### Heatmap of Top DE Genes

```python
import seaborn as sns

# Get top DE genes
top_genes = de.sort_values("lfc_mean", ascending=False).head(50).index

# Get normalized expression
norm_expr = model.get_normalized_expression(
    adata,
    indices=adata.obs["condition"].isin(["treated", "control"]),
    gene_list=top_genes
)

# Plot heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(
    norm_expr.T,
    cmap="viridis",
    xticklabels=False,
    yticklabels=top_genes
)
plt.title("Top 50 DE Genes")
plt.show()
```

### Ranked Gene Plot

```python
# Plot genes ranked by effect size
de_sorted = de.sort_values("lfc_mean", ascending=False)

plt.figure(figsize=(12, 6))
plt.plot(range(len(de_sorted)), de_sorted["lfc_mean"].values)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel("Gene Rank")
plt.ylabel("Log Fold Change")
plt.title("Genes Ranked by Effect Size")
plt.show()
```

## Comparison with Traditional Methods

### scvi-tools vs. Wilcoxon Test

```python
import scanpy as sc

# Traditional Wilcoxon test
sc.tl.rank_genes_groups(
    adata,
    groupby="cell_type",
    method="wilcoxon",
    key_added="wilcoxon"
)

# scvi-tools DE
de_scvi = model.differential_expression(
    groupby="cell_type",
    group1="T cells"
)

# Compare results
wilcox_results = sc.get.rank_genes_groups_df(adata, group="T cells", key="wilcoxon")
```

**Advantages of scvi-tools**:
- Accounts for batch effects automatically
- Handles zero-inflation properly
- Provides uncertainty quantification
- No arbitrary pseudocount needed
- Better statistical properties

**When to use Wilcoxon**:
- Very quick exploratory analysis
- Comparison with published results using Wilcoxon

## Multi-Modal DE

### Protein DE (totalVI)

```python
# Train totalVI on CITE-seq data
totalvi_model = scvi.model.TOTALVI(adata)
totalvi_model.train()

# RNA differential expression
rna_de = totalvi_model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells",
    protein_expression=False  # Default
)

# Protein differential expression
protein_de = totalvi_model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells",
    protein_expression=True
)

print(f"DE genes: {rna_de['is_de_fdr_0.05'].sum()}")
print(f"DE proteins: {protein_de['is_de_fdr_0.05'].sum()}")
```

### Differential Accessibility (PeakVI)

```python
# Train PeakVI on ATAC-seq data
peakvi_model = scvi.model.PEAKVI(atac_adata)
peakvi_model.train()

# Differential accessibility
da = peakvi_model.differential_accessibility(
    groupby="cell_type",
    group1="T cells",
    group2="B cells"
)

# Same interpretation as DE
```

## Handling Special Cases

### Low Cell Count Groups

```python
# Increase posterior samples for stability
de = model.differential_expression(
    groupby="cell_type",
    group1="rare_type",  # e.g., 50 cells
    group2="common_type",  # e.g., 5000 cells
    n_samples=10000
)
```

### Imbalanced Comparisons

```python
# When groups have very different sizes
# Use change mode to avoid tiny effects

de = model.differential_expression(
    groupby="condition",
    group1="rare_condition",
    group2="common_condition",
    mode="change",
    delta=0.5
)
```

### Multiple Testing Correction

```python
# Already included via FDP control
# But can apply additional corrections

from statsmodels.stats.multitest import multipletests

# Bonferroni correction (very conservative)
_, pvals_corrected, _, _ = multipletests(
    1 / (de["bayes_factor"] + 1),
    method="bonferroni"
)
```

## Performance Considerations

### Speed Optimization

```python
# Faster DE testing for large datasets
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    n_samples=1000,  # Reduce samples
    batch_size=512    # Increase batch size
)
```

### Memory Management

```python
# For very large datasets
# Test one comparison at a time rather than all pairwise

cell_types = adata.obs["cell_type"].unique()
for ct in cell_types:
    de = model.differential_expression(
        groupby="cell_type",
        group1=ct
    )
    # Save results
    de.to_csv(f"de_results_{ct}.csv")
```

## Best Practices

1. **Use "change" mode**: For biologically interpretable results
2. **Set appropriate delta**: Based on biological significance
3. **Check expression levels**: Filter lowly expressed genes
4. **Validate findings**: Check marker genes for sanity
5. **Visualize results**: Always plot top DE genes
6. **Report parameters**: Document mode, delta, FDR used
7. **Consider batch effects**: Use batch_correction=True
8. **Multiple comparisons**: Be aware of testing many groups
9. **Sample size**: Ensure sufficient cells per group (>50 recommended)
10. **Biological validation**: Follow up with functional experiments

## Example: Complete DE Analysis Workflow

```python
import scvi
import scanpy as sc
import matplotlib.pyplot as plt

# 1. Train model
scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
model = scvi.model.SCVI(adata)
model.train()

# 2. Perform DE analysis
de_results = model.differential_expression(
    groupby="cell_type",
    group1="Disease_T_cells",
    group2="Healthy_T_cells",
    mode="change",
    delta=0.5,
    fdr_target=0.05
)

# 3. Filter and analyze
sig_genes = de_results[de_results["is_de_fdr_0.05"]]
upreg = sig_genes[sig_genes["lfc_mean"] > 0].sort_values("lfc_mean", ascending=False)
downreg = sig_genes[sig_genes["lfc_mean"] < 0].sort_values("lfc_mean")

print(f"Significant genes: {len(sig_genes)}")
print(f"Upregulated: {len(upreg)}")
print(f"Downregulated: {len(downreg)}")

# 4. Visualize top genes
top_genes = upreg.head(10).index.tolist() + downreg.head(10).index.tolist()

sc.pl.violin(
    adata[adata.obs["cell_type"].isin(["Disease_T_cells", "Healthy_T_cells"])],
    keys=top_genes,
    groupby="cell_type",
    rotation=90
)

# 5. Functional enrichment (using external tools)
# E.g., g:Profiler, DAVID, or gprofiler-official Python package
upreg_genes = upreg.head(100).index.tolist()
# Perform pathway analysis...

# 6. Save results
de_results.to_csv("de_results_disease_vs_healthy.csv")
upreg.to_csv("upregulated_genes.csv")
downreg.to_csv("downregulated_genes.csv")
```

---

## models-atac-seq.md

# ATAC-seq and Chromatin Accessibility Models

This document covers models for analyzing single-cell ATAC-seq and chromatin accessibility data in scvi-tools.

## PeakVI

**Purpose**: Analysis and integration of single-cell ATAC-seq data using peak counts.

**Key Features**:
- Variational autoencoder specifically designed for scATAC-seq peak data
- Learns low-dimensional representations of chromatin accessibility
- Performs batch correction across samples
- Enables differential accessibility testing
- Integrates multiple ATAC-seq datasets

**When to Use**:
- Analyzing scATAC-seq peak count matrices
- Integrating multiple ATAC-seq experiments
- Batch correction of chromatin accessibility data
- Dimensionality reduction for ATAC-seq
- Differential accessibility analysis between cell types or conditions

**Data Requirements**:
- Peak count matrix (cells × peaks)
- Binary or count data for peak accessibility
- Batch/sample annotations (optional, for batch correction)

**Basic Usage**:
```python
import scvi

# Prepare data (peaks should be in adata.X)
# Optional: filter peaks
sc.pp.filter_genes(adata, min_cells=3)

# Setup data
scvi.model.PEAKVI.setup_anndata(
    adata,
    batch_key="batch"
)

# Train model
model = scvi.model.PEAKVI(adata)
model.train()

# Get latent representation (batch-corrected)
latent = model.get_latent_representation()
adata.obsm["X_PeakVI"] = latent

# Differential accessibility
da_results = model.differential_accessibility(
    groupby="cell_type",
    group1="TypeA",
    group2="TypeB"
)
```

**Key Parameters**:
- `n_latent`: Dimensionality of latent space (default: 10)
- `n_hidden`: Number of nodes per hidden layer (default: 128)
- `n_layers`: Number of hidden layers (default: 1)
- `region_factors`: Whether to learn region-specific factors (default: True)
- `latent_distribution`: Distribution for latent space ("normal" or "ln")

**Outputs**:
- `get_latent_representation()`: Low-dimensional embeddings for cells
- `get_accessibility_estimates()`: Normalized accessibility values
- `differential_accessibility()`: Statistical testing for differential peaks
- `get_region_factors()`: Peak-specific scaling factors

**Best Practices**:
1. Filter out low-quality peaks (present in very few cells)
2. Include batch information if integrating multiple samples
3. Use latent representations for clustering and UMAP visualization
4. Consider using `region_factors=True` for datasets with high technical variation
5. Store latent embeddings in `adata.obsm` for downstream analysis with scanpy

## PoissonVI

**Purpose**: Quantitative analysis of scATAC-seq fragment counts (more detailed than peak counts).

**Key Features**:
- Models fragment counts directly (not just peak presence/absence)
- Poisson distribution for count data
- Captures quantitative differences in accessibility
- Enables fine-grained analysis of chromatin state

**When to Use**:
- Analyzing fragment-level ATAC-seq data
- Need quantitative accessibility measurements
- Higher resolution analysis than binary peak calls
- Investigating gradual changes in chromatin accessibility

**Data Requirements**:
- Fragment count matrix (cells × genomic regions)
- Count data (not binary)

**Basic Usage**:
```python
scvi.model.POISSONVI.setup_anndata(
    adata,
    batch_key="batch"
)

model = scvi.model.POISSONVI(adata)
model.train()

# Get results
latent = model.get_latent_representation()
accessibility = model.get_accessibility_estimates()
```

**Key Differences from PeakVI**:
- **PeakVI**: Best for standard peak count matrices, faster
- **PoissonVI**: Best for quantitative fragment counts, more detailed

**When to Choose PoissonVI over PeakVI**:
- Working with fragment counts rather than called peaks
- Need to capture quantitative differences
- Have high-quality, high-coverage data
- Interested in subtle accessibility changes

## scBasset

**Purpose**: Deep learning approach to scATAC-seq analysis with interpretability and motif analysis.

**Key Features**:
- Convolutional neural network (CNN) architecture for sequence-based analysis
- Models raw DNA sequences, not just peak counts
- Enables motif discovery and transcription factor (TF) binding prediction
- Provides interpretable feature importance
- Performs batch correction

**When to Use**:
- Want to incorporate DNA sequence information
- Interested in TF motif analysis
- Need interpretable models (which sequences drive accessibility)
- Analyzing regulatory elements and TF binding sites
- Predicting accessibility from sequence alone

**Data Requirements**:
- Peak sequences (extracted from genome)
- Peak accessibility matrix
- Genome reference (for sequence extraction)

**Basic Usage**:
```python
# scBasset requires sequence information
# First, extract sequences for peaks
from scbasset import utils
sequences = utils.fetch_sequences(adata, genome="hg38")

# Setup and train
scvi.model.SCBASSET.setup_anndata(
    adata,
    batch_key="batch"
)

model = scvi.model.SCBASSET(adata, sequences=sequences)
model.train()

# Get latent representation
latent = model.get_latent_representation()

# Interpret model: which sequences/motifs are important
importance_scores = model.get_feature_importance()
```

**Key Parameters**:
- `n_latent`: Latent space dimensionality
- `conv_layers`: Number of convolutional layers
- `n_filters`: Number of filters per conv layer
- `filter_size`: Size of convolutional filters

**Advanced Features**:
- **In silico mutagenesis**: Predict how sequence changes affect accessibility
- **Motif enrichment**: Identify enriched TF motifs in accessible regions
- **Batch correction**: Similar to other scvi-tools models
- **Transfer learning**: Fine-tune on new datasets

**Interpretability Tools**:
```python
# Get importance scores for sequences
importance = model.get_sequence_importance(region_indices=[0, 1, 2])

# Predict accessibility for new sequences
predictions = model.predict_accessibility(new_sequences)
```

## Model Selection for ATAC-seq

### PeakVI
**Choose when**:
- Standard scATAC-seq analysis workflow
- Have peak count matrices (most common format)
- Need fast, efficient batch correction
- Want straightforward differential accessibility
- Prioritize computational efficiency

**Advantages**:
- Fast training and inference
- Proven track record for scATAC-seq
- Easy integration with scanpy workflow
- Robust batch correction

### PoissonVI
**Choose when**:
- Have fragment-level count data
- Need quantitative accessibility measures
- Interested in subtle differences
- Have high-coverage, high-quality data

**Advantages**:
- More detailed quantitative information
- Better for gradient changes
- Appropriate statistical model for counts

### scBasset
**Choose when**:
- Want to incorporate DNA sequence
- Need biological interpretation (motifs, TFs)
- Interested in regulatory mechanisms
- Have computational resources for CNN training
- Want predictive power for new sequences

**Advantages**:
- Sequence-based, biologically interpretable
- Motif and TF analysis built-in
- Predictive modeling capabilities
- In silico perturbation experiments

## Workflow Example: Complete ATAC-seq Analysis

```python
import scvi
import scanpy as sc

# 1. Load and preprocess ATAC-seq data
adata = sc.read_h5ad("atac_data.h5ad")

# 2. Filter low-quality peaks
sc.pp.filter_genes(adata, min_cells=10)

# 3. Setup and train PeakVI
scvi.model.PEAKVI.setup_anndata(
    adata,
    batch_key="sample"
)

model = scvi.model.PEAKVI(adata, n_latent=20)
model.train(max_epochs=400)

# 4. Extract latent representation
latent = model.get_latent_representation()
adata.obsm["X_PeakVI"] = latent

# 5. Downstream analysis
sc.pp.neighbors(adata, use_rep="X_PeakVI")
sc.tl.umap(adata)
sc.tl.leiden(adata, key_added="clusters")

# 6. Differential accessibility
da_results = model.differential_accessibility(
    groupby="clusters",
    group1="0",
    group2="1"
)

# 7. Save model
model.save("peakvi_model")
```

## Integration with Gene Expression (RNA+ATAC)

For paired multimodal data (RNA+ATAC from same cells), use **MultiVI** instead:

```python
# For 10x Multiome or similar paired data
scvi.model.MULTIVI.setup_anndata(
    adata,
    batch_key="sample",
    modality_key="modality"  # "RNA" or "ATAC"
)

model = scvi.model.MULTIVI(adata)
model.train()

# Get joint latent space
latent = model.get_latent_representation()
```

See `models-multimodal.md` for more details on multimodal integration.

## Best Practices for ATAC-seq Analysis

1. **Quality Control**:
   - Filter cells with very low or very high peak counts
   - Remove peaks present in very few cells
   - Filter mitochondrial and sex chromosome peaks if needed

2. **Batch Correction**:
   - Always include `batch_key` if integrating multiple samples
   - Consider technical covariates (sequencing depth, TSS enrichment)

3. **Feature Selection**:
   - Unlike RNA-seq, all peaks are often used
   - Consider filtering very rare peaks for efficiency

4. **Latent Dimensions**:
   - Start with `n_latent=10-30` depending on dataset complexity
   - Larger values for more heterogeneous datasets

5. **Downstream Analysis**:
   - Use latent representations for clustering and visualization
   - Link peaks to genes for regulatory analysis
   - Perform motif enrichment on cluster-specific peaks

6. **Computational Considerations**:
   - ATAC-seq matrices are often very large (many peaks)
   - Consider downsampling peaks for initial exploration
   - Use GPU acceleration for large datasets

---

## models-multimodal.md

# Multimodal and Multi-omics Integration Models

This document covers models for joint analysis of multiple data modalities in scvi-tools.

## totalVI (Total Variational Inference)

**Purpose**: Joint analysis of CITE-seq data (simultaneous RNA and protein measurements from same cells).

**Key Features**:
- Jointly models gene expression and protein abundance
- Learns shared low-dimensional representations
- Enables protein imputation from RNA data
- Performs differential expression for both modalities
- Handles batch effects in both RNA and protein layers

**When to Use**:
- Analyzing CITE-seq or REAP-seq data
- Joint RNA + surface protein measurements
- Imputing missing proteins
- Integrating protein and RNA information
- Multi-batch CITE-seq integration

**Data Requirements**:
- AnnData with gene expression in `.X` or a layer
- Protein measurements in `.obsm["protein_expression"]`
- Same cells measured for both modalities

**Basic Usage**:
```python
import scvi

# Setup data - specify both RNA and protein layers
scvi.model.TOTALVI.setup_anndata(
    adata,
    layer="counts",  # RNA counts
    protein_expression_obsm_key="protein_expression",  # Protein counts
    batch_key="batch"
)

# Train model
model = scvi.model.TOTALVI(adata)
model.train()

# Get joint latent representation
latent = model.get_latent_representation()

# Get normalized values for both modalities
rna_normalized = model.get_normalized_expression()
protein_normalized = model.get_normalized_expression(
    transform_batch="batch1",
    protein_expression=True
)

# Differential expression (works for both RNA and protein)
rna_de = model.differential_expression(groupby="cell_type")
protein_de = model.differential_expression(
    groupby="cell_type",
    protein_expression=True
)
```

**Key Parameters**:
- `n_latent`: Latent space dimensionality (default: 20)
- `n_layers_encoder`: Number of encoder layers (default: 1)
- `n_layers_decoder`: Number of decoder layers (default: 1)
- `protein_dispersion`: Protein dispersion handling ("protein" or "protein-batch")
- `empirical_protein_background_prior`: Use empirical background for proteins

**Advanced Features**:

**Protein Imputation**:
```python
# Impute missing proteins for RNA-only cells
# (useful for mapping RNA-seq to CITE-seq reference)
protein_foreground = model.get_protein_foreground_probability()
imputed_proteins = model.get_normalized_expression(
    protein_expression=True,
    n_samples=25
)
```

**Denoising**:
```python
# Get denoised counts for both modalities
denoised_rna = model.get_normalized_expression(n_samples=25)
denoised_protein = model.get_normalized_expression(
    protein_expression=True,
    n_samples=25
)
```

**Best Practices**:
1. Use empirical protein background prior for datasets with ambient protein
2. Consider protein-specific dispersion for heterogeneous protein data
3. Use joint latent space for clustering (better than RNA alone)
4. Validate protein imputation with known markers
5. Check protein QC metrics before training

## MultiVI (Multi-modal Variational Inference)

**Purpose**: Integration of paired and unpaired multi-omic data (e.g., RNA + ATAC, paired and unpaired cells).

**Key Features**:
- Handles paired data (same cells) and unpaired data (different cells)
- Integrates multiple modalities: RNA, ATAC, proteins, etc.
- Missing modality imputation
- Learns shared representations across modalities
- Flexible integration strategy

**When to Use**:
- 10x Multiome data (paired RNA + ATAC)
- Integrating separate RNA-seq and ATAC-seq experiments
- Some cells with both modalities, some with only one
- Cross-modality imputation tasks

**Data Requirements**:
- AnnData with multiple modalities
- Modality indicators (which measurements each cell has)
- Can handle:
  - All cells with both modalities (fully paired)
  - Mix of paired and unpaired cells
  - Completely unpaired datasets

**Basic Usage**:
```python
# Prepare data with modality information
# adata.X should contain all features (genes + peaks)
# adata.var["modality"] indicates "Gene" or "Peak"
# adata.obs["modality"] indicates which modality each cell has

scvi.model.MULTIVI.setup_anndata(
    adata,
    batch_key="batch",
    modality_key="modality"  # Column indicating cell modality
)

model = scvi.model.MULTIVI(adata)
model.train()

# Get joint latent representation
latent = model.get_latent_representation()

# Impute missing modalities
# E.g., predict ATAC for RNA-only cells
imputed_accessibility = model.get_accessibility_estimates(
    indices=rna_only_indices
)

# Get normalized expression/accessibility
rna_normalized = model.get_normalized_expression()
atac_normalized = model.get_accessibility_estimates()
```

**Key Parameters**:
- `n_genes`: Number of gene features
- `n_regions`: Number of accessibility regions
- `n_latent`: Latent dimensionality (default: 20)

**Integration Scenarios**:

**Scenario 1: Fully Paired (10x Multiome)**:
```python
# All cells have both RNA and ATAC
# Single modality key: "paired"
adata.obs["modality"] = "paired"
```

**Scenario 2: Partially Paired**:
```python
# Some cells have both, some RNA-only, some ATAC-only
adata.obs["modality"] = ["RNA+ATAC", "RNA", "ATAC", ...]
```

**Scenario 3: Completely Unpaired**:
```python
# Separate RNA and ATAC experiments
adata.obs["modality"] = ["RNA"] * n_rna + ["ATAC"] * n_atac
```

**Advanced Use Cases**:

**Cross-Modality Prediction**:
```python
# Predict peaks from gene expression
accessibility_from_rna = model.get_accessibility_estimates(
    indices=rna_only_cells
)

# Predict genes from accessibility
expression_from_atac = model.get_normalized_expression(
    indices=atac_only_cells
)
```

**Modality-Specific Analysis**:
```python
# Separate analysis per modality
rna_subset = adata[adata.obs["modality"].str.contains("RNA")]
atac_subset = adata[adata.obs["modality"].str.contains("ATAC")]
```

## MrVI (Multi-resolution Variational Inference)

**Purpose**: Multi-sample analysis accounting for sample-specific and shared variation.

**Key Features**:
- Simultaneously analyzes multiple samples/conditions
- Decomposes variation into:
  - Shared variation (common across samples)
  - Sample-specific variation
- Enables sample-level comparisons
- Identifies sample-specific cell states

**When to Use**:
- Comparing multiple biological samples or conditions
- Identifying sample-specific vs. shared cell states
- Disease vs. healthy sample comparisons
- Understanding inter-sample heterogeneity
- Multi-donor studies

**Basic Usage**:
```python
scvi.model.MRVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch",
    sample_key="sample"  # Critical: defines biological samples
)

model = scvi.model.MRVI(adata, n_latent=10, n_latent_sample=5)
model.train()

# Get representations
shared_latent = model.get_latent_representation()  # Shared across samples
sample_specific = model.get_sample_specific_representation()

# Sample distance matrix
sample_distances = model.get_sample_distances()
```

**Key Parameters**:
- `n_latent`: Dimensionality of shared latent space
- `n_latent_sample`: Dimensionality of sample-specific space
- `sample_key`: Column defining biological samples

**Analysis Workflow**:
```python
# 1. Identify shared cell types across samples
sc.pp.neighbors(adata, use_rep="X_MrVI_shared")
sc.tl.umap(adata)
sc.tl.leiden(adata, key_added="shared_clusters")

# 2. Analyze sample-specific variation
sample_repr = model.get_sample_specific_representation()

# 3. Compare samples
distances = model.get_sample_distances()

# 4. Find sample-enriched genes
de_results = model.differential_expression(
    groupby="sample",
    group1="Disease",
    group2="Healthy"
)
```

**Use Cases**:
- **Multi-donor studies**: Separate donor effects from cell type variation
- **Disease studies**: Identify disease-specific vs. shared biology
- **Time series**: Separate temporal from stable variation
- **Batch + biology**: Disentangle technical and biological variation

## totalVI vs. MultiVI vs. MrVI: When to Use Which?

### totalVI
**Use for**: CITE-seq (RNA + protein, same cells)
- Paired measurements
- Single modality type per feature
- Focus: protein imputation, joint analysis

### MultiVI
**Use for**: Multiple modalities (RNA + ATAC, etc.)
- Paired, unpaired, or mixed
- Different feature types
- Focus: cross-modality integration and imputation

### MrVI
**Use for**: Multi-sample RNA-seq
- Single modality (RNA)
- Multiple biological samples
- Focus: sample-level variation decomposition

## Integration Best Practices

### For CITE-seq (totalVI)
1. **Quality control proteins**: Remove low-quality antibodies
2. **Background subtraction**: Use empirical background prior
3. **Joint clustering**: Use joint latent space, not RNA alone
4. **Validation**: Check known markers in both modalities

### For Multiome/Multi-modal (MultiVI)
1. **Feature filtering**: Filter genes and peaks independently
2. **Balance modalities**: Ensure reasonable representation of each
3. **Modality weights**: Consider if one modality dominates
4. **Imputation validation**: Validate imputed values carefully

### For Multi-sample (MrVI)
1. **Sample definition**: Carefully define biological samples
2. **Sample size**: Need sufficient cells per sample
3. **Covariate handling**: Properly account for batch vs. sample
4. **Interpretation**: Distinguish technical from biological variation

## Complete Example: CITE-seq Analysis with totalVI

```python
import scvi
import scanpy as sc

# 1. Load CITE-seq data
adata = sc.read_h5ad("cite_seq.h5ad")

# 2. QC and filtering
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.highly_variable_genes(adata, n_top_genes=4000)

# Protein QC
protein_counts = adata.obsm["protein_expression"]
# Remove low-quality proteins

# 3. Setup totalVI
scvi.model.TOTALVI.setup_anndata(
    adata,
    layer="counts",
    protein_expression_obsm_key="protein_expression",
    batch_key="batch"
)

# 4. Train
model = scvi.model.TOTALVI(adata, n_latent=20)
model.train(max_epochs=400)

# 5. Extract joint representation
latent = model.get_latent_representation()
adata.obsm["X_totalVI"] = latent

# 6. Clustering on joint space
sc.pp.neighbors(adata, use_rep="X_totalVI")
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)

# 7. Differential expression for both modalities
rna_de = model.differential_expression(
    groupby="leiden",
    group1="0",
    group2="1"
)

protein_de = model.differential_expression(
    groupby="leiden",
    group1="0",
    group2="1",
    protein_expression=True
)

# 8. Save model
model.save("totalvi_model")
```

---

## models-scrna-seq.md

# Single-Cell RNA-seq Models

This document covers core models for analyzing single-cell RNA sequencing data in scvi-tools.

## scVI (Single-Cell Variational Inference)

**Purpose**: Unsupervised analysis, dimensionality reduction, and batch correction for scRNA-seq data.

**Key Features**:
- Deep generative model based on variational autoencoders (VAE)
- Learns low-dimensional latent representations that capture biological variation
- Automatically corrects for batch effects and technical covariates
- Enables normalized gene expression estimation
- Supports differential expression analysis

**When to Use**:
- Initial exploration and dimensionality reduction of scRNA-seq datasets
- Integrating multiple batches or studies
- Generating batch-corrected expression matrices
- Performing probabilistic differential expression analysis

**Basic Usage**:
```python
import scvi

# Setup data
scvi.model.SCVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch"
)

# Train model
model = scvi.model.SCVI(adata, n_latent=30)
model.train()

# Extract results
latent = model.get_latent_representation()
normalized = model.get_normalized_expression()
```

**Key Parameters**:
- `n_latent`: Dimensionality of latent space (default: 10)
- `n_layers`: Number of hidden layers (default: 1)
- `n_hidden`: Number of nodes per hidden layer (default: 128)
- `dropout_rate`: Dropout rate for neural networks (default: 0.1)
- `dispersion`: Gene-specific or cell-specific dispersion ("gene" or "gene-batch")
- `gene_likelihood`: Distribution for data ("zinb", "nb", "poisson")

**Outputs**:
- `get_latent_representation()`: Batch-corrected low-dimensional embeddings
- `get_normalized_expression()`: Denoised, normalized expression values
- `differential_expression()`: Probabilistic DE testing between groups
- `get_feature_correlation_matrix()`: Gene-gene correlation estimates

## scANVI (Single-Cell ANnotation using Variational Inference)

**Purpose**: Semi-supervised cell type annotation and integration using labeled and unlabeled cells.

**Key Features**:
- Extends scVI with cell type labels
- Leverages partially labeled datasets for annotation transfer
- Performs simultaneous batch correction and cell type prediction
- Enables query-to-reference mapping

**When to Use**:
- Annotating new datasets using reference labels
- Transfer learning from well-annotated to unlabeled datasets
- Joint analysis of labeled and unlabeled cells
- Building cell type classifiers with uncertainty quantification

**Basic Usage**:
```python
# Option 1: Train from scratch
scvi.model.SCANVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch",
    labels_key="cell_type",
    unlabeled_category="Unknown"
)
model = scvi.model.SCANVI(adata)
model.train()

# Option 2: Initialize from pretrained scVI
scvi_model = scvi.model.SCVI(adata)
scvi_model.train()
scanvi_model = scvi.model.SCANVI.from_scvi_model(
    scvi_model,
    unlabeled_category="Unknown"
)
scanvi_model.train()

# Predict cell types
predictions = scanvi_model.predict()
```

**Key Parameters**:
- `labels_key`: Column in `adata.obs` containing cell type labels
- `unlabeled_category`: Label for cells without annotations
- All scVI parameters are also available

**Outputs**:
- `predict()`: Cell type predictions for all cells
- `predict_proba()`: Prediction probabilities
- `get_latent_representation()`: Cell type-aware latent space

## AUTOZI

**Purpose**: Automatic identification and modeling of zero-inflated genes in scRNA-seq data.

**Key Features**:
- Distinguishes biological zeros from technical dropout
- Learns which genes exhibit zero-inflation
- Provides gene-specific zero-inflation probabilities
- Improves downstream analysis by accounting for dropout

**When to Use**:
- Detecting which genes are affected by technical dropout
- Improving imputation and normalization for sparse datasets
- Understanding the extent of zero-inflation in your data

**Basic Usage**:
```python
scvi.model.AUTOZI.setup_anndata(adata, layer="counts")
model = scvi.model.AUTOZI(adata)
model.train()

# Get zero-inflation probabilities per gene
zi_probs = model.get_alphas_betas()
```

## VeloVI

**Purpose**: RNA velocity analysis using variational inference.

**Key Features**:
- Joint modeling of spliced and unspliced RNA counts
- Probabilistic estimation of RNA velocity
- Accounts for technical noise and batch effects
- Provides uncertainty quantification for velocity estimates

**When to Use**:
- Inferring cellular dynamics and differentiation trajectories
- Analyzing spliced/unspliced count data
- RNA velocity analysis with batch correction

**Basic Usage**:
```python
import scvelo as scv

# Prepare velocity data
scv.pp.filter_and_normalize(adata)
scv.pp.moments(adata)

# Train VeloVI
scvi.model.VELOVI.setup_anndata(adata, spliced_layer="Ms", unspliced_layer="Mu")
model = scvi.model.VELOVI(adata)
model.train()

# Get velocity estimates
latent_time = model.get_latent_time()
velocities = model.get_velocity()
```

## contrastiveVI

**Purpose**: Isolating perturbation-specific variations from background biological variation.

**Key Features**:
- Separates shared variation (common across conditions) from target-specific variation
- Useful for perturbation studies (drug treatments, genetic perturbations)
- Identifies condition-specific gene programs
- Enables discovery of treatment-specific effects

**When to Use**:
- Analyzing perturbation experiments (drug screens, CRISPR, etc.)
- Identifying genes responding specifically to treatments
- Separating treatment effects from background variation
- Comparing control vs. perturbed conditions

**Basic Usage**:
```python
scvi.model.CONTRASTIVEVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch",
    categorical_covariate_keys=["condition"]  # control vs treated
)

model = scvi.model.CONTRASTIVEVI(
    adata,
    n_latent=10,        # Shared variation
    n_latent_target=5   # Target-specific variation
)
model.train()

# Extract representations
shared = model.get_latent_representation(representation="shared")
target_specific = model.get_latent_representation(representation="target")
```

## CellAssign

**Purpose**: Marker-based cell type annotation using known marker genes.

**Key Features**:
- Uses prior knowledge of marker genes for cell types
- Probabilistic assignment of cells to types
- Handles marker gene overlap and ambiguity
- Provides soft assignments with uncertainty

**When to Use**:
- Annotating cells using known marker genes
- Leveraging existing biological knowledge for classification
- Cases where marker gene lists are available but reference datasets are not

**Basic Usage**:
```python
# Create marker gene matrix (cell types x genes)
marker_gene_mat = pd.DataFrame({
    "CD4 T cells": [1, 1, 0, 0],  # CD3D, CD4, CD8A, CD19
    "CD8 T cells": [1, 0, 1, 0],
    "B cells": [0, 0, 0, 1]
}, index=["CD3D", "CD4", "CD8A", "CD19"])

scvi.model.CELLASSIGN.setup_anndata(adata, layer="counts")
model = scvi.model.CELLASSIGN(adata, marker_gene_mat)
model.train()

predictions = model.predict()
```

## Solo (Doublet Detection)

**Purpose**: Identifying doublets (cells containing two or more cells) in scRNA-seq data.

**Key Features**:
- Semi-supervised doublet detection using scVI embeddings
- Simulates artificial doublets for training
- Provides doublet probability scores
- Can be applied to any scVI model

**When to Use**:
- Quality control of scRNA-seq datasets
- Removing doublets before downstream analysis
- Assessing doublet rates in your data

**Basic Usage**:
```python
# Train scVI model first
scvi.model.SCVI.setup_anndata(adata, layer="counts")
scvi_model = scvi.model.SCVI(adata)
scvi_model.train()

# Train Solo for doublet detection
solo_model = scvi.external.SOLO.from_scvi_model(scvi_model)
solo_model.train()

# Predict doublets
predictions = solo_model.predict()
doublet_scores = predictions["doublet"]
adata.obs["doublet_score"] = doublet_scores
```

## Amortized LDA (Topic Modeling)

**Purpose**: Topic modeling for gene expression using Latent Dirichlet Allocation.

**Key Features**:
- Discovers gene expression programs (topics)
- Amortized variational inference for scalability
- Each cell is a mixture of topics
- Each topic is a distribution over genes

**When to Use**:
- Discovering gene programs or expression modules
- Understanding compositional structure of expression
- Alternative dimensionality reduction approach
- Interpretable decomposition of expression patterns

**Basic Usage**:
```python
scvi.model.AMORTIZEDLDA.setup_anndata(adata, layer="counts")
model = scvi.model.AMORTIZEDLDA(adata, n_topics=10)
model.train()

# Get topic compositions per cell
topic_proportions = model.get_latent_representation()

# Get gene loadings per topic
topic_gene_loadings = model.get_topic_distribution()
```

## Model Selection Guidelines

**Choose scVI when**:
- Starting with unsupervised analysis
- Need batch correction and integration
- Want normalized expression and DE analysis

**Choose scANVI when**:
- Have some labeled cells for training
- Need cell type annotation
- Want to transfer labels from reference to query

**Choose AUTOZI when**:
- Concerned about technical dropout
- Need to identify zero-inflated genes
- Working with very sparse datasets

**Choose VeloVI when**:
- Have spliced/unspliced count data
- Interested in cellular dynamics
- Need RNA velocity with batch correction

**Choose contrastiveVI when**:
- Analyzing perturbation experiments
- Need to separate treatment effects
- Want to identify condition-specific programs

**Choose CellAssign when**:
- Have marker gene lists available
- Want probabilistic marker-based annotation
- No reference dataset available

**Choose Solo when**:
- Need doublet detection
- Already using scVI for analysis
- Want probabilistic doublet scores

---

## models-spatial.md

# Spatial Transcriptomics Models

This document covers models for analyzing spatially-resolved transcriptomics data in scvi-tools.

## DestVI (Deconvolution of Spatial Transcriptomics using Variational Inference)

**Purpose**: Multi-resolution deconvolution of spatial transcriptomics using single-cell reference data.

**Key Features**:
- Estimates cell type proportions at each spatial location
- Uses single-cell RNA-seq reference for deconvolution
- Multi-resolution approach (global and local patterns)
- Accounts for spatial correlation
- Provides uncertainty quantification

**When to Use**:
- Deconvolving Visium or similar spatial transcriptomics
- Have scRNA-seq reference data with cell type labels
- Want to map cell types to spatial locations
- Interested in spatial organization of cell types
- Need probabilistic estimates of cell type abundance

**Data Requirements**:
- **Spatial data**: Visium or similar spot-based measurements (target data)
- **Single-cell reference**: scRNA-seq with cell type annotations
- Both datasets should share genes

**Basic Usage**:
```python
import scvi

# Step 1: Train scVI on single-cell reference
scvi.model.SCVI.setup_anndata(sc_adata, layer="counts")
sc_model = scvi.model.SCVI(sc_adata)
sc_model.train()

# Step 2: Setup spatial data
scvi.model.DESTVI.setup_anndata(
    spatial_adata,
    layer="counts"
)

# Step 3: Train DestVI using reference
model = scvi.model.DESTVI.from_rna_model(
    spatial_adata,
    sc_model,
    cell_type_key="cell_type"  # Cell type labels in reference
)
model.train(max_epochs=2500)

# Step 4: Get cell type proportions
proportions = model.get_proportions()
spatial_adata.obsm["proportions"] = proportions

# Step 5: Get cell type-specific expression
# Expression of genes specific to each cell type at each spot
ct_expression = model.get_scale_for_ct("T cells")
```

**Key Parameters**:
- `amortization`: Amortization strategy ("both", "latent", "proportion")
- `n_latent`: Latent dimensionality (inherited from scVI model)

**Outputs**:
- `get_proportions()`: Cell type proportions at each spot
- `get_scale_for_ct(cell_type)`: Cell type-specific expression patterns
- `get_gamma()`: Proportion-specific gene expression scaling

**Visualization**:
```python
import scanpy as sc
import matplotlib.pyplot as plt

# Visualize specific cell type proportions spatially
sc.pl.spatial(
    spatial_adata,
    color="T cells",  # If proportions added to .obs
    spot_size=150
)

# Or use obsm directly
for ct in cell_types:
    plt.figure()
    sc.pl.spatial(
        spatial_adata,
        color=spatial_adata.obsm["proportions"][ct],
        title=f"{ct} proportions"
    )
```

## Stereoscope

**Purpose**: Cell type deconvolution for spatial transcriptomics using probabilistic modeling.

**Key Features**:
- Reference-based deconvolution
- Probabilistic framework for cell type proportions
- Works with various spatial technologies
- Handles gene selection and normalization

**When to Use**:
- Similar to DestVI but simpler approach
- Deconvolving spatial data with reference
- Faster alternative for basic deconvolution

**Basic Usage**:
```python
scvi.model.STEREOSCOPE.setup_anndata(
    sc_adata,
    labels_key="cell_type",
    layer="counts"
)

# Train on reference
ref_model = scvi.model.STEREOSCOPE(sc_adata)
ref_model.train()

# Setup spatial data
scvi.model.STEREOSCOPE.setup_anndata(spatial_adata, layer="counts")

# Transfer to spatial
spatial_model = scvi.model.STEREOSCOPE.from_reference_model(
    spatial_adata,
    ref_model
)
spatial_model.train()

# Get proportions
proportions = spatial_model.get_proportions()
```

## Tangram

**Purpose**: Spatial mapping and integration of single-cell data to spatial locations.

**Key Features**:
- Maps single cells to spatial coordinates
- Learns optimal transport between single-cell and spatial data
- Gene imputation at spatial locations
- Cell type mapping

**When to Use**:
- Mapping cells from scRNA-seq to spatial locations
- Imputing unmeasured genes in spatial data
- Understanding spatial organization at single-cell resolution
- Integrating scRNA-seq and spatial transcriptomics

**Data Requirements**:
- Single-cell RNA-seq data with annotations
- Spatial transcriptomics data
- Shared genes between modalities

**Basic Usage**:
```python
import tangram as tg

# Map cells to spatial locations
ad_map = tg.map_cells_to_space(
    adata_sc=sc_adata,
    adata_sp=spatial_adata,
    mode="cells",  # or "clusters" for cell type mapping
    density_prior="rna_count_based"
)

# Get mapping matrix (cells × spots)
mapping = ad_map.X

# Project cell annotations to space
tg.project_cell_annotations(
    ad_map,
    spatial_adata,
    annotation="cell_type"
)

# Impute genes in spatial data
genes_to_impute = ["CD3D", "CD8A", "CD4"]
tg.project_genes(ad_map, spatial_adata, genes=genes_to_impute)
```

**Visualization**:
```python
# Visualize cell type mapping
sc.pl.spatial(
    spatial_adata,
    color="cell_type_projected",
    spot_size=100
)
```

## gimVI (Gaussian Identity Multivi for Imputation)

**Purpose**: Cross-modality imputation between spatial and single-cell data.

**Key Features**:
- Joint model of spatial and single-cell data
- Imputes missing genes in spatial data
- Enables cross-dataset queries
- Learns shared representations

**When to Use**:
- Imputing genes not measured in spatial data
- Joint analysis of spatial and single-cell datasets
- Mapping between modalities

**Basic Usage**:
```python
# Combine datasets
combined_adata = sc.concat([sc_adata, spatial_adata])

scvi.model.GIMVI.setup_anndata(
    combined_adata,
    layer="counts"
)

model = scvi.model.GIMVI(combined_adata)
model.train()

# Impute genes in spatial data
imputed = model.get_imputed_values(spatial_indices)
```

## scVIVA (Variation in Variational Autoencoders for Spatial)

**Purpose**: Analyzing cell-environment relationships in spatial data.

**Key Features**:
- Models cellular neighborhoods and environments
- Identifies environment-associated gene expression
- Accounts for spatial correlation structure
- Cell-cell interaction analysis

**When to Use**:
- Understanding how spatial context affects cells
- Identifying niche-specific gene programs
- Cell-cell interaction studies
- Microenvironment analysis

**Data Requirements**:
- Spatial transcriptomics with coordinates
- Cell type annotations (optional)

**Basic Usage**:
```python
scvi.model.SCVIVA.setup_anndata(
    spatial_adata,
    layer="counts",
    spatial_key="spatial"  # Coordinates in .obsm
)

model = scvi.model.SCVIVA(spatial_adata)
model.train()

# Get environment representations
env_latent = model.get_environment_representation()

# Identify environment-associated genes
env_genes = model.get_environment_specific_genes()
```

## ResolVI

**Purpose**: Addressing spatial transcriptomics noise through resolution-aware modeling.

**Key Features**:
- Accounts for spatial resolution effects
- Denoises spatial data
- Multi-scale analysis
- Improves downstream analysis quality

**When to Use**:
- Noisy spatial data
- Multiple spatial resolutions
- Need denoising before analysis
- Improving data quality

**Basic Usage**:
```python
scvi.model.RESOLVI.setup_anndata(
    spatial_adata,
    layer="counts",
    spatial_key="spatial"
)

model = scvi.model.RESOLVI(spatial_adata)
model.train()

# Get denoised expression
denoised = model.get_denoised_expression()
```

## Model Selection for Spatial Transcriptomics

### DestVI
**Choose when**:
- Need detailed deconvolution with reference
- Have high-quality scRNA-seq reference
- Want multi-resolution analysis
- Need uncertainty quantification

**Best for**: Visium, spot-based technologies

### Stereoscope
**Choose when**:
- Need simpler, faster deconvolution
- Basic cell type proportion estimates
- Limited computational resources

**Best for**: Quick deconvolution tasks

### Tangram
**Choose when**:
- Want single-cell resolution mapping
- Need to impute many genes
- Interested in cell positioning
- Optimal transport approach preferred

**Best for**: Detailed spatial mapping

### gimVI
**Choose when**:
- Need bidirectional imputation
- Joint modeling of spatial and single-cell
- Cross-dataset queries

**Best for**: Integration and imputation

### scVIVA
**Choose when**:
- Interested in cellular environments
- Cell-cell interaction analysis
- Neighborhood effects

**Best for**: Microenvironment studies

### ResolVI
**Choose when**:
- Data quality is a concern
- Need denoising
- Multi-scale analysis

**Best for**: Noisy data preprocessing

## Complete Workflow: Spatial Deconvolution with DestVI

```python
import scvi
import scanpy as sc
import squidpy as sq

# ===== Part 1: Prepare single-cell reference =====
# Load and process scRNA-seq reference
sc_adata = sc.read_h5ad("reference_scrna.h5ad")

# QC and filtering
sc.pp.filter_genes(sc_adata, min_cells=10)
sc.pp.highly_variable_genes(sc_adata, n_top_genes=4000)

# Train scVI on reference
scvi.model.SCVI.setup_anndata(
    sc_adata,
    layer="counts",
    batch_key="batch"
)

sc_model = scvi.model.SCVI(sc_adata)
sc_model.train(max_epochs=400)

# ===== Part 2: Load spatial data =====
spatial_adata = sc.read_visium("path/to/visium")
spatial_adata.var_names_make_unique()

# QC spatial data
sc.pp.filter_genes(spatial_adata, min_cells=10)

# ===== Part 3: Run DestVI =====
scvi.model.DESTVI.setup_anndata(
    spatial_adata,
    layer="counts"
)

destvi_model = scvi.model.DESTVI.from_rna_model(
    spatial_adata,
    sc_model,
    cell_type_key="cell_type"
)

destvi_model.train(max_epochs=2500)

# ===== Part 4: Extract results =====
# Get proportions
proportions = destvi_model.get_proportions()
spatial_adata.obsm["proportions"] = proportions

# Add proportions to .obs for easy plotting
for i, ct in enumerate(sc_model.adata.obs["cell_type"].cat.categories):
    spatial_adata.obs[f"prop_{ct}"] = proportions[:, i]

# ===== Part 5: Visualization =====
# Plot specific cell types
cell_types = ["T cells", "B cells", "Macrophages"]

for ct in cell_types:
    sc.pl.spatial(
        spatial_adata,
        color=f"prop_{ct}",
        title=f"{ct} proportions",
        spot_size=150,
        cmap="viridis"
    )

# ===== Part 6: Spatial analysis =====
# Compute spatial neighbors
sq.gr.spatial_neighbors(spatial_adata)

# Spatial autocorrelation of cell types
for ct in cell_types:
    sq.gr.spatial_autocorr(
        spatial_adata,
        attr="obs",
        mode="moran",
        genes=[f"prop_{ct}"]
    )

# ===== Part 7: Save results =====
destvi_model.save("destvi_model")
spatial_adata.write("spatial_deconvolved.h5ad")
```

## Best Practices for Spatial Analysis

1. **Reference quality**: Use high-quality, well-annotated scRNA-seq reference
2. **Gene overlap**: Ensure sufficient shared genes between reference and spatial
3. **Spatial coordinates**: Properly register spatial coordinates in `.obsm["spatial"]`
4. **Validation**: Use known marker genes to validate deconvolution
5. **Visualization**: Always visualize results spatially to check biological plausibility
6. **Cell type granularity**: Consider appropriate cell type resolution
7. **Computational resources**: Spatial models can be memory-intensive
8. **Quality control**: Filter low-quality spots before analysis

---

## models-specialized.md

# Specialized Modality Models

This document covers models for specialized single-cell data modalities in scvi-tools.

## MethylVI / MethylANVI (Methylation Analysis)

**Purpose**: Analysis of single-cell bisulfite sequencing (scBS-seq) data for DNA methylation.

**Key Features**:
- Models methylation patterns at single-cell resolution
- Handles sparsity in methylation data
- Batch correction for methylation experiments
- Label transfer (MethylANVI) for cell type annotation

**When to Use**:
- Analyzing scBS-seq or similar methylation data
- Studying DNA methylation patterns across cell types
- Integrating methylation data across batches
- Cell type annotation based on methylation profiles

**Data Requirements**:
- Methylation count matrices (methylated vs. total reads per CpG site)
- Format: Cells × CpG sites with methylation ratios or counts

### MethylVI (Unsupervised)

**Basic Usage**:
```python
import scvi

# Setup methylation data
scvi.model.METHYLVI.setup_anndata(
    adata,
    layer="methylation_counts",  # Methylation data
    batch_key="batch"
)

model = scvi.model.METHYLVI(adata)
model.train()

# Get latent representation
latent = model.get_latent_representation()

# Get normalized methylation values
normalized_meth = model.get_normalized_methylation()
```

### MethylANVI (Semi-supervised with cell types)

**Basic Usage**:
```python
# Setup with cell type labels
scvi.model.METHYLANVI.setup_anndata(
    adata,
    layer="methylation_counts",
    batch_key="batch",
    labels_key="cell_type",
    unlabeled_category="Unknown"
)

model = scvi.model.METHYLANVI(adata)
model.train()

# Predict cell types
predictions = model.predict()
```

**Key Parameters**:
- `n_latent`: Latent dimensionality
- `region_factors`: Model region-specific effects

**Use Cases**:
- Epigenetic heterogeneity analysis
- Cell type identification via methylation
- Integration with gene expression data (separate analysis)
- Differential methylation analysis

## CytoVI (Flow and Mass Cytometry)

**Purpose**: Batch correction and integration of flow cytometry and mass cytometry (CyTOF) data.

**Key Features**:
- Handles antibody-based protein measurements
- Corrects batch effects in cytometry data
- Enables integration across experiments
- Designed for high-dimensional protein panels

**When to Use**:
- Analyzing flow cytometry or CyTOF data
- Integrating cytometry experiments across batches
- Batch correction for protein panels
- Cross-study cytometry integration

**Data Requirements**:
- Protein expression matrix (cells × proteins)
- Flow cytometry or CyTOF measurements
- Batch/experiment annotations

**Basic Usage**:
```python
scvi.model.CYTOVI.setup_anndata(
    adata,
    protein_expression_obsm_key="protein_expression",
    batch_key="batch"
)

model = scvi.model.CYTOVI(adata)
model.train()

# Get batch-corrected representation
latent = model.get_latent_representation()

# Get normalized protein values
normalized = model.get_normalized_expression()
```

**Key Parameters**:
- `n_latent`: Latent space dimensionality
- `n_layers`: Network depth

**Typical Workflow**:
```python
import scanpy as sc

# 1. Load cytometry data
adata = sc.read_h5ad("cytof_data.h5ad")

# 2. Train CytoVI
scvi.model.CYTOVI.setup_anndata(
    adata,
    protein_expression_obsm_key="protein",
    batch_key="experiment"
)
model = scvi.model.CYTOVI(adata)
model.train()

# 3. Get batch-corrected values
latent = model.get_latent_representation()
adata.obsm["X_CytoVI"] = latent

# 4. Downstream analysis
sc.pp.neighbors(adata, use_rep="X_CytoVI")
sc.tl.umap(adata)
sc.tl.leiden(adata)

# 5. Visualize batch correction
sc.pl.umap(adata, color=["batch", "leiden"])
```

## SysVI (Systems-level Integration)

**Purpose**: Batch effect correction with emphasis on preserving biological variation.

**Key Features**:
- Specialized batch integration approach
- Preserves biological signals while removing technical effects
- Designed for large-scale integration studies

**When to Use**:
- Large-scale multi-batch integration
- Need to preserve subtle biological variation
- Systems-level analysis across many studies

**Basic Usage**:
```python
scvi.model.SYSVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch"
)

model = scvi.model.SYSVI(adata)
model.train()

latent = model.get_latent_representation()
```

## Decipher (Trajectory Inference)

**Purpose**: Trajectory inference and pseudotime analysis for single-cell data.

**Key Features**:
- Learns cellular trajectories and differentiation paths
- Pseudotime estimation
- Accounts for uncertainty in trajectory structure
- Compatible with scVI embeddings

**When to Use**:
- Studying cellular differentiation
- Time-course or developmental datasets
- Understanding cell state transitions
- Identifying branching points in development

**Basic Usage**:
```python
# Typically used after scVI for embeddings
scvi_model = scvi.model.SCVI(adata)
scvi_model.train()

# Decipher for trajectory
scvi.model.DECIPHER.setup_anndata(adata)
decipher_model = scvi.model.DECIPHER(adata, scvi_model)
decipher_model.train()

# Get pseudotime
pseudotime = decipher_model.get_pseudotime()
adata.obs["pseudotime"] = pseudotime
```

**Visualization**:
```python
import scanpy as sc

# Plot pseudotime on UMAP
sc.pl.umap(adata, color="pseudotime", cmap="viridis")

# Gene expression along pseudotime
sc.pl.scatter(adata, x="pseudotime", y="gene_of_interest")
```

## peRegLM (Peak Regulatory Linear Model)

**Purpose**: Linking chromatin accessibility to gene expression for regulatory analysis.

**Key Features**:
- Links ATAC-seq peaks to gene expression
- Identifies regulatory relationships
- Works with paired multiome data

**When to Use**:
- Multiome data (RNA + ATAC from same cells)
- Understanding gene regulation
- Linking peaks to target genes
- Regulatory network construction

**Basic Usage**:
```python
# Requires paired RNA + ATAC data
scvi.model.PEREGLM.setup_anndata(
    multiome_adata,
    rna_layer="counts",
    atac_layer="atac_counts"
)

model = scvi.model.PEREGLM(multiome_adata)
model.train()

# Get peak-gene links
peak_gene_links = model.get_regulatory_links()
```

## Model-Specific Best Practices

### MethylVI/MethylANVI
1. **Sparsity**: Methylation data is inherently sparse; model accounts for this
2. **CpG selection**: Filter CpGs with very low coverage
3. **Biological interpretation**: Consider genomic context (promoters, enhancers)
4. **Integration**: For multi-omics, analyze separately then integrate results

### CytoVI
1. **Protein QC**: Remove low-quality or uninformative proteins
2. **Compensation**: Ensure proper spectral compensation before analysis
3. **Batch design**: Include biological and technical replicates
4. **Controls**: Use control samples to validate batch correction

### SysVI
1. **Sample size**: Designed for large-scale integration
2. **Batch definition**: Carefully define batch structure
3. **Biological validation**: Verify biological signals preserved

### Decipher
1. **Start point**: Define trajectory start cells if known
2. **Branching**: Specify expected number of branches
3. **Validation**: Use known markers to validate pseudotime
4. **Integration**: Works well with scVI embeddings

## Integration with Other Models

Many specialized models work well in combination:

**Methylation + Expression**:
```python
# Analyze separately, then integrate
methylvi_model = scvi.model.METHYLVI(meth_adata)
scvi_model = scvi.model.SCVI(rna_adata)

# Integrate results at analysis level
# E.g., correlate methylation and expression patterns
```

**Cytometry + CITE-seq**:
```python
# CytoVI for flow/CyTOF
cyto_model = scvi.model.CYTOVI(cyto_adata)

# totalVI for CITE-seq
cite_model = scvi.model.TOTALVI(cite_adata)

# Compare protein measurements across platforms
```

**ATAC + RNA (Multiome)**:
```python
# MultiVI for joint analysis
multivi_model = scvi.model.MULTIVI(multiome_adata)

# peRegLM for regulatory links
pereglm_model = scvi.model.PEREGLM(multiome_adata)
```

## Choosing Specialized Models

### Decision Tree

1. **What data modality?**
   - Methylation → MethylVI/MethylANVI
   - Flow/CyTOF → CytoVI
   - Trajectory → Decipher
   - Multi-batch integration → SysVI
   - Regulatory links → peRegLM

2. **Do you have labels?**
   - Yes → MethylANVI (methylation)
   - No → MethylVI (methylation)

3. **What's your main goal?**
   - Batch correction → CytoVI, SysVI
   - Trajectory/pseudotime → Decipher
   - Peak-gene links → peRegLM
   - Methylation patterns → MethylVI/ANVI

## Example: Complete Methylation Analysis

```python
import scvi
import scanpy as sc

# 1. Load methylation data
meth_adata = sc.read_h5ad("methylation_data.h5ad")

# 2. QC: filter low-coverage CpG sites
sc.pp.filter_genes(meth_adata, min_cells=10)

# 3. Setup MethylVI
scvi.model.METHYLVI.setup_anndata(
    meth_adata,
    layer="methylation",
    batch_key="batch"
)

# 4. Train model
model = scvi.model.METHYLVI(meth_adata, n_latent=15)
model.train(max_epochs=400)

# 5. Get latent representation
latent = model.get_latent_representation()
meth_adata.obsm["X_MethylVI"] = latent

# 6. Clustering
sc.pp.neighbors(meth_adata, use_rep="X_MethylVI")
sc.tl.umap(meth_adata)
sc.tl.leiden(meth_adata)

# 7. Differential methylation
dm_results = model.differential_methylation(
    groupby="leiden",
    group1="0",
    group2="1"
)

# 8. Save
model.save("methylvi_model")
meth_adata.write("methylation_analyzed.h5ad")
```

## External Tools Integration

Some specialized models are available as external packages:

**SOLO** (doublet detection):
```python
from scvi.external import SOLO

solo = SOLO.from_scvi_model(scvi_model)
solo.train()
doublets = solo.predict()
```

**scArches** (reference mapping):
```python
from scvi.external import SCARCHES

# For transfer learning and query-to-reference mapping
```

These external tools extend scvi-tools functionality for specific use cases.

## Summary Table

| Model | Data Type | Primary Use | Supervised? |
|-------|-----------|-------------|-------------|
| MethylVI | Methylation | Unsupervised analysis | No |
| MethylANVI | Methylation | Cell type annotation | Semi |
| CytoVI | Cytometry | Batch correction | No |
| SysVI | scRNA-seq | Large-scale integration | No |
| Decipher | scRNA-seq | Trajectory inference | No |
| peRegLM | Multiome | Peak-gene links | No |
| SOLO | scRNA-seq | Doublet detection | Semi |

---

## theoretical-foundations.md

# Theoretical Foundations of scvi-tools

This document explains the mathematical and statistical principles underlying scvi-tools.

## Core Concepts

### Variational Inference

**What is it?**
Variational inference is a technique for approximating complex probability distributions. In single-cell analysis, we want to understand the posterior distribution p(z|x) - the probability of latent variables z given observed data x.

**Why use it?**
- Exact inference is computationally intractable for complex models
- Scales to large datasets (millions of cells)
- Provides uncertainty quantification
- Enables Bayesian reasoning about cell states

**How does it work?**
1. Define a simpler approximate distribution q(z|x) with learnable parameters
2. Minimize the KL divergence between q(z|x) and true posterior p(z|x)
3. Equivalent to maximizing the Evidence Lower Bound (ELBO)

**ELBO Objective**:
```
ELBO = E_q[log p(x|z)] - KL(q(z|x) || p(z))
       ↑                    ↑
  Reconstruction          Regularization
```

- **Reconstruction term**: Model should generate data similar to observed
- **Regularization term**: Latent representation should match prior

### Variational Autoencoders (VAEs)

**Architecture**:
```
x (observed data)
    ↓
[Encoder Neural Network]
    ↓
z (latent representation)
    ↓
[Decoder Neural Network]
    ↓
x̂ (reconstructed data)
```

**Encoder**: Maps cells (x) to latent space (z)
- Learns q(z|x), the approximate posterior
- Parameterized by neural network with learnable weights
- Outputs mean and variance of latent distribution

**Decoder**: Maps latent space (z) back to gene space
- Learns p(x|z), the likelihood
- Generates gene expression from latent representation
- Models count distributions (Negative Binomial, Zero-Inflated NB)

**Reparameterization Trick**:
- Allows backpropagation through stochastic sampling
- Sample z = μ + σ ⊙ ε, where ε ~ N(0,1)
- Enables end-to-end training with gradient descent

### Amortized Inference

**Concept**: Share encoder parameters across all cells.

**Traditional inference**: Learn separate latent variables for each cell
- n_cells × n_latent parameters
- Doesn't scale to large datasets

**Amortized inference**: Learn single encoder for all cells
- Fixed number of parameters regardless of cell count
- Enables fast inference on new cells
- Transfers learned patterns across dataset

**Benefits**:
- Scalable to millions of cells
- Fast inference on query data
- Leverages shared structure across cells
- Enables few-shot learning

## Statistical Modeling

### Count Data Distributions

Single-cell data are counts (integer-valued), requiring appropriate distributions.

#### Negative Binomial (NB)
```
x ~ NB(μ, θ)
```
- **μ (mean)**: Expected expression level
- **θ (dispersion)**: Controls variance
- **Variance**: Var(x) = μ + μ²/θ

**When to use**: Gene expression without zero-inflation
- More flexible than Poisson (allows overdispersion)
- Models technical and biological variation

#### Zero-Inflated Negative Binomial (ZINB)
```
x ~ π·δ₀ + (1-π)·NB(μ, θ)
```
- **π (dropout rate)**: Probability of technical zero
- **δ₀**: Point mass at zero
- **NB(μ, θ)**: Expression when not dropped out

**When to use**: Sparse scRNA-seq data
- Models technical dropout separately from biological zeros
- Better fit for highly sparse data (e.g., 10x data)

#### Poisson
```
x ~ Poisson(μ)
```
- Simplest count distribution
- Mean equals variance: Var(x) = μ

**When to use**: Less common; ATAC-seq fragment counts
- More restrictive than NB
- Faster computation

### Batch Correction Framework

**Problem**: Technical variation confounds biological signal
- Different sequencing runs, protocols, labs
- Must remove technical effects while preserving biology

**scvi-tools approach**:
1. Encode batch as categorical variable s
2. Include s in generative model
3. Latent space z is batch-invariant
4. Decoder conditions on s for batch-specific effects

**Mathematical formulation**:
```
Encoder: q(z|x, s)  - batch-aware encoding
Latent: z           - batch-corrected representation
Decoder: p(x|z, s)  - batch-specific decoding
```

**Key insight**: Batch info flows through decoder, not latent space
- z captures biological variation
- s explains technical variation
- Separable biology and batch effects

### Deep Generative Modeling

**Generative model**: Learns p(x), the data distribution

**Process**:
1. Sample latent variable: z ~ p(z) = N(0, I)
2. Generate expression: x ~ p(x|z)
3. Joint distribution: p(x, z) = p(x|z)p(z)

**Benefits**:
- Generate synthetic cells
- Impute missing values
- Quantify uncertainty
- Perform counterfactual predictions

**Inference network**: Inverts generative process
- Given x, infer z
- q(z|x) approximates true posterior p(z|x)

## Model Architecture Details

### scVI Architecture

**Input**: Gene expression counts x ∈ ℕ^G (G genes)

**Encoder**:
```
h = ReLU(W₁·x + b₁)
μ_z = W₂·h + b₂
log σ²_z = W₃·h + b₃
z ~ N(μ_z, σ²_z)
```

**Latent space**: z ∈ ℝ^d (typically d=10-30)

**Decoder**:
```
h = ReLU(W₄·z + b₄)
μ = softmax(W₅·h + b₅) · library_size
θ = exp(W₆·h + b₆)
π = sigmoid(W₇·h + b₇)  # for ZINB
x ~ ZINB(μ, θ, π)
```

**Loss function (ELBO)**:
```
L = E_q[log p(x|z)] - KL(q(z|x) || N(0,I))
```

### Handling Covariates

**Categorical covariates** (batch, donor, etc.):
- One-hot encoded: s ∈ {0,1}^K
- Concatenate with latent: [z, s]
- Or use conditional layers

**Continuous covariates** (library size, percent_mito):
- Standardize to zero mean, unit variance
- Include in encoder and/or decoder

**Covariate injection strategies**:
- **Concatenation**: [z, s] fed to decoder
- **Deep injection**: s added at multiple layers
- **Conditional batch norm**: Batch-specific normalization

## Advanced Theoretical Concepts

### Transfer Learning (scArches)

**Concept**: Use pretrained model as initialization for new data

**Process**:
1. Train reference model on large dataset
2. Freeze encoder parameters
3. Fine-tune decoder on query data
4. Or fine-tune all with lower learning rate

**Why it works**:
- Encoder learns general cellular representations
- Decoder adapts to query-specific characteristics
- Prevents catastrophic forgetting

**Applications**:
- Query-to-reference mapping
- Few-shot learning for rare cell types
- Rapid analysis of new datasets

### Multi-Resolution Modeling (MrVI)

**Idea**: Separate shared and sample-specific variation

**Latent space decomposition**:
```
z = z_shared + z_sample
```
- **z_shared**: Common across samples
- **z_sample**: Sample-specific effects

**Hierarchical structure**:
```
Sample level: ρ_s ~ N(0, I)
Cell level: z_i ~ N(ρ_{s(i)}, σ²)
```

**Benefits**:
- Disentangle biological sources of variation
- Compare samples at different resolutions
- Identify sample-specific cell states

### Counterfactual Prediction

**Goal**: Predict outcome under different conditions

**Example**: "What would this cell look like if from different batch?"

**Method**:
1. Encode cell to latent: z = Encoder(x, s_original)
2. Decode with new condition: x_new = Decoder(z, s_new)
3. x_new is counterfactual prediction

**Applications**:
- Batch effect assessment
- Predicting treatment response
- In silico perturbation studies

### Posterior Predictive Distribution

**Definition**: Distribution of new data given observed data

```
p(x_new | x_observed) = ∫ p(x_new|z) q(z|x_observed) dz
```

**Estimation**: Sample z from q(z|x), generate x_new from p(x_new|z)

**Uses**:
- Uncertainty quantification
- Robust predictions
- Outlier detection

## Differential Expression Framework

### Bayesian Approach

**Traditional methods**: Compare point estimates
- Wilcoxon, t-test, etc.
- Ignore uncertainty
- Require pseudocounts

**scvi-tools approach**: Compare distributions
- Sample from posterior: μ_A ~ p(μ|x_A), μ_B ~ p(μ|x_B)
- Compute log fold-change: LFC = log(μ_B) - log(μ_A)
- Posterior distribution of LFC quantifies uncertainty

### Bayes Factor

**Definition**: Ratio of posterior odds to prior odds

```
BF = P(H₁|data) / P(H₀|data)
     ─────────────────────────
     P(H₁) / P(H₀)
```

**Interpretation**:
- BF > 3: Moderate evidence for H₁
- BF > 10: Strong evidence
- BF > 100: Decisive evidence

**In scvi-tools**: Used to rank genes by evidence for DE

### False Discovery Proportion (FDP)

**Goal**: Control expected false discovery rate

**Procedure**:
1. For each gene, compute posterior probability of DE
2. Rank genes by evidence (Bayes factor)
3. Select top k genes such that E[FDP] ≤ α

**Advantage over p-values**:
- Fully Bayesian
- Natural for posterior inference
- No arbitrary thresholds

## Implementation Details

### Optimization

**Optimizer**: Adam (adaptive learning rates)
- Default lr = 0.001
- Momentum parameters: β₁=0.9, β₂=0.999

**Training loop**:
1. Sample mini-batch of cells
2. Compute ELBO loss
3. Backpropagate gradients
4. Update parameters with Adam
5. Repeat until convergence

**Convergence criteria**:
- ELBO plateaus on validation set
- Early stopping prevents overfitting
- Typically 200-500 epochs

### Regularization

**KL annealing**: Gradually increase KL weight
- Prevents posterior collapse
- Starts at 0, increases to 1 over epochs

**Dropout**: Random neuron dropping during training
- Default: 0.1 dropout rate
- Prevents overfitting
- Improves generalization

**Weight decay**: L2 regularization on weights
- Prevents large weights
- Improves stability

### Scalability

**Mini-batch training**:
- Process subset of cells per iteration
- Batch size: 64-256 cells
- Enables scaling to millions of cells

**Stochastic optimization**:
- Estimates ELBO on mini-batches
- Unbiased gradient estimates
- Converges to optimal solution

**GPU acceleration**:
- Neural networks naturally parallelize
- Order of magnitude speedup
- Essential for large datasets

## Connections to Other Methods

### vs. PCA
- **PCA**: Linear, deterministic
- **scVI**: Nonlinear, probabilistic
- **Advantage**: scVI captures complex structure, handles counts

### vs. t-SNE/UMAP
- **t-SNE/UMAP**: Visualization-focused
- **scVI**: Full generative model
- **Advantage**: scVI enables downstream tasks (DE, imputation)

### vs. Seurat Integration
- **Seurat**: Anchor-based alignment
- **scVI**: Probabilistic modeling
- **Advantage**: scVI provides uncertainty, works for multiple batches

### vs. Harmony
- **Harmony**: PCA + batch correction
- **scVI**: VAE-based
- **Advantage**: scVI handles counts natively, more flexible

## Mathematical Notation

**Common symbols**:
- x: Observed gene expression (counts)
- z: Latent representation
- θ: Model parameters
- q(z|x): Approximate posterior (encoder)
- p(x|z): Likelihood (decoder)
- p(z): Prior on latent variables
- μ, σ²: Mean and variance
- π: Dropout probability (ZINB)
- θ (in NB): Dispersion parameter
- s: Batch/covariate indicator

## Further Reading

**Key Papers**:
1. Lopez et al. (2018): "Deep generative modeling for single-cell transcriptomics"
2. Xu et al. (2021): "Probabilistic harmonization and annotation of single-cell transcriptomics"
3. Boyeau et al. (2019): "Deep generative models for detecting differential expression in single cells"

**Concepts to explore**:
- Variational inference in machine learning
- Bayesian deep learning
- Information theory (KL divergence, mutual information)
- Generative models (GANs, normalizing flows, diffusion models)
- Probabilistic programming (Pyro, PyTorch)

**Mathematical background**:
- Probability theory and statistics
- Linear algebra and calculus
- Optimization theory
- Information theory

---

## workflows.md

# Common Workflows and Best Practices

This document covers common workflows, best practices, and advanced usage patterns for scvi-tools.

## Standard Analysis Workflow

### 1. Data Loading and Preparation

```python
import scvi
import scanpy as sc
import numpy as np

# Load data (AnnData format required)
adata = sc.read_h5ad("data.h5ad")
# Or load from other formats
# adata = sc.read_10x_mtx("filtered_feature_bc_matrix/")
# adata = sc.read_csv("counts.csv")

# Basic QC metrics
sc.pp.calculate_qc_metrics(adata, inplace=True)
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
```

### 2. Quality Control

```python
# Filter cells
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_cells(adata, max_genes=5000)

# Filter genes
sc.pp.filter_genes(adata, min_cells=3)

# Filter by mitochondrial content
adata = adata[adata.obs['pct_counts_mt'] < 20, :]

# Remove doublets (optional, before training)
sc.external.pp.scrublet(adata)
adata = adata[~adata.obs['predicted_doublet'], :]
```

### 3. Preprocessing for scvi-tools

```python
# IMPORTANT: scvi-tools needs RAW counts
# If you've already normalized, use the raw layer or reload data

# Save raw counts if not already available
if 'counts' not in adata.layers:
    adata.layers['counts'] = adata.X.copy()

# Feature selection (optional but recommended)
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=4000,
    subset=False,  # Keep all genes, just mark HVGs
    batch_key="batch"  # If multiple batches
)

# Filter to HVGs (optional)
# adata = adata[:, adata.var['highly_variable']]
```

### 4. Register Data with scvi-tools

```python
# Setup AnnData for scvi-tools
scvi.model.SCVI.setup_anndata(
    adata,
    layer="counts",  # Use raw counts
    batch_key="batch",  # Technical batches
    categorical_covariate_keys=["donor", "condition"],
    continuous_covariate_keys=["percent_mito", "n_counts"]
)

# Check registration
adata.uns['_scvi']['summary_stats']
```

### 5. Model Training

```python
# Create model
model = scvi.model.SCVI(
    adata,
    n_latent=30,  # Latent dimensions
    n_layers=2,   # Network depth
    n_hidden=128, # Hidden layer size
    dropout_rate=0.1,
    gene_likelihood="zinb"  # zero-inflated negative binomial
)

# Train model
model.train(
    max_epochs=400,
    batch_size=128,
    train_size=0.9,
    early_stopping=True,
    check_val_every_n_epoch=10
)

# View training history
train_history = model.history["elbo_train"]
val_history = model.history["elbo_validation"]
```

### 6. Extract Results

```python
# Get latent representation
latent = model.get_latent_representation()
adata.obsm["X_scVI"] = latent

# Get normalized expression
normalized = model.get_normalized_expression(
    adata,
    library_size=1e4,
    n_samples=25  # Monte Carlo samples
)
adata.layers["scvi_normalized"] = normalized
```

### 7. Downstream Analysis

```python
# Clustering on scVI latent space
sc.pp.neighbors(adata, use_rep="X_scVI", n_neighbors=15)
sc.tl.umap(adata, min_dist=0.3)
sc.tl.leiden(adata, resolution=0.8, key_added="leiden")

# Visualization
sc.pl.umap(adata, color=["leiden", "batch", "cell_type"])

# Differential expression
de_results = model.differential_expression(
    groupby="leiden",
    group1="0",
    group2="1",
    mode="change",
    delta=0.25
)
```

### 8. Model Persistence

```python
# Save model
model_dir = "./scvi_model/"
model.save(model_dir, overwrite=True)

# Save AnnData with results
adata.write("analyzed_data.h5ad")

# Load model later
model = scvi.model.SCVI.load(model_dir, adata=adata)
```

## Hyperparameter Tuning

### Key Hyperparameters

**Architecture**:
- `n_latent`: Latent space dimensionality (10-50)
  - Larger for complex, heterogeneous datasets
  - Smaller for simple datasets or to prevent overfitting
- `n_layers`: Number of hidden layers (1-3)
  - More layers for complex data, but diminishing returns
- `n_hidden`: Nodes per hidden layer (64-256)
  - Scale with dataset size and complexity

**Training**:
- `max_epochs`: Training iterations (200-500)
  - Use early stopping to prevent overfitting
- `batch_size`: Samples per batch (64-256)
  - Larger for big datasets, smaller for limited memory
- `lr`: Learning rate (0.001 default, usually good)

**Model-specific**:
- `gene_likelihood`: Distribution ("zinb", "nb", "poisson")
  - "zinb" for sparse data with zero-inflation
  - "nb" for less sparse data
- `dispersion`: Gene or gene-batch specific
  - "gene" for simple, "gene-batch" for complex batch effects

### Hyperparameter Search Example

```python
from scvi.model import SCVI

# Define search space
latent_dims = [10, 20, 30]
n_layers_options = [1, 2]

best_score = float('-inf')
best_params = None

for n_latent in latent_dims:
    for n_layers in n_layers_options:
        model = SCVI(
            adata,
            n_latent=n_latent,
            n_layers=n_layers
        )
        model.train(max_epochs=200)

        # Evaluate on validation set
        val_elbo = model.history["elbo_validation"][-1]

        if val_elbo > best_score:
            best_score = val_elbo
            best_params = {"n_latent": n_latent, "n_layers": n_layers}

print(f"Best params: {best_params}")
```

### Using Optuna for Hyperparameter Optimization

```python
import optuna

def objective(trial):
    n_latent = trial.suggest_int("n_latent", 10, 50)
    n_layers = trial.suggest_int("n_layers", 1, 3)
    n_hidden = trial.suggest_categorical("n_hidden", [64, 128, 256])

    model = scvi.model.SCVI(
        adata,
        n_latent=n_latent,
        n_layers=n_layers,
        n_hidden=n_hidden
    )

    model.train(max_epochs=200, early_stopping=True)
    return model.history["elbo_validation"][-1]

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=20)

print(f"Best parameters: {study.best_params}")
```

## GPU Acceleration

### Enable GPU Training

```python
# Automatic GPU detection
model = scvi.model.SCVI(adata)
model.train(accelerator="auto")  # Uses GPU if available

# Force GPU
model.train(accelerator="gpu")

# Multi-GPU
model.train(accelerator="gpu", devices=2)

# Check if GPU is being used
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
```

### GPU Memory Management

```python
# Reduce batch size if OOM
model.train(batch_size=64)  # Instead of default 128

# Mixed precision training (saves memory)
model.train(precision=16)

# Clear cache between runs
import torch
torch.cuda.empty_cache()
```

## Batch Integration Strategies

### Strategy 1: Simple Batch Key

```python
# For standard batch correction
scvi.model.SCVI.setup_anndata(adata, batch_key="batch")
model = scvi.model.SCVI(adata)
```

### Strategy 2: Multiple Covariates

```python
# Correct for multiple technical factors
scvi.model.SCVI.setup_anndata(
    adata,
    batch_key="sequencing_batch",
    categorical_covariate_keys=["donor", "tissue"],
    continuous_covariate_keys=["percent_mito"]
)
```

### Strategy 3: Hierarchical Batches

```python
# When batches have hierarchical structure
# E.g., samples within studies
adata.obs["batch_hierarchy"] = (
    adata.obs["study"].astype(str) + "_" +
    adata.obs["sample"].astype(str)
)

scvi.model.SCVI.setup_anndata(adata, batch_key="batch_hierarchy")
```

## Reference Mapping (scArches)

### Training Reference Model

```python
# Train on reference dataset
scvi.model.SCVI.setup_anndata(ref_adata, batch_key="batch")
ref_model = scvi.model.SCVI(ref_adata)
ref_model.train()

# Save reference
ref_model.save("reference_model")
```

### Mapping Query to Reference

```python
# Load reference
ref_model = scvi.model.SCVI.load("reference_model", adata=ref_adata)

# Setup query with same parameters
scvi.model.SCVI.setup_anndata(query_adata, batch_key="batch")

# Transfer learning
query_model = scvi.model.SCVI.load_query_data(
    query_adata,
    "reference_model"
)

# Fine-tune on query (optional)
query_model.train(max_epochs=200)

# Get query embeddings
query_latent = query_model.get_latent_representation()

# Transfer labels using KNN
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=15)
knn.fit(ref_model.get_latent_representation(), ref_adata.obs["cell_type"])
query_adata.obs["predicted_cell_type"] = knn.predict(query_latent)
```

## Model Minification

Reduce model size for faster inference:

```python
# Train full model
model = scvi.model.SCVI(adata)
model.train()

# Minify for deployment
minified = model.minify_adata(adata)

# Save minified version
minified.write("minified_data.h5ad")
model.save("minified_model")

# Load and use (much faster)
mini_model = scvi.model.SCVI.load("minified_model", adata=minified)
```

## Memory-Efficient Data Loading

### Using AnnDataLoader

```python
from scvi.data import AnnDataLoader

# For very large datasets
dataloader = AnnDataLoader(
    adata,
    batch_size=128,
    shuffle=True,
    drop_last=False
)

# Custom training loop (advanced)
for batch in dataloader:
    # Process batch
    pass
```

### Using Backed AnnData

```python
# For data too large for memory
adata = sc.read_h5ad("huge_dataset.h5ad", backed='r')

# scvi-tools works with backed mode
scvi.model.SCVI.setup_anndata(adata)
model = scvi.model.SCVI(adata)
model.train()
```

## Model Interpretation

### Feature Importance with SHAP

```python
import shap

# Get SHAP values for interpretability
explainer = shap.DeepExplainer(model.module, background_data)
shap_values = explainer.shap_values(test_data)

# Visualize
shap.summary_plot(shap_values, feature_names=adata.var_names)
```

### Gene Correlation Analysis

```python
# Get gene-gene correlation matrix
correlation = model.get_feature_correlation_matrix(
    adata,
    transform_batch="batch1"
)

# Visualize top correlated genes
import seaborn as sns
sns.heatmap(correlation[:50, :50], cmap="coolwarm")
```

## Troubleshooting Common Issues

### Issue: NaN Loss During Training

**Causes**:
- Learning rate too high
- Unnormalized input (must use raw counts)
- Data quality issues

**Solutions**:
```python
# Reduce learning rate
model.train(lr=0.0001)

# Check data
assert adata.X.min() >= 0  # No negative values
assert np.isnan(adata.X).sum() == 0  # No NaNs

# Use more stable likelihood
model = scvi.model.SCVI(adata, gene_likelihood="nb")
```

### Issue: Poor Batch Correction

**Solutions**:
```python
# Increase batch effect modeling
model = scvi.model.SCVI(
    adata,
    encode_covariates=True,  # Encode batch in encoder
    deeply_inject_covariates=False
)

# Or try opposite
model = scvi.model.SCVI(adata, deeply_inject_covariates=True)

# Use more latent dimensions
model = scvi.model.SCVI(adata, n_latent=50)
```

### Issue: Model Not Training (ELBO Not Decreasing)

**Solutions**:
```python
# Increase learning rate
model.train(lr=0.005)

# Increase network capacity
model = scvi.model.SCVI(adata, n_hidden=256, n_layers=2)

# Train longer
model.train(max_epochs=500)
```

### Issue: Out of Memory (OOM)

**Solutions**:
```python
# Reduce batch size
model.train(batch_size=64)

# Use mixed precision
model.train(precision=16)

# Reduce model size
model = scvi.model.SCVI(adata, n_latent=10, n_hidden=64)

# Use backed AnnData
adata = sc.read_h5ad("data.h5ad", backed='r')
```

## Performance Benchmarking

```python
import time

# Time training
start = time.time()
model.train(max_epochs=400)
training_time = time.time() - start
print(f"Training time: {training_time:.2f}s")

# Time inference
start = time.time()
latent = model.get_latent_representation()
inference_time = time.time() - start
print(f"Inference time: {inference_time:.2f}s")

# Memory usage
import psutil
import os
process = psutil.Process(os.getpid())
memory_gb = process.memory_info().rss / 1024**3
print(f"Memory usage: {memory_gb:.2f} GB")
```

## Best Practices Summary

1. **Always use raw counts**: Never log-normalize before scvi-tools
2. **Feature selection**: Use highly variable genes for efficiency
3. **Batch correction**: Register all known technical covariates
4. **Early stopping**: Use validation set to prevent overfitting
5. **Model saving**: Always save trained models
6. **GPU usage**: Use GPU for large datasets (>10k cells)
7. **Hyperparameter tuning**: Start with defaults, tune if needed
8. **Validation**: Check batch correction visually (UMAP colored by batch)
9. **Documentation**: Keep track of preprocessing steps
10. **Reproducibility**: Set random seeds (`scvi.settings.seed = 0`)
