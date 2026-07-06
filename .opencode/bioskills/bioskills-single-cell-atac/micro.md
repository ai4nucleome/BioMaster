## Ecosystem Selection & Data Loading

_modules: data-loading, ecosystem, signac, archr, snapatac2_

```r
# === Signac / Seurat (R) ===
library(Signac); library(Seurat); library(EnsDb.Hsapiens.v86)
library(BSgenome.Hsapiens.UCSC.hg38)

counts <- Read10X_h5('outs/filtered_peak_bc_matrix.h5')
metadata <- read.csv('outs/singlecell.csv', row.names=1)

chrom_assay <- CreateChromatinAssay(
    counts=counts,
    sep=c(':', '-'),
    fragments='outs/fragments.tsv.gz',
    annotation=GetGRangesFromEnsDb(EnsDb.Hsapiens.v86),
    genome='hg38')
obj <- CreateSeuratObject(counts=chrom_assay, assay='ATAC', meta.data=metadata)

# === ArchR (R) ===
library(ArchR)
addArchRGenome('hg38')
ArrowFiles <- createArrowFiles(
    inputFiles=c('rep1=fragments_rep1.tsv.gz', 'rep2=fragments_rep2.tsv.gz'),
    sampleNames=c('rep1', 'rep2'),
    minTSS=4, minFrags=1000,
    addTileMat=TRUE, addGeneScoreMat=TRUE)
```

```python
# === SnapATAC2 (Python) ===
import snapatac2 as snap

# NOTE: use snap.pp.import_fragments (snap.read_10x does not exist).
data = snap.pp.import_fragments(
    fragment_file='outs/fragments.tsv.gz',
    chrom_sizes=snap.genome.hg38,
    file='out.h5ad',            # backed AnnData
    sorted_by_barcode=False)
data.obs['sample_id'] = 'rep1'
```

## Per-Cell QC & Doublet Detection

_modules: qc, doublet-detection, amulet, tss-enrichment, nucleosome-signal_

```r
# === Signac QC + filter ===
obj <- NucleosomeSignal(obj)              # Mono/NFR ratio
obj <- TSSEnrichment(obj, fast=FALSE)
obj$pct_reads_in_peaks <- obj$peak_region_fragments / obj$passed_filters * 100
obj$blacklist_ratio <- obj$blacklist_region_fragments / obj$peak_region_fragments

obj <- subset(obj,
    subset = peak_region_fragments > 1000 & peak_region_fragments < 20000 &
             pct_reads_in_peaks > 15 & blacklist_ratio < 0.05 &
             nucleosome_signal < 4 & TSS.enrichment > 4)

# === ArchR doublet detection + filter ===
doubletScores <- addDoubletScores(input=ArrowFiles, k=10, knnMethod='UMAP')
proj <- ArchRProject(ArrowFiles=ArrowFiles, outputDirectory='ArchR_out')
proj <- filterDoublets(proj)
```

```python
# === SnapATAC2 QC ===
snap.metrics.tsse(data, gene_anno=snap.genome.hg38)
snap.metrics.frag_size_distr(data)
snap.pp.filter_cells(data, min_counts=1000, min_tsse=4)
```

```bash
# AMULET (CLI): primary ATAC-specific doublet check; needs >=5000 frags/cell.
amulet --fragments fragments.tsv.gz --cells barcodes.tsv --out amulet_out
```
# Per-cell threshold guide: fragments 3000-50000 pass / <1000 or >80000 reject;
# TSS enrichment >=4 pass / <2 reject; nucleosome signal <=4 pass / >10 reject;
# FRiP >=0.15 pass / <0.05 reject; blacklist <0.05 pass / >0.10 reject.

## Dimensionality Reduction & Clustering

_modules: tfidf, lsi, spectral, umap, leiden, clustering_

```r
# === Signac: TF-IDF + SVD, SKIP component 1 (depth artifact) ===
obj <- RunTFIDF(obj)
obj <- FindTopFeatures(obj, min.cutoff='q0')
obj <- RunSVD(obj)
obj <- RunUMAP(obj, reduction='lsi', dims=2:30)
obj <- FindNeighbors(obj, reduction='lsi', dims=2:30)
obj <- FindClusters(obj, algorithm=4, resolution=0.5)   # algorithm=4 = Leiden

# === ArchR: iterative LSI (depth component handled automatically) ===
proj <- addIterativeLSI(proj, useMatrix='TileMatrix', name='IterativeLSI')
proj <- addClusters(proj, reducedDims='IterativeLSI', method='Seurat', resolution=0.5)
proj <- addUMAP(proj, reducedDims='IterativeLSI')
```

```python
# === SnapATAC2: spectral embedding (depth component handled automatically) ===
snap.pp.add_tile_matrix(data, bin_size=500)
snap.pp.select_features(data, n_features=250000)
snap.tl.spectral(data)
snap.tl.umap(data)
snap.tl.leiden(data)
```

## Per-Cluster Peak Calling

_modules: peak-calling, macs3, pseudobulk, consensus-peakset_

```r
# === Signac: per-cluster MACS3 + consensus ===
peaks <- CallPecks(obj, group.by='seurat_clusters',
                   macs2.path='/path/to/macs3', cleanup=FALSE,
                   format='BAMPE', extra.args='--shift -75 --extsize 150 -p 0.01')
# iterative-overlap consensus across clusters (see atac-seq/consensus-peakset)

# === ArchR: reproducible peakset ===
proj <- addGroupCoverages(proj, groupBy='Clusters')
proj <- addReproduciblePeakSet(proj, groupBy='Clusters', pathToMacs2='/path/macs3')
proj <- addPeakMatrix(proj)
```

```python
# === SnapATAC2: per-cluster MACS3 ===
snap.tl.macs3(data, groupby='leiden')
```

## Cell-Type Annotation

_modules: gene-activity, annotation, cell-cycle, sex-qc_

```r
# === Signac: gene activity for annotation ===
gene.activities <- GeneActivity(obj)
obj[['ACT']] <- CreateAssayObject(counts=gene.activities)
DefaultAssay(obj) <- 'ACT'
obj <- NormalizeData(obj, normalization.method='LogNormalize',
                     scale.factor=median(obj$nCount_ACT))
# then run single-cell/markers-annotation on the ACT assay

# Cell-cycle correction: regress S-phase score on TF-IDF residuals before LSI:
#   obj <- ScaleData(obj, vars.to.regress='S.score')
# Sex QC: fraction of fragments at XIST (chrX:73820651-73852723 hg38) vs chrY peak count
```

```python
# === SnapATAC2: gene matrix ===
gene_mat = snap.pp.make_gene_matrix(data, gene_anno=snap.genome.hg38)
```

## Multiome Integration (Optional)

_modules: multiome, wnn, multimodal-integration_

```r
# === Signac/Seurat WNN for 10X Multiome ===
# Assume `obj` has both 'RNA' and 'ATAC' assays from the same Multiome experiment.
DefaultAssay(obj) <- 'RNA'
obj <- NormalizeData(obj) %>% FindVariableFeatures() %>% ScaleData() %>% RunPCA()

DefaultAssay(obj) <- 'ATAC'
obj <- RunTFIDF(obj) %>% FindTopFeatures(min.cutoff='q0') %>% RunSVD()

# Joint embedding (note: ATAC dims start at 2 to skip depth component)
obj <- FindMultiModalNeighbors(obj, reduction.list=list('pca', 'lsi'),
                               dims.list=list(1:30, 2:30))
obj <- RunUMAP(obj, nn.name='weighted.nn', reduction.name='wnn.umap')
```

## Advanced Analyses & Reference Mapping

_modules: reference-mapping, scarches, peakvi, chrombpnet, reconciliation_

```python
# === scArches / PEAKVI reference mapping ===
import scvi

# Pre-trained reference model (e.g. PBMC scATAC atlas).
# PEAKVI.load_query_data implements the scArches algorithm directly;
# an explicit `import scarches` is not required.
query_model = scvi.model.PEAKVI.load_query_data(adata_query, reference_path)
query_model.train(max_epochs=200)
adata_query.obsm['X_emb'] = query_model.get_latent_representation()
```

```bash
# chromBPNet per-cluster pseudobulk (reserve for top 5-10 priority clusters):
#   1. aggregate fragments per cluster -> pseudobulk BAM
#   2. run chromBPNet pipeline per cluster (~24h GPU/cluster)
#   3. use the resulting model for in silico variant scoring at GWAS / rare-variant SNPs
```
