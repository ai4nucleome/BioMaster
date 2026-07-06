## Environment Setup and Data Preparation

_modules: setup, environment, databases, data-loading_

```bash
# Dedicated environment (pySCENIC tested on Python 3.10)
conda create -n scenic python=3.10
conda activate scenic
pip install pyscenic loompy

# Human hg38 ranking databases (large, ~1.5 GB each; mc9nr = motif collection v9, non-redundant)
wget https://resources.aertslab.org/cistarget/databases/homo_sapiens/hg38/refseq_r80/mc9nr/gene_based/hg38__refseq-r80__10kb_up_and_down_tss.mc9nr.genes_vs_motifs.rankings.feather

# Motif-to-TF annotations
wget https://resources.aertslab.org/cistarget/motif2tf/motifs-v9-nr.hgnc-m0.001-o0.0.tbl
```

```python
import loompy
import pandas as pd
from pyscenic.utils import load_tf_names

# Load expression matrix from loom (rows = cells, columns = genes after transpose)
ds = loompy.connect('filtered.loom')
expr_matrix = pd.DataFrame(ds[:, :], index=ds.ra.Gene, columns=ds.ca.CellID).T
ds.close()

# Load species-appropriate TF list (human or mouse)
tf_names = load_tf_names('allTFs_hg38.txt')
```

## GRN Inference with GRNBoost2

_modules: grn, grnboost2, arboreto, coexpression_

```bash
# Recommended: bundled multiprocessing script (avoids dask >= 2.0 issues)
python arboreto_with_multiprocessing.py \
    filtered.loom \
    allTFs_hg38.txt \
    --method grnboost2 \
    --output adj.tsv \
    --num_workers 8 \
    --seed 42

# CLI alternative
pyscenic grn filtered.loom allTFs_hg38.txt -o adj.tsv --num_workers 8
```

```python
# Python API (only if dask < 2.0)
from arboreto.algo import grnboost2

adjacencies = grnboost2(expr_matrix, tf_names=tf_names, verbose=True)
adjacencies.to_csv('adj.tsv', sep='\t', index=False)
```

## Regulon Pruning with cisTarget

_modules: pruning, cistarget, motif-enrichment, regulons_

```python
import glob, pickle
import pandas as pd
from pyscenic.prune import prune2df, df2regulons
from ctxcore.rnkdb import FeatherRankingDatabase

# Load ranking databases and motif annotations
db_fnames = glob.glob('*.genes_vs_motifs.rankings.feather')
dbs = [FeatherRankingDatabase(fname) for fname in db_fnames]
motif_annotations_fname = 'motifs-v9-nr.hgnc-m0.001-o0.0.tbl'

# Load adjacencies from Step 2
adjacencies = pd.read_csv('adj.tsv', sep='\t')

# Prune: keep only TF-target links supported by cis-regulatory motifs
df = prune2df(dbs, adjacencies, motif_annotations_fname)
regulons = df2regulons(df)

with open('regulons.pkl', 'wb') as f:
    pickle.dump(regulons, f)

print(f'Found {len(regulons)} regulons')
for reg in sorted(regulons, key=lambda r: -len(r))[:10]:
    print(f'  {reg.name}: {len(reg)} targets')
```

```bash
# CLI alternative
pyscenic ctx adj.tsv \
    hg38__refseq-r80__10kb_up_and_down_tss.mc9nr.genes_vs_motifs.rankings.feather \
    --annotations_fname motifs-v9-nr.hgnc-m0.001-o0.0.tbl \
    --expression_mtx_fname filtered.loom \
    --output reg.csv \
    --num_workers 8
```

## AUCell Activity Scoring

_modules: aucell, activity-scoring, auc-matrix_

```python
import pickle
import pandas as pd
import loompy
from pyscenic.aucell import aucell

# Reload expression matrix and regulons
ds = loompy.connect('filtered.loom')
expr_matrix = pd.DataFrame(ds[:, :], index=ds.ra.Gene, columns=ds.ca.CellID).T
ds.close()

with open('regulons.pkl', 'rb') as f:
    regulons = pickle.load(f)

# Score regulon activity per cell
# auc_threshold: fraction of ranked genes to consider (default 0.05 = top 5%)
auc_mtx = aucell(expr_matrix, regulons, auc_threshold=0.05, num_workers=8)
auc_mtx.to_csv('auc_matrix.csv')
print(f'Scored {auc_mtx.shape[1]} regulons across {auc_mtx.shape[0]} cells')
```

```bash
# CLI alternative
pyscenic aucell filtered.loom reg.csv \
    --output scenic_output.loom \
    --num_workers 8
```

## Interpretation and Visualization

_modules: rss, binarization, visualization, umap, heatmap_

```python
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt
import seaborn as sns
from pyscenic.rss import regulon_specificity_scores
from pyscenic.binarization import binarize

# Cell-type labels (from prior clustering/annotation)
cell_types = pd.read_csv('cell_types.csv', index_col=0)['cell_type']

# Regulon Specificity Scores: regulons enriched per cell type
rss = regulon_specificity_scores(auc_mtx, cell_types)
for ct in rss.columns:
    top_regs = rss[ct].sort_values(ascending=False).head(5)
    print(f'\n{ct}:')
    for reg, score in top_regs.items():
        print(f'  {reg}: {score:.3f}')

# Binarize AUC scores (on/off per cell)
binary_mtx, thresholds = binarize(auc_mtx)
cluster_activity = binary_mtx.groupby(cell_types).mean()

# Regulon activity on UMAP
adata = sc.read_h5ad('clustered.h5ad')
adata.obsm['X_aucell'] = auc_mtx.loc[adata.obs_names].values
sc.pl.umap(adata, color=['CEBPB(+)', 'SPI1(+)', 'PAX5(+)'], cmap='viridis')

# Heatmap of top regulons per cell type
top_regulons = rss.apply(lambda x: x.nlargest(3).index.tolist()).explode().unique()
sns.clustermap(auc_mtx[top_regulons].groupby(cell_types).mean().T,
               cmap='viridis', figsize=(10, 8), z_score=0)
plt.savefig('regulon_heatmap.pdf', bbox_inches='tight')
```
