## System Selection

_modules: system-selection, extract-choice_

# CFPS system decision matrix
# System              | Best For                          | Yield          | PTMs          | Disulfides        | Cost
# --------------------|-----------------------------------|----------------|---------------|-------------------|----------
# E. coli extract     | Rapid prototyping, prokaryotic    | 100-400 ug/mL  | None          | Poor (reducing)   | Low
# E. coli PURE        | Defined conditions, unnatural AAs | 50-150 ug/mL   | None          | Controllable      | High
# Wheat germ          | Eukaryotic, membrane proteins     | 100-500 ug/mL  | Limited       | Moderate          | Medium
# Rabbit reticulocyte | Mammalian, post-translational     | 10-50 ug/mL    | Some          | Poor              | High
# Insect (Sf21)       | Glycoproteins, complex folds      | 50-100 ug/mL   | Glycosylation | Good              | High
# HeLa/CHO            | Native mammalian proteins         | 10-50 ug/mL    | Full mammalian| Good              | Very High

# Selection logic:
#   prokaryotic / rapid prototype      -> E. coli extract
#   unnatural AAs / defined conditions -> E. coli PURE
#   eukaryotic / membrane              -> Wheat germ
#   mammalian PTM studies              -> Rabbit reticulocyte
#   glycosylation required             -> Insect Sf21
#   native mammalian folding/PTMs      -> HeLa/CHO

## Template Design

_modules: codon-optimization, utr-design, template-format_

# Codons to AVOID in E. coli CFPS (low tRNA abundance):
#   AGG (Arg, 0.2%), AGA (Arg, 0.4%), CUA (Leu, 0.4%),
#   AUA (Ile, 0.5%), CGA (Arg, 0.6%), CCC (Pro, 0.5%), GGA (Gly, 1.1%)

# Codon optimization design rules:
#   1. First 30 codons: use ONLY high-frequency codons (most critical)
#   2. Rare codon clusters: avoid 2+ rare codons within 10 nt
#   3. Overall rare codon content: <5% of coding sequence
#   4. GC content: 40-60% (ideal 45-55%)
#   5. Avoid runs: no >6 consecutive G or C residues
#   6. Strategic slow codons: place rare codons BETWEEN domains (aids folding)

# 5' UTR design:
#   RBS (Shine-Dalgarno): AGGAGG, 7-9 nt upstream of start
#   Spacing: 7 nt between SD and AUG
#   Secondary structure: dG > -5 kcal/mol (-30 to +30 around AUG)
#   Full 5' UTR dG > -10 kcal/mol
#   RBS must be unpaired (accessible)
#   Avoid upstream AUG (prevents false starts / truncations)

# Template format choice:
#   Plasmid     -> stable, high yield; requires cloning
#   Linear PCR  -> fast, no cloning; may need stabilization
#   mRNA        -> direct translation; unstable, expensive

## Expression Prediction

_modules: sequence-assessment, yield-prediction_

# Sequence feature scoring for expression prediction
#
# Feature                | Good            | Marginal            | Bad
# -----------------------|-----------------|---------------------|----------------------
# Rare codon content     | <3%             | 3-8%                | >10%
# First 30 codons (rare) | 0               | 1-2                 | >2
# GC content             | 45-55%          | 35-45% or 55-65%    | <30% or >70%
# 5' UTR dG              | > -3 kcal/mol   | -3 to -8 kcal/mol   | < -10 kcal/mol
# Hydrophobic stretches  | <5 consecutive  | 5-7                 | >8 consecutive
# N-terminal residue     | Met-Ala/Ser/Gly | Met-Val/Thr         | Met-Arg/Lys
# Cysteine pairs         | Paired (even)   | Mixed               | Odd (free thiols)
#
# Action:
#   any Bad feature    -> redesign template before expression
#   Marginal features  -> proceed with monitoring / apply targeted fixes

## Disulfide Bond Engineering

_modules: disulfide, oxidative-folding, pdi, redox_

# Oxidative folding protocol (E. coli extract) for disulfide-rich proteins
```python
# 1. Deplete DTT from extract (dialysis or treat with IAM 5 mM)
# 2. Add oxidized/reduced glutathione redox pair:
#      4 mM GSSG : 1 mM GSH  (4:1 ratio)
# 3. Add 10 uM PDI (protein disulfide isomerase)
# 4. Optional: add 5 uM DsbC (disulfide isomerase)
# 5. Express at 25 C (NOT 37 C) for better folding
# 6. Incubation time: 4-6 hours
# 7. Verify disulfide formation by non-reducing SDS-PAGE
```

# System disulfide capabilities:
#   Standard E. coli extract  -> Poor (DTT present); add IAM, PDI, GSSG/GSH
#   Oxidizing E. coli extract -> Good; pre-oxidized glutathione
#   Wheat germ                -> Moderate; lower DTT, add PDI
#   PURE system               -> Minimal; supply full oxidative system
#   Insect/Mammalian          -> Good; microsome membranes
#
# Tips for disulfide-rich proteins:
#   - Start with wheat germ or oxidizing extract
#   - Use PURE system for precise redox control
#   - Co-express PDI/DsbC

## Solubility Enhancement

_modules: solubility, fusion-tags, chaperones, additives_

# Fusion tags (ranked by solubility enhancement):
#   MBP  (40 kDa) - Excellent  - cleavage: TEV/Factor Xa - best overall
#   SUMO (11 kDa) - Very Good  - cleavage: SUMO protease  - native N-terminus after cleavage
#   NusA (55 kDa) - Excellent  - no cleavage             - large size
#   Trx  (12 kDa) - Good       - cleavage: Enterokinase  - for disulfide proteins
#   GST  (26 kDa) - Moderate   - dimeric
#   His6 (1 kDa)  - Minimal    - mainly for purification

# Buffer additives for solubility:
#   Trehalose   50-100 mM   chemical chaperone
#   Glycerol    5-10%       reduces hydrophobic aggregation
#   L-Arginine  50-100 mM   suppresses aggregation
#   Tween-20    0.05-0.1%   prevents surface adsorption
#   Proline     50 mM       osmolyte stabilization

# Chaperone supplementation:
#   GroEL/GroES        general folding             1-2 uM
#   DnaK/DnaJ/GrpE     aggregation-prone           1 uM each
#   Trigger Factor     nascent chain               1-2 uM
#   ClpB               aggregate resolubilization  0.5 uM

## Troubleshooting and Optimization

_modules: troubleshooting, yield-optimization, diagnostics_

# CFPS troubleshooting matrix
#
# Problem          | Likely Causes                     | Design Fix                       | Reagent Fix
# -----------------|-----------------------------------|----------------------------------|--------------------------------
# No expression    | Rare codons at N-term, poor RBS   | Codon optimize first 30 codons   | BL21-CodonPlus extract
# Low yield        | mRNA 2nd structure, template      | Optimize 5' UTR (dG > -5)        | Increase Mg2+ (10-18 mM), ATP
# Aggregation      | Hydrophobic, fast translation     | Add solubility tags (MBP/SUMO)   | 0.1% Tween-20, chaperones
# Inactive protein | Misfolding, missing cofactors     | Slow translation (rare codons)   | GroEL/ES, DnaK/J
# Truncation       | Rare codon clusters, mRNA unstable| Remove AGG/AGA/CUA clusters      | Supplement rare tRNAs
# Degradation      | Proteolysis                       | N-terminal Met-Ala               | Protease inhibitors
