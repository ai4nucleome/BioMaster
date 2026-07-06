## Input Preparation

_modules: input-loading, version-check_

```python
# Python: load processed AnnData (already normalized + clustered)
import scanpy as sc
adata = sc.read_h5ad('adata_processed.h5ad')
```
```r
# R: load processed Seurat object
library(Seurat)
seurat_obj <- readRDS('seurat_processed.rds')
```
```python
# Version compatibility check (reference examples: pandas 2.2+, scanpy 1.10+, scikit-learn 1.4+)
# Python:  pip show <package>  ->  help(module.function)  to verify signatures
# R:       packageVersion('<pkg>')  ->  ?function_name
# On ImportError / AttributeError / TypeError, introspect the installed API and adapt.
```

## Reference-Based Annotation

_modules: celltypist, singler, azimuth, reference-mapping_

```python
# CellTypist (Python): pre-trained model with majority voting
import celltypist
import scanpy as sc

adata = sc.read_h5ad('adata_processed.h5ad')
celltypist.models.models_description()
celltypist.models.download_models(model='Immune_All_Low.pkl')
model = celltypist.models.Model.load(model='Immune_All_Low.pkl')

predictions = celltypist.annotate(adata, model=model, majority_voting=True)
adata = predictions.to_adata()
adata.obs['cell_type_celltypist'] = adata.obs['majority_voting']
adata.obs['cell_type_confidence'] = adata.obs['conf_score']
sc.pl.umap(adata, color=['cell_type_celltypist', 'conf_score'])
```
```r
# SingleR (R): correlation-based annotation against curated references
library(SingleR); library(celldex); library(Seurat); library(SingleCellExperiment)

sce <- as.SingleCellExperiment(seurat_obj)
ref <- celldex::HumanPrimaryCellAtlasData()
# Alternatives: BlueprintEncodeData(), MonacoImmuneData(), ImmGenData() (mouse)

pred <- SingleR(test = sce, ref = ref, labels = ref$label.main, de.method = 'wilcox')
seurat_obj$SingleR_labels  <- pred$labels
seurat_obj$SingleR_pruned  <- pred$pruned.labels
plotScoreHeatmap(pred)
plotDeltaDistribution(pred)

# Fine-grained labels
pred_fine <- SingleR(test = sce, ref = ref, labels = ref$label.fine)

# Combine multiple references
ref1 <- celldex::BlueprintEncodeData()
ref2 <- celldex::MonacoImmuneData()
pred_combined <- SingleR(test = sce, ref = list(BP = ref1, Monaco = ref2),
                         labels = list(ref1$label.main, ref2$label.main))
```
```r
# Azimuth (R/Seurat): map query onto a pre-built reference atlas
library(Seurat); library(Azimuth)

seurat_obj <- RunAzimuth(seurat_obj, reference = 'pbmcref')
# Available references: pbmcref, bonemarrowref, lungref, etc.
seurat_obj$azimuth_labels <- seurat_obj$predicted.celltype.l2
seurat_obj$azimuth_score  <- seurat_obj$predicted.celltype.l2.score

DimPlot(seurat_obj, group.by = 'azimuth_labels', label = TRUE) + NoLegend()
FeaturePlot(seurat_obj, features = 'predicted.celltype.l2.score')
```

## Custom Model Annotation

_modules: celltypist-train, scpred, custom-model_

```python
# CellTypist: train a custom model on labeled reference data
import celltypist

new_model = celltypist.train(adata_reference, labels='cell_type', n_jobs=10,
                             feature_selection=True, use_SGD=True)
new_model.write('custom_model.pkl')

predictions = celltypist.annotate(adata_query, model='custom_model.pkl')
```
```r
# scPred (R): PCA-feature SVM/RF classifier trained on a labeled reference
library(scPred); library(Seurat)

reference <- readRDS('reference_seurat.rds')
reference <- getFeatureSpace(reference, 'cell_type')
reference <- trainModel(reference)

get_probabilities(reference)
get_scpred(reference)
plot_probabilities(reference)

query <- readRDS('query_seurat.rds')
query <- scPredict(query, reference)
query$scpred_prediction
query$scpred_max
```

## Confidence Filtering

_modules: confidence-filtering, quality-control_

```python
# CellTypist: filter low-confidence cells
high_conf = adata[adata.obs['conf_score'] > 0.5].copy()
adata.obs['annotation_uncertain'] = adata.obs['conf_score'] < 0.3
```
```r
# SingleR: use pruned labels (low-quality calls set to NA)
seurat_obj$final_labels <- ifelse(is.na(pred$pruned.labels), 'Unknown', pred$labels)

# Azimuth: filter by prediction score
seurat_obj$high_conf_labels <- ifelse(seurat_obj$predicted.celltype.l2.score > 0.7,
                                      seurat_obj$predicted.celltype.l2, 'Low_confidence')
```

## Consensus Annotation

_modules: consensus, majority-voting_

```r
# Combine predictions from multiple tools via majority voting
annotations <- data.frame(
    SingleR    = seurat_obj$SingleR_labels,
    Azimuth    = seurat_obj$azimuth_labels,
    CellTypist = seurat_obj$celltypist_labels
)

get_consensus <- function(x) {
    tbl <- table(x)
    if (max(tbl) >= 2) names(which.max(tbl)) else 'Ambiguous'
}
seurat_obj$consensus_label <- apply(annotations, 1, get_consensus)
```

## Validation & Comparison

_modules: validation, ari, nmi, marker-genes_

```python
# Quantitative agreement between annotation sets
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

ari = adjusted_rand_score(adata.obs['manual_annotation'], adata.obs['celltypist'])
nmi = normalized_mutual_info_score(adata.obs['manual_annotation'], adata.obs['celltypist'])

# Confusion matrix
pd.crosstab(adata.obs['manual_annotation'], adata.obs['celltypist'])
```
```r
# Validate predictions against canonical marker genes
canonical_markers <- list(
    T_cell   = c('CD3D', 'CD3E', 'CD4', 'CD8A'),
    B_cell   = c('CD19', 'MS4A1', 'CD79A'),
    Monocyte = c('CD14', 'LYZ', 'S100A8'),
    NK       = c('NKG7', 'GNLY', 'NCAM1')
)

DotPlot(seurat_obj, features = unlist(canonical_markers), group.by = 'predicted_labels') +
    RotatedAxis()
```
