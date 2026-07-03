## Environment Setup

_modules: setup, installation, environment_

```bash
# --- Option 1: Modal (recommended, no local GPU needed) ---
# First time: follow docs/installation.md to set up Modal and biomodals
cd biomodals

# --- Option 2: Local installation ---
git clone https://github.com/martinacesa/BindCraft.git
cd BindCraft
pip install -r requirements.txt
```

Prerequisites table:
| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python      | 3.9+    | 3.10        |
| CUDA        | 11.7+   | 12.0+       |
| GPU VRAM    | 32GB    | 48GB (L40S) |
| RAM         | 32GB    | 64GB        |

## Input Preparation & Protocol Selection

_modules: input-preparation, protocol-selection, parameters_

Key parameters:
| Parameter           | Default  | Range      | Description            |
|---------------------|----------|------------|------------------------|
| --target-pdb        | required | path       | Target structure       |
| --target-chain      | required | A-Z        | Target chain(s)        |
| --binder-lengths    | 70-100   | 40-150     | Length range           |
| --hotspots          | None     | residues   | Target hotspots        |
| --num-designs       | 50       | 1-500      | Number of designs      |
| --protocol          | default  | fast/default/slow | Quality vs speed |

Protocols:
| Protocol | Speed | Quality | Use Case           |
|----------|-------|---------|--------------------|
| fast     | Fast  | Lower   | Initial screening  |
| default  | Medium| Good    | Standard campaigns |
| slow     | Slow  | High    | Final production   |

## Campaign Execution

_modules: execution, hallucination, af2-validation_

```bash
# --- Option 1: Modal (recommended) ---
cd biomodals
modal run modal_bindcraft.py \
  --target-pdb target.pdb \
  --target-chain A \
  --binder-lengths 70-100 \
  --hotspots "A45,A67,A89" \
  --num-designs 50
# GPU: L40S (48GB) | Timeout: 3600s default

# --- Option 2: Local installation ---
python bindcraft.py \
  --target target.pdb \
  --target_chains A \
  --binder_lengths 70-100 \
  --hotspots A45,A67,A89 \
  --num_designs 50
```

Typical performance (L40S):
| Campaign Size | Time     | Cost (Modal) | Notes            |
|---------------|----------|--------------|------------------|
| 50 designs    | 2-4h     | ~$15         | Quick campaign   |
| 100 designs   | 4-8h     | ~$30         | Standard         |
| 200 designs   | 8-16h    | ~$60         | Large campaign   |

## Output & Metrics QC

_modules: qc, metrics, output-interpretation_

Output layout:
```
output/
├── design_0/
│   ├── binder.pdb         # Final design
│   ├── complex.pdb        # Binder + target
│   ├── metrics.json       # QC scores
│   └── trajectory/        # Optimization trajectory
├── design_1/
│   └── ...
└── summary.csv            # All metrics
```

Per-design metrics.json:
```json
{
  "plddt": 0.89,
  "ptm": 0.78,
  "iptm": 0.62,
  "pae": 8.5,
  "rmsd": 1.2,
  "sequence": "MKTAYIAK..."
}
```

Quality thresholds:
- pLDDT: > 0.85 for most designs (well-folded)
- ipTM: > 0.5 for passing designs (binder-target interface)
- Pass rate: 30-70% depending on target
- Diverse sequences across designs

Next: Rank by ipSAE -> experimental validation.

## Verification & Troubleshooting

_modules: verification, troubleshooting, error-handling_

```bash
# Verify output count matches num_designs
find output -name "binder.pdb" | wc -l
```

Troubleshooting:
| Error                              | Cause                          | Fix                                          |
|------------------------------------|--------------------------------|----------------------------------------------|
| RuntimeError: CUDA out of memory   | Large target or long binder    | Use L40S/A100, reduce binder length          |
| ValueError: no hotspots            | Hotspots not found             | Check residue numbering matches PDB          |
| TimeoutError                       | Design taking too long         | Use fast protocol                            |

General guidance:
- Low ipTM scores: check hotspot selection, increase num-designs
- Slow convergence: use fast protocol for screening
- OOM errors: reduce num_models, use L40S/A100 GPU
- Poor diversity: lower sampling_temp, run multiple seeds
