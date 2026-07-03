# Example Request: Debug RNA-seq Execution Failure

## Goal

Please diagnose why the RNA-seq differential expression step failed and propose a safe retry plan.

## Data Paths

- Count matrix: `./examples/data/rnaseq_counts.csv`
- Sample metadata: `./examples/data/rnaseq_metadata.csv`

## Failure Log

```text
/bin/sh: 1: Rscript: not found
```

## Execution Permission

Do not install packages automatically. Diagnosis commands are allowed.

## Expected Outputs

- Identify the likely cause of the failure.
- Explain whether the failure is due to a missing runtime, missing package, or invalid input.
- Provide a minimal retry plan that preserves the input data and outputs.
