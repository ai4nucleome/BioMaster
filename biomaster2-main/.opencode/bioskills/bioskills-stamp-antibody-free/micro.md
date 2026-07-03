## Method Selection & Experimental Design

_modules: method-selection, experimental-design, control-planning, stamp, tribe, dart-seq_

```bash
# Decision logic (no code execution; reference for planning)
# - No antibody for RBP, or UV not possible, or single-cell needed -> STAMP or TRIBE
# - Mammalian RBP, want cleaner background -> STAMP (APOBEC1, C->U)
# - Drosophila RBP -> TRIBE (ADAR, A->I)
# - m6A reader profiling -> DART-seq (APOBEC1-YTH)
# - Precise binding site needed -> use eCLIP instead (editing is offset 0-50 nt)

# Required samples per experiment:
#   1. fusion sample  (deaminase-RBP expressed)
#   2. control sample (deaminase-only, same promoter/cells)
#   3. (optional) wild-type / empty vector baseline

# Expression titration (Yeo lab convention): doxycycline-inducible promoter,
# mid-range dox dose; verify fusion-vs-control edit ratio > 3 at chosen dose.
```

## Alignment & BAM Generation

_modules: alignment, star, cellranger, bam, indexing_

```bash
# Bulk RNA-seq -- STAR two-pass alignment (fusion + control in parallel)
STAR --runMode genomeGenerate --genomeDir star_index \
    --genomeFastaFiles genome.fa --sjdbGTFfile genes.gtf
STAR --runThreadN 16 --genomeDir star_index \
    --readFilesIn sample_R1.fastq.gz sample_R2.fastq.gz \
    --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate \
    --twopassMode Basic --outFileNamePrefix stamp_sample_
samtools index stamp_sample_Aligned.sortedByCoord.out.bam

# 10x single-cell -- cellranger count (produces per-cell-barcode BAM)
cellranger count \
    --id=scstamp_sample \
    --transcriptome=refdata-gex-GRCh38 \
    --fastqs=fastq_dir \
    --localcores=16 --localmem=64
# BAM:  scstamp_sample/outs/possorted_genome_bam.bam
# Barcodes: scstamp_sample/outs/filtered_feature_bc_matrix/barcodes.tsv.gz
```

## Editing-Site Detection

_modules: edit-calling, jacusa2, bullseye, sailor, reditools2, c-to-u, a-to-i_

```bash
# --- JACUSA2 (general-purpose, multi-sample; BAM args are POSITIONAL) ---
# -R reference, -r output, -p threads, -F 1024 min coverage
java -jar JACUSA2.jar call-2 \
    -R genome.fa \
    -p 8 \
    -F 1024 \
    -r jacusa_edits.tsv \
    stamp1.bam,stamp2.bam control1.bam,control2.bam

# --- Bullseye (STAMP/DART, multi-script Perl; verify against repo) ---
perl parseBAM.pl --input stamp_sample.bam --output stamp.parsed.tsv
perl parseBAM.pl --input apobec1_only.bam --output control.parsed.tsv
perl summarize_sites.pl --in stamp.parsed.tsv > stamp.summary.tsv
perl summarize_sites.pl --in control.parsed.tsv > control.summary.tsv
perl find_edit_site.pl --ip stamp.summary.tsv --ctrl control.summary.tsv \
    --edit_type c2t --threshold 0.1 --min_coverage 10 --out stamp_edits.bed

# --- SAILOR (Yeo lab, Snakemake; configure inputs in config.yaml first) ---
snakemake -s SAILOR.smk --configfile config.yaml --cores 8
```

## Control Subtraction & Specificity Filtering

_modules: control-subtraction, filtering, strand-specificity, alu-filtering, qc, specificity_

```bash
# Post-filter JACUSA2 output for STAMP C->U at edit rate >= 0.1
# Columns (example): $5=ref, $9=edit, $11=edit_rate -- adjust to actual header
awk '$5 == "C" && $9 ~ /U/ && $11 >= 0.1' jacusa_edits.tsv > stamp_edits_filtered.tsv

# Require fusion-vs-control edit ratio > 3 (site-level)
# join fusion and control summary on chr:pos, then:
awk 'BEGIN{OFS="\t"} NR==FNR{ctrl[$1":"$2]=$3; next} \
    {k=$1":"$2; if(k in ctrl && ($3/(ctrl[k]+0.001))>3) print}' \
    control.summary.tsv stamp.summary.tsv > stamp_specific.tsv

# Remove ALU-overlapping edits (TRIBE in mammals)
bedtools intersect -v -a tribe_edits.bed -b alu_repeats.bed > tribe_filtered.bed

# Strand-aware filter: keep C->U on +sense, G->A on -sense only
# (editing-aware tools handle this internally; manual filter shown for QC)
```

## Single-Cell scSTAMP Analysis

_modules: single-cell, scstamp, pseudobulk, clustering, scanpy, leiden, umap_

```bash
# scSTAMP per-cell editing quantification (Yeo lab script)
python scstamp_analysis.py \
    --bam scstamp_sample/outs/possorted_genome_bam.bam \
    --barcodes scstamp_sample/outs/filtered_feature_bc_matrix/barcodes.tsv.gz \
    --control apobec1_only_sample/outs/possorted_genome_bam.bam \
    --output per_cell_edits.h5
```

```python
# Pseudobulk aggregation by cluster with scanpy (cells need >=10000 unique reads)
import scanpy as sc, anndata as ad, numpy as np, pandas as pd

adata = sc.read_h5ad("scstamp_rna.h5ad")          # standard scRNA-seq object
edits = pd.read_hdf("per_cell_edits.h5", key="edits")  # cells x sites edit-rate

# pseudobulk mean edit rate per Leiden cluster
edits_aligned = edits.reindex(index=adata.obs_names)
pseudobulk = edits_aligned.groupby(adata.obs["leiden"]).mean()
pseudobulk.to_csv("pseudobulk_edits_by_cluster.tsv", sep="\t")

# overlay per-cell total edit count on UMAP for QC
adata.obs["total_edits"] = edits_aligned.sum(axis=1).reindex(adata.obs_names, fill_value=0)
sc.pl.umap(adata, color=["leiden", "total_edits"])
```

## Validation & Failure-Mode Handling

_modules: validation, failure-modes, clip-reconciliation, saturation, qc, diagnostics_

```bash
# Diagnostic 1: saturation check -- compare edit counts fusion vs control
# If control edits ~= fusion edits per gene, APOBEC1 is saturated -> titrate down
awk '{c[$1]++} END{for(g in c) print g, c[g]}' stamp.summary.tsv | sort -k2 -nr | head
awk '{c[$1]++} END{for(g in c) print g, c[g]}' control.summary.tsv | sort -k2 -nr | head

# Diagnostic 2: ALU fraction in TRIBE (high fraction -> subtract control + filter)
bedtools intersect -u -a tribe_edits.bed -b alu_repeats.bed | wc -l
# compare to total edit count; if >50% overlap ALU, baseline ADAR dominates

# Diagnostic 3: strand check -- C->U should be on transcribed strand only
# (editing-aware tools report strand; flag sites with mixed-strand support)

# Diagnostic 4: scSTAMP sparsity -- cells with 0 detected targets
awk 'NR>1 {s[$1]+=$3} END{for(c in s) print c, s[c]}' per_cell_edits.tsv | \
    awk '$2==0{zero++} {tot++} END{print zero"/"tot" cells with 0 targets"}'
# if >50% cells have 0 targets -> pseudobulk by cluster or use Smart-seq2
```

```python
# Concordance with eCLIP (top-target overlap)
import pandas as pd
stamp_targets = pd.read_csv("stamp_specific.tsv", sep="\t")
eclip_targets = pd.read_csv("rbp_eclip_peaks.bed", sep="\t", header=None)
# intersect gene-level target lists; report Jaccard / overlap for top N
overlap = set(stamp_targets["gene"]) & set(eclip_targets[4])
print(f"STAMP-eCLIP concordant targets: {len(overlap)}")
```
