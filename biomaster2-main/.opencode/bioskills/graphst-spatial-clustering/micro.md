## Installation & Environment Setup

_modules: installation, conda, r-mclust_

```bash
# 1. Create a Python 3.8 conda environment
conda create -n graphst python=3.8 -y
conda activate graphst

# 2. PyTorch >= 1.8 with CUDA (example: CUDA 11.1). Use CPU-only build if no GPU.
conda install pytorch==1.8.0 torchvision==0.9.0 cudatoolkit=11.1 -c pytorch -y

# 3. Core scientific stack (pin versions known to work with GraphST)
pip install numpy==1.22.3 pandas==1.4.2 scipy==1.8.1 scikit-learn==1.1.1
pip install scanpy==1.9.1 anndata==0.8.0 matplotlib==3.4.2 tqdm==4.64.0
pip install POT            # 'ot' module, used for spatial distance matrices

# 4. R + rpy2 + mclust (REQUIRED for the default 'mclust' clustering method)
conda install -c conda-forge r-base=4.0 rpy2=3.4.1 -y
R -e 'install.packages("mclust", repos="https://cloud.r-project.org")'

# 5. Install GraphST
pip install GraphST
# Alternative (from source, latest main):
#   git clone https://github.com/JinmiaoChenLab/GraphST.git
#   cd GraphST && pip install .

# 6. Sanity check
python -c "import GraphST, scanpy, torch, rpy2; print('GraphST ready')"
```

## Data Loading & Preprocessing

_modules: data-loading, preprocessing, hvg, normalization_

```python
import scanpy as sc
import GraphST

# --- 10X Visium ---
# 'path' must contain filtered_feature_bc_matrix.h5 and a spatial/ subfolder
# (tissue_positions_list.csv / tissue_positions.csv, scalefactors_json.json).
adata = sc.read_visium(
    path='path/to/visium_sample',
    count_file='filtered_feature_bc_matrix.h5',
    load_images=True,
)
adata.var_names_make_unique()

# adata.obsm['spatial'] is created by sc.read_visium and is REQUIRED by GraphST.
# Verify it exists:
assert 'spatial' in adata.obsm, "adata.obsm['spatial'] is missing; GraphST needs spot coordinates"

# Optional QC before running GraphST
adata.var['mt'] = adata.var_names.str.startswith('mt-')  # 'MT-' for human
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
# (optionally filter spots/genes here; keep raw counts in adata.X for HVG selection)

# --- Stereo-seq / Slide-seq (non-Visium) ---
# Build AnnData manually and ALWAYS store coordinates in adata.obsm['spatial']:
#   adata = sc.AnnData(X=counts)            # spots x genes, raw counts recommended
#   adata.obsm['spatial'] = coords_array    # shape (n_spots, 2), same order as adata.obs_names
# Then pass datatype='Stereo' or datatype='Slide' to the GraphST constructor (next step).

# NOTE: do NOT pre-run normalize/log1p yourself unless you also set adata.var['highly_variable'].
# GraphST's constructor calls preprocess() automatically, which performs:
#   sc.pp.highly_variable_genes(flavor='seurat_v3', n_top_genes=3000)
#   sc.pp.normalize_total(target_sum=1e4) -> sc.pp.log1p -> sc.pp.scale(zero_center=False, max_value=10)
```

## Graph Construction & Representation Learning

_modules: graph-construction, representation-learning, gnn, contrastive-learning_

```python
import torch
import GraphST

# Use GPU if available, otherwise CPU
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# Instantiate GraphST. The constructor auto-runs preprocess(), construct_interaction(),
# add_contrastive_label() and get_feature() if the corresponding keys are absent.
graphst = GraphST.GraphST(
    adata,
    device=device,
    datatype='10X',        # '10X' (Visium) | 'Stereo' | 'Slide'
    epochs=600,            # training epochs (default 600)
    learning_rate=0.001,   # Adam learning rate for ST representation learning
    dim_output=64,         # dimension of the learned spot embedding
    random_seed=41,        # fixes torch/numpy/RNG for reproducibility
    alpha=10,              # weight of the reconstruction loss
    beta=1,                # weight of the contrastive loss
    weight_decay=0.00,
    deconvolution=False,   # keep False for plain clustering
)

# Train: learns spot representations and stores them in adata.obsm['emb']
adata = graphst.train()
print('Learned embedding shape:', adata.obsm['emb'].shape)
```

## Spatial Clustering & Refinement

_modules: clustering, mclust, leiden, louvain, refinement_

```python
from GraphST.utils import clustering

# Cluster learned embeddings into spatial domains.
# clustering() runs PCA(n_components=20) on adata.obsm['emb'] -> adata.obsm['emb_pca'],
# then applies the chosen method and writes results to adata.obs['domain'].
clustering(
    adata,
    n_clusters=7,          # target number of spatial domains
    method='mclust',       # 'mclust' (needs R+mclust) | 'leiden' | 'louvain'
    key='emb',             # representation key in adata.obsm to cluster on
    refinement=True,       # spatial label smoothing using nearest spots
    radius=50,             # number of spatial neighbors used in refinement
)

# --- Leiden / Louvain alternative ---
# Resolution is auto-searched to hit n_clusters exactly:
# clustering(
#     adata,
#     n_clusters=7,
#     method='leiden',     # or 'louvain'
#     start=0.1, end=3.0, increment=0.01,   # resolution search range/step
#     refinement=True,
#     radius=50,
# )

print(adata.obs['domain'].value_counts())
```

## Visualization & Evaluation

_modules: visualization, umap, ari_

```python
import scanpy as sc
import matplotlib.pyplot as plt
from sklearn import metrics

# 1. Spatial map of predicted domains overlaid on the tissue image (Visium)
sc.pl.spatial(adata, color='domain', img_key='hires', spot_size=50, show=True)

# 2. UMAP of the learned embedding, colored by domain
sc.pp.neighbors(adata, use_rep='emb', n_neighbors=50)
sc.tl.umap(adata)
sc.pl.umap(adata, color='domain', show=True)

# 3. Quantitative evaluation against ground-truth annotations (if available)
if 'ground_truth' in adata.obs.columns:
    # drop spots without a ground-truth label before scoring
    valid = adata.obs.dropna(subset=['ground_truth'])
    ari = metrics.adjusted_rand_score(valid['ground_truth'], valid['domain'])
    print(f'ARI: {ari:.4f}')
else:
    print('No ground_truth in adata.obs; skipping ARI.')

# 4. Save results
adata.write('graphst_clustered.h5ad')
```
