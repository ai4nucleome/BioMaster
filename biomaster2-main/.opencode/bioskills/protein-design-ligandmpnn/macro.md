# Protein Design Ligandmpnn

## Overview

LigandMPNN performs ligand-aware protein sequence design (inverse folding) that conditions on small molecules, metals, cofactors, and DNA/RNA present in the input structure. Use it for enzyme active site design, ligand binding pocket optimization, metal coordination site design, and cofactor-binding proteins.

Inputs: a PDB file containing the protein backbone plus ligand(s) encoded as HETATM records with valid residue names and real atomic coordinates. Supported ligand types include small molecules (HETATM), metal ions (Zn, Fe, Mg, Ca, etc.), cofactors (NAD, FAD, ATP), and DNA/RNA.

Outputs: a FASTA file of designed sequences (each header carries per-sequence score and global_score) and PDB files with the designed sequences threaded onto the input backbone.

When to use: choose LigandMPNN when the binding site contains a small molecule, metal, cofactor, or nucleic acid whose context should guide the design. For standard protein design without ligands, use ProteinMPNN; for solubility/expression optimization, consider SolubleMPNN. Typical throughput is ~50-100 sequences/minute on a T4 GPU (16GB); a 100-backbone x 8-sequence campaign takes ~15-20 minutes (~$2 on Modal). Downstream steps: structure prediction for validation, then protein-QC for filtering.

## Input Preparation

Prepare and validate the input PDB so that LigandMPNN can detect the ligand. The ligand must be present as HETATM records with a valid residue name and real atomic coordinates, while protein atoms are ATOM records. Confirm the ligand type is supported (small molecules, metals such as Zn/Fe/Mg/Ca, cofactors such as NAD/FAD/ATP, or DNA/RNA). This step gates the rest of the workflow because LigandMPNN will fail or ignore the ligand if the HETATM records are malformed, misnamed, or empty.

## Design Execution

Run LigandMPNN to generate designed sequences conditioned on the ligand context. Two execution paths are supported: Modal (recommended, cloud T4 GPU 16GB, 600s default timeout) for convenience and autoscaling, or a local installation cloned from the LigandMPNN repository for full control and offline use. Key parameters control the number of sequences per target and the sampling temperature (passed as a string); ligand side-chain context is enabled by default. Lower sampling temperatures yield more conservative/greedy sequences.

## Output Verification

Verify that the run produced the expected number of sequences and that the ligand was incorporated into the design context. Check the FASTA sequence count against backbone_count x num_seq_per_target, inspect per-sequence scores (lower is more confident; good designs typically score 1.0-2.0), and confirm the output PDBs were written. This step ensures the campaign is complete before downstream structure prediction or QC filtering.

## Troubleshooting

Diagnose and resolve common LigandMPNN failures. Typical issues include CUDA out-of-memory on long proteins or large batches (reduce batch size), ligand not found in the PDB (check HETATM records and residue name), and empty ligand atoms (verify ligand coordinates are present). Poor binding residues or missing contacts can often be improved by increasing sampling around the active site and re-verifying ligand coordinates in the PDB.
