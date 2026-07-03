# Complex Example Request: RNA-seq from featureCounts Output

## Goal

Please analyze the featureCounts output as an RNA-seq count table and prepare it for downstream differential expression analysis.

## Data Paths

- featureCounts table: `./examples/real_data/slamseq_featurecounts_subset.tsv`

## Analysis Parameters

- Input type: featureCounts count table
- Gene or feature identifier column: `Geneid`
- Count columns: all BAM-derived sample columns after `Length`
- Species context: mouse-like transcript annotations

## Execution Permission

Execution is allowed for lightweight parsing, validation, and summary generation.

## Expected Outputs

- Validate the featureCounts table structure.
- Extract the count matrix from the featureCounts output.
- Summarize sample columns, feature counts, and basic count distributions.
- Save parsed outputs under `./examples/results/featurecounts_rnaseq/`.
