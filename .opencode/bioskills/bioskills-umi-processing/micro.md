## UMI Extraction

_modules: umi-extraction, fastq, quality-filter, umi-tools-extract_

```bash
# UMI at start of R1 (8bp UMI)
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN

# UMI at start of R2
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern2=NNNNNNNN

# UMI in both reads
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN \
    --bc-pattern2=NNNNNNNN
```

Pattern syntax: `N` = UMI base (extracted), `C` = cell barcode (extracted, kept separate), `X` = discard base. Examples: `NNNNNNNN` = 8bp UMI; `CCCCCCCCNNNNNNNN` = 8bp cell barcode + 8bp UMI; `NNNXXXNNN` = 3bp UMI, skip 3bp, 3bp UMI.

```bash
# 10X Genomics 3' v3 (16bp cell barcode + 12bp UMI in R1)
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern=CCCCCCCCCCCCCCCCNNNNNNNNNNNN

# Skip bases between barcode and UMI (8bp UMI, skip 4bp)
umi_tools extract \
    --stdin=R1.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --bc-pattern=NNNNNNNNXXXX

# Fixed anchor sequence (regex)
umi_tools extract \
    --stdin=R1.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --bc-pattern='(?P<umi_1>.{8})ATGC(?P<discard_1>.{4})'

# UMI in separate I1 index read
umi_tools extract \
    --stdin=R1.fastq.gz \
    --read2-in=R2.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --read2-out=R2_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN \
    --extract-method=string \
    --umi-separator=":"
```

Quality filtering during extraction:
```bash
# Filter by UMI quality (Phred 20)
umi_tools extract \
    --stdin=R1.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN \
    --quality-filter-threshold=20 \
    --quality-encoding=phred33

# Filter UMIs containing N bases
umi_tools extract \
    --stdin=R1.fastq.gz \
    --stdout=R1_extracted.fastq.gz \
    --bc-pattern=NNNNNNNN \
    --filter-cell-barcode
```

Alternative: fastp for simple UMI extraction during QC (no dedup):
```bash
fastp -i R1.fq.gz -I R2.fq.gz \
      -o R1_umi.fq.gz -O R2_umi.fq.gz \
      --umi --umi_loc read1 --umi_len 8
```

## Alignment

_modules: alignment, star, samtools, bam-sorting_

```bash
# Align paired-end UMI-tagged reads with STAR
STAR --runThreadN 8 \
    --genomeDir $REFERENCE \
    --readFilesIn ${SAMPLE}_R1_umi.fastq.gz ${SAMPLE}_R2_umi.fastq.gz \
    --readFilesCommand zcat \
    --outFileNamePrefix ${SAMPLE}_ \
    --outSAMtype BAM SortedByCoordinate

# Sort and index (required before dedup)
samtools sort -o aligned_sorted.bam aligned.bam
samtools index aligned_sorted.bam
```

## Deduplication

_modules: deduplication, pcr-duplicates, paired-end, per-gene, per-cell, umi-tools-dedup_

```bash
# Basic deduplication (input must be sorted + indexed)
umi_tools dedup \
    --stdin=aligned_sorted.bam \
    --stdout=deduplicated.bam \
    --log=dedup.log

# Deduplication methods
umi_tools dedup -I input.bam -S output.bam --method=directional   # default, recommended
umi_tools dedup -I input.bam -S output.bam --method=unique        # exact matches only
umi_tools dedup -I input.bam -S output.bam --method=cluster       # network-based
umi_tools dedup -I input.bam -S output.bam --method=adjacency     # balanced
umi_tools dedup -I input.bam -S output.bam --method=percentile    # extreme duplication
```

Method selection: `directional` = standard RNA-seq, fast; `unique` = very high diversity / PCR-free, fastest; `cluster` = low diversity / high errors, slow; `adjacency` = balance, medium; `percentile` = extremely high duplication, fast.

```bash
# Paired-end deduplication
umi_tools dedup \
    -I aligned_sorted.bam \
    -S deduplicated.bam \
    --paired

# Use read2 for grouping (R2-based libraries)
umi_tools dedup \
    -I aligned_sorted.bam \
    -S deduplicated.bam \
    --paired \
    --read2-in-read1

# Gene-level deduplication (RNA-seq)
umi_tools dedup \
    -I aligned_sorted.bam \
    -S deduplicated.bam \
    --per-gene \
    --gene-tag=GX

# Per-gene + per-cell (single-cell)
umi_tools dedup \
    -I aligned_sorted.bam \
    -S deduplicated.bam \
    --per-gene \
    --per-cell \
    --gene-tag=XT

# Single-cell post-CellRanger (CB cell barcode + UB UMI tags)
umi_tools dedup \
    -I possorted_genome_bam.bam \
    -S deduplicated.bam \
    --per-cell \
    --cell-tag=CB \
    --umi-tag=UB \
    --extract-umi-method=tag \
    --per-gene \
    --gene-tag=GX

# Group UMIs without deduplication (adds BX group tag)
umi_tools group \
    -I aligned_sorted.bam \
    -S grouped.bam \
    --group-out=groups.tsv \
    --output-bam
```

## UMI Counting

_modules: counting, gene-counts, count-matrix, umi-tools-count_

```bash
# Count UMIs per gene per cell (long format: gene\tcell\tcount)
umi_tools count \
    -I deduplicated.bam \
    -S counts.tsv \
    --per-gene \
    --gene-tag=GX \
    --per-cell \
    --cell-tag=CB

# Wide format (gene x cell matrix)
umi_tools count \
    -I deduplicated.bam \
    -S counts.tsv \
    --per-gene \
    --gene-tag=GX \
    --wide-format-cell-counts
```

Long-format output example:
```
gene    cell    count
ENSG00000139618    ACGT    15
ENSG00000139618    TGCA    8
ENSG00000141510    ACGT    42
```

## Statistics & QC

_modules: qc, statistics, performance, dedup-stats_

```bash
# Generate deduplication statistics
umi_tools dedup \
    -I input.bam \
    -S output.bam \
    --output-stats=dedup_stats
# Outputs:
#   dedup_stats_per_umi_per_position.tsv
#   dedup_stats_per_umi.tsv
#   dedup_stats_edit_distance.tsv
```

Interpret the deduplication rate:
```python
import pandas as pd

stats = pd.read_csv('dedup.log', sep='\t', comment='#')
total_reads = stats['total_reads'].iloc[0]
unique_reads = stats['unique_reads'].iloc[0]
dedup_rate = 1 - (unique_reads / total_reads)
print(f'Deduplication rate: {dedup_rate:.1%}')
```

Performance tuning for large files:
```bash
# Multiple cores
umi_tools dedup -I input.bam -S output.bam --parallel

# Reduce memory
umi_tools dedup -I input.bam -S output.bam --buffer-whole-contig

# Skip output sorting for speed
umi_tools dedup -I input.bam -S output.bam --no-sort-output
```
