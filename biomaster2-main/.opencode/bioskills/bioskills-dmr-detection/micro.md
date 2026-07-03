## Data Loading & Preprocessing

_modules: data-loading, coverage-filter, bismark_

```r
library(methylKit)
library(bsseq)

# --- methylKit path (Bismark coverage files) ---
meth_obj <- methRead(location = file_list, sample.id = sample_ids,
                     treatment = treatment, assembly = 'hg38',
                     pipeline = 'bismarkCoverage')
meth_filt <- filterByCoverage(meth_obj, lo.count = 10, hi.perc = 99.9)

# --- bsseq path (Bismark CpG reports) ---
bs <- read.bismark(files = c('sample1.CpG_report.txt.gz',
                             'sample2.CpG_report.txt.gz'),
                   sampleNames = c('ctrl', 'treat'),
                   rmZeroCov = TRUE, strandCollapse = TRUE)

# --- DMRcate path (array beta matrix) ---
# meth_matrix: rows = CpGs, columns = samples
design <- model.matrix(~ treatment)
```

## DMR Detection

_modules: dmr-detection, tiling, smoothing, differential-methylation, qvalue_

```r
# --- methylKit tile-based DMRs ---
tiles <- tileMethylCounts(meth_filt, win.size = 1000, step.size = 1000,
                          cov.bases = 3)
tiles_united <- unite(tiles, destrand = TRUE)
diff_tiles <- calculateDiffMeth(tiles_united, overdispersion = 'MN',
                                mc.cores = 4)
dmrs <- getMethylDiff(diff_tiles, difference = 25, qvalue = 0.01)
dmrs_hyper <- getMethylDiff(diff_tiles, difference = 25, qvalue = 0.01,
                            type = 'hyper')
dmrs_hypo  <- getMethylDiff(diff_tiles, difference = 25, qvalue = 0.01,
                            type = 'hypo')

# --- bsseq BSmooth DMRs ---
bs_smooth <- BSmooth(bs, mc.cores = 4, verbose = TRUE)
bs_cov <- getCoverage(bs_smooth)
keep <- which(rowSums(bs_cov >= 2) == ncol(bs_cov))
bs_filt <- bs_smooth[keep, ]
dmrs_bsseq <- dmrFinder(bs_filt, cutoff = c(-0.1, 0.1),
                        stat = 'tstat.corrected')

# --- DMRcate (array data) ---
library(DMRcate); library(minfi)
myannotation <- cpg.annotate('array', meth_matrix, what = 'Beta',
                             arraytype = 'EPIC', design = design, coef = 2)
dmr_results <- dmrcate(myannotation, lambda = 1000, C = 2)
dmr_ranges <- extractRanges(dmr_results)
```

## DMR Refinement & Merging

_modules: merge, refinement, granges_

```r
library(GenomicRanges)

dmr_gr <- as(dmrs, 'GRanges')

# Merge DMRs within 500 bp
dmr_merged <- reduce(dmr_gr, min.gapwidth = 500)
```

## Genomic Annotation

_modules: annotation, genes, promoters, cpg-islands_

```r
# --- annotatr ---
library(annotatr)
annots <- build_annotations(genome = 'hg38', annotations = c(
    'hg38_basicgenes',
    'hg38_genes_promoters',
    'hg38_cpg_islands'
))
dmr_annotated <- annotate_regions(regions = dmr_gr, annotations = annots,
                                  ignore.strand = TRUE)
dmr_df <- data.frame(dmr_annotated)

# --- genomation alternative ---
library(genomation)
gene_obj <- readTranscriptFeatures('genes.bed12')
annot_result <- annotateWithGeneParts(dmr_gr, gene_obj)
getTargetAnnotationStats(annot_result, percentage = TRUE, precedence = TRUE)
```

## Visualization & Export

_modules: visualization, export, gviz, bed_

```r
library(Gviz)
library(rtracklayer)

# --- Visualization ---
chr <- 'chr1'; start <- 1000000; end <- 1010000
meth_track <- DataTrack(range = bs_smooth, genome = 'hg38',
                        name = 'Methylation', type = 'smooth')
gene_track <- GeneRegionTrack(TxDb.Hsapiens.UCSC.hg38.knownGene,
                              genome = 'hg38', name = 'Genes')
plotTracks(list(meth_track, gene_track), from = start, to = end,
           chromosome = chr)

# --- Export ---
export(dmr_gr, 'dmrs.bed',  format = 'BED')
export(dmr_gr, 'dmrs.gff3', format = 'GFF3')
dmr_df <- getData(dmrs)
write.csv(dmr_df, 'dmrs.csv', row.names = FALSE)
```
