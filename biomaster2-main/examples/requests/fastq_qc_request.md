# Example Request: FASTQ Quality Control

## Goal

Please assess the raw read quality of the provided FASTQ file.

## Data Paths

- FASTQ: `./examples/data/tiny_reads.fastq`

## Execution Permission

Execution is allowed.

## Expected Outputs

- Validate that the FASTQ file has a valid record structure.
- Generate a lightweight QC summary for the input reads.
- Save any generated QC outputs under `./examples/results/fastq_qc/`.
- Report whether the file is suitable for downstream RNA-seq demonstration workflows.
