# Complex Example Request: ChIP-seq Peak Interpretation

## Goal

Please summarize and validate the ChIP-seq peak-calling results from the provided narrowPeak file.

## Data Paths

- Peak file: `./examples/real_data/srr620208_peaks_subset.narrowPeak`

## Analysis Parameters

- Input type: MACS-style narrowPeak
- Genome context: human-like chromosome labels
- Primary metrics: peak width, score, signal value, q-value, summit offset

## Execution Permission

Execution is allowed for lightweight parsing, validation, and summary generation.

## Expected Outputs

- Validate that the file follows the 10-column narrowPeak structure.
- Summarize the number of peaks, genomic coordinate range, score distribution, and peak widths.
- Identify any malformed rows or suspicious coordinates.
- Save summary outputs under `./examples/results/chipseq_peaks/`.
