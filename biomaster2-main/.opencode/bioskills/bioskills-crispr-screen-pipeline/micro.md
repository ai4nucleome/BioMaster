## Library Design and Pre-Screen Validation

_modules: library-design, qc, validation, gini_

```bash
# Pre-screen library validation checklist (apply to plasmid pool counts):
#   - Plasmid pool Gini < 0.1
#   - >= 99% guides detected at > 25 reads/guide
#   - Skew (p90 / p10) < 2
#   - NTCs comprise ~1% of library
#   - CEGv2 reference essentials + NEGv1 non-essentials included
```

```python
import numpy as np
import pandas as pd

def gini(x):
    x = np.sort(x[x > 0].astype(float))
    if x.size == 0:
        return np.nan
    n = x.size
    cumx = np.cumsum(x)
    return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n

# plasmid_counts: array/Series of per-guide read counts in the plasmid pool
gini_val = gini(plasmid_counts)
pct_detected = (plasmid_counts > 25).mean() * 100
p90, p10 = np.percentile(plasmid_counts, [90, 10])
skew = p90 / p10
print(f"Gini={gini_val:.3f}  detected={pct_detected:.1f}%  skew={skew:.2f}")
assert gini_val < 0.1 and pct_detected >= 99 and skew < 2
```

## Guide Counting

_modules: counting, mageck, fastq, normalization_

```bash
mageck count \
    --list-seq library.csv \
    --sample-label Plasmid,Day0,Veh_r1,Veh_r2,Drug_r1,Drug_r2 \
    --fastq Plasmid.fq.gz Day0.fq.gz Veh_r1.fq.gz Veh_r2.fq.gz Drug_r1.fq.gz Drug_r2.fq.gz \
    --norm-method median \
    --output-prefix experiment \
    --trim-5 CACCG
```

# Outputs:
#   experiment.count.txt            -> raw count matrix (genes x samples)
#   experiment.countsummary.txt     -> per-sample Gini, mapping rate, % zero

## Quality Control

_modules: qc, gini, replicate-correlation, pr-auc, screen-qc_

```python
import pandas as pd
import numpy as np
from sklearn.metrics import precision_recall_curve, auc

counts = pd.read_csv('experiment.count.txt', sep='\t', index_col=0)
genes = counts['Gene']
count_matrix = counts.drop('Gene', axis=1)

def gini(x):
    x = np.sort(x[x > 0].astype(float))
    if x.size == 0:
        return np.nan
    n = x.size
    cumx = np.cumsum(x)
    return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n

per_sample = pd.DataFrame({
    'pct_zero': (count_matrix == 0).sum() / len(count_matrix) * 100,
    'gini': count_matrix.apply(gini),
    'reads_per_sgrna': count_matrix.sum() / len(count_matrix),
})

log_counts = np.log10(count_matrix + 1)
pearson = log_counts.corr()
print(per_sample)
print('Replicate Pearson:', pearson.values[pearson.values < 1].mean())

# Hard gates (screen-qc):
#   - Plasmid Gini < 0.1; endpoint < 0.3 (or < 0.55 for heavy drug screens)
#   - Replicate Pearson on log-counts > 0.85
#   - CEGv2 PR-AUC > 0.7 against Hart 2017 reference essential gene set
#   - Reads per sgRNA per sample >= 300 (DepMap convention)
```

## Copy-Number and Batch Correction

_modules: copy-number, batch-correction, crisprcleanr, chronos, mageck-mle_

```r
library(CRISPRcleanR)
data(KY_Library_v1.0)
norm <- ccr.NormfoldChanges(read.table('experiment.count.txt', header=TRUE, sep='\t'),
                              min_reads = 30, EXPname = 'screen',
                              libraryAnnotation = KY_Library_v1.0)
gw_lfc <- ccr.logFCs2chromPos(norm$norm_fold_changes, KY_Library_v1.0)
cleaned <- ccr.GWclean(gw_lfc, display = TRUE, label = 'screen')
corrected_counts <- ccr.correctCounts(my_screen = norm, correction = cleaned,
                                        outprefix = 'screen_cleanr',
                                        libraryAnnotation = KY_Library_v1.0)
# Feed corrected counts into MAGeCK / BAGEL2 / drugZ downstream.
# For DepMap-scale panels with longitudinal data + matched CN, use Chronos instead.
```

```bash
# Multi-batch screens: add batch as a covariate in MAGeCK MLE (do NOT pre-correct with ComBat).
# design.txt columns: sample, batch, condition, [interaction terms]
mageck mle --count-table experiment.count.txt --design-matrix design.txt \
    --output-prefix batch_mle --norm-method median
```

## Hit Calling

_modules: hit-calling, mageck-rra, mageck-mle, bagel, drugz, jacks, chronos_

```bash
# 6a. Two-condition essentiality -- MAGeCK RRA
mageck test \
    --count-table experiment.count.txt \
    --treatment-id Day14_r1,Day14_r2,Day14_r3 \
    --control-id Day0 \
    --norm-method median \
    --output-prefix essentiality_rra
```

```bash
# 6a. Two-condition essentiality -- BAGEL2
BAGEL.py fc -i experiment.count.txt -o foldchange.txt -c Day0 --min-reads 30
BAGEL.py bf -i foldchange.txt -o bayes_factor.txt -e CEGv2.txt -n NEGv1.txt \
    -c Day14_r1,Day14_r2,Day14_r3 -k 1000
```

```bash
# 6b. Time-course / multi-condition -- MAGeCK MLE
mageck mle --count-table experiment.count.txt --design-matrix design.txt \
    --output-prefix timecourse_mle --norm-method median
```

```bash
# 6c. Drug-modifier -- drugZ (vehicle as control, NOT Day-0)
python drugz.py \
    -i experiment.count.txt \
    -o drugz_output.txt \
    -c Veh_r1,Veh_r2,Veh_r3 \
    -x Drug_r1,Drug_r2,Drug_r3 \
    -p 5
```

```bash
# 6d. Multi-screen joint analysis -- JACKS
python run_JACKS.py experiment.count.txt replicatemap.txt guidemap.txt \
    --rep_hdr Replicate --sample_hdr Sample --ctrl_sample_hdr Control \
    --sgrna_hdr sgRNA --gene_hdr Gene --outprefix jacks_out --apply_w_hp
```

```python
# 6e. Cancer cell-line panels -- Chronos (DepMap standard)
import chronos
model = chronos.Chronos(sequence_map=sequence_map, guide_gene_map=guide_gene_map,
                          reads=counts_df, copy_number=cn_df)
model.train(n_steps=2000)
gene_effects = model.gene_effect()
```

## Consensus and Visualization

_modules: consensus, tiering, visualization, volcano, enrichment, mageckflute_

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Tier-based consensus ---
mageck = pd.read_csv('essentiality_rra.gene_summary.txt', sep='\t')[['id', 'neg|fdr']].rename(
    columns={'id': 'gene', 'neg|fdr': 'mageck_neg_fdr'})
bagel = pd.read_csv('bayes_factor.txt', sep='\t')[['GENE', 'BF']].rename(
    columns={'GENE': 'gene', 'BF': 'bagel_bf'})
drugz_df = pd.read_csv('drugz_output.txt', sep='\t')[['GENE', 'fdr_synth']].rename(
    columns={'GENE': 'gene', 'fdr_synth': 'drugz_synth_fdr'})

merged = mageck.merge(bagel, on='gene', how='outer').merge(drugz_df, on='gene', how='outer')
merged['mageck_hit'] = merged['mageck_neg_fdr'] < 0.05
merged['bagel_hit'] = merged['bagel_bf'] > 6
merged['drugz_hit'] = merged['drugz_synth_fdr'] < 0.05
merged['tier'] = merged[['mageck_hit', 'bagel_hit', 'drugz_hit']].astype(int).sum(axis=1)
tier1 = merged[merged['tier'] >= 3]
tier2 = merged[merged['tier'] == 2]
merged.to_csv('tier_consensus.csv', index=False)
```

```python
# --- Volcano plot ---
fig, ax = plt.subplots(figsize=(10, 8))
gene_summary = pd.read_csv('essentiality_rra.gene_summary.txt', sep='\t')
sig = gene_summary['neg|fdr'] < 0.05
ax.scatter(gene_summary.loc[~sig, 'neg|lfc'],
            -np.log10(gene_summary.loc[~sig, 'neg|fdr'].clip(lower=1e-10)),
            c='lightgray', alpha=0.5, s=10)
ax.scatter(gene_summary.loc[sig, 'neg|lfc'],
            -np.log10(gene_summary.loc[sig, 'neg|fdr'].clip(lower=1e-10)),
            c='red', alpha=0.7, s=18)
ax.axhline(-np.log10(0.05), ls='--', c='black', lw=0.5)
ax.set_xlabel('Log2 Fold Change')
ax.set_ylabel('-Log10(FDR)')
plt.savefig('volcano.png', dpi=150)
```

```r
# --- MAGeCKFlute one-shot enrichment dashboard ---
# library(MAGeCKFlute)
# FluteRRA(gene_summary = 'essentiality_rra.gene_summary.txt',
#          lfcCutoff = 1, prefix = 'flute_rra')
# FluteMLE(...)  # for MLE-based results
```
