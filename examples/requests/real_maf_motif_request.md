# Complex Example Request: MAF Motif Search

## Goal

Please search the multiple-alignment file for candidate conserved motif occurrences.

## Data Paths

- MAF file: `./examples/real_data/test_alignment_subset.maf`

## Analysis Parameters

- Input type: MAF multiple alignment
- Motifs: `AGT`, `CTGCCCGCA`
- Reference sequence prefix: `ref_genome`
- Report motif occurrences across aligned sequence rows when possible

## Execution Permission

Execution is allowed for lightweight parsing, validation, and motif scanning.

## Expected Outputs

- Validate the MAF header and alignment block structure.
- Count alignment blocks and sequence rows.
- Report motif matches by block and sequence name.
- Save summary outputs under `./examples/results/maf_motif/`.
