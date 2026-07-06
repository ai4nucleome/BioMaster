## Backend Selection

_modules: tool-selection, prerequisites, environment_

```text
Decision tree:

What are you predicting?
  - Single protein          -> ESMFold (faster)
  - Protein-protein complex -> AlphaFold / ColabFold
  - Protein + ligand        -> Chai or Boltz (not this skill)
  - Batch of sequences      -> ColabFold

What do you need?
  - Highest accuracy        -> AlphaFold / ColabFold
  - Fast screening          -> ESMFold
  - MSA-free prediction     -> Chai or ESMFold

Which AF2 option?
  - Local installation      -> Full control, slow setup
  - ColabFold               -> Easier, MSA server
  - Modal                   -> Recommended for batch

Prerequisites:
  Python:   3.8+ (3.10 recommended)
  CUDA:     11.0+ (12.0+ recommended)
  GPU VRAM: 32GB min (40GB A100 recommended)
  RAM:      32GB min (64GB recommended)
  Disk:     100GB min (500GB recommended for databases)
```

## Structure Prediction

_modules: structure-prediction, colabfold, alphafold, esmfold, multimer_

```bash
# Option 1: ColabFold (recommended for multimer / batch)
cd biomodals
modal run modal_colabfold.py \
  --input-faa sequences.fasta \
  --out-dir output/
# GPU: A100 (40GB) | Timeout: 3600s default

# Option 2: Local AlphaFold2 installation
git clone https://github.com/deepmind/alphafold.git
cd alphafold

python run_alphafold.py \
  --fasta_paths=query.fasta \
  --output_dir=output/ \
  --model_preset=monomer \
  --max_template_date=2026-01-01

# Option 3: ESMFold (fast single-chain)
modal run modal_esmfold.py \
  --sequence "MKTAYIAKQRQISFVK..."

# Key parameters:
#   --model_preset      monomer | multimer   (default: monomer)
#   --num_recycle       1-20                  (default: 3)
#   --max_template_date YYYY-MM-DD            (template cutoff)
#   --use_templates     True | False          (default: True)
```

Expected output directory layout:
```text
output/
  ranked_0.pdb           # Best model
  ranked_1.pdb           # Second best
  ranking_debug.json     # Confidence scores
  result_model_1.pkl     # Full results
  msas/                  # MSA files
  features.pkl           # Input features
```

## Confidence Metric Extraction

_modules: confidence-metrics, plddt, ptm, iptm, pae, metric-extraction_

```python
import pickle

with open('result_model_1.pkl', 'rb') as f:
    result = pickle.load(f)

plddt = result['plddt']              # per-residue + mean, 0-100 scale
ptm = result['ptm']                  # predicted TM-score
iptm = result.get('iptm', None)      # interface pTM (multimer only)
pae = result['predicted_aligned_error']  # PAE matrix
```

Typical successful-run metrics (multimer example):
```text
ranked_0.pdb:
  pLDDT: 87.3 (mean)
  pTM:   0.78
  ipTM:  0.62
  PAE (interface): 8.5
```

## Quality Assessment & Verification

_modules: qc, validation, thresholds, verification_

```text
Quality thresholds (good output):
  pLDDT:           > 85   (mean, 0-100 scale)  or  > 0.85 (normalized)
  pTM:             > 0.70
  ipTM:            > 0.50  (complexes only)
  PAE_interface:   < 10

Interpretation guide:
  Low pLDDT regions      -> disorder or poor design
  Low ipTM               -> interface not confident, check hotspots
  High PAE off-diagonal  -> chains may not interact
```

```bash
# Verify all expected outputs were produced
find output -name "ranked_0.pdb" | wc -l  # Should match input count
```

Typical performance (A100):
```text
  100 complexes  -> 1-2h   ~$8   (with MSA server)
  500 complexes  -> 5-10h  ~$40  (standard campaign)
  1000 complexes -> 10-20h ~$80  (large campaign)
  Per-complex    -> ~30-60s      (with MSA server)
```

## Troubleshooting

_modules: troubleshooting, error-handling, diagnostics_

```text
Error interpretation table:

Error                                  | Cause                          | Fix
---------------------------------------|--------------------------------|------------------------------------------
RuntimeError: CUDA out of memory       | Sequence too long              | Use A100 or split prediction
KeyError: 'iptm'                       | Running monomer on complex     | Use multimer preset
FileNotFoundError: database            | Missing MSA databases          | Use ColabFold MSA server
TimeoutError                           | MSA search slow                | Reduce num_recycles

General guidance:
  - OOM errors        -> Use ColabFold with MSA server instead of local
  - Low pLDDT regions -> May indicate disorder or poor design
  - Low ipTM          -> Interface not confident, check hotspots
  - High PAE off-diag -> Chains may not interact

Next step: protein-qc for filtering and ranking of designs.
```
