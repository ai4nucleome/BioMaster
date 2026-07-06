## Validate Annotations

_modules: qc, annotation-validation_

```python
import scanpy as sc
import pandas as pd

# Load annotated AnnData object
adata = sc.read_h5ad('path/to/annotated_object.h5ad')

# Check cell type label distribution
print(adata.obs['cell_type'].value_counts())

# Verify marker gene expression per cluster
sc.tl.rank_genes_groups(adata, groupby='cell_type', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=5)

# Confirm no missing or ambiguous labels
assert adata.obs['cell_type'].notna().all(), 'Missing cell type labels detected'
```

## Load Ligand-Receptor Resource

_modules: ligand-receptor, database_

```python
import liana as li

# Load OmniPath L-R resource (human default)
lr_resource = li.resource.select_resource()
print(f'Loaded {lr_resource.shape[0]} L-R interactions')

# Optionally filter by organism
lr_resource_mouse = li.resource.select_resource(organism='mouse')

# Inspect columns
print(lr_resource.columns.tolist())
# Expected: ['ligand', 'receptor', 'source', 'score', ...]
```

## Run Interaction Scoring

_modules: interaction-scoring, liana, permutation-test_

```python
import liana as li

# Run LIANA's consensus method (aggregates multiple scoring methods)
li.mt.rank_aggregate(
    adata,
    groupby='cell_type',
    resource_name='consensus',
    expr_prop=0.1,          # min fraction of cells expressing
    min_cells=10,           # min cells per group
    n_perms=1000,           # permutations for significance
    seed=42
)

# Access results
interactions = adata.uns['liana_res']
print(interactions.head())

# Filter significant interactions
significant = interactions[interactions['pvalue'] < 0.05]
print(f'Significant interactions: {significant.shape[0]}')
```

## Aggregate and Summarize

_modules: aggregation, summarization, sender-receiver_

```python
import pandas as pd

# Load interaction results
interactions = adata.uns['liana_res']

# Summarize outgoing signals per cell type (sender)
sender_summary = interactions.groupby('source')['magnitude'].sum().sort_values(ascending=False)
print('Top senders:\n', sender_summary.head())

# Summarize incoming signals per cell type (receiver)
receiver_summary = interactions.groupby('target')['magnitude'].sum().sort_values(ascending=False)
print('Top receivers:\n', receiver_summary.head())

# Build sender-receiver matrix
sr_matrix = interactions.pivot_table(
    index='source', columns='target',
    values='magnitude', aggfunc='sum', fill_value=0
)
print(sr_matrix)

# Optionally compare conditions
# if 'condition' in adata.obs:
#     li.mt.rank_aggregate(adata, groupby='cell_type', condition='condition')
```

## Visualize and Report Caveats

_modules: visualization, interpretation, caveats_

```python
import liana as li
import matplotlib.pyplot as plt

# Heatmap of interaction strength between cell types
li.pl.heatmap(
    adata,
    label='magnitude',
    source_title='Sender',
    target_title='Receiver',
    figsize=(8, 6)
)
plt.savefig('figures/communication_heatmap.png', dpi=150, bbox_inches='tight')

# Chord diagram (requires circos-style plotting)
li.pl.chordplot(
    adata,
    label='magnitude',
    figsize=(10, 10)
)
plt.savefig('figures/communication_chord.png', dpi=150, bbox_inches='tight')

# Network plot
li.pl.network(
    adata,
    label='magnitude',
    figsize=(12, 12)
)
plt.savefig('figures/communication_network.png', dpi=150, bbox_inches='tight')

# Save interaction tables
interactions = adata.uns['liana_res']
interactions.to_csv('results/interaction_table.csv', index=False)

# Report caveats
print('CAVEAT: All inferred interactions are hypothesis-generating.')
print('CAVEAT: Expression correlation does not equal validated signaling.')
print('CAVEAT: Dense uninterpretable networks should be avoided.')
```
