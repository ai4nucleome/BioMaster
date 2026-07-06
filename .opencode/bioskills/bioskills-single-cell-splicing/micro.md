## Chemistry Assessment & Tool Selection

_modules: chemistry-assessment, tool-selection, qc_

```python
# Chemistry gate — verify BEFORE any splicing analysis
# 10X 3' (v3/GEM-X/v4/Flex) -> NOT viable for transcriptome-wide splicing
#   pivot to Sierra (APA) or upgrade chemistry to MAS-Iso-seq
# 10X 5' GEX -> limited (near-5'-end events only)
# Smart-seq2/3, FLASH-seq, VASA-seq, STORM-seq -> viable (MARVEL or BRIE2)
# MAS-Iso-seq, scISOr-Seq2, ONT direct cDNA/RNA -> viable (FLAMES, IsoQuant)

# Tool selection by goal:
#   cassette exon + modality (Smart-seq)         -> MARVEL
#   per-cell PSI with uncertainty (low coverage)  -> BRIE2
#   annotation-free cell-state discovery          -> SpliZ
#   regulated AS along pseudotime                 -> Psix
#   APA in 10X 3' (NOT splicing)                  -> Sierra
#   between-cell-type differential splicing       -> pseudobulk leafcutter/rMATS
#   full-length isoforms at scale                 -> MAS-Iso-seq + FLAMES
#   microexons (3-27 nt)                          -> long-read or uLTRA/deSALT aligner

# Verify installed versions before running:
#   pip show <package>; help(module.function)    # Python
#   packageVersion('<pkg>'); ?function_name       # R
#   <tool> --version; <tool> --help              # CLI
# Reference versions: MARVEL 2.0+, BRIE2 0.2.4+, scQuint 0.1+, SpliZ 0.0.1+,
#   Sierra 1.0+, Psix 0.1+, anndata 0.10+, scanpy 1.10+, pandas 2.2+, scipy 1.13+
```

## Junction Quantification & Object Construction

_modules: junction-quantification, star, data-io, marvel, brie2_

```r
library(MARVEL); library(Seurat); library(data.table)

seurat_obj <- readRDS('cells.rds')

# Build wide SJ matrix: first column 'coord.intron' (e.g. 'chr1:100007082:100022621'),
# subsequent columns are per-cell sample IDs with junction counts as values.
# Constructed from STAR SJ.out.tab files (one per cell) merged on intron coord.
sj_files <- list.files('star_pass2/', pattern='SJ.out.tab$', full.names=TRUE)
sj_long <- rbindlist(lapply(sj_files, function(f) {
    d <- fread(f, sep='\t', header=FALSE,
               col.names=c('chr','start','end','strand','motif','annot','unique','multi','overhang'))
    d$coord.intron <- paste(d$chr, d$start, d$end, sep=':')
    d$sample <- gsub('_SJ.out.tab$', '', basename(f))
    d[, .(coord.intron, sample, unique)]
}))
sj <- dcast(sj_long, coord.intron ~ sample, value.var='unique', fill=0)

# SpliceFeature: NAMED LIST keyed by event class
df.feature.list <- list(
    SE   = read.table('events_SE.txt',   header=TRUE, sep='\t'),
    A5SS = read.table('events_A5SS.txt', header=TRUE, sep='\t'),
    A3SS = read.table('events_A3SS.txt', header=TRUE, sep='\t'),
    MXE  = read.table('events_MXE.txt',  header=TRUE, sep='\t'),
    RI   = read.table('events_RI.txt',   header=TRUE, sep='\t')
)

# SplicePheno: per-cell metadata; sample.id maps to SpliceJunction column names
df.pheno <- seurat_obj@meta.data
df.pheno$sample.id <- rownames(df.pheno)

marvel <- CreateMarvelObject(
    SpliceJunction = sj,
    SplicePheno    = df.pheno,
    SpliceFeature  = df.feature.list,
    GeneFeature    = read.table('gene_features.tsv', header=TRUE, sep='\t'),
    Exp            = read.table('tpm.tsv', header=TRUE, sep='\t', row.names=1),
    GTF            = rtracklayer::import('annotation.gtf')
)
```

```bash
# BRIE2 alternative: count splicing events per cell
brie-count \
    -a splicing_events.gff3 \
    -S sample_list.tsv \
    -o brie_counts/ \
    -p 16
```

## Per-Cell PSI Estimation & Modality Classification

_modules: psi-estimation, modality-classification, bayesian-inference, marvel, brie2_

```r
# MARVEL: quantify PSI and classify modality per event class
marvel <- ComputePSI(marvel, CoverageThreshold=10, EventType='SE')
marvel <- AssignModality(marvel, EventType='SE')
# Repeat for other event types: A5SS, A3SS, MXE, RI
```

```bash
# BRIE2: variational inference + LRT against cell-type covariate
brie-quant \
    -i brie_counts/brie_count.h5ad \
    -c cell_metadata.tsv \
    -o brie_quant.h5ad \
    --interceptMode gene \
    --LRTindex All \
    --testBase null \
    --MCsize 3 \
    --batchSize 1000000 \
    -p 16
# --interceptMode gene: gene-specific intercept (recommended)
# --LRTindex All: test all covariates
# --testBase null: null model as LRT reference
# For large cohorts (>10k cells) reduce --batchSize to 100000 or 50000 to avoid OOM
# Verify exact flags via: brie-quant -h
```

```python
import scanpy as sc
adata_splice = sc.read_h5ad('brie_quant.h5ad')
# Per-event covariate effects, ELBO values, and LRT statistics live in
# adata_splice.varm and adata_splice.var; column names depend on BRIE2 version.
# Inspect with: print(adata_splice); print(adata_splice.varm.keys())
# Per-event significance derived from LRT delta-ELBO; threshold ~3 (log-Bayes-factor)
```

## Differential Splicing & Cell-State Association Testing

_modules: differential-splicing, lrt, trajectory, pseudobulk, marvel, spliz, psix, leafcutter_

```r
# MARVEL: differential splicing between two cell groups
marvel <- CompareValues(
    marvel,
    cell.group.g1 = neurons, cell.group.g2 = glia,
    method = 'wilcox', n.cells = 25, psi.delta = 0.1
)
```

```bash
# SpliZ: annotation-free discovery of cell-state-associated splicing
spliz \
    --bams sample1.bam sample2.bam \
    --metadata cell_metadata.tsv \
    --gtf annotation.gtf \
    --output spliz_output/ \
    --threads 8
```

```python
# Psix: regulated AS along trajectories (requires precomputed kNN graph)
import psix
import scanpy as sc

adata = sc.read_h5ad('cells.h5ad')
sc.pp.neighbors(adata, n_neighbors=30, use_rep='X_pca')

psix_obj = psix.Psix(adata, psi_matrix_path='psi_matrix.tsv')
psix_obj.run_psix()
regulated = psix_obj.psix_results.query('psix_score > 1.5 and pvalue < 0.05')
```

```python
# Pseudobulk: aggregate junction counts per cluster, then run leafcutter/rMATS
import pandas as pd
import numpy as np

def pseudobulk_junctions(junction_counts, cell_metadata, groupby='cell_type'):
    out = {}
    for group, cells in cell_metadata.groupby(groupby).groups.items():
        mask = junction_counts.columns.isin(cells)
        out[group] = junction_counts.loc[:, mask].sum(axis=1)
    return pd.DataFrame(out)
```

## APA Analysis with Sierra (10X 3' Pivot)

_modules: apa, sierra, 3utr, alternative-polyadenylation_

```r
library(Sierra)

# 1. Peak-call read pile-ups at 3' ends
peak_file <- FindPeaks(
    output.file = 'peaks.txt',
    gtf.file = 'annotation.gtf',
    bam.file = 'possorted_genome_bam.bam'
)

# 2. Count reads per peak per cell barcode
counts <- CountPeaks(
    peak.sites.file = 'peaks.txt',
    gtf.file = 'annotation.gtf',
    bamfile = 'possorted_genome_bam.bam',
    whitelist.file = 'barcodes.tsv'
)

# 3. Differential UTR usage between cell groups (DEXSeq-style DTU)
apa_results <- DUTest(counts, group1 = ctrl_cells, group2 = trt_cells)
```
```python
# If GTF missing 3'UTR annotations -> few peaks detected
# Fix: use comprehensive GENCODE annotation, or run de-novo peak calling first
```

## Quality Control, Failure Modes & Reconciliation

_modules: qc, failure-modes, reconciliation, doublet-detection, quality-thresholds_

```python
# Quality thresholds (apply before and during splicing analysis)
# Cells per event with reads:    >=50 (per-cell PSI); >=200/cluster (pseudobulk)
# Junction reads per event/cell: >=5 with coverage; <=1 = unreliable
# PSI variance:                  <0.1 within cluster, >0.2 between clusters
# Cells per cluster (pseudobulk):>=100 ideal; >=50 minimum
# Doublet filtering:             REQUIRED (DoubletFinder / Scrublet) before splicing
# snRNA-seq IR:                  high baseline — interpret cautiously

# Per-tool failure modes and fixes:
# MARVEL ComputePSI returns empty:
#   cause: STAR SJ.out.tab missing strand info
#   fix:   re-run STAR with --outSJtype Standard
# MARVEL SpliceJunction matrix error ('no coord.intron column'):
#   cause: long-format instead of wide matrix
#   fix:   use data.table::dcast for long->wide reshape; first col = coord.intron
# MARVEL ggplot error:
#   cause: Seurat version mismatch
#   fix:   match MARVEL and Seurat versions
# BRIE2 NaN loss / OOM:
#   cause: insufficient junction reads per cell; TensorFlow GPU OOM on >10k cells
#   fix:   filter cells min_reads=20; reduce --batchSize to 100000 or 50000
#          (flag is camelCase --batchSize, NOT --batch_size)
# scQuint convergence not reached / all cells one cluster:
#   cause: 10X 3' too sparse; authors recommend AGAINST 10X 3'/5' use
#   fix:   pivot to Sierra (APA) or upgrade chemistry to MAS-Iso-seq
# Psix missing connectivities / empty results:
#   cause: neighbors graph not computed
#   fix:   run sc.pp.neighbors(adata) first; ensure connectivities in adata.obsp
# Sierra no peaks called:
#   cause: GTF missing 3'UTR annotations
#   fix:   use comprehensive GENCODE; or de-novo peak-call first
# FLAMES barcode rescue failed:
#   cause: short-read 10X output not in expected directory
#   fix:   verify cellranger output structure
```
