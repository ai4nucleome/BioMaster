## Barcode Processing & Character Matrix Construction

_modules: barcode-calling, allele-filtering, character-matrix_

```python
import cassiopeia as cas

# --- (1) CRISPR barcodes from BAM alignment ---
barcodes = cas.pp.call_alleles(
    alignment_file='aligned_barcodes.bam',
    reference='barcode_reference.fa',
    min_base_quality=20,
    min_read_quality=10
)
barcodes = cas.pp.filter_cells(barcodes, min_umi_per_cell=10)
barcodes = cas.pp.filter_alleles(barcodes, min_cells_per_allele=3)
char_matrix = cas.pp.convert_alleles_to_character_matrix(
    barcodes,
    missing_state_indicator=-1
)

# --- (2) LARRY lentiviral barcodes from FASTQ ---
import larry
barcodes = larry.parse_barcodes(
    r1='barcodes_R1.fastq.gz',
    r2='barcodes_R2.fastq.gz',
    whitelist='cell_barcodes.txt'
)
adata.obs['clone_id'] = barcodes.loc[adata.obs_names, 'clone_id']
clone_sizes = adata.obs['clone_id'].value_counts()
print(f'Number of clones: {len(clone_sizes)}')
print(f'Median clone size: {clone_sizes.median():.0f}')

# --- (3) Mitochondrial (MitoTracing) natural barcodes from scRNA-seq BAM ---
import mito_utils as mu
variants = mu.call_variants(
    adata,
    bam_path='possorted_genome_bam.bam',
    min_cell_quality=0.9,
    min_coverage=10
)
variants = mu.filter_variants(
    variants,
    min_cells=10,
    max_af=0.9,
    min_af=0.01
)
distances = mu.compute_distances(variants, method='jaccard')
tree = mu.build_tree(distances, method='nj')
```

## Character Matrix QC

_modules: qc, missing-data, filtering_

```python
import numpy as np

# Barcode diversity
n_states = (char_matrix > 0).sum(axis=0)
print(f'Mean states per site: {n_states.mean():.1f}')

# Drop uninformative characters (mutated in only one cell)
informative = (char_matrix > 0).sum(axis=0) > 1
char_matrix = char_matrix[:, informative]

# Missing-data profiling
missing_per_cell = (char_matrix == -1).mean(axis=1)
missing_per_site = (char_matrix == -1).mean(axis=0)

# Remove cells with too much missing data
keep_cells = missing_per_cell < 0.5
char_matrix = char_matrix[keep_cells]
```

## Lineage Tree Reconstruction

_modules: tree-reconstruction, greedy-solver, ilp-solver, neighbor-joining_

```python
import cassiopeia as cas

tree = cas.data.CassiopeiaTree(
    character_matrix=char_matrix,
    cell_meta=cell_metadata
)

# Data-quality summary
print(f'Cells: {tree.n_cell}')
print(f'Characters: {tree.n_character}')
print(f'Missing fraction: {(char_matrix == -1).mean():.2%}')

# Greedy solver (fast, scalable)
solver = cas.solver.VanillaGreedySolver()
solver.solve(tree)

# Alternative: maximum-parsimony ILP (slower, optimal)
solver = cas.solver.ILPSolver()
solver.solve(tree, convergence_time_limit=600)

# Hybrid: greedy for large clades, ILP refinement below cell_cutoff
solver = cas.solver.HybridSolver(
    top_solver=cas.solver.VanillaGreedySolver(),
    bottom_solver=cas.solver.ILPSolver(),
    cell_cutoff=200
)
solver.solve(tree)

# Distance-based comparison via neighbor-joining
nj_solver = cas.solver.NeighborJoiningSolver(
    dissimilarity_function=cas.solver.dissimilarity_functions.weighted_hamming_distance
)
nj_solver.solve(tree)
```

## Tree Quality Assessment & Visualization

_modules: tree-critique, bootstrap, visualization_

```python
from cassiopeia.critique import compare

# Topological comparison
rf_distance = compare.robinson_foulds(tree1, tree2)
triplet_acc = compare.triplets_correct(tree, ground_truth_tree)

# Bootstrap support
bootstrapped_trees = cas.solver.bootstrap(
    tree,
    solver=solver,
    n_replicates=100
)
support = cas.critique.bootstrap_support(tree, bootstrapped_trees)

# Summary statistics (typical ranges):
#   Tree depth      10-50   (max root-to-leaf distance)
#   Colless balance 0-1     (tree asymmetry)
#   Sackin index    varies  (sum of root-leaf depths)
#   Gamma statistic -3 to 3 (tempo of diversification)

# Visualization
import cassiopeia as cas
cas.pl.local.plot_matplotlib(
    tree,
    meta_data=['cell_type'],
    clade_colors=cell_type_colors,
    orient='down',
    figsize=(15, 10)
)
cas.pl.local.export_to_itol(tree, 'tree_for_itol.txt')
cas.pl.local.plot_ete3(tree, meta_data='cell_type', show_internal=False)
```

## Clonal Dynamics with CoSpar

_modules: transition-map, fate-probability, clone-dynamics_

```python
import cospar as cs

adata = cs.read_h5ad('lineage_traced.h5ad')
# obs must contain 'clone_id' or 'barcode'; time key (e.g. 'day') for time-series

# Infer transition map with intraclone smoothing
cs.tl.infer_Tmap(
    adata,
    smooth_array=[15, 10, 5],
    intraclone_threshold=0.2,
    neighbor_method='embedding'
)

# Clonal structure visualization
cs.pl.clonal_embedding(adata, color='clone_id')

# Fate probabilities from source to sink
cs.tl.fate_map(adata, source='HSC', sink='Monocyte', method='norm-sum')
cs.pl.fate_map(adata, source='HSC')

# Fate coupling between cell types
cs.tl.fate_coupling(adata, source='HSC')
cs.pl.fate_coupling(adata, source='HSC')

# Time-resolved transition probabilities and clone-size dynamics
cs.tl.transition_map(adata, time_key='day')
cs.pl.transition_map(adata)
cs.tl.clone_size(adata, time_key='day')
cs.pl.clone_size(adata)
```

## Integration with scRNA-seq & Clonal Expansion

_modules: integration, clonal-expansion, differential-expression_

```python
import scanpy as sc

# Match tree leaves to expression data
common_cells = set(tree.leaves).intersection(adata.obs_names)
adata_matched = adata[list(common_cells)]
tree_matched = tree.copy()
tree_matched.subset_leaves(list(common_cells))

# Compute pairwise tree distances (store in adata.obsp as a sparse matrix)
for i, cell in enumerate(adata_matched.obs_names):
    for j, cell2 in enumerate(adata_matched.obs_names):
        if i < j:
            dist = tree_matched.get_distance(cell, cell2)
            # store dist into obsp sparse matrix
# Correlate clonal relatedness with transcriptomic similarity

# Find expanded clones
clone_sizes = adata.obs['clone_id'].value_counts()
expanded = clone_sizes[clone_sizes > 10].index
adata.obs['is_expanded'] = adata.obs['clone_id'].isin(expanded)

# Differential expression: expanded vs non-expanded
sc.tl.rank_genes_groups(adata, groupby='is_expanded', method='wilcoxon')

# Clone-specific signatures
for clone in expanded[:5]:
    clone_cells = adata[adata.obs['clone_id'] == clone]
    sc.tl.score_genes(clone_cells, gene_list=signature_genes)
```
