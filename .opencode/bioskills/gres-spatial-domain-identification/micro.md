## Installation & Resource Setup

_modules: installation, environment-setup_

```bash
# Clone the repository
git clone https://github.com/ai4nucleome/GreS.git
cd GreS

# Create and activate a Python 3.9+ environment (example with conda)
conda create -n gres python=3.9 -y
conda activate gres

# Install dependencies (Python 3.9+, PyTorch 1.13+)
pip install -r environment/requirements_sc.txt

# Download pretrained gene embeddings + vocabulary from Hugging Face
# Dataset repo: https://huggingface.co/datasets/ylu99/Gres
mkdir -p embedding/text_embedd_large
huggingface-cli download ylu99/Gres \
    pretrained_gene_embeddings.pt vocab.json \
    --repo-type dataset \
    --local-dir embedding/text_embedd_large
```

Expected layout after setup:
```
GreS/
└── embedding/
    └── text_embedd_large/
        ├── pretrained_gene_embeddings.pt
        └── vocab.json
```

## Data Preparation

_modules: data-preparation, visium_

```bash
# Each dataset lives under data/raw_h5ad/<dataset_id>/
# Example: 10x Visium DLPFC sample 151672
mkdir -p data/raw_h5ad/151672
```

Required files for 10x Visium:
```
data/raw_h5ad/151672/
├── filtered_feature_bc_matrix.h5   # raw gene expression counts
├── spatial/                        # tissue positions, scale factors, images
└── metadata.tsv                    # per-spot annotations (label column)
```

Alternative: a pre-built AnnData `.h5ad` is also accepted.
```python
import anndata as ad
adata = ad.read_h5ad('data/raw_h5ad/151672/data.h5ad')
# Must contain:
#   adata.X                 -> raw integer counts (N_spots x N_genes)
#   adata.obsm['spatial']   -> spatial coordinates (N_spots x 2)
#   a label column in adata.obs (e.g. 'layer_guess_reordered')
```

## Data Preprocessing

_modules: preprocessing, scanpy, hvg, normalization, spatial-graph_

```bash
# Build graph-augmented data.h5ad from raw data.
# Implements the Scanpy preprocessing pipeline:
#   - filter genes expressed in < 100 spots
#   - select top 3000 HVGs (Seurat v3 dispersion method)
#   - normalize to 1e4 counts/spot, log-transform, scale (clip at 10)
#   - retain raw counts for the ZINB loss
#   - build spatial neighborhood graph from coordinates
python preprocess/generate_data.py \
    --dataset_id 151672 \
    --label_column layer_guess_reordered
```

Arguments:

| Argument | Description | Default |
|---|---|---|
| `--dataset_id` | Dataset ID; locates input and names output | (required) |
| `--label_column` | Label column in metadata.tsv (DLPFC uses `layer_guess_reordered`) | `ground_truth` |

Output: graph-augmented AnnData written under `data/generated/`.

## Generate Semantic Embeddings

_modules: semantic-embeddings, grn, nichenet, gene-semantics_

```bash
# Build per-spot semantic embeddings from data.h5ad + pretrained gene embeddings.
# Refines gene semantics via NicheNet GRN propagation (alpha_grn = 0.2),
# then aggregates into spot-level descriptors weighted by expression.
python preprocess/generate_raw_gene_concat_spot_embedding.py \
    --dataset_id 151672 \
    --embedding embedding/text_embedd_large/pretrained_gene_embeddings.pt \
    --vocab embedding/text_embedd_large/vocab.json
```

Output written to `data/npys_grn_raw_concat/`:
- `embeddings_<dataset_id>.npy` — spot semantic embeddings used during training
- `embeddings_<dataset_id>_attribution.npz` — gene attribution per spot
- `embeddings_<dataset_id>_stats.json` — coverage statistics

## Training & Clustering

_modules: training, gcn, zinb, fusion, k-means, clustering_

```bash
# Train GreS end-to-end and cluster spots.
# Hyperparameters are read from config/<config_name>.ini (default: DLPFC).
python tools/train.py --dataset_id 151672
```

Key hyperparameters (config ini / paper defaults):
- GCN encoder: hidden dim 256, output dim 128, two-layer GCN per view
- GRN propagation weight: `alpha_grn = 0.2`
- Loss weights: `lambda_zinb = 1.0`, `lambda_reg = 0.1`, `lambda_dicr = 0.1`
- Optimizer: Adam
- Number of clusters (k-means): set to the ground-truth count for benchmarking, or a user-defined value in real applications
- Graph neighbor count `k`: shared between spatial and feature graphs

To run with an explicit config:
```bash
python tools/train.py --dataset_id 151672 --config_name DLPFC
```

## Output & Evaluation

_modules: output, evaluation, ari, nmi, visualization_

```python
import anndata as ad
import scanpy as sc
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score,
    fowlkes_mallows_score,
)

# Load results (also saved as <dataset_id>_clusters.png by train.py)
adata = ad.read_h5ad('data/results/151672/151672.h5ad')
labels = adata.obs['idx']                 # predicted spatial domain labels
print(adata.obs['idx'].value_counts())

# Spatial cluster plot
sc.pl.spatial(adata, color='idx', spot_size=50)

# Quantitative evaluation vs. ground truth (if available)
if 'layer_guess_reordered' in adata.obs:
    gt = adata.obs['layer_guess_reordered']
    ari = adjusted_rand_score(gt, labels)
    nmi = normalized_mutual_info_score(gt, labels)
    fmi = fowlkes_mallows_score(gt, labels)
    print(f'ARI={ari:.4f}  NMI={nmi:.4f}  FMI={fmi:.4f}')

# UMAP of the learned embedding to inspect domain separation.
# (Check the output h5ad for the exact embedding key; re-extract from the
# trained model if it is not stored in adata.obsm.)
# sc.pp.neighbors(adata, use_rep=<embedding_key>)
# sc.tl.umap(adata)
# sc.pl.umap(adata, color='idx')
```
