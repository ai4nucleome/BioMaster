# Examples

This directory contains small inputs, request templates, and expected artifacts used by BioMaster tests.

## Tumor scRNA-seq Demo

`examples/tumor_scrnaseq_heterogeneity/` is the MVP reference route.

| File | Purpose |
|---|---|
| `user_request.md` | Example user request |
| `demo_config.yaml` | Demo run configuration |
| `expected_PLAN.yaml` | Reference 9-step plan |

Run the short and long workflow tests:

```bash
PYTHONPATH=.opencode/runtime python3 -m pytest tests/test_short_workflow.py tests/test_long_workflow.py -q
```

## Test Data

- `data/` contains synthetic RNA-seq counts, metadata, and a tiny FASTQ file.
- `real_data/` contains small sample files for FASTQ, featureCounts, ClinVar, narrowPeak, 10x, and MAF-style scenarios.
- `requests/` contains prompt templates for manual smoke tests.
- `.opencode/bioskills` is the unified skill and knowledge source that is synced into SQLite.

## Validation

```bash
make examples
make knowledge-test
make pytest
```

Generated files under `examples/results/` are ignored by Git. Use `make clean` to remove local outputs.
