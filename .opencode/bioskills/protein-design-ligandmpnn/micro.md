## Input Preparation

_modules: input-prep, pdb-validation, ligand-context_

```bash
# Inspect HETATM records in the input PDB
grep "^HETATM" protein_ligand.pdb | head

# Confirm ligand residue name(s) and that atoms are present
grep "^HETATM" protein_ligand.pdb | awk '{print $4}' | sort -u

# Expected: a ligand residue name (e.g. LIG, ZN, NAD) with non-zero atoms.
# Protein atoms must be ATOM records; ligand atoms HETATM records, e.g.:
#   HETATM  1  C1  LIG A 999      x.xxx  y.yyy  z.zzz  1.00  0.00           C
```

## Design Execution

_modules: sequence-design, inverse-folding, sampling_

```bash
# Option 1: Modal (recommended) — T4 GPU (16GB), 600s default timeout
cd biomodals
modal run modal_ligandmpnn.py \
  --pdb-path protein_ligand.pdb \
  --num-seq-per-target 16 \
  --sampling-temp 0.1

# Option 2: Local installation
git clone https://github.com/dauparas/LigandMPNN.git
cd LigandMPNN
python run.py \
  --pdb_path protein_ligand.pdb \
  --out_folder output/ \
  --num_seq_per_target 16

# Key parameters:
#   --pdb_path                            required   path to PDB with ligand
#   --num_seq_per_target                  1          1-1000   sequences per structure
#   --sampling_temp                       "0.1"      "0.0001-1.0"  temperature (STRING!)
#   --ligand_mpnn_use_side_chain_context  true       bool     use ligand context
# GPU: T4 (16GB) recommended, 8GB minimum. ~50-100 seq/min on T4.
```

## Output Verification

_modules: output-verification, qc, scoring_

```bash
# Count designed sequences (should equal backbone_count x num_seq_per_target)
grep -c "^>" output/seqs/*.fa

# Inspect per-sequence scores (lower = more confident; good range 1.0-2.0)
head output/seqs/*.fa

# Confirm output PDBs were written
ls output/protein_pdb/

# Expected output layout:
# output/
# ├── seqs/protein.fa              # FASTA with score=, global_score= headers
# └── protein_pdb/protein_0001.pdb # PDBs with designed sequence
```

## Troubleshooting

_modules: troubleshooting, error-handling, debugging_

```bash
# Common errors and fixes:
# RuntimeError: CUDA out of memory
#   Cause: long protein or large batch
#   Fix:  reduce batch_size
#
# KeyError: 'LIG'
#   Cause: ligand residue name not found in PDB
#   Fix:  verify HETATM records and ligand residue name
#
# ValueError: no ligand atoms
#   Cause: ligand entry has no atoms
#   Fix:  verify ligand coordinates are present in PDB
#
# Poor binding residues / missing contacts:
#   Increase sampling around the active site; verify ligand coordinates.
```
