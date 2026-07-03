## Prepare Data

_modules: preprocessing, normalization, qc_

```python
import scanpy as sc

def prepare_for_mebocost(adata, cell_type_col='cell_type', min_cells=50):
    '''Prepare AnnData for MeboCost analysis.

    Requirements:
    - Log-normalized expression (sc.pp.normalize_total, sc.pp.log1p)
    - Cell type annotations
    - Gene symbols (not Ensembl IDs)
    '''
    # Check normalization (log-normalized data typically max < ~50)
    if adata.X.max() > 50:
        print('Warning: Data may not be log-normalized')

    # Filter rare cell types
    cell_counts = adata.obs[cell_type_col].value_counts()
    valid_types = cell_counts[cell_counts >= min_cells].index
    adata = adata[adata.obs[cell_type_col].isin(valid_types)].copy()

    print(f'Cell types: {len(valid_types)}')
    print(f'Cells: {adata.n_obs}')

    return adata
```

## Run Communication Analysis

_modules: mebocost, communication-inference, permutation_

```python
import mebocost as mbc

def run_mebocost(adata, cell_type_col='cell_type', species='human'):
    '''Run MeboCost metabolite communication analysis.

    Args:
        adata: AnnData with log-normalized expression
        cell_type_col: Column with cell type annotations
        species: 'human' or 'mouse'

    Returns:
        MeboCost object with communication results
    '''
    # Create MeboCost object
    mebo = mbc.create_obj(
        adata=adata,
        group_col=cell_type_col,
        species=species
    )

    # Infer enzyme-metabolite-receptor communication
    # n_permutations: Higher = more accurate p-values but slower
    # 1000 is standard; use 100 for quick exploration
    mebo.infer_commu(n_permutations=1000, seed=42)

    return mebo
```

## Analyze and Filter Results

_modules: results-analysis, filtering, summarization_

```python
def analyze_metabolite_communication(mebo, pval_threshold=0.05):
    '''Extract and summarize significant communications.'''
    results = mebo.commu_res.copy()

    # Filter significant interactions
    sig = results[results['pval'] < pval_threshold]

    # Summary statistics
    summary = {
        'total_interactions': len(results),
        'significant_interactions': len(sig),
        'unique_metabolites': sig['metabolite'].nunique(),
        'unique_sender_types': sig['sender'].nunique(),
        'unique_receiver_types': sig['receiver'].nunique()
    }

    # Top metabolites by frequency
    top_metabolites = sig['metabolite'].value_counts().head(10)

    # Top sender-receiver pairs
    sig['pair'] = sig['sender'] + ' -> ' + sig['receiver']
    top_pairs = sig['pair'].value_counts().head(10)

    return {
        'summary': summary,
        'top_metabolites': top_metabolites,
        'top_pairs': top_pairs,
        'significant_interactions': sig
    }


# MeboCost includes curated metabolite-receptor pairs.
# Major categories:
METABOLITE_CATEGORIES = {
    'amino_acids': ['Glutamine', 'Glutamate', 'Tryptophan', 'Arginine'],
    'lipids': ['Prostaglandin E2', 'Leukotriene B4', 'Sphingosine-1-phosphate'],
    'nucleotides': ['ATP', 'Adenosine', 'UDP'],
    'vitamins': ['Retinoic acid', 'Vitamin D'],
    'other': ['Lactate', 'Succinate', 'Itaconate']
}

def filter_by_category(results, category):
    '''Filter results to a specific metabolite category.'''
    metabolites = METABOLITE_CATEGORIES.get(category, [])
    return results[results['metabolite'].isin(metabolites)]
```

## Visualization

_modules: visualization, heatmap, network_

```python
import matplotlib.pyplot as plt

def plot_communication_network(mebo, pval_threshold=0.05):
    '''Plot metabolite communication network as a sender-receiver heatmap.'''
    # Filter significant
    sig = mebo.commu_res[mebo.commu_res['pval'] < pval_threshold]

    # Aggregate by cell type pair
    pair_counts = sig.groupby(['sender', 'receiver']).size().reset_index(name='count')

    # Build pivot table for heatmap
    pivot = pair_counts.pivot(index='sender', columns='receiver', values='count')
    pivot = pivot.fillna(0)

    plt.figure(figsize=(10, 8))
    plt.imshow(pivot.values, cmap='Reds')
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha='right')
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.colorbar(label='Number of interactions')
    plt.xlabel('Receiver')
    plt.ylabel('Sender')
    plt.title('Metabolite Communication Network')
    plt.tight_layout()

    return plt.gcf()


def plot_metabolite_flow(mebo, metabolite, pval_threshold=0.05):
    '''Visualize communication flow for a specific metabolite.'''
    sig = mebo.commu_res[
        (mebo.commu_res['metabolite'] == metabolite) &
        (mebo.commu_res['pval'] < pval_threshold)
    ]

    print(f'\n{metabolite} communication:')
    for _, row in sig.iterrows():
        print(f"  {row['sender']} ({row['enzyme']}) -> "
              f"{row['receiver']} ({row['receptor']})")
        print(f"    Score: {row['commu_score']:.3f}, p-value: {row['pval']:.4f}")
```

## Compare Conditions

_modules: differential-analysis, comparison, conditions_

```python
import mebocost as mbc

def compare_conditions(adata, condition_col, cell_type_col, species='human'):
    '''Compare metabolite communication between conditions.

    Useful for:
    - Tumor vs normal
    - Treatment vs control
    - Disease vs healthy
    '''
    conditions = adata.obs[condition_col].unique()
    results = {}

    for condition in conditions:
        adata_subset = adata[adata.obs[condition_col] == condition].copy()

        mebo = mbc.create_obj(
            adata=adata_subset,
            group_col=cell_type_col,
            species=species
        )
        mebo.infer_commu(n_permutations=1000, seed=42)

        results[condition] = mebo.commu_res

    # Find differential communications:
    # interactions significant in one condition but not another.
    return results
```
