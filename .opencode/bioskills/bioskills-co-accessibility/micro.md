## Input Preparation

_modules: input-preparation, monocle3, cds, peak-formatting_

```r
library(cicero); library(monocle3); library(GenomicRanges)

# Input: peak-cell binary matrix from Signac/ArchR (rows = peaks, cols = cells)
# Convert peaks to "chrN_start_end" format required by Cicero
peak_names <- paste0(seqnames(peaks), '_', start(peaks), '_', end(peaks))

input_cds <- new_cell_data_set(peak_matrix,
                               cell_metadata = metadata,
                               gene_metadata = peak_metadata)
```

ArchR alternative (input is an existing ArchR project; ensure PeakMatrix exists):
```r
library(ArchR)
proj <- loadArchRProject('ArchR_out')
# getCoAccessibility requires a PeakMatrix, not a TileMatrix
proj <- addPeakMatrix(proj)
```

SCENIC+ alternative (Multiome: paired RNA + ATAC + motifs):
```python
import scenicplus as sp

scplus_obj = sp.create_SCENICPLUS_object(
    GEX_anndata = rna_adata,      # paired RNA AnnData
    cisTopic_obj = topic_obj,     # pycisTopic cisTopic object
    menr = motif_enr_dict)        # motif-enrichment dictionary
```

## Dimensionality Reduction & Metacell Aggregation

_modules: dimensionality-reduction, lsi, umap, metacell, make_cicero_cds_

```r
# Reduce dimensionality (UMAP from LSI-preprocessed input)
input_cds <- detect_genes(input_cds)
input_cds <- estimate_size_factors(input_cds)
input_cds <- preprocess_cds(input_cds, method = 'LSI')
input_cds <- reduce_dimension(input_cds,
                              reduction_method = 'UMAP',
                              preprocess_method = 'LSI')

# Build metacell-aggregated CDS (default k = 50 cells per metacell)
umap_coords <- reducedDims(input_cds)$UMAP
cicero_cds <- make_cicero_cds(input_cds,
                             reduced_coordinates = umap_coords,
                             k = 50)
```

Notes:
- If make_cicero_cds is slow / crashes: reduce k or subsample cells.
- For per-cluster runs: subset input_cds by cluster label before make_cicero_cds, run each cluster separately, then merge connection tables with a cluster column.

## Co-accessibility Inference

_modules: co-accessibility, cicero, graphical-lasso, run_cicero, archr, scenicplus_

```r
# Run Cicero with hg38 chrom sizes
library(BSgenome.Hsapiens.UCSC.hg38)
genome_df <- data.frame(
    chr    = seqnames(seqinfo(BSgenome.Hsapiens.UCSC.hg38)),
    length = seqlengths(seqinfo(BSgenome.Hsapiens.UCSC.hg38)))

conns <- run_cicero(cicero_cds,
                   genomic_coords = genome_df,
                   window = 500000,     # 500 kb cis (widen to 1e6 for gene-desert TADs)
                   sample_num = 100)

# (Optional) data-driven alpha via distance parameter estimation
# dp <- estimate_distance_parameter(cicero_cds, window = 500000,
#                                    maxit = 100, sample_num = 100)
```

ArchR alternative (Cicero wrapper inside ArchR):
```r
proj <- addCoAccessibility(proj,
                          reducedDims = 'IterativeLSI',
                          k = 100, knnIteration = 500,
                          maxDist = 250000)   # 250 kb cis (tighter than Cicero default)
co_acc <- getCoAccessibility(proj,
                            corCutOff = 0.5,   # default 0.5; lower for more (calibrate vs Hi-C)
                            returnLoops = FALSE)
```

SCENIC+ alternative (TF-driven enhancer-gene networks; requires Multiome):
```python
import scenicplus as sp

sp.run_scenicplus(scplus_obj, ...)
# Output: TF -> enhancer -> gene triples in scplus_obj.uns['eRegulon_metadata']
```

## Connection Filtering & Visualization

_modules: thresholding, visualization, arc-plot, genome-browser, genomicinteractions_

```r
# Filter to high-confidence connections.
# Threshold 0.25 is a Cicero-documentation working default; the optimal cutoff
# is dataset-dependent and is best calibrated against orthogonal Hi-C / HiChIP.
strong <- conns[conns$coaccess > 0.25, ]
cat(sprintf('Total conns: %d; strong (>0.25): %d\n',
            nrow(conns), nrow(strong)))

# Arc plot at a locus of interest
library(Gviz); library(GenomicInteractions)
gi <- GenomicInteractions(anchorOne = GRanges(strong[, 1:3]),
                          anchorTwo  = GRanges(strong[, 4:6]),
                          counts     = as.integer(strong$coaccess * 100))
plotInteractions(gi, view = 'arc', interactions.color = 'red')
```

ArchR genome-browser visualization:
```r
# Peak-gene linkage matrix
plotPeak2GeneHeatmap(proj)
# Overlay connections on genome-browser tracks
plotBrowserTrack(proj, groupby = 'Clusters', region = 'chr1-1000000-2000000')
```

## Hi-C Concordance Validation

_modules: validation, hi-c, concordance, hiccups, genomicinteractions_

```r
# Compare Cicero against published Hi-C loops
library(GenomicInteractions)

hic_loops <- import('hiccups_loops.bedpe', format = 'bedpe')
ci <- GenomicInteractions(anchorOne = GRanges(strong$Peak1),
                          anchorTwo  = GRanges(strong$Peak2))
overlap <- countOverlaps(ci, hic_loops, type = 'equal') > 0
cat(sprintf('Cicero connections overlapping HiCCUPS loops: %.1f%%\n',
            100 * mean(overlap)))
```

Interpretation guide:
- > 50% overlap  -> high confidence; Cicero captures real 3D structure
- 30-50% overlap -> standard; some 3D contacts don't vary in accessibility
- < 20% overlap  -> co-accessibility may not reflect contacts; lineage-specific contacts may be missing

Decision rule: if Hi-C / Micro-C is available, use the ABC model (atac-seq/enhancer-gene-linking)
as the primary enhancer-gene method and treat Cicero as an ATAC-only sanity check.
