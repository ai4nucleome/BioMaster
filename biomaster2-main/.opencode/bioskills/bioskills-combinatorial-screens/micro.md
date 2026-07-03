## Architecture Selection & Library Design

_modules: library-design, architecture-selection, singleton-controls, cas12a, big-papi_

```python
# Architecture decision tree: pick architecture from screen goal
ARCHITECTURE = {
    'paralog_buffering_genome_scale': {
        'architecture': 'enCas12a single-array 4-guide multiplex',
        'library': 'Inzolia (Bayle 2024)',
        'rationale': 'Cas9 single-KO misses ~half of paralog-buffered essentials',
    },
    'specific_pathway_pair': {
        'architecture': 'Big Papi paired-Cas9 dual sgRNA cassette',
        'library': 'Custom',
        'rationale': 'Mature methodology; SpCas9 well-characterized',
    },
    'three_or_four_way_KO': {
        'architecture': 'in4mer 4-guide single Cas12a array',
        'library': 'Custom (in4mer)',
        'rationale': 'Single transcript processed by Cas12a; multi-gene',
    },
    'drug_modifier_plus_KO': {
        'architecture': 'Cas9 KO + drug treatment',
        'library': 'Standard libraries',
        'rationale': 'Drug as second perturbation',
    },
}

# Library design requirements
LIBRARY_REQUIREMENTS = {
    'cas9_paired_cassettes_per_pair': '4-6',
    'cas12a_in4mer_arrays_per_pair': 4,
    'singletons_per_single_gene': '4-6 (REQUIRED for GI scoring)',
    'cells_per_cassette_at_infection': '>=500',
    'cas12a_editing_efficiency_for_inclusion': '>50%',
}

# Verify versions before running
# CLI: mageck --version ; mageck mle --help
# For Cas12a libraries: verify against published Inzolia / in4mer / Big Papi annotations
```

## Library QC & Singleton Verification

_modules: qc, library-skew, gini, singleton-verification, coverage_

```python
import pandas as pd
import numpy as np

def library_qc(counts_df, gene_pairs=None, min_cells=500):
    '''QC a combinatorial library count table.
    counts_df: rows = cassettes/sgRNAs; columns = sample count columns.
    gene_pairs: optional cassette_id -> [gene_A, gene_B, ...] annotation.
    Returns a QC report DataFrame.
    '''
    report = {}
    total = counts_df.select_dtypes('number').sum(axis=0)
    report['total_reads_per_sample'] = total.to_dict()
    # Gini coefficient of cassette representation (per sample)
    def gini(x):
        x = np.sort(np.asarray(x, dtype=float))
        n = len(x)
        cum = np.cumsum(x)
        return (n + 1 - 2 * np.sum(cum) / cum[-1]) / n if cum[-1] > 0 else np.nan
    report['gini_per_sample'] = {s: gini(counts_df[s].values) for s in total.index}
    # Per-cassette coverage (mean across samples)
    mean_cov = counts_df.select_dtypes('number').mean(axis=1)
    report['low_coverage_cassettes'] = int((mean_cov < min_cells).sum())
    report['median_coverage'] = float(np.median(mean_cov))
    # Singleton presence check
    if gene_pairs is not None:
        gp = gene_pairs.copy()
        # singleton = cassette where only one real gene is targeted (others placeholder)
        n_real = gp[[c for c in gp.columns if c.startswith('gene_')]].notna().sum(axis=1)
        report['singleton_cassettes'] = int((n_real == 1).sum())
        report['paired_cassettes'] = int((n_real == 2).sum())
    return pd.DataFrame([report])

# Version checks (run in shell):
#   mageck --version
#   python -c "import pandas,numpy,scipy,matplotlib; print(pandas.__version__,numpy.__version__,scipy.__version__,matplotlib.__version__)"
```

## MAGeCK MLE with Interaction Terms (Cas9 / Big Papi Path)

_modules: mageck-mle, interaction-terms, design-matrix, big-papi, cas9_

```bash
# Design matrix encoding double-KO as a separate interaction indicator.
# Conditions: NT (control), A_KO, B_KO, A_B_KO
cat > combo_design.txt <<EOF
Samples         baseline    geneA       geneB       interaction
NT_r1           1           0           0           0
NT_r2           1           0           0           0
A_r1            1           1           0           0
A_r2            1           1           0           0
B_r1            1           0           1           0
B_r2            1           0           1           0
AB_r1           1           1           1           1
AB_r2           1           1           1           1
EOF

mageck mle \
    --count-table combo_counts.txt \
    --design-matrix combo_design.txt \
    --output-prefix combo_mle

# Output: per-gene beta scores per design column.
# interaction|beta  = additional effect under joint perturbation beyond sum of singles.
# interaction|fdr   = significance of interaction|beta vs zero.
# Negative interaction|beta -> synthetic lethal; positive -> synthetic rescue.
```

```python
import pandas as pd

def read_mle_interaction(prefix='combo_mle'):
    '''Parse MAGeCK MLE gene summary and extract interaction betas.'''
    df = pd.read_csv(f'{prefix}.gene_summary.txt', sep='\t')
    # Columns of interest: geneA|beta, geneB|beta, interaction|beta, interaction|fdr
    cols = [c for c in df.columns if c.endswith('|beta') or c.endswith('|fdr')]
    return df[['Gene'] + cols]
```

## Cas12a 4-Guide Array Aggregation (in4mer / Inzolia Path)

_modules: cas12a, in4mer, inzolia, cassette-aggregation, lfc_

```python
import pandas as pd
import numpy as np

def in4mer_pair_analysis(paired_counts_df, gene_pairs, control_samples=None):
    '''Aggregate cassette-level counts to per-pair LFCs for in4mer/Inzolia screens.
    paired_counts_df: rows = cassettes; columns = sample count columns.
    gene_pairs: DataFrame with cassette_id -> [gene_A, gene_B, gene_C, gene_D].
    control_samples: list of control (NT) sample column names for LFC baseline.
    Returns per-pair mean LFC and per-singleton LFC.
    '''
    merged = paired_counts_df.merge(gene_pairs, on='cassette_id')
    count_cols = [c for c in paired_counts_df.columns if c not in ('cassette_id',)]
    if control_samples is None:
        control_samples = [c for c in count_cols if c.startswith('NT')]
    ctrl = merged[control_samples].mean(axis=1)
    # LFC per cassette (log2 ratio vs control mean, pseudocount 1)
    for s in count_cols:
        merged[f'{s}_lfc'] = np.log2((merged[s] + 1) / (ctrl + 1))
    lfc_cols = [f'{s}_lfc' for s in count_cols]
    # Aggregate by (gene_A, gene_B) pair
    pair_lfc = merged.groupby(['gene_A', 'gene_B'])[lfc_cols].agg(['mean', 'std', 'count'])
    # Singleton LFCs (cassettes where only one real gene is targeted)
    n_real = merged[[c for c in merged.columns if c.startswith('gene_')]].notna().sum(axis=1)
    singletons = merged[n_real == 1]
    single_lfc = {}
    for _, row in singletons.iterrows():
        gene = next(row[c] for c in singletons.columns if c.startswith('gene_') and pd.notna(row[c]))
        single_lfc.setdefault(gene, []).append(row[lfc_cols].mean())
    single_lfc = {g: np.mean(v) for g, v in single_lfc.items()}
    return pair_lfc, single_lfc
```

## Genetic Interaction Scoring

_modules: gi-scoring, synthetic-lethal, synthetic-rescue, additive-null, zscore_

```python
import pandas as pd
import numpy as np
from scipy.stats import zscore

def gi_score(paired_lfc_df, single_lfc_df):
    '''Score genetic interactions from paired vs single LFCs.
    paired_lfc_df: rows = paired-KO; columns = ['gene_A', 'gene_B', 'paired_lfc']
    single_lfc_df: rows = single-KO; columns = ['gene', 'single_lfc']
    Returns DataFrame sorted by gi_z with classification column.
    '''
    single = dict(zip(single_lfc_df['gene'], single_lfc_df['single_lfc']))
    df = paired_lfc_df.copy()
    df['single_A_lfc'] = df['gene_A'].map(single)
    df['single_B_lfc'] = df['gene_B'].map(single)
    df['expected_additive'] = df['single_A_lfc'] + df['single_B_lfc']
    df['gi_score'] = df['paired_lfc'] - df['expected_additive']
    df['gi_z'] = zscore(df['gi_score'])
    df['gi_class'] = np.where(df['gi_z'] < -2, 'synthetic_lethal',
                                np.where(df['gi_z'] > 2, 'synthetic_rescue', 'no_interaction'))
    return df.sort_values('gi_z')

# Classification thresholds:
#   GI z < -2  -> synthetic lethal (candidate drug-target combinations)
#   GI z >  2  -> synthetic rescue (compensatory pathway / paradoxical hit)
#   -1 <= z <= 1 -> no interaction (additive)
```

## Failure Diagnosis & Cross-Modality Validation

_modules: failure-diagnosis, validation, saturation, cross-modality, quality-control_

```python
import pandas as pd
import numpy as np

def diagnose_failures(gi_df, coverage_df=None, editing_eff=None):
    '''Flag likely failure modes in a GI result table.
    gi_df: output of gi_score() with columns gene_A, gene_B, gi_z, gi_class.
    coverage_df: optional cassette_id -> mean coverage; flag low-coverage pairs.
    editing_eff: optional dict gene -> Cas12a editing efficiency fraction.
    Returns a flagged copy of gi_df.
    '''
    df = gi_df.copy()
    df['flag'] = ''
    # Saturation artifact: positive GI (rescue) for pairs of strong single negatives
    if 'single_A_lfc' in df.columns and 'single_B_lfc' in df.columns:
        both_strong = (df['single_A_lfc'] < -1) & (df['single_B_lfc'] < -1)
        df.loc[both_strong & (df['gi_z'] > 2), 'flag'] += 'saturation_artifact;'
    # Low editing efficiency loci (Cas12a)
    if editing_eff is not None:
        low_eff = df['gene_A'].map(editing_eff).fillna(1) < 0.5
        df.loc[low_eff, 'flag'] += 'low_cas12a_efficiency;'
    # Missing singletons
    df.loc[df['single_A_lfc'].isna() | df['single_B_lfc'].isna(), 'flag'] += 'missing_singleton;'
    return df

# Cross-modality validation checklist for high-stakes synthetic-lethal hits:
VALIDATION_STEPS = [
    '1. Orthogonal chemistry: re-validate with Cas9 if Cas12a screen (or vice versa).',
    '2. Arrayed validation: single-KO arrayed setup in same cell line; quantify proliferation.',
    '3. CRISPRi orthogonal: dCas9-KRAB knockdown to confirm phenotype without DNA damage.',
    '4. Pharmacological: inhibit paralog with drug; confirms target accessibility for drug development.',
]
```
