## Annotation Source Setup

_modules: setup, txdb, gtf, coordinate-system, convention_

```r
# --- Standard genome: load pre-built TxDb + annoDb ---
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)
txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

# --- Custom GTF: build TxDb (symbols mapped later, no annoDb) ---
library(GenomicFeatures)
library(rtracklayer)
txdb <- makeTxDbFromGFF('genes.gtf.gz', format = 'gtf')

# Verify genome match; fix chr vs no-chr naming if needed
seqlevelsStyle(peaks) <- 'UCSC'
stopifnot(all(seqlevels(peaks) == seqlevels(txdb)))
```

```python
# --- Coordinate conversions (BED 0-based half-open, GTF 1-based closed) ---
peak_center = (start + end) // 2

# TSS from GTF (1-based -> 0-based)
tss_0based = (start - 1) if strand == '+' else end

# Signed distance (negative = upstream of TSS)
distance = (peak_center - tss) if strand == '+' else -(peak_center - tss)
```

## Gene-Feature Annotation

_modules: chipseeker, homer, annotatepeak, gene-feature, promoter_

```r
# --- ChIPseeker: standard genome ---
peaks <- readPeakFile('peaks.narrowPeak')
peak_anno <- annotatePeak(peaks,
                           TxDb = txdb,
                           tssRegion = c(-2000, 2000),
                           annoDb = 'org.Hs.eg.db',
                           overlap = 'all')   # host-gene convention
anno_df <- as.data.frame(peak_anno)

# --- ChIPseeker: custom GTF (map symbols from original GTF) ---
peak_anno <- annotatePeak(peaks, TxDb = txdb, tssRegion = c(-2000, 2000),
                           overlap = 'all')
gtf <- import('genes.gtf.gz')
gene_map <- unique(data.frame(
    gene_id = sub('\\..*', '', gtf$gene_id),
    symbol  = gtf$gene_name, stringsAsFactors = FALSE))
gene_map <- gene_map[!is.na(gene_map$symbol), ]
anno_df <- as.data.frame(peak_anno)
anno_df$gene_id_base <- sub('\\..*', '', anno_df$geneId)
anno_df$SYMBOL <- gene_map$symbol[match(anno_df$gene_id_base, gene_map$gene_id)]
```

```bash
# --- HOMER annotatePeaks.pl ---
# Standard genome (HOMER's installed annotation)
annotatePeaks.pl peaks.bed hg38 > annotated.txt
# Custom GTF (overrides HOMER's default)
annotatePeaks.pl peaks.bed hg38 -gtf genes.gtf > annotated.txt
# Without installed genome, GTF only
annotatePeaks.pl peaks.bed none -gtf genes.gtf > annotated.txt
# Generate annotation statistics
annotatePeaks.pl peaks.bed hg38 -gtf genes.gtf -annStats stats.txt > annotated.txt
```

## ENCODE cCRE Classification

_modules: ccre, encode, screen, bedtools, regulatory-element_

```bash
# Download ENCODE cCRE BED from SCREEN (hg38)
wget https://api.wenglab.org/screen_v13/screen_human_ccres_simple.bed.gz
gunzip screen_human_ccres_simple.bed.gz

# Intersect peaks with cCRE; -wa preserves peak coords, -wb adds cCRE class
bedtools intersect -a peaks.narrowPeak -b screen_human_ccres_simple.bed -wa -wb \
    > peaks_ccre.tsv
```

## Gene-Set Enrichment

_modules: great, rgreat, chipenrich, enrichment, go_

```r
# --- rGREAT: regulatory-domain gene-set enrichment ---
library(rGREAT)
res <- great(gr = peaks, gene_sets = 'GO:BP',
             tss_source = 'TxDb.Hsapiens.UCSC.hg38.knownGene',
             biomart_dataset = 'hsapiens_gene_ensembl')
table_results <- getEnrichmentTable(res)
head(table_results)
plotVolcano(res)
plotRegionGeneAssociationGraphs(res)

# --- ChIP-Enrich: locus-length-adjusted enrichment ---
library(chipenrich)
res <- chipenrich(peaks = 'peaks.bed', genome = 'hg38',
                   genesets = 'GOBP', locusdef = 'nearest_tss',
                   out_name = 'chipenrich_out', n_cores = 4)
# Locus definitions: nearest_tss, nearest_gene, 1kb, 5kb, 10kb, gene_body, exon
# Methods: chipenrich (default), polyenrich (high peak counts),
#          broadenrich (broad marks H3K27me3 / H3K9me3)
```

## Troubleshooting & Reconciliation

_modules: troubleshooting, failure-modes, reconciliation, debugging_

```r
# --- Fix: seqlevels / chr naming mismatch in ChIPseeker ---
seqlevelsStyle(peaks) <- 'UCSC'
stopifnot(all(seqlevels(peaks) == seqlevels(txdb)))

# --- Fix: overlap convention decoupling gene from feature ---
# Use overlap = 'all' (host-gene) instead of default 'TSS'
peak_anno <- annotatePeak(peaks, TxDb = txdb, overlap = 'all')

# --- Fix: custom TxDb returns NA symbols ---
# Map symbols from original GTF; strip Ensembl version suffixes before joining
anno_df$gene_id_base <- sub('\\..*', '', anno_df$geneId)
anno_df$SYMBOL <- gene_map$symbol[match(anno_df$gene_id_base, gene_map$gene_id)]
```

```bash
# --- Fix: HOMER hard-coded promoter window -> post-hoc reclassify ---
awk -F'\t' 'NR>1 { dist = ($10 < 0) ? -$10 : $10; \
    feat = (dist <= 2000) ? "promoter_custom" : $8; \
    print $2, $3, $4, $16, $10, feat }' OFS='\t' annotated.txt

# --- Fix: HOMER "no annotation" -> install genome ---
perl configureHomer.pl -install hg38
```
