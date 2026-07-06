## Setup & Source Selection

_modules: setup, source-selection, cache-config, accession-hierarchy_

```bash
# --- Install tooling ---
# sra-tools (NCBI toolkit: prefetch, fasterq-dump, vdb-validate, vdb-config)
conda install -c bioconda sra-tools           # 3.0+
fasterq-dump --version                        # confirm

# pysradb for metadata resolution
pip install pysradb                           # 2.2+

# AWS CLI for STRIDES cloud path (no NCBI auth needed for public buckets)
# aws s3 ls s3://sra-pub-run-odp/sra/SRR12345678/ --no-sign-request

# --- Configure SRA cache (default ~/ncbi/ is often too small) ---
vdb-config --cfg                              # show current config
vdb-config --set /repository/user/main/public/root=/data/sra_cache
# In Docker: mount a host volume at ~/.ncbi/ so user-settings.mkfg persists.

# --- Decision matrix: where to pull from ---
# ENA mirror        : default off-cloud; direct FASTQ; often fastest; free
# STRIDES (AWS/GCP) : same-region cloud compute; zero egress; us-east-1 / us-central1
# SRA-direct        : on-prem fallback; NCBI throttles by IP; slow 9-17 ET
# Aspera            : retired for public use (NCBI 2019, ENA ~2023); institutional only

# --- SRA accession hierarchy (download unit = SRR/ERR/DRR run) ---
# SRR/ERR/DRR       : Run        (file-level; the actual download unit)
# SRX/ERX/DRX       : Experiment (library prep + sequencing strategy)
# SRS/ERS/DRS       : Sample     (biological sample)
# SRP/ERP/DRP       : Study      (deprecated; use BioProject)
# PRJNA/PRJEB/PRJDB : BioProject (top-level project handle)
# SAMN/SAMEA/SAMD   : BioSample
```

## Metadata Resolution

_modules: metadata, pysradb, accession-resolution_

```python
from pysradb import SRAweb
import pandas as pd


def gse_to_srr(gse):
    """GSE -> SRP -> list of SRR run accessions."""
    db = SRAweb()
    df = db.gse_to_srp(gse)
    if df.empty:
        return []
    srp = df['study_accession'].iloc[0]
    runs = db.srp_to_srr(srp)
    return runs['run_accession'].tolist()


def bioproject_to_runs(prjna):
    """BioProject (PRJNA...) -> full metadata table including run accessions."""
    db = SRAweb()
    return db.sra_metadata(prjna, detailed=True)


def batch_resolve(ids):
    """Resolve a list of GSE/BioProject/SRX IDs; collect failures gracefully."""
    db = SRAweb()
    rows = []
    for id in ids:
        try:
            meta = db.sra_metadata(id, detailed=True)
            rows.append(meta)
        except Exception as e:
            print(f'{id}: {e}')
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


# Example: resolve a GSE to all its SRRs
srrs = gse_to_srr('GSE123456')
print(f'GSE123456 -> {len(srrs)} SRRs')
```

## Download & Extract

_modules: download, ena, prefetch, fasterq-dump, strides, aws-s3, compression_

```bash
# ============================================================
# Path A: ENA mirror (preferred off-cloud default)
# Direct FASTQ (pre-compressed); query portal API for URLs + md5.
# ============================================================
SRR="${1:-SRR12345678}"
OUT="${2:-./fastq}"
mkdir -p "${OUT}"

# Get FASTQ URLs + md5 from ENA portal API
META=$(curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=${SRR}&result=read_run&fields=fastq_ftp,fastq_md5&format=tsv" | tail -1)
URLS=$(echo "${META}" | cut -f1 | tr ';' '\n')
MD5S=$(echo "${META}" | cut -f2 | tr ';' '\n')

i=0
while read url; do
    fname="${OUT}/$(basename ${url})"
    expected_md5=$(echo "${MD5S}" | sed -n "$((i+1))p")
    curl -sL -o "${fname}" "https://${url}"
    actual_md5=$(md5sum "${fname}" | awk '{print $1}')
    [ "${actual_md5}" != "${expected_md5}" ] && { echo "MD5 MISMATCH ${fname}"; exit 1; }
    i=$((i+1))
done <<< "${URLS}"

# ============================================================
# Path B: SRA toolkit (prefetch + fasterq-dump; classic on-prem)
# Watch: --max-size silent skip; ~3x scratch; no built-in gzip.
# ============================================================
SRR="${1:-SRR12345678}"
OUT="${2:-./fastq}"
THREADS="${3:-8}"
mkdir -p "${OUT}"

# prefetch with explicit max-size (default 20G silently skips larger runs)
prefetch "${SRR}" --max-size 100G -p

# Validate the .sra file
vdb-validate "${SRR}" || { echo "Validation FAILED"; exit 1; }

# Extract FASTQ (multi-threaded; uncompressed scratch ~3x final size)
fasterq-dump "${SRR}" -O "${OUT}" -e "${THREADS}" -p --split-files

# Compress post-hoc (fasterq-dump does NOT compress)
pigz -p "${THREADS}" "${OUT}/${SRR}"_*.fastq

# ============================================================
# Path C: AWS STRIDES (cloud-native; run from us-east-1 EC2)
# Object is named without .sra suffix; rename on copy.
# ============================================================
SRR="${1:-SRR12345678}"

# Check availability on AWS Open Data (no auth needed)
aws s3 ls "s3://sra-pub-run-odp/sra/${SRR}/" --no-sign-request

# Download .sra (rename to .sra to keep fasterq-dump happy)
aws s3 cp "s3://sra-pub-run-odp/sra/${SRR}/${SRR}" "./${SRR}.sra" --no-sign-request

# Extract locally, then compress
fasterq-dump "./${SRR}.sra" -p -e 8 --split-files
pigz -p 8 "${SRR}"_*.fastq
```

## Single-cell / 10x Handling

_modules: single-cell, 10x, technical-reads, sra-stat_

```bash
SRR="${1:-SRR_10x_run}"
OUT="${2:-./fastq_10x}"
mkdir -p "${OUT}"

# Inspect read structure first (spotCount, baseCount, tags)
sra-stat --xml "${SRR}" | grep -E '(spotCount|baseCount|tag)'

# Extract ALL reads including technical (barcode / UMI / sample index)
# Default fasterq-dump skips technical reads -> breaks CellRanger/STARsolo.
fasterq-dump "${SRR}" --include-technical --split-files -p -O "${OUT}" -e 8

# 10x v3 expects: R1 (28-bp barcode+UMI), R2 (cDNA), I1 (sample index)
# 10x v2 expects: R1 (barcode), R2 (UMI+cDNA), I1
ls -la "${OUT}/${SRR}"_*.fastq
pigz -p 8 "${OUT}/${SRR}"_*.fastq
```

## Verification

_modules: verification, md5, vdb-validate_

```bash
# --- SRA-format files (.sra): use vdb-validate ---
vdb-validate SRR12345678

# --- ENA FASTQ files: use md5sum against ENA-provided md5 ---
# md5 comes from the ENA portal API (fastq_md5 field)
md5sum -c <(echo "<expected_md5>  SRR12345678_1.fastq.gz")

# Guard against the prefetch --max-size silent-skip trap:
# if vdb-validate fails because no file exists, re-run prefetch with
# an explicit --max-size (e.g. 200G) for unknown-size runs.
```
