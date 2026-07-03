## Read QC and optional host depletion

_modules: qc, host-depletion, fastp_

```bash
# Verify tool versions in the environment
fastp --version
kraken2 --version
bracken -v
metaphlan --version
humann --version

# Read QC: adapter trimming, quality filtering, report generation
fastp \
  -i sample_R1.fastq.gz \
  -I sample_R2.fastq.gz \
  -o qc/sample.clean.R1.fastq.gz \
  -O qc/sample.clean.R2.fastq.gz \
  --html qc/sample.fastp.html \
  --json qc/sample.fastp.json

# Optional host depletion (host-associated samples only):
# Align cleaned reads to host reference, retain unmapped pairs.
# Tool and parameters depend on host genome; document reference + version.
# Example pattern with bowtie2:
#   bowtie2 -x $HOST_DB \
#     -1 qc/sample.clean.R1.fastq.gz \
#     -2 qc/sample.clean.R2.fastq.gz \
#     --un-conc-gz qc/sample.hostdepleted.R%.fastq.gz \
#     -S /dev/null 2> qc/sample.host_depletion.log

# Record retained read counts in qc/read_processing_summary.tsv
```

## Taxonomic profiling

_modules: taxonomy, kraken2, classification, metaphlan_

```bash
# Kraken2 classification (k-mer based)
kraken2 \
  --db $KRAKEN_DB \
  --paired qc/sample.clean.R1.fastq.gz qc/sample.clean.R2.fastq.gz \
  --report results/taxonomy/sample.kraken.report \
  --output results/taxonomy/sample.kraken.out \
  --confidence 0.1

# Alternative: MetaPhlAn (marker-gene based)
# metaphlan qc/sample.clean.R1.fastq.gz,qc/sample.clean.R2.fastq.gz \
#   --input_type fastq \
#   --bowtie2db $METAPHLAN_DB \
#   -o results/taxonomy/sample.metaphlan.txt
```

## Abundance refinement

_modules: abundance, bracken, species, genus_

```bash
# Species-level abundance estimation
bracken \
  -d $KRAKEN_DB \
  -i results/taxonomy/sample.kraken.report \
  -o results/taxonomy/sample.bracken.species \
  -r 150 \
  -l S

# Genus-level abundance estimation
bracken \
  -d $KRAKEN_DB \
  -i results/taxonomy/sample.kraken.report \
  -o results/taxonomy/sample.bracken.genus \
  -r 150 \
  -l G

# Merge per-sample bracken outputs into cohort matrices:
#   bracken_species.tsv, bracken_genus.tsv
# (use bracken's combine scripts or a custom merge with metadata joins)
```

## Functional and AMR profiling

_modules: function, amr, humann, pathways_

```bash
# Functional pathway profiling with HUMAnN
humann \
  --input qc/sample.clean.R1.fastq.gz \
  --output results/function/ \
  --threads 8

# HUMAnN produces gene families and pathway abundance/reaction files.
# Rename/collect pathway abundance to results/function/pathabundance.tsv

# AMR profiling (tool depends on setup):
#   - AMRFinderPlus: amrfinder -n assembled_contigs.fa --output results/amr/sample.amr.tsv
#   - RGI: rgi main --input assembly.fa --output results/amr/sample.rgi
# Collect per-sample AMR hits into results/amr/amr_summary.tsv
```

## Cohort-ready output export

_modules: export, cohort, merge, metadata_

```bash
# Merge per-sample HUMAnN pathway tables into a cohort matrix
humann_join_tables \
  --input results/function/ \
  --output results/function/pathabundance.tsv \
  --file_name pathabundance

# Merge per-sample bracken tables into cohort matrices
# (bracken_species.tsv, bracken_genus.tsv)
# Merge per-sample AMR hits into amr_summary.tsv

# Final expected output layout:
# results/
#   taxonomy/  -> bracken_species.tsv, bracken_genus.tsv, *.kraken.report
#   function/  -> pathabundance.tsv
#   amr/       -> amr_summary.tsv
# qc/          -> read_processing_summary.tsv, *.fastp.html
```
