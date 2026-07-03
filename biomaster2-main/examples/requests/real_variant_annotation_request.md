# Complex Example Request: ClinVar-Style Variant Review

## Goal

Please review the ClinVar-style variant annotation table and summarize clinically relevant EXOSC variants.

## Data Paths

- Variant table: `./examples/real_data/exosc_clinvar_subset.tsv`

## Analysis Parameters

- Input type: tabular variant annotation
- Gene column: `gene_name`
- Variant descriptor column: `HGVS`
- Clinical classification column: `clinical_significance`
- Prioritize: `Pathogenic`, `Likely pathogenic`, and `Uncertain significance`

## Execution Permission

Execution is allowed for lightweight parsing, validation, and summary generation.

## Expected Outputs

- Validate the required columns.
- Count variants by gene and clinical significance.
- List clinically relevant variants with HGVS, accession, preferred name, and condition.
- Save summary outputs under `./examples/results/variant_annotation/`.
