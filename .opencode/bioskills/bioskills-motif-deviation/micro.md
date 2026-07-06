## Data Preparation

_modules: qc, filtering, gc-bias, summarized-experiment_

```r
library(chromVAR); library(motifmatchr); library(BSgenome.Hsapiens.UCSC.hg38)
library(SummarizedExperiment)

peaks <- rtracklayer::import('consensus_peaks.bed')                # GRanges
# If addGCBias errors on missing seqlengths:
#   seqlengths(peaks) <- seqlengths(BSgenome.Hsapiens.UCSC.hg38)
counts <- as.matrix(read.delim('peak_counts.tsv', row.names=1))    # rows=peaks, cols=samples
se <- SummarizedExperiment(assays=list(counts=counts), rowRanges=peaks)
se <- addGCBias(se, genome=BSgenome.Hsapiens.UCSC.hg38)

# Quality filters: depth >= 1500, FRiP >= 0.15, peak in >= 10% samples with >= 10 reads
se <- filterSamples(se, min_depth=1500, min_in_peaks=0.15, shiny=FALSE)
se <- filterPeaks(se, non_overlapping=TRUE, min_count=10, n_samples_frac=0.1)

# Single-cell prerequisites (finalize peak set BEFORE motif matching):
#   Signac: seurat_obj with ATAC assay + consensus peaks already in place
#   ArchR:  proj <- addReproduciblePeakSet(proj, groupBy='Clusters', pathToMacs2='/path/macs2')
#           proj <- addPeakMatrix(proj)
```

## Motif Matching

_modules: motif-matching, jaspar, cisbp, motifmatchr_

```r
library(JASPAR2024); library(TFBSTools); library(RSQLite)

# JASPAR2024 + TFBSTools workaround (TFBSTools issue #39):
jaspar2024 <- JASPAR2024::JASPAR2024()
sq <- dbConnect(SQLite(), db(jaspar2024))
pfm <- getMatrixSet(sq, opts=list(collection='CORE', tax_group='vertebrates'))
# JASPAR2020 (older) accepts the package object directly:
#   pfm <- getMatrixSet(JASPAR2020, opts=list(collection='CORE', tax_group='vertebrates'))

# Bulk chromVAR:
motif_ix <- matchMotifs(pfm, se, genome=BSgenome.Hsapiens.UCSC.hg38, p.cutoff=5e-05)

# Signac:
seurat_obj <- AddMotifs(seurat_obj, genome=BSgenome.Hsapiens.UCSC.hg38, pfm=pfm)

# ArchR (cisbp default; switch to 'JASPAR2020' for fewer curated motifs):
proj <- addMotifAnnotations(proj, motifSet='cisbp', name='Motif')
```

## Deviation Computation

_modules: chromvar, background-peaks, deviations, variability_

```r
# Bulk chromVAR:
bg <- getBackgroundPeaks(object=se, niterations=50)
dev <- computeDeviations(object=se, annotations=motif_ix, background_peaks=bg)
zscores <- deviations(dev)               # motif x sample z-score matrix
variability <- computeVariability(dev)   # per-motif variability ranking

# Signac:
seurat_obj <- RunChromVAR(seurat_obj,
                          genome=BSgenome.Hsapiens.UCSC.hg38,
                          new.assay.name='chromvar')
DefaultAssay(seurat_obj) <- 'chromvar'

# ArchR:
proj <- addBgdPeaks(proj)
proj <- addDeviationsMatrix(proj, peakAnnotation='Motif')
```

## Differential Motif Analysis

_modules: differential, limma, findmarkers, marker-features_

```r
library(limma)
# Bulk: limma on z-scores
-groups <- factor(colData(se)$condition, levels=c('control', 'treated'))  # first level = reference
design <- model.matrix(~groups)
fit <- lmFit(zscores, design); fit <- eBayes(fit)
diff_motifs <- topTable(fit, coef=2, number=Inf, p.value=0.05)   # use adj.P.Val (BH FDR), not 'FDR'

# Signac: per-cluster differential motifs (mean.fxn=rowMeans is REQUIRED for z-scores)
markers <- FindAllMarkers(seurat_obj, only.pos=TRUE,
                          mean.fxn=rowMeans, fc.name='avg_diff')

# ArchR: per-cluster deviation summary
markersMotifs <- getMarkerFeatures(proj, useMatrix='MotifMatrix',
                                   groupBy='Clusters', useSeqnames='z')
```

## Multi-Method TF Activity Integration

_modules: decoupler, tf-activity, consensus, multi-omics_

```python
import decoupler as dc
# adata: AnnData with motif_x_cell chromVAR deviation matrix in adata.obsm['chromvar']
# collectri_net: TF-target network (e.g. dc.op_resource('Collectri'))
acts_ulm = dc.run_ulm(mat=adata.obsm['chromvar'], net=collectri_net,
                      source='source', target='target')
acts_mlm = dc.run_mlm(mat=adata.obsm['chromvar'], net=collectri_net,
                      source='source', target='target')
acts_consensus = dc.run_consensus(mat=adata.obsm['chromvar'], net=collectri_net)
```
