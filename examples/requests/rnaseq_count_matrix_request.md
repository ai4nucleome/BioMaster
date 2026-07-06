# Example Request: RNA-seq Differential Expression

## Goal

Please perform an RNA-seq differential expression analysis using the current example data.

## Data Paths

- Count matrix: `./examples/data/rnaseq_counts.csv`
- Sample metadata: `./examples/data/rnaseq_metadata.csv`
- Raw read example for QC context: `./examples/data/tiny_reads.fastq`

## Analysis Parameters

- Group column: `condition`
- Control group: `control`
- Treatment group: `treatment`
- Contrast: `treatment` versus `control`

## Execution Permission

Execution is allowed.

## Expected Outputs

- Validate that the count matrix and metadata are compatible.
- Run a minimal differential expression workflow suitable for the provided data.
- Save tabular results and diagnostic plots under `./examples/results/`.
- Summarize the main findings and any limitations caused by the small example dataset.
