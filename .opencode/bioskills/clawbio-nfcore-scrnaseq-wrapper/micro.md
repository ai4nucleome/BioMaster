## Preflight & Validation

_modules: preflight, validation, samplesheet, environment-check, pipeline-source_

```bash
# Preflight check only (no Nextflow execution) — validates everything then exits
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./scrnaseq_run --check

# Full run (preflight runs first, then continues to execution)
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./scrnaseq_run

# Via ClawBio runner
python clawbio.py run scrnaseq-pipeline --input samplesheet.csv --output ./scrnaseq_run
```

Validation checks performed (in order):
1. Pipeline source resolution: look for ../scrnaseq sibling checkout; fall back to remote tag (default 4.1.0)
2. Samplesheet validation: parse CSV, resolve FASTQ paths, normalize names, check readability/extensions, reject duplicates, enforce consistent expected_cells & seq_center
3. Preflight: Java >=17, Nextflow >=25.04.0 (zero-padded 3-tuple comparison), backend binary check (docker info / conda / mamba / singularity / apptainer)
4. Protocol compatibility: standard/star/kallisto require non-auto protocol; standard rejects smartseq
5. Reference conflict check: --genome is mutually exclusive with --fasta/--gtf and all index flags

Samplesheet format (CSV):
  Required columns: sample, fastq_1, fastq_2
  Optional columns: expected_cells, seq_center, sample_type, fastq_barcode, feature_type

Key flags for this step:
  --preset {standard,star,kallisto,cellranger,cellrangerarc,cellrangermulti}  (default: standard)
  --profile {docker,conda,mamba,singularity,apptainer,podman,shifter,charliecloud,wave,gpu}  (default: docker)
  --pipeline-version <tag>  (default: 4.1.0, used when no local checkout)
  --protocol <chemistry>  (required non-auto for standard/star/kallisto; e.g. 10XV3, dropseq)
  --check  (preflight only, no execution)

## Configuration

_modules: configuration, params, preset, reference-resolution_

```bash
# Standard (simpleaf/alevin-fry) with iGenomes shortcut
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./run --preset standard --protocol 10XV3 \
  --genome GRCh38

# STARsolo with local FASTA+GTF (STAR index built by the pipeline)
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./run --preset star --protocol 10XV3 \
  --fasta /refs/hg38.fa --gtf /refs/hg38.gtf

# STARsolo with prebuilt STAR index
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./run --preset star --protocol 10XV3 \
  --star-index /refs/star_index

# Kallisto RNA velocity (NAC workflow)
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./run --preset kallisto \
  --kb-workflow nac --fasta /refs/hg38.fa --gtf /refs/hg38.gtf

# Air-gapped cluster: local iGenomes mirror
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./run --preset star --protocol 10XV3 \
  --genome GRCh38 --igenomes-base /mnt/local_igenomes
```

Reference options (exactly one group required):
  --genome <iGenomes_shortcut>              (e.g. GRCh38, mm10) — mutually exclusive with all below
  --fasta <path> + --gtf <path>             (pipeline builds the index)
  --star-index / --simpleaf-index / --kallisto-index / --cellranger-index <path>  (prebuilt)
  --transcript-fasta + --txp2gene           (simpleaf transcriptome)

Params.yaml construction rules:
  - All paths written via .as_posix() for cross-platform forward slashes
  - igenomes_ignore: true whenever any explicit reference path is provided (automatic)
  - Skip flags written only when true (keeps params.yaml minimal)
  - Normalized samplesheet written to reproducibility/samplesheet.valid.csv

Nextflow command shape:
  nextflow run <pipeline_source> -profile <profile> -params-file <output>/reproducibility/params.yaml -work-dir <output>/upstream/work

## Execution

_modules: execution, nextflow, nf-core, docker, macos-workaround_

```bash
# Standard execution
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./scrnaseq_run

# Demo mode (nf-core test profile; forces star preset + skip_cellbender; Docker must be running)
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --demo --output ./scrnaseq_demo

# STARsolo RNA velocity (requires BOTH flags together)
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./run --preset star \
  --star-feature "Gene Velocyto" --star-ignore-sjdbgtf \
  --fasta /refs/hg38.fa --gtf /refs/hg38.gtf

# Simpleaf with UMI resolution override
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./run --preset standard --protocol 10XV3 \
  --simpleaf-umi-resolution cr-like-em --genome GRCh38

# CellRanger Multi (CMO multiplexing)
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./run --preset cellrangermulti \
  --cellranger-index /refs/refdata-gex-GRCh38 \
  --gex-cmo-set /refs/cmo_set.csv \
  --cellranger-multi-barcodes /refs/multi_barcodes.csv

# Resume a prior run (checksum-verified against prior manifest)
python skills/nfcore-scrnaseq-wrapper/nfcore_scrnaseq_wrapper.py \
  --input samplesheet.csv --output ./scrnaseq_run --resume
```

Execution internals:
  - Launch: subprocess.Popen with stdout/stderr piped to logs/stdout.txt, logs/stderr.txt
  - Work dir: <output>/upstream/work
  - macOS Docker: macos_docker.config auto-applied (stageInMode=copy, --platform linux/amd64, STAR _STARtmp -> /tmp)
  - Timeout: on TimeoutExpired, process killed, EXECUTION_FAILED raised
  - --resume: validates manifest matches preset/profile/pipeline_source; mismatch -> INVALID_RESUME_STATE
  - --demo: forces preset=star, skip_cellbender=true

Execution-affecting flags:
  --resume                          Nextflow resume (checksum-verified)
  --save-reference                  Save built reference index for reuse
  --save-align-intermeds            Save alignment intermediate BAM files
  --skip-cellbender                 Disable CellBender ambient RNA removal
  --skip-emptydrops                 Skip emptyDrops cell calling (independent of skip-cellbender)
  --skip-fastqc                     Skip FastQC quality control
  --skip-multiqc                    Skip MultiQC report generation
  --email <addr>                    Pipeline completion notification
  --multiqc-title <title>           Custom MultiQC report title

## Output Resolution

_modules: output-parsing, h5ad, multiqc, artifact-detection_

```text
# Output directory structure produced by this step's scanning logic:
output_directory/
├── logs/
│   ├── stdout.txt                    # Nextflow stdout
│   └── stderr.txt                    # Nextflow stderr
└── upstream/
    └── results/                      # nf-core/scrnaseq output tree
        ├── fastqc/                   # Per-read FastQC reports
        ├── multiqc/
        │   └── multiqc_report.html
        ├── pipeline_info/            # Execution report, timeline, trace, DAG
        └── <aligner>/                # Aligner-specific outputs
            ├── <sample>/             # Per-sample STAR/simpleaf/kallisto outputs
            └── mtx_conversions/      # AnnData (.h5ad), SCE (.rds), Seurat (.rds)
                ├── <sample>_filtered_matrix.h5ad
                ├── <sample>_raw_matrix.h5ad
                ├── combined_filtered_matrix.h5ad   <- preferred_h5ad (when present)
                └── combined_raw_matrix.h5ad
```

Resolution priority for preferred_h5ad:
  1. combined_filtered_matrix.h5ad  (highest priority)
  2. combined_raw_matrix.h5ad
  3. <sample>_filtered_matrix.h5ad  (only if single sample)
  4. None -> handoff_available = false

Detected artifact categories written to provenance/outputs.json:
  - multiqc_html: path to multiqc_report.html
  - pipeline_info_dir: path to pipeline_info/
  - h5ad_files: list of all .h5ad paths found
  - rds_files: list of all .rds paths found
  - cellbender_outputs: list of CellBender-derived files (if not skipped)
  - preferred_h5ad: canonical handoff path (or null)
  - handoff_available: boolean

## Provenance & Handoff

_modules: provenance, reproducibility, reporting, handoff, checksum_

```text
# Reproducibility bundle written by this step:
output_directory/
├── report.md                         # Wrapper run summary + medical disclaimer + Next Steps
├── result.json                       # Structured result payload
├── reproducibility/
│   ├── samplesheet.valid.csv         # Normalized samplesheet (absolute POSIX paths)
│   ├── params.yaml                   # Effective Nextflow parameters
│   ├── commands.sh                   # Portable replay script
│   ├── environment.yml               # Conda environment spec (for reference)
│   ├── checksums.sha256              # SHA-256 for samplesheet, params, refs, h5ad, MultiQC
│   ├── manifest.json                 # Run metadata: preset, profile, versions, checksums
│   ├── macos_docker.config           # macOS+Docker workarounds (when applicable)
│   └── remap_paths.py                # Helper for replaying on a different machine
└── provenance/
    ├── inputs.json                   # Samplesheet and reference paths + checksums
    ├── invocation.json               # Timestamp, preset, profile, pipeline version
    ├── preflight.json                # Java/Nextflow/backend info
    ├── upstream.json                 # Pipeline source resolution details
    ├── outputs.json                  # Detected artifacts
    ├── runtime.json                  # Execution timing
    └── skill.json                    # Skill name and version
```

result.json (abbreviated):
```json
{
  "skill": "scrnaseq-pipeline",
  "version": "0.1.0",
  "summary": {
    "preset": "star",
    "aligner_effective": "star",
    "pipeline_source_kind": "remote_repo",
    "pipeline_version_or_commit": "4.1.0",
    "profile": "docker",
    "preferred_h5ad": "<output>/upstream/results/star/mtx_conversions/combined_filtered_matrix.h5ad",
    "handoff_available": true,
    "samples_detected": 2,
    "cellbender_used": false
  }
}
```

report.md closes with Next Steps (when handoff_available = true):
```bash
python clawbio.py run scrna --input <preferred_h5ad> --output <dir>
python clawbio.py run scrna-embedding --input <preferred_h5ad> --output <dir>
```

Handoff flag:
  --run-downstream    Opt in to scrna_orchestrator handoff after pipeline completion

Chaining partners:
  scrna-orchestrator  -> clustering, QC, markers (pass preferred_h5ad)
  scrna-embedding     -> scVI/scANVI batch integration (pass preferred_h5ad)
  multiqc-reporter    -> re-aggregate QC across multiple wrapper runs
