## Reference & Query Preparation

_modules: reference-loading, gene-alignment, prepare-query_

```python
import scvi
import scanpy as sc

# Load pre-trained reference model and its AnnData
# (model must have been saved with save_anndata=True)
adata_ref = sc.read_h5ad('reference.h5ad')
scvi.model.SCVI.setup_anndata(adata_ref, layer='counts', batch_key='batch')
ref_model = scvi.model.SCVI.load('reference_model/', adata=adata_ref)

# Load query and subset to the reference gene set
adata_query = sc.read_h5ad('query.h5ad')
adata_query = adata_query[:, adata_ref.var_names].copy()

# Prepare query AnnData against the reference model setup
scvi.model.SCVI.prepare_query_anndata(adata_query, ref_model)
```

## scVI Surgical Mapping

_modules: scvi, surgical-finetuning, latent-embedding_

```python
# Load query into the reference model (creates the surgical fine-tuned model)
query_model = scvi.model.SCVI.load_query_data(adata_query, ref_model)

# Surgical training: weight_decay=0.0 is standard for surgery and prevents reference drift
query_model.train(max_epochs=200, plan_kwargs={'weight_decay': 0.0})

# Shared latent representation
adata_query.obsm['X_scVI'] = query_model.get_latent_representation()
```

## scANVI Label Transfer

_modules: scanvi, label-transfer, semi-supervised_

```python
import scvi
import scanpy as sc

# --- Build reference scANVI from a labeled reference (skip if a saved model exists) ---
adata_ref = sc.read_h5ad('reference_labeled.h5ad')
scvi.model.SCVI.setup_anndata(adata_ref, layer='counts', batch_key='batch')
ref_vae = scvi.model.SCVI(adata_ref, n_latent=30)
ref_vae.train(max_epochs=100)

scvi.model.SCANVI.setup_anndata(
    adata_ref, layer='counts', batch_key='batch',
    labels_key='cell_type', unlabeled_category='Unknown')
ref_scanvi = scvi.model.SCANVI.from_scvi_model(
    ref_vae, labels_key='cell_type', unlabeled_category='Unknown')
ref_scanvi.train(max_epochs=50)
ref_scanvi.save('reference_scanvi/')

# --- Map query data via surgical fine-tuning ---
adata_query = adata_query[:, adata_ref.var_names].copy()
scvi.model.SCANVI.prepare_query_anndata(adata_query, ref_scanvi)
query_scanvi = scvi.model.SCANVI.load_query_data(adata_query, ref_scanvi)
query_scanvi.train(max_epochs=100, plan_kwargs={'weight_decay': 0.0})

# Transfer labels and latent representation
adata_query.obs['predicted_cell_type'] = query_scanvi.predict()
adata_query.obsm['X_scANVI'] = query_scanvi.get_latent_representation()
```

## Prediction Confidence

_modules: confidence, soft-predictions, novelty-flagging_

```python
# Soft prediction probabilities (per-class)
soft_predictions = query_scanvi.predict(soft=True)
adata_query.obs['prediction_confidence'] = soft_predictions.max(axis=1)

# Flag low-confidence predictions (confidence < 0.5 -> possible novel type / poor mapping)
low_conf = adata_query.obs['prediction_confidence'] < 0.5
print(f'Low confidence predictions: {low_conf.sum()} ({low_conf.mean():.1%})')
```

## Joint Embedding Visualization

_modules: umap, visualization, integration-assessment_

```python
import scanpy as sc

# Combine reference and query for visualization
adata_combined = adata_ref.concatenate(
    adata_query, batch_key='dataset', batch_categories=['reference', 'query'])

# Neighbors + UMAP from the shared latent space
sc.pp.neighbors(adata_combined, use_rep='X_scVI')
sc.tl.umap(adata_combined)
sc.pl.umap(adata_combined, color=['dataset', 'cell_type'], save='_transfer.png')
```
