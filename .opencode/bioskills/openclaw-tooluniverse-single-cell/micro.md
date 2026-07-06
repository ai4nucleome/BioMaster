## cell_communication.md

# Cell-Cell Communication Analysis

Complete guide for analyzing ligand-receptor interactions and cell-cell communication using OmniPath database (integrates CellPhoneDB, CellChatDB, and 100+ other databases) via ToolUniverse.

---

## Overview

Cell-cell communication analysis identifies which cell types are signaling to each other through ligand-receptor (L-R) pairs. This is critical for understanding:
- Immune cell interactions (T cell exhaustion, activation)
- Tumor-immune communication (checkpoint blockade targets)
- Development and differentiation (niche signals)
- Tissue homeostasis (stromal-epithelial crosstalk)

**Data sources**: OmniPath integrates CellPhoneDB, CellChatDB, ICELLNET, Kirouac2010, Ramilowski2015, and 100+ other curated databases.

---

## Workflow Overview

```
1. Get L-R Pairs from OmniPath
   └─ Query databases (CellPhoneDB, CellChatDB)

2. Filter to Expressed Pairs
   └─ Check genes present in dataset
   └─ Filter by expression thresholds

3. Score Cell-Cell Communication
   └─ Sender-receiver matrix
   └─ Calculate communication scores

4. Identify Top Interactions
   └─ Rank by score
   └─ Filter by biology (e.g., tumor-immune)

5. Trace Signaling Cascades
   └─ Get downstream targets
   └─ Identify transcription factors

6. Validate and Report
   └─ Cross-check with literature
   └─ Generate communication network
```

---

## Step 1: Get Ligand-Receptor Pairs from OmniPath

```python
from tooluniverse import ToolUniverse
import pandas as pd

tu = ToolUniverse()
tu.load_tools()

def get_ligand_receptor_pairs(proteins=None, databases=None):
    """Get ligand-receptor pairs from OmniPath.

    Args:
        proteins: Comma-separated protein names (None = all)
        databases: Comma-separated database names (None = all)
                  Options: CellPhoneDB, CellChatDB, etc.

    Returns:
        DataFrame with L-R interactions
    """
    result = tu.run_tool(
        "OmniPath_get_ligand_receptor_interactions",
        proteins=proteins,
        databases=databases
    )

    if result['metadata']['success']:
        interactions = result['data']['interactions']
        df = pd.DataFrame(interactions)
        return df
    else:
        print(f"Error: {result.get('error', 'Unknown')}")
        return pd.DataFrame()

# Example: Get all CellPhoneDB pairs
lr_pairs = get_ligand_receptor_pairs(databases="CellPhoneDB")
print(f"Found {len(lr_pairs)} L-R pairs from CellPhoneDB")

# Example: Get specific immune checkpoints
immune_checkpoints = "CD274,PDCD1,CTLA4,CD80,CD86,HAVCR2,TIGIT"
checkpoint_lr = get_ligand_receptor_pairs(proteins=immune_checkpoints)
print(checkpoint_lr[['source_genesymbol', 'target_genesymbol', 'curation_effort']])
```

**Important columns**:
- `source_genesymbol`: Ligand gene name
- `target_genesymbol`: Receptor gene name
- `is_directed`: True for directed interactions
- `sources`: Database sources (comma-separated)
- `references`: PubMed IDs
- `curation_effort`: Number of supporting evidences

---

## Step 2: Filter to Expressed L-R Pairs

```python
def filter_expressed_lr_pairs(adata, lr_pairs, min_frac=0.1, min_mean=0.1):
    """Filter L-R pairs to only those expressed in the dataset.

    Args:
        adata: AnnData object with normalized expression
        lr_pairs: DataFrame from get_ligand_receptor_pairs()
        min_frac: Minimum fraction of cells expressing (default 0.1 = 10%)
        min_mean: Minimum mean expression level (default 0.1)

    Returns:
        DataFrame with expressed L-R pairs
    """
    from scipy.sparse import issparse

    # Get genes in dataset
    genes_in_data = set(adata.var_names)

    # Filter to genes in data
    expressed_lr = lr_pairs[
        lr_pairs['source_genesymbol'].isin(genes_in_data) &
        lr_pairs['target_genesymbol'].isin(genes_in_data)
    ].copy()

    # Calculate expression statistics
    def gene_stats(gene):
        if gene not in genes_in_data:
            return 0, 0
        X = adata[:, gene].X
        if issparse(X):
            X = X.toarray()
        mean_expr = X.mean()
        frac_expr = (X > 0).mean()
        return mean_expr, frac_expr

    expressed_lr['ligand_mean'] = expressed_lr['source_genesymbol'].apply(
        lambda g: gene_stats(g)[0]
    )
    expressed_lr['ligand_frac'] = expressed_lr['source_genesymbol'].apply(
        lambda g: gene_stats(g)[1]
    )
    expressed_lr['receptor_mean'] = expressed_lr['target_genesymbol'].apply(
        lambda g: gene_stats(g)[0]
    )
    expressed_lr['receptor_frac'] = expressed_lr['target_genesymbol'].apply(
        lambda g: gene_stats(g)[1]
    )

    # Filter by thresholds
    expressed_lr = expressed_lr[
        (expressed_lr['ligand_mean'] >= min_mean) &
        (expressed_lr['receptor_mean'] >= min_mean) &
        (expressed_lr['ligand_frac'] >= min_frac) &
        (expressed_lr['receptor_frac'] >= min_frac)
    ]

    return expressed_lr

# Example
expressed_lr = filter_expressed_lr_pairs(adata, lr_pairs, min_frac=0.05, min_mean=0.05)
print(f"Expressed: {len(expressed_lr)}/{len(lr_pairs)} L-R pairs ({100*len(expressed_lr)/len(lr_pairs):.1f}%)")
```

---

## Step 3: Score Cell-Cell Communication

```python
def score_cell_communication(adata, lr_pairs, cell_type_col='cell_type',
                             method='mean_product'):
    """Score cell-cell communication for each cell type pair.

    Args:
        adata: AnnData with cell type annotations
        lr_pairs: Expressed L-R pairs from filter_expressed_lr_pairs()
        cell_type_col: Column in adata.obs with cell type labels
        method: 'mean_product' or 'fraction_product'

    Returns:
        DataFrame with columns: sender, receiver, ligand, receptor, score
    """
    import numpy as np
    from scipy.sparse import issparse

    cell_types = adata.obs[cell_type_col].unique()
    results = []

    for _, row in lr_pairs.iterrows():
        ligand = row['source_genesymbol']
        receptor = row['target_genesymbol']

        if ligand not in adata.var_names or receptor not in adata.var_names:
            continue

        for sender_ct in cell_types:
            for receiver_ct in cell_types:
                # Sender cells
                sender_mask = adata.obs[cell_type_col] == sender_ct
                ligand_expr = adata[sender_mask, ligand].X
                if issparse(ligand_expr):
                    ligand_expr = ligand_expr.toarray().flatten()

                # Receiver cells
                receiver_mask = adata.obs[cell_type_col] == receiver_ct
                receptor_expr = adata[receiver_mask, receptor].X
                if issparse(receptor_expr):
                    receptor_expr = receptor_expr.toarray().flatten()

                # Calculate score
                if method == 'mean_product':
                    ligand_mean = np.mean(ligand_expr)
                    receptor_mean = np.mean(receptor_expr)
                    score = ligand_mean * receptor_mean

                elif method == 'fraction_product':
                    ligand_frac = np.mean(ligand_expr > 0)
                    receptor_frac = np.mean(receptor_expr > 0)
                    ligand_mean = np.mean(ligand_expr[ligand_expr > 0]) if ligand_frac > 0 else 0
                    receptor_mean = np.mean(receptor_expr[receptor_expr > 0]) if receptor_frac > 0 else 0
                    score = ligand_frac * receptor_frac * ligand_mean * receptor_mean

                if score > 0:
                    results.append({
                        'sender': sender_ct,
                        'receiver': receiver_ct,
                        'ligand': ligand,
                        'receptor': receptor,
                        'ligand_mean': ligand_mean,
                        'receptor_mean': receptor_mean,
                        'score': score,
                        'curation_effort': row.get('curation_effort', 0),
                        'databases': row.get('sources', 'Unknown')
                    })

    return pd.DataFrame(results)

# Example
communication_scores = score_cell_communication(
    adata, expressed_lr, cell_type_col='cell_type'
)

# Top 20 interactions
top_20 = communication_scores.nlargest(20, 'score')
print("\nTop 20 cell-cell interactions:")
print(top_20[['sender', 'receiver', 'ligand', 'receptor', 'score']])
```

---

## Step 4: Identify Top Interactions

### Filter by Cell Type Pair
```python
# Example: Tumor → T cell interactions
tumor_to_tcell = communication_scores[
    (communication_scores['sender'] == 'Tumor') &
    (communication_scores['receiver'].str.contains('T cell|CD4|CD8'))
]

print(f"\nTumor → T cell interactions: {len(tumor_to_tcell)}")
print(tumor_to_tcell.nlargest(10, 'score'))
```

### Filter by Pathway
```python
# Immune checkpoints
checkpoints = ['CD274', 'PDCD1', 'CTLA4', 'CD80', 'CD86', 'HAVCR2', 'TIGIT']
checkpoint_interactions = communication_scores[
    communication_scores['ligand'].isin(checkpoints) |
    communication_scores['receptor'].isin(checkpoints)
].sort_values('score', ascending=False)

print(f"\nCheckpoint interactions: {len(checkpoint_interactions)}")
print(checkpoint_interactions.head(10))
```

---

## Step 5: Trace Downstream Signaling

```python
def get_downstream_signaling(receptor_gene):
    """Get downstream signaling from a receptor.

    Args:
        receptor_gene: Receptor gene symbol

    Returns:
        DataFrame with signaling interactions
    """
    result = tu.run_tool(
        "OmniPath_get_signaling_interactions",
        proteins=receptor_gene,
        is_directed=True
    )

    if result['metadata']['success']:
        interactions = result['data']['interactions']
        df = pd.DataFrame(interactions)

        # Filter to receptor as source
        df = df[df['source_genesymbol'] == receptor_gene]

        return df[[
            'source_genesymbol', 'target_genesymbol',
            'is_stimulation', 'is_inhibition',
            'sources', 'references'
        ]]

    return pd.DataFrame()

# Example: PDCD1 (PD-1) signaling
pdcd1_signaling = get_downstream_signaling('PDCD1')
print(f"\nPDCD1 signals to {len(pdcd1_signaling)} targets")
print(pdcd1_signaling.head(10))

# Find transcription factors
tfs = pdcd1_signaling[pdcd1_signaling['target_genesymbol'].str.contains('NFAT|FOS|JUN|STAT')]
print(f"\nTranscription factors: {list(tfs['target_genesymbol'])}")
```

---

## Step 6: Handle Protein Complexes

Some receptors are multi-subunit complexes (e.g., TGF-beta receptors):

```python
def check_complex_expression(adata, complex_name, cell_type=None):
    """Check if all subunits of a protein complex are expressed.

    Args:
        adata: AnnData object
        complex_name: Complex name (e.g., "TGFBR2")
        cell_type: Optional cell type to subset

    Returns:
        List of dicts with complex info
    """
    import numpy as np

    # Get complex composition from OmniPath
    result = tu.run_tool("OmniPath_get_complexes", proteins=complex_name)

    if not result['metadata']['success'] or not result['data']['complexes']:
        return {'complex_found': False}

    complexes = result['data']['complexes']

    # Subset to cell type
    if cell_type:
        adata_subset = adata[adata.obs.cell_type == cell_type, :]
    else:
        adata_subset = adata

    results = []
    for complex_info in complexes:
        components = complex_info.get('components_genesymbols', '').split('_')

        # Check expression of each component
        component_expr = {}
        for comp in components:
            if comp in adata_subset.var_names:
                X = adata_subset[:, comp].X
                if issparse(X):
                    X = X.toarray().flatten()
                mean_expr = np.mean(X)
                frac_expr = np.mean(X > 0)
                component_expr[comp] = {'mean': mean_expr, 'fraction': frac_expr}
            else:
                component_expr[comp] = {'mean': 0, 'fraction': 0}

        # Complex score = minimum of subunit expressions
        min_mean = min([v['mean'] for v in component_expr.values()])
        min_frac = min([v['fraction'] for v in component_expr.values()])

        results.append({
            'complex_name': complex_info.get('name', 'Unknown'),
            'components': components,
            'component_expression': component_expr,
            'complex_score': min_mean * min_frac,
            'all_subunits_expressed': all([v['fraction'] > 0.1 for v in component_expr.values()])
        })

    return results

# Example: TGF-beta receptor
tgfb_receptor = check_complex_expression(adata, "TGFBR2", cell_type="Fibroblast")
for comp_result in tgfb_receptor:
    print(f"\nComplex: {comp_result['complex_name']}")
    print(f"Components: {comp_result['components']}")
    print(f"All expressed: {comp_result['all_subunits_expressed']}")
    print(f"Score: {comp_result['complex_score']:.4f}")
```

---

## Step 7: Generate Communication Report

```python
def generate_communication_report(adata, cell_type_col='cell_type',
                                 databases="CellPhoneDB,CellChatDB",
                                 min_score=0.01):
    """Generate complete cell-cell communication report."""

    report = []
    report.append("# Cell-Cell Communication Analysis Report\n")

    # Step 1: Get L-R pairs
    report.append("## 1. Ligand-Receptor Database Query")
    lr_pairs = get_ligand_receptor_pairs(databases=databases)
    report.append(f"- Total L-R pairs: {len(lr_pairs)}")
    report.append(f"- Databases: {databases}\n")

    # Step 2: Filter expressed
    report.append("## 2. Expressed Ligand-Receptor Pairs")
    expressed_lr = filter_expressed_lr_pairs(adata, lr_pairs, min_frac=0.05, min_mean=0.05)
    report.append(f"- Expressed: {len(expressed_lr)}/{len(lr_pairs)} ({100*len(expressed_lr)/len(lr_pairs):.1f}%)")
    report.append(f"- Thresholds: >5% cells, mean >0.05\n")

    # Step 3: Score communication
    report.append("## 3. Cell-Cell Communication Scores")
    communication_scores = score_cell_communication(adata, expressed_lr, cell_type_col=cell_type_col)
    communication_scores = communication_scores[communication_scores['score'] >= min_score]
    report.append(f"- Total interactions: {len(communication_scores)}")
    report.append(f"- Min score: {min_score}\n")

    # Top 20 table
    report.append("### Top 20 Interactions")
    report.append("| Sender | Receiver | Ligand | Receptor | Score | Curation |")
    report.append("|--------|----------|--------|----------|-------|----------|")
    for _, row in communication_scores.nlargest(20, 'score').iterrows():
        report.append(
            f"| {row['sender']} | {row['receiver']} | {row['ligand']} | "
            f"{row['receptor']} | {row['score']:.4f} | {row['curation_effort']} |"
        )
    report.append("")

    # Communication by cell type
    report.append("## 4. Communication Summary by Cell Type")
    sender_counts = communication_scores.groupby('sender').size().sort_values(ascending=False)
    receiver_counts = communication_scores.groupby('receiver').size().sort_values(ascending=False)

    report.append("\n### Top Sender Cell Types")
    report.append("| Cell Type | Outgoing Interactions |")
    report.append("|-----------|----------------------|")
    for ct, count in sender_counts.head(10).items():
        report.append(f"| {ct} | {count} |")

    report.append("\n### Top Receiver Cell Types")
    report.append("| Cell Type | Incoming Interactions |")
    report.append("|-----------|----------------------|")
    for ct, count in receiver_counts.head(10).items():
        report.append(f"| {ct} | {count} |")

    return "\n".join(report)

# Generate and save report
report = generate_communication_report(adata, cell_type_col='cell_type')
print(report)

with open('cell_communication_report.md', 'w') as f:
    f.write(report)
```

---

## Example: Tumor-Immune Cell Communication

Complete workflow for T cell exhaustion analysis:

```python
# Step 1: Get immune checkpoint L-R pairs
checkpoint_proteins = "CD274,PDCD1,CTLA4,CD80,CD86,HAVCR2,TIGIT,CD96,NECTIN2,LAG3"
checkpoint_lr = get_ligand_receptor_pairs(proteins=checkpoint_proteins)

# Step 2: Filter to expressed
expressed_checkpoints = filter_expressed_lr_pairs(adata, checkpoint_lr, min_frac=0.05)

# Step 3: Score communication
communication_scores = score_cell_communication(adata, expressed_checkpoints)

# Step 4: Tumor-T cell interactions
tumor_tcell = communication_scores[
    ((communication_scores['sender'] == 'Tumor') &
     (communication_scores['receiver'].str.contains('T cell|CD4|CD8'))) |
    ((communication_scores['receiver'] == 'Tumor') &
     (communication_scores['sender'].str.contains('T cell|CD4|CD8')))
]

# Step 5: Find exhaustion signals
exhaustion_pairs = tumor_tcell[
    tumor_tcell['ligand'].isin(['CD274', 'HAVCR2']) |  # PD-L1, TIM-3
    tumor_tcell['receptor'].isin(['PDCD1', 'HAVCR2', 'CTLA4', 'LAG3'])
].sort_values('score', ascending=False)

print("\nTop tumor-T cell exhaustion signals:")
print(exhaustion_pairs[['sender', 'receiver', 'ligand', 'receptor', 'score']])

# Step 6: Expression levels
print(f"\nCD274 (PD-L1) in tumor: {adata[adata.obs.cell_type=='Tumor', 'CD274'].X.mean():.3f}")
print(f"PDCD1 (PD-1) in T cells: {adata[adata.obs.cell_type.str.contains('T cell'), 'PDCD1'].X.mean():.3f}")

# Step 7: Downstream signaling
pdcd1_cascade = get_downstream_signaling('PDCD1')
print(f"\nPDCD1 downstream targets: {len(pdcd1_cascade)}")
```

---

## Visualization

```python
def plot_communication_network(communication_scores, top_n=50, min_score=0.01):
    """Plot cell-cell communication network."""
    import matplotlib.pyplot as plt
    import networkx as nx

    # Filter
    comm_filtered = communication_scores[communication_scores['score'] >= min_score]
    comm_top = comm_filtered.nlargest(top_n, 'score')

    # Build network
    G = nx.DiGraph()
    for _, row in comm_top.iterrows():
        edge_label = f"{row['ligand']}→{row['receptor']}"
        G.add_edge(row['sender'], row['receiver'],
                  weight=row['score'], label=edge_label)

    # Plot
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, k=2, iterations=50)

    # Nodes
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue', alpha=0.9)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    # Edges
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    max_weight = max(weights)
    widths = [5 * w / max_weight for w in weights]

    nx.draw_networkx_edges(G, pos, width=widths, alpha=0.6,
                          edge_color='gray', arrows=True, arrowsize=20)

    plt.title(f"Cell-Cell Communication Network (Top {top_n})", fontsize=14)
    plt.axis('off')
    plt.tight_layout()

    return plt

# Plot
plot = plot_communication_network(communication_scores, top_n=30)
plot.savefig('communication_network.png', dpi=300, bbox_inches='tight')
```

---

## Tips and Best Practices

1. **Expression thresholds**: Balance sensitivity vs specificity
   - Stringent: min_frac=0.1, min_mean=0.1 (fewer false positives)
   - Permissive: min_frac=0.05, min_mean=0.05 (capture rare interactions)

2. **Communication score**: Mean product method is simple and interpretable
   - Fraction product accounts for expression breadth
   - Can add log-transform for very skewed distributions

3. **Database selection**:
   - CellPhoneDB: Well-curated, human-focused
   - CellChatDB: Broader coverage, mouse + human
   - Use both for comprehensive analysis

4. **Validation**: Always cross-validate top hits:
   - Check expression in UMAP/violin plots
   - Verify with literature (PubMed IDs in `references` column)
   - Compare across replicates/cohorts

5. **Protein complexes**: Check multi-subunit receptors
   - Use `check_complex_expression()` for receptors like TGFBR1/2
   - All subunits must be expressed for functional complex

6. **Statistical testing**: For rigorous analysis:
   - Permutation test (shuffle cell labels)
   - Compare to random cell type assignments
   - Correct for multiple testing

---

## See Also

- **scanpy_workflow.md** - Load and normalize data before communication analysis
- **marker_identification.md** - Cell type annotation for communication analysis
- **troubleshooting.md** - Common OmniPath API issues

---

## clustering_guide.md

# Clustering Methods for Single-Cell Data

Guide to different clustering methods: Leiden, Louvain, hierarchical, and bootstrap consensus clustering.

---

## Leiden Clustering (Recommended)

Best all-around method for single-cell data.

```python
import scanpy as sc

# Build neighbor graph
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Run Leiden
sc.tl.leiden(adata, resolution=0.5, random_state=0)

print(f"Clusters: {adata.obs['leiden'].nunique()}")
```

**Resolution parameter**:
- Higher = More clusters
- Typical range: 0.3 - 1.5
- Start with 0.5, adjust based on biology

---

## Louvain Clustering

Alternative to Leiden (older algorithm).

```python
sc.tl.louvain(adata, resolution=0.5, random_state=0)
```

**Leiden vs Louvain**:
- Leiden: Better optimization, guaranteed connected communities
- Louvain: Faster, may produce disconnected communities
- For publication: Use Leiden

---

## Hierarchical Clustering

For expression matrices (not single-cell level).

```python
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist
import numpy as np

def hierarchical_clustering(expression_df, n_clusters=3, method='ward', metric='euclidean'):
    """Hierarchical clustering on expression matrix.

    Args:
        expression_df: DataFrame (samples as rows, genes as columns)
        n_clusters: Number of clusters
        method: 'ward', 'complete', 'average', 'single'
        metric: Distance metric

    Returns:
        dict with labels, linkage_matrix
    """
    # Compute linkage
    if method == 'ward':
        Z = linkage(expression_df.values, method='ward')
    else:
        dist = pdist(expression_df.values, metric=metric)
        Z = linkage(dist, method=method)

    # Cut tree
    labels = fcluster(Z, t=n_clusters, criterion='maxclust')

    # Cluster sizes
    unique, counts = np.unique(labels, return_counts=True)
    for c, n in zip(unique, counts):
        print(f"  Cluster {c}: {n} samples")

    return {
        'labels': labels,
        'linkage_matrix': Z,
        'n_clusters': n_clusters
    }

# Example
result = hierarchical_clustering(expr_df, n_clusters=3, method='ward')
```

**Linkage methods**:
- `ward`: Minimizes within-cluster variance (best for most data)
- `complete`: Maximum distance between clusters (compact clusters)
- `average`: Average distance (balanced)
- `single`: Minimum distance (can create chains)

---

## Bootstrap Consensus Clustering

Robust clustering with logistic regression prediction (BixBench pattern).

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def bootstrap_consensus_clustering(expression_df, n_clusters=3, n_iterations=50,
                                    train_fraction=0.7, random_state=42):
    """Bootstrap consensus clustering.

    Args:
        expression_df: DataFrame (samples as rows, genes as columns)
        n_clusters: Number of clusters
        n_iterations: Bootstrap iterations
        train_fraction: Fraction for training
        random_state: Random seed

    Returns:
        dict with labels, consensus_matrix, consistent_count
    """
    np.random.seed(random_state)
    n_samples = len(expression_df)
    n_train = int(n_samples * train_fraction)

    # Consensus matrices
    train_consensus = np.zeros((n_samples, n_samples))
    test_consensus = np.zeros((n_samples, n_samples))
    train_count = np.zeros((n_samples, n_samples))
    test_count = np.zeros((n_samples, n_samples))

    for i in range(n_iterations):
        # Random split
        indices = np.random.permutation(n_samples)
        train_idx = indices[:n_train]
        test_idx = indices[n_train:]

        # Cluster training data
        train_data = expression_df.iloc[train_idx]
        Z = linkage(train_data.values, method='ward')
        train_labels = fcluster(Z, t=n_clusters, criterion='maxclust')

        # Update train consensus
        for a_i, a in enumerate(train_idx):
            for b_i, b in enumerate(train_idx):
                train_count[a, b] += 1
                if train_labels[a_i] == train_labels[b_i]:
                    train_consensus[a, b] += 1

        # Predict test labels
        scaler = StandardScaler()
        X_train = scaler.fit_transform(train_data.values)
        X_test = scaler.transform(expression_df.iloc[test_idx].values)

        lr = LogisticRegression(max_iter=1000, random_state=random_state)
        lr.fit(X_train, train_labels)
        test_labels = lr.predict(X_test)

        # Update test consensus
        for a_i, a in enumerate(test_idx):
            for b_i, b in enumerate(test_idx):
                test_count[a, b] += 1
                if test_labels[a_i] == test_labels[b_i]:
                    test_consensus[a, b] += 1

    # Normalize
    with np.errstate(divide='ignore', invalid='ignore'):
        train_consensus_norm = np.where(train_count > 0, train_consensus / train_count, 0)
        test_consensus_norm = np.where(test_count > 0, test_consensus / test_count, 0)

    # Final clustering
    combined_consensus = (train_consensus_norm + test_consensus_norm) / 2
    np.fill_diagonal(combined_consensus, 1.0)

    from scipy.spatial.distance import squareform
    dist = 1 - combined_consensus
    np.fill_diagonal(dist, 0)
    dist = np.maximum(dist, 0)
    dist = (dist + dist.T) / 2
    condensed = squareform(dist)
    Z_final = linkage(condensed, method='average')
    final_labels = fcluster(Z_final, t=n_clusters, criterion='maxclust')

    # Count consistent samples
    consistent_count = 0
    for s in range(n_samples):
        cluster = final_labels[s]
        same_cluster = np.where(final_labels == cluster)[0]
        same_cluster = same_cluster[same_cluster != s]

        if len(same_cluster) > 0:
            train_scores = [train_consensus_norm[s, j] for j in same_cluster if train_count[s, j] > 0]
            test_scores = [test_consensus_norm[s, j] for j in same_cluster if test_count[s, j] > 0]

            if train_scores and test_scores:
                if np.mean(train_scores) > 0.7 and np.mean(test_scores) > 0.7:
                    consistent_count += 1

    print(f"Consistently classified: {consistent_count}/{n_samples}")

    return {
        'labels': final_labels,
        'train_consensus': train_consensus_norm,
        'test_consensus': test_consensus_norm,
        'combined_consensus': combined_consensus,
        'consistent_count': consistent_count
    }

# Example
result = bootstrap_consensus_clustering(expr_df, n_clusters=3, n_iterations=50)
print(f"Answer: {result['consistent_count']} samples consistently classified")
```

---

## PCA for Clustering

Perform PCA on expression matrix for BixBench questions.

```python
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np

def manual_pca(expression_df, log_transform='log10', pseudocount=1):
    """Run PCA with specific transforms.

    Args:
        expression_df: DataFrame (samples as rows, genes as columns)
        log_transform: 'log10', 'log2', 'log1p', or None
        pseudocount: Pseudocount for log

    Returns:
        dict with variance_ratio, pc_coords, loadings
    """
    X = expression_df.values.astype(float)

    # Transform
    if log_transform == 'log10':
        X = np.log10(X + pseudocount)
    elif log_transform == 'log2':
        X = np.log2(X + pseudocount)
    elif log_transform == 'log1p':
        X = np.log1p(X)

    # Run PCA
    n_components = min(X.shape[0], X.shape[1])
    pca = PCA(n_components=n_components)
    pc_coords = pca.fit_transform(X)

    # Results
    result = {
        'variance_ratio': pca.explained_variance_ratio_,
        'variance_explained': pca.explained_variance_,
        'pc_coords': pd.DataFrame(
            pc_coords,
            index=expression_df.index,
            columns=[f'PC{i+1}' for i in range(n_components)]
        ),
        'loadings': pd.DataFrame(
            pca.components_.T,
            index=expression_df.columns,
            columns=[f'PC{i+1}' for i in range(n_components)]
        ),
        'cumulative_variance': np.cumsum(pca.explained_variance_ratio_)
    }

    print(f"PC1: {result['variance_ratio'][0]*100:.2f}% variance")
    print(f"PC1-10: {result['cumulative_variance'][9]*100:.2f}% variance")

    return result

# Example
pca_result = manual_pca(expr_df, log_transform='log10', pseudocount=1)
```

---

## Choosing the Right Method

| Use Case | Method | When to Use |
|----------|--------|-------------|
| Single-cell clustering | **Leiden** | Default for scRNA-seq |
| Older pipeline compatibility | **Louvain** | If comparing to old analyses |
| Expression matrix clustering | **Hierarchical** | Bulk RNA-seq, <1000 samples |
| Robust clustering | **Bootstrap consensus** | Need confidence estimates |
| Dimensionality reduction | **PCA** | Variance analysis, visualization |

---

## Validation

### Silhouette Score
```python
from sklearn.metrics import silhouette_score

# After clustering
silhouette_avg = silhouette_score(X, labels)
print(f"Silhouette score: {silhouette_avg:.3f}")
# Range: -1 to 1. >0.5 is good.
```

### Cluster Stability
```python
# Run clustering multiple times with different random seeds
from collections import Counter

all_labels = []
for seed in range(10):
    sc.tl.leiden(adata, resolution=0.5, random_state=seed, key_added=f'leiden_{seed}')
    all_labels.append(adata.obs[f'leiden_{seed}'])

# Check consistency
# (Implementation depends on label alignment)
```

---

## See Also

- **scanpy_workflow.md** - Prepare data for clustering
- **marker_identification.md** - Annotate clusters after clustering

---

## marker_identification.md

# Marker Gene Identification and Cell Type Annotation

Guide to finding marker genes and annotating cell types in single-cell data.

---

## Find Marker Genes for Clusters

```python
import scanpy as sc

# Run DE for all clusters
sc.tl.rank_genes_groups(
    adata,
    groupby='leiden',
    method='wilcoxon',  # or 't-test', 'logreg'
    n_genes=100,
    corr_method='benjamini-hochberg'
)

# Get results for cluster 0
markers_0 = sc.get.rank_genes_groups_df(adata, group='0')
print(markers_0.head(10))
```

**Available methods**:
- `wilcoxon`: Non-parametric, robust (default)
- `t-test`: Fast, parametric
- `logreg`: Logistic regression, good for classification

---

## Cell Type Annotation Strategies

### 1. Known Marker Genes

```python
# Define markers for cell types
marker_genes = {
    'T cells': ['CD3D', 'CD3E', 'CD8A', 'CD4'],
    'CD4 T cells': ['CD3D', 'CD4', 'IL7R'],
    'CD8 T cells': ['CD3D', 'CD8A', 'CD8B'],
    'B cells': ['CD19', 'MS4A1', 'CD79A'],
    'Monocytes': ['CD14', 'LYZ', 'S100A9'],
    'CD14 Monocytes': ['CD14', 'LYZ'],
    'CD16 Monocytes': ['FCGR3A', 'MS4A7'],
    'NK cells': ['NKG7', 'GNLY', 'KLRB1'],
    'Dendritic cells': ['FCER1A', 'CD1C'],
}

# Score clusters
from scipy.sparse import issparse
X = adata.X.toarray() if issparse(adata.X) else adata.X
expr_df = pd.DataFrame(X, index=adata.obs_names, columns=adata.var_names)

cluster_scores = {}
for ct, markers in marker_genes.items():
    available = [m for m in markers if m in adata.var_names]
    if available:
        scores = expr_df[available].mean(axis=1)
        cluster_scores[ct] = scores.groupby(adata.obs['leiden']).mean()

# Assign cell types
score_df = pd.DataFrame(cluster_scores)
assignments = score_df.idxmax(axis=1)
adata.obs['cell_type'] = adata.obs['leiden'].map(assignments)
```

### 2. ToolUniverse HPA Database

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

# Search for cell-type markers
result = tu.tools.HPA_search_genes_by_query(query="T cell marker blood")
if result:
    print("HPA T cell markers:", [g.get('gene_name') for g in result[:10]])

# Get tissue-specific expression
result = tu.tools.HPA_get_rna_expression_in_specific_tissues(
    ensembl_id="ENSG00000167286",  # CD3D
    tissue_name="blood"
)
```

### 3. Automated Annotation (scanpy)

```python
# Using marker gene scores
sc.tl.marker_gene_overlap(adata, marker_genes)

# Using cell type prediction (if reference available)
import scanpy.external as sce
# sce.tl.ingest(adata, adata_ref, obs='cell_type')
```

---

## Visualize Marker Expression

```python
# Dot plot
sc.pl.dotplot(adata, marker_genes, groupby='leiden')

# Stacked violin
sc.pl.stacked_violin(adata, marker_genes, groupby='leiden')

# UMAP with marker overlay
sc.pl.umap(adata, color=['leiden', 'CD3D', 'CD79A', 'CD14'])
```

---

## Validate Annotations

### Check Marker Specificity
```python
# Calculate marker specificity
for ct in adata.obs['cell_type'].unique():
    mask = adata.obs['cell_type'] == ct
    markers_for_ct = marker_genes.get(ct, [])

    for marker in markers_for_ct:
        if marker in adata.var_names:
            expr_in_ct = adata[mask, marker].X.mean()
            expr_out_ct = adata[~mask, marker].X.mean()
            fold_enrichment = expr_in_ct / (expr_out_ct + 0.001)
            print(f"{ct} - {marker}: {fold_enrichment:.2f}x enriched")
```

### Cross-Reference with Literature
```python
# Get top expressed genes in cell type
ct_data = adata[adata.obs['cell_type'] == 'CD4 T cells']
X = ct_data.X.toarray() if issparse(ct_data.X) else ct_data.X
mean_expr = np.mean(X, axis=0)
top_genes = ct_data.var_names[np.argsort(mean_expr)[::-1][:20]]
print(f"Top genes in CD4 T cells: {list(top_genes)}")
```

---

## Common Cell Type Markers

### Immune Cells (PBMC)
```python
immune_markers = {
    'T cells': ['CD3D', 'CD3E', 'CD3G'],
    'CD4 T cells': ['CD3D', 'CD4', 'IL7R', 'TCF7'],
    'CD8 T cells': ['CD3D', 'CD8A', 'CD8B', 'GZMK'],
    'Regulatory T cells': ['FOXP3', 'IL2RA', 'CTLA4'],
    'NK cells': ['NKG7', 'GNLY', 'KLRD1', 'KLRB1'],
    'B cells': ['CD19', 'MS4A1', 'CD79A', 'CD79B'],
    'Plasma cells': ['IGHG1', 'MZB1', 'SDC1', 'XBP1'],
    'Monocytes': ['CD14', 'LYZ', 'S100A9', 'S100A8'],
    'CD14 Monocytes': ['CD14', 'LYZ', 'FCN1'],
    'CD16 Monocytes': ['FCGR3A', 'MS4A7', 'CDKN1C'],
    'Dendritic cells': ['FCER1A', 'CD1C', 'CLEC10A'],
    'pDC': ['IL3RA', 'GZMB', 'SERPINF1', 'ITM2C'],
    'Platelets': ['PPBP', 'PF4', 'TUBB1'],
}
```

### Tumor Microenvironment
```python
tme_markers = {
    'Cancer cells': ['EPCAM', 'KRT8', 'KRT18', 'KRT19'],
    'CAFs': ['COL1A1', 'COL1A2', 'DCN', 'ACTA2'],
    'Endothelial': ['PECAM1', 'VWF', 'CDH5'],
    'TAMs': ['CD68', 'CD163', 'MSR1'],
    'Exhausted T cells': ['PDCD1', 'HAVCR2', 'LAG3', 'TIGIT'],
}
```

---

## Tips

1. **Multiple markers**: Use 3-5 markers per cell type for robustness
2. **Negative markers**: Also check genes NOT expressed
3. **Expression levels**: Mean expression matters, not just presence
4. **Subclustering**: For ambiguous clusters, re-cluster at higher resolution
5. **Manual curation**: Always manually review top markers

---

## See Also

- **scanpy_workflow.md** - Clustering before annotation
- **cell_communication.md** - Use annotated cell types for communication

---

## scanpy_workflow.md

# Complete Scanpy Workflow

Complete reference for single-cell RNA-seq analysis using scanpy, from raw counts to annotated cell types.

---

## Phase 1: Data Loading and Validation

### Load h5ad Files
```python
import scanpy as sc
adata = sc.read_h5ad("data.h5ad")
print(f"Shape: {adata.n_obs} cells x {adata.n_vars} genes")
print(f"Obs columns: {list(adata.obs.columns)}")
print(f"Var columns: {list(adata.var.columns)}")
```

### Load 10X Files
```python
# From directory
adata = sc.read_10x_mtx("filtered_gene_bc_matrices/hg19/")

# From HDF5
adata = sc.read_10x_h5("filtered_feature_bc_matrix.h5")
```

### Load CSV/TSV and Convert to AnnData
```python
import anndata as ad
import pandas as pd

df = pd.read_csv("counts.csv", index_col=0)

# Check orientation (genes vs cells)
if df.shape[0] > df.shape[1] * 5:
    print("Transposing: genes were rows")
    df = df.T

adata = ad.AnnData(df)
```

### Attach Metadata
```python
meta = pd.read_csv("metadata.csv", index_col=0, sep='\t')

# Align indices
common = adata.obs_names.intersection(meta.index)
adata = adata[common].copy()

for col in meta.columns:
    adata.obs[col] = meta.loc[common, col]
```

### Attach Gene Annotations
```python
gene_info = pd.read_csv("gene_info.tsv", sep='\t', index_col=0)

common_genes = adata.var_names.intersection(gene_info.index)

for col in ['gene_length', 'gene_type', 'chromosome']:
    if col in gene_info.columns:
        adata.var[col] = gene_info.loc[adata.var_names, col]
```

---

## Phase 2: Quality Control

### Calculate QC Metrics
```python
# Identify mitochondrial genes
adata.var['mt'] = adata.var_names.str.startswith(('MT-', 'mt-'))

# Calculate metrics
sc.pp.calculate_qc_metrics(
    adata, qc_vars=['mt'],
    percent_top=None,
    log1p=False,
    inplace=True
)

# Available metrics:
# - total_counts: Total UMI counts per cell
# - n_genes_by_counts: Number of genes expressed per cell
# - pct_counts_mt: Percentage of counts in mitochondrial genes
```

### Filter Cells
```python
n_before = adata.n_obs

# Minimum genes per cell
sc.pp.filter_cells(adata, min_genes=200)

# Maximum mitochondrial percentage
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()

# Optional: Remove doublets by gene count
# adata = adata[adata.obs['n_genes_by_counts'] < 5000].copy()

# Optional: Minimum UMI counts
# sc.pp.filter_cells(adata, min_counts=500)

n_after = adata.n_obs
print(f"Filtered: {n_before} → {n_after} cells ({n_before - n_after} removed)")
```

### Filter Genes
```python
# Minimum cells per gene (remove rare genes)
sc.pp.filter_genes(adata, min_cells=3)

print(f"After gene filtering: {adata.n_vars} genes")
```

### Doublet Detection (Optional)
```python
# Using scrublet via scanpy
sc.external.pp.scrublet(adata, expected_doublet_rate=0.06)

n_doublets = adata.obs['predicted_doublet'].sum()
print(f"Detected {n_doublets} doublets ({n_doublets/adata.n_obs*100:.1f}%)")

# Remove doublets
adata = adata[~adata.obs['predicted_doublet']].copy()
```

---

## Phase 3: Normalization and Scaling

### Store Raw Counts
```python
# Important: Store raw counts before normalization
adata.raw = adata.copy()
```

### Library-Size Normalization
```python
# Normalize each cell to 10,000 total counts
sc.pp.normalize_total(adata, target_sum=1e4)
```

### Log Transformation
```python
# Natural log (log1p = log(x + 1))
sc.pp.log1p(adata)
```

### Highly Variable Genes
```python
# Find top variable genes
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=2000,
    flavor='seurat_v3'  # Use 'seurat' if already log-transformed
)

print(f"Highly variable genes: {adata.var['highly_variable'].sum()}")
```

### Scale Data
```python
# Z-score scaling
sc.pp.scale(adata, max_value=10)
```

---

## Phase 4: Dimensionality Reduction

### PCA
```python
# Run PCA on highly variable genes
sc.tl.pca(adata, n_comps=50, use_highly_variable=True)

# Variance explained
var_ratio = adata.uns['pca']['variance_ratio']
print(f"PC1: {var_ratio[0]*100:.2f}% variance")
print(f"Top 10 PCs: {sum(var_ratio[:10])*100:.2f}% variance")

# PC coordinates: adata.obsm['X_pca']
# PC loadings: adata.varm['PCs']
```

### UMAP
```python
# Compute neighbors first
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Run UMAP
sc.tl.umap(adata)

# UMAP coordinates: adata.obsm['X_umap']
```

### t-SNE (Alternative)
```python
sc.tl.tsne(adata, n_pcs=30)
# t-SNE coordinates: adata.obsm['X_tsne']
```

---

## Phase 5: Clustering

### Leiden Clustering (Recommended)
```python
# Build neighbor graph (if not done for UMAP)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Leiden clustering
sc.tl.leiden(adata, resolution=0.5, random_state=0)

n_clusters = adata.obs['leiden'].nunique()
print(f"Leiden clustering: {n_clusters} clusters")
```

### Louvain Clustering (Alternative)
```python
sc.tl.louvain(adata, resolution=0.5, random_state=0)
```

### Resolution Parameter
- Higher resolution = More clusters
- Typical range: 0.3 - 1.5
- Start with 0.5, adjust based on biological expectations

---

## Phase 6: Marker Gene Identification

### Find Marker Genes for Each Cluster
```python
# Run DE test for all clusters
sc.tl.rank_genes_groups(
    adata,
    groupby='leiden',
    method='wilcoxon',  # or 't-test', 'logreg'
    n_genes=100,
    corr_method='benjamini-hochberg'
)

# Get results for cluster 0
markers_0 = sc.get.rank_genes_groups_df(adata, group='0')
print(markers_0.head(10))

# Top marker genes per cluster
sc.pl.rank_genes_groups(adata, n_genes=5, sharey=False)
```

---

## Phase 7: Cell Type Annotation

### Marker-Based Annotation
```python
# Known markers
marker_genes = {
    'T cells': ['CD3D', 'CD3E', 'CD8A', 'CD4'],
    'B cells': ['CD19', 'MS4A1', 'CD79A'],
    'Monocytes': ['CD14', 'LYZ', 'S100A9'],
    'NK cells': ['NKG7', 'GNLY', 'KLRB1'],
    'Dendritic cells': ['FCER1A', 'CD1C'],
}

# Score each cluster
from scipy.sparse import issparse
X = adata.X.toarray() if issparse(adata.X) else adata.X
expr_df = pd.DataFrame(X, index=adata.obs_names, columns=adata.var_names)

cluster_scores = {}
for ct, markers in marker_genes.items():
    available_markers = [m for m in markers if m in adata.var_names]
    if available_markers:
        scores = expr_df[available_markers].mean(axis=1)
        cluster_scores[ct] = scores.groupby(adata.obs['leiden']).mean()

# Assign cell types
score_df = pd.DataFrame(cluster_scores)
assignments = score_df.idxmax(axis=1)
adata.obs['cell_type'] = adata.obs['leiden'].map(assignments)
```

### Use ToolUniverse for Marker Discovery
```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

# Search HPA for tissue-specific markers
result = tu.tools.HPA_search_genes_by_query(
    query="T cell marker blood"
)
```

---

## Phase 8: Differential Expression Analysis

### Per-Cell-Type DE Between Conditions
```python
cell_types = adata.obs['cell_type'].unique()
de_results = {}

for ct in cell_types:
    # Subset to cell type
    adata_ct = adata[adata.obs['cell_type'] == ct].copy()

    # Check sufficient cells
    n_treat = (adata_ct.obs['condition'] == 'treatment').sum()
    n_ctrl = (adata_ct.obs['condition'] == 'control').sum()

    if n_treat < 3 or n_ctrl < 3:
        print(f"{ct}: Skipped (insufficient cells)")
        continue

    # Run DE
    sc.tl.rank_genes_groups(
        adata_ct,
        groupby='condition',
        groups=['treatment'],
        reference='control',
        method='wilcoxon',
        n_genes=adata_ct.n_vars
    )

    # Get results
    df = sc.get.rank_genes_groups_df(adata_ct, group='treatment')

    # Filter significant
    sig = df[(df['pvals_adj'] < 0.05) & (df['logfoldchanges'].abs() > 0.5)]

    de_results[ct] = {
        'all': df,
        'significant': sig,
        'n_sig': len(sig),
        'n_up': (sig['logfoldchanges'] > 0).sum(),
        'n_down': (sig['logfoldchanges'] < 0).sum(),
    }

    print(f"{ct}: {len(sig)} DEGs ({de_results[ct]['n_up']} up, {de_results[ct]['n_down']} down)")
```

---

## Phase 9: Batch Correction with Harmony

```python
import harmonypy

# After PCA
sc.tl.pca(adata, n_comps=50)

# Run Harmony
ho = harmonypy.run_harmony(
    adata.obsm['X_pca'][:, :30],  # Use first 30 PCs
    adata.obs,
    'batch',  # Batch column name
    random_state=0
)

# Store corrected PCs
adata.obsm['X_pca_harmony'] = ho.Z_corr.T

# Re-compute neighbors and cluster on corrected PCs
sc.pp.neighbors(adata, use_rep='X_pca_harmony', n_pcs=30)
sc.tl.leiden(adata, resolution=0.5)
sc.tl.umap(adata)
```

---

## Complete Pipeline Example

```python
import scanpy as sc

# 1. Load
adata = sc.read_10x_h5("data.h5")

# 2. QC
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# 3. Normalize
adata.raw = adata.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# 4. HVG + Scale
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pp.scale(adata, max_value=10)

# 5. PCA
sc.tl.pca(adata, n_comps=50)

# 6. Cluster
sc.pp.neighbors(adata, n_pcs=30)
sc.tl.leiden(adata, resolution=0.5)
sc.tl.umap(adata)

# 7. Markers
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')

# 8. Annotate (manual step)
# 9. DE analysis (per cell type, if conditions present)

# Save
adata.write_h5ad("processed.h5ad")
```

---

## Tips and Best Practices

1. **Always store raw counts** before normalization (`adata.raw = adata.copy()`)
2. **QC thresholds** depend on dataset:
   - min_genes: 200-500
   - pct_counts_mt: 10-20%
   - max_genes: 5000-7000 (doublet filter)
3. **Highly variable genes**: 2000-3000 for most datasets
4. **PCA components**: 30-50 sufficient for most analyses
5. **Resolution tuning**: Start with 0.5, increase for finer clusters
6. **Batch correction**: Use Harmony for multiple batches/samples
7. **DE method**: Wilcoxon (default) good for most cases; t-test faster
8. **Statistical power**: Need >= 3 cells per condition per cell type

---

## See Also

- **clustering_guide.md** - Advanced clustering methods
- **marker_identification.md** - Cell type annotation strategies
- **troubleshooting.md** - Common errors and solutions

---

## seurat_workflow.md

# Seurat to Scanpy Translation

Quick reference for Seurat (R) users transitioning to Scanpy (Python).

---

## Seurat vs Scanpy Equivalents

| Operation | Seurat (R) | Scanpy (Python) |
|-----------|------------|-----------------|
| Load 10X | `Read10X()` | `sc.read_10x_mtx()` |
| Create object | `CreateSeuratObject()` | `ad.AnnData()` |
| Normalize | `NormalizeData()` | `sc.pp.normalize_total() + sc.pp.log1p()` |
| Find HVGs | `FindVariableFeatures()` | `sc.pp.highly_variable_genes()` |
| Scale | `ScaleData()` | `sc.pp.scale()` |
| PCA | `RunPCA()` | `sc.tl.pca()` |
| Find neighbors | `FindNeighbors()` | `sc.pp.neighbors()` |
| Cluster | `FindClusters()` | `sc.tl.leiden()` |
| UMAP | `RunUMAP()` | `sc.tl.umap()` |
| t-SNE | `RunTSNE()` | `sc.tl.tsne()` |
| Find markers | `FindMarkers()` | `sc.tl.rank_genes_groups()` |
| DE test | `FindMarkers(test.use="wilcox")` | `method='wilcoxon'` |
| Subset | `subset(seurat, subset = ...)` | `adata[adata.obs['col'] == val]` |
| Batch correction | `RunHarmony()` | `harmonypy.run_harmony()` |

---

## Side-by-Side Workflows

### Seurat (R)
```r
library(Seurat)

# Load and create object
data <- Read10X("filtered_gene_bc_matrices/hg19/")
seurat <- CreateSeuratObject(counts = data, min.cells = 3, min.features = 200)

# QC
seurat[["percent.mt"]] <- PercentageFeatureSet(seurat, pattern = "^MT-")
seurat <- subset(seurat, subset = percent.mt < 20)

# Normalize
seurat <- NormalizeData(seurat)
seurat <- FindVariableFeatures(seurat, nfeatures = 2000)
seurat <- ScaleData(seurat)

# PCA
seurat <- RunPCA(seurat, npcs = 50)

# Cluster
seurat <- FindNeighbors(seurat, dims = 1:30)
seurat <- FindClusters(seurat, resolution = 0.5)
seurat <- RunUMAP(seurat, dims = 1:30)

# Find markers
markers <- FindMarkers(seurat, ident.1 = 0, ident.2 = 1)
```

### Scanpy (Python)
```python
import scanpy as sc

# Load
adata = sc.read_10x_mtx("filtered_gene_bc_matrices/hg19/")

# QC
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# Normalize
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# HVG + Scale
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pp.scale(adata, max_value=10)

# PCA
sc.tl.pca(adata, n_comps=50)

# Cluster
sc.pp.neighbors(adata, n_pcs=30)
sc.tl.leiden(adata, resolution=0.5)
sc.tl.umap(adata)

# Find markers
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')
markers_0 = sc.get.rank_genes_groups_df(adata, group='0')
```

---

## Key Differences

### 1. Data Structure
- **Seurat**: Seurat object with `@data`, `@meta.data`, `@reductions`
- **Scanpy**: AnnData object with `.X`, `.obs`, `.var`, `.obsm`, `.varm`

### 2. Normalization
- **Seurat**: `NormalizeData()` does log-normalization in one step
- **Scanpy**: Two steps: `normalize_total()` then `log1p()`

### 3. Clustering
- **Seurat**: Louvain algorithm via `FindClusters()`
- **Scanpy**: Leiden (recommended) or Louvain via `sc.tl.leiden()` or `sc.tl.louvain()`

### 4. Subsetting
- **Seurat**: `subset(seurat, subset = cell_type == "T cells")`
- **Scanpy**: `adata[adata.obs['cell_type'] == 'T cells']`

### 5. Metadata
- **Seurat**: `seurat@meta.data$new_column <- values`
- **Scanpy**: `adata.obs['new_column'] = values`

---

## Converting Between Formats

### Seurat to AnnData
```python
import scanpy as sc

# Save from R
# saveRDS(seurat, "seurat.rds")

# Load in Python (requires rpy2)
import anndata2ri
anndata2ri.activate()

from rpy2.robjects import r
r('library(Seurat)')
r('seurat <- readRDS("seurat.rds")')
r('SaveH5Seurat(seurat, "seurat.h5seurat")')
r('Convert("seurat.h5seurat", "h5ad")')

adata = sc.read_h5ad("seurat.h5ad")
```

### AnnData to Seurat
```python
# Save from Python
adata.write_h5ad("adata.h5ad")

# Load in R
library(SeuratDisk)
Convert("adata.h5ad", "seurat.h5seurat")
seurat <- LoadH5Seurat("seurat.h5seurat")
```

---

## When to Use Each

### Use Seurat (R) when:
- Working in R ecosystem (Bioconductor, ggplot2)
- Using Seurat-specific methods (SCTransform, CCA integration)
- Team uses R

### Use Scanpy (Python) when:
- Working in Python ecosystem (pandas, scikit-learn, PyTorch)
- Need integration with ML pipelines
- Large datasets (Scanpy generally faster)
- Prefer Leiden clustering

---

## See Also

- **scanpy_workflow.md** - Full Scanpy pipeline
- **clustering_guide.md** - Leiden vs Louvain

---

## trajectory_analysis.md

# Trajectory Inference and Pseudotime Analysis

Guide to trajectory analysis and pseudotime ordering in single-cell data.

---

## Overview

Trajectory analysis orders cells along a developmental or temporal continuum (pseudotime). Use for:
- Differentiation studies (stem cells → mature cells)
- Cell cycle analysis
- Response to stimulation over time
- Disease progression

---

## Diffusion Pseudotime (DPT)

Built into scanpy, based on diffusion maps.

```python
import scanpy as sc

# After standard preprocessing and clustering
# 1. Identify root cell (start of trajectory)
adata.uns['iroot'] = np.flatnonzero(
    adata.obs['leiden'] == '0'  # Choose starting cluster
)[0]

# 2. Compute diffusion map
sc.tl.diffmap(adata)

# 3. Compute DPT
sc.tl.dpt(adata)

# 4. Visualize
sc.pl.umap(adata, color=['dpt_pseudotime', 'leiden'])

# Pseudotime values in: adata.obs['dpt_pseudotime']
```

---

## PAGA (Partition-based Graph Abstraction)

Models trajectories as cluster connectivity graph.

```python
# After clustering
sc.tl.paga(adata, groups='leiden')

# Plot PAGA graph
sc.pl.paga(adata, color='leiden')

# Initialize UMAP positions from PAGA
sc.tl.umap(adata, init_pos='paga')

# Plot trajectory
sc.pl.umap(adata, color=['leiden', 'CD34'])  # Stem cell marker
```

---

## Gene Expression Along Pseudotime

```python
# Genes that change along pseudotime
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')

# Plot gene expression vs pseudotime
import matplotlib.pyplot as plt

genes_of_interest = ['CD34', 'CD38', 'CD14']
for gene in genes_of_interest:
    if gene in adata.var_names:
        plt.figure()
        plt.scatter(
            adata.obs['dpt_pseudotime'],
            adata[:, gene].X.toarray().flatten(),
            alpha=0.3, s=5
        )
        plt.xlabel('Pseudotime')
        plt.ylabel(f'{gene} expression')
        plt.title(f'{gene} along trajectory')
        plt.show()
```

---

## External Tools

### PAGA with RNA velocity (scVelo)
```python
import scvelo as scv

# Compute RNA velocity
scv.pp.filter_and_normalize(adata)
scv.pp.moments(adata)
scv.tl.velocity(adata)
scv.tl.velocity_graph(adata)

# Visualize
scv.pl.velocity_embedding_stream(adata, basis='umap')
```

### Monocle-style (via Python wrapper)
```python
# Not native to scanpy, requires specialized packages
# For Monocle analysis, consider using R/Seurat integration
```

---

## Tips

1. **Root cell selection**: Critical for pseudotime. Choose starting cell type.
2. **Linear vs branched**: DPT handles linear trajectories, PAGA handles branching.
3. **Validation**: Check marker gene expression matches biological expectation.
4. **Multiple trajectories**: For complex differentiation, use PAGA.

---

## See Also

- **scanpy_workflow.md** - Preprocessing before trajectory
- **clustering_guide.md** - Clustering for PAGA

---

## troubleshooting.md

# Troubleshooting Guide

Common errors and solutions for single-cell analysis.

---

## Installation Issues

### `ModuleNotFoundError: scanpy`
```bash
pip install scanpy anndata
```

### `ModuleNotFoundError: leidenalg`
Leiden clustering requires leidenalg package:
```bash
pip install leidenalg
```

### `ModuleNotFoundError: umap`
UMAP requires umap-learn:
```bash
pip install umap-learn
```

### `ModuleNotFoundError: harmonypy`
Batch correction requires Harmony:
```bash
pip install harmonypy
```

---

## Data Loading Issues

### Wrong Matrix Orientation
**Problem**: Genes and samples/cells swapped

**Solution**: Check and transpose
```python
# AnnData expects: cells as rows, genes as columns
if df.shape[0] > df.shape[1] * 5:
    print("Transposing: genes were rows")
    df = df.T
adata = ad.AnnData(df)
```

### Index Mismatch
**Problem**: Metadata doesn't align with expression

**Solution**: Find common indices
```python
common = adata.obs_names.intersection(meta.index)
adata = adata[common].copy()
for col in meta.columns:
    adata.obs[col] = meta.loc[common, col]
```

### Gene Name Mismatch
**Problem**: Gene names in different formats (Ensembl vs Symbol)

**Solution**: Convert IDs
```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

result = tu.tools.MyGene_batch_query(
    gene_ids=['ENSG00000141510', 'ENSG00000139618'],
    fields='symbol,ensembl.gene'
)
# Extract symbols from result
```

---

## Sparse Matrix Issues

### `TypeError: can't multiply sequence`
**Problem**: Operating on sparse matrix incorrectly

**Solution**: Convert to dense
```python
from scipy.sparse import issparse

X = adata.X.toarray() if issparse(adata.X) else adata.X
```

### Memory Error
**Problem**: Dataset too large to convert to dense

**Solution**: Use sparse operations
```python
# Good: Works on sparse
mean_expr = np.array(adata.X.mean(axis=0)).flatten()

# Bad: Converts entire matrix to dense
# mean_expr = adata.X.toarray().mean(axis=0)
```

---

## QC and Filtering Issues

### No mitochondrial genes found
**Problem**: Gene names don't start with "MT-"

**Solution**: Check prefix
```python
# Check gene name format
print(adata.var_names[:10])

# Try different prefixes
adata.var['mt'] = adata.var_names.str.startswith(('MT-', 'mt-', 'Mt-'))

# Or manually specify
mt_genes = ['MT-CO1', 'MT-CO2', 'MT-ND1', ...]  # Add all MT genes
adata.var['mt'] = adata.var_names.isin(mt_genes)
```

### All cells filtered out
**Problem**: QC thresholds too stringent

**Solution**: Adjust thresholds
```python
# Check distributions first
print(adata.obs['n_genes_by_counts'].describe())
print(adata.obs['pct_counts_mt'].describe())

# Adjust thresholds
sc.pp.filter_cells(adata, min_genes=100)  # Lower from 200
adata = adata[adata.obs['pct_counts_mt'] < 25].copy()  # Higher from 20
```

---

## Clustering Issues

### `ValueError: n_neighbors must be less than n_samples`
**Problem**: Too few cells for neighbor graph

**Solution**: Reduce n_neighbors
```python
# Default is 15, reduce for small datasets
sc.pp.neighbors(adata, n_neighbors=min(15, adata.n_obs - 1))
```

### Only one cluster
**Problem**: Resolution too low

**Solution**: Increase resolution
```python
# Default is 1.0, increase for more clusters
sc.tl.leiden(adata, resolution=1.5)  # or 2.0
```

### Too many clusters
**Problem**: Resolution too high

**Solution**: Decrease resolution
```python
sc.tl.leiden(adata, resolution=0.3)  # or 0.5
```

---

## Differential Expression Issues

### `ValueError: Not enough cells`
**Problem**: < 3 cells per condition

**Solution**: Skip cell types with insufficient cells
```python
n_treat = (adata_ct.obs['condition'] == 'treatment').sum()
n_ctrl = (adata_ct.obs['condition'] == 'control').sum()

if n_treat < 3 or n_ctrl < 3:
    print(f"Skipping {cell_type}: insufficient cells")
    continue
```

### NaN values in results
**Problem**: Gene not expressed or zero variance

**Solution**: Filter before analysis
```python
# Filter lowly expressed genes
sc.pp.filter_genes(adata, min_cells=3)

# Remove genes with zero variance
from sklearn.feature_selection import VarianceThreshold
selector = VarianceThreshold(threshold=0)
X_filtered = selector.fit_transform(X)
```

---

## Statistical Issues

### NaN in correlation
**Problem**: NaN values in data

**Solution**: Filter NaN before computing
```python
valid = ~np.isnan(gene_lengths) & ~np.isnan(mean_expr)
r, p = stats.pearsonr(gene_lengths[valid], mean_expr[valid])
```

### Inf values in log transform
**Problem**: log(0) = -inf

**Solution**: Use log1p or pseudocount
```python
# Good: log1p(x) = log(x + 1)
sc.pp.log1p(adata)

# Good: log(x + pseudocount)
X_log = np.log10(X + 1)

# Bad: log(x) directly
# X_log = np.log10(X)  # Will produce -inf for zeros
```

---

## Performance Issues

### Memory error on large datasets
**Problem**: Dataset too large to fit in memory

**Solution**: Subsample or use HVG
```python
# Option 1: Subsample cells
sc.pp.subsample(adata, fraction=0.5)

# Option 2: Use only highly variable genes
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
adata = adata[:, adata.var['highly_variable']].copy()
```

### Slow clustering
**Problem**: Large dataset (>100k cells)

**Solution**: Reduce PCs or subsample
```python
# Use fewer PCs
sc.pp.neighbors(adata, n_pcs=20)  # instead of 30

# Or subsample for exploration
adata_sample = sc.pp.subsample(adata, fraction=0.1, copy=True)
# Analyze adata_sample first
```

---

## ToolUniverse Integration Issues

### API timeout
**Problem**: ToolUniverse API call times out

**Solution**: Reduce query size or retry
```python
# Split large queries
batch_size = 50
for i in range(0, len(gene_list), batch_size):
    batch = gene_list[i:i+batch_size]
    result = tu.tools.MyGene_batch_query(gene_ids=batch)
```

### ID conversion fails
**Problem**: Gene IDs not recognized

**Solution**: Try different ID types
```python
# Try Ensembl ID
result = tu.tools.MyGene_query_genes(query="ENSG00000141510")

# Try gene symbol
result = tu.tools.MyGene_query_genes(query="TP53")

# Try with species
result = tu.tools.ensembl_lookup_gene(
    gene_id="ENSG00000141510",
    species="homo_sapiens"
)
```

---

## OmniPath / Cell Communication Issues

### No interactions found
**Problem**: Gene names don't match database

**Solution**: Check gene name format
```python
# OmniPath uses gene symbols (not Ensembl IDs)
# Convert first if needed
result = tu.tools.STRING_map_identifiers(
    protein_ids=['ENSG00000141510'],
    species=9606
)
# Use preferredName from result
```

### Empty communication matrix
**Problem**: Expression thresholds too stringent

**Solution**: Reduce thresholds
```python
expressed_lr = filter_expressed_lr_pairs(
    adata, lr_pairs,
    min_frac=0.02,  # Lower from 0.05
    min_mean=0.01   # Lower from 0.05
)
```

---

## Batch Correction Issues

### Harmony not converging
**Problem**: Batch effects too strong

**Solution**: Adjust Harmony parameters
```python
# Increase max iterations
ho = harmonypy.run_harmony(
    adata.obsm['X_pca'],
    adata.obs,
    'batch',
    max_iter_harmony=20  # Increase from default 10
)
```

### Overcorrection
**Problem**: Biological variation removed

**Solution**: Use fewer PCs or weaker correction
```python
# Use fewer PCs
ho = harmonypy.run_harmony(
    adata.obsm['X_pca'][:, :20],  # Instead of :30
    adata.obs,
    'batch'
)
```

---

## File Format Issues

### h5ad version mismatch
**Problem**: "Cannot read h5ad file"

**Solution**: Update anndata
```bash
pip install --upgrade anndata
```

### 10X format changed
**Problem**: Features file instead of genes file

**Solution**: Specify file names
```python
# CellRanger v3+
adata = sc.read_10x_mtx(
    "filtered_feature_bc_matrix/",
    var_names='gene_symbols',
    cache=True
)
```

---

## Tips

1. **Always check data shape**: Cells vs genes orientation
2. **Check for NaN/Inf**: Before statistical tests
3. **Visualize before filtering**: Check QC metric distributions
4. **Save intermediate results**: After time-consuming steps
5. **Use try/except**: For robust per-cell-type analysis

---

## Debugging Checklist

- [ ] Data loaded correctly (check shape, obs, var)
- [ ] Matrix oriented correctly (cells as rows)
- [ ] Metadata aligned with expression data
- [ ] No NaN/Inf values in expression
- [ ] QC thresholds appropriate for dataset
- [ ] Sufficient cells per condition (>= 3)
- [ ] Gene names match between data and annotations
- [ ] Sparse matrix handled correctly
- [ ] Random seed set for reproducibility

---

## See Also

- **scanpy_workflow.md** - Standard pipeline
- **clustering_guide.md** - Clustering troubleshooting
- **cell_communication.md** - OmniPath API issues
