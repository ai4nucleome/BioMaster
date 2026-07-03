## Environment Setup & Reference Resources

_modules: setup, installation, reference-resources, version-check_

```bash
# LDSC Python 3 fork (official bulik/ldsc is Python 2.7, unmaintained since 2019)
# belowlab/ldsc v3.0.1 broke the --h2 / --rg / --h2-cts CLI; use abdenlab/ldsc-python3 v2.0.0
# OR run belowlab/ldsc via Docker: `docker pull jtb114/ldsc:latest`
git clone https://github.com/abdenlab/ldsc-python3.git
cd ldsc-python3
conda env create -f environment.yml
conda activate ldsc

# LDAK 6+
wget http://dougspeed.com/wp-content/uploads/ldak6.linux_.zip
unzip ldak6.linux_.zip && chmod +x ldak6.linux

# HDL (R); UKB reference panel ~5 GB from zhenin/HDL wiki
remotes::install_github('zhenin/HDL/HDL')

# HESS (Python 3 fork: huwenboshi/hess)
git clone https://github.com/huwenboshi/hess.git
pip install -r hess/requirements.txt

# BOLT-LMM / BOLT-REML, GCTA, Popcorn
wget https://alkesgroup.broadinstitute.org/BOLT-LMM/downloads/BOLT-LMM_v2.4.1.tar.gz
wget https://yanglab.westlake.edu.cn/software/gcta/bin/gcta-1.94.1-linux-kernel-3-x86_64.zip
pip install popcorn-stats

# Pre-computed reference resources (one-time download)
wget https://alkesgroup.broadinstitute.org/LDSCORE/eur_w_ld_chr.tar.bz2                       # EUR LD scores (HapMap3)
wget https://alkesgroup.broadinstitute.org/LDSCORE/1000G_Phase3_baselineLD_v2.2_ldscores.tgz # baseline-LD v2.2
wget https://alkesgroup.broadinstitute.org/LDSCORE/1000G_Phase3_frq.tgz                     # 1000G EUR frequency files
wget https://alkesgroup.broadinstitute.org/LDSCORE/1000G_Phase3_weights_hm3_no_MHC.tgz       # weights
wget https://alkesgroup.broadinstitute.org/LDSCORE/Multi_tissue_chromatin_1000Gv3_ldscores.tgz # multi-tissue chromatin ldcts

# Version checks before running
pip show <package>; python -c 'import <module>; help(<module>)'   # Python
packageVersion('<pkg>'); ?function_name                             # R
<tool> --version; <tool> --help                                    # CLI
```

## Summary Statistics Munging

_modules: munging, sumstats, allele-harmonization_

```bash
# Munge GWAS summary statistics into LDSC format
# Produces trait.sumstats.gz with SNP, A1, A2, Z, N columns
munge_sumstats.py \
    --sumstats gwas_raw.tsv \
    --N-col N \
    --snp SNP --a1 A1 --a2 A2 --p P --signed-sumstats BETA,0 \
    --merge-alleles w_hm3.snplist \
    --out trait

# For case-control or fixed-N GWAS, pass total N: --N <Ntot>
# Use --signed-sumstats BETA,0 for additive effect sign, Z,0 for Z-score (never both)
# Inspect drop count; >50% drops usually mean allele mismatch or A1/A2 swap vs HM3 reference
# Verify direction with a known sentinel SNP after munging
```

## Total SNP Heritability & Diagnostics

_modules: h2, ldsc, intercept, liability-scale, diagnostics_

```bash
# Total h2 (univariate); intercept, ratio, mean chi2 reported
ldsc.py \
    --h2 trait.sumstats.gz \
    --ref-ld-chr eur_w_ld_chr/ \
    --w-ld-chr eur_w_ld_chr/ \
    --out trait_h2

# Case-control: supply prevalence to report liability-scale h2 (Lee 2011 conversion)
ldsc.py \
    --h2 trait.sumstats.gz \
    --ref-ld-chr eur_w_ld_chr/ \
    --w-ld-chr eur_w_ld_chr/ \
    --samp-prev <case_fraction> \
    --pop-prev <population_lifetime_prevalence> \
    --out trait_h2_liab

# Diagnostics: report intercept, mean chi-square, ratio = (intercept-1)/(mean_chi2-1) jointly
#   ratio < 0.2  -> mostly polygenic, h2 trustworthy
#   ratio > 0.3  -> investigate stratification / overlap
#   mean chi-square < 1.02 OR h2 SE >= 0.02 -> estimate unreliable
#
# Intercept > 1.5 troubleshooting ladder (in order; stop when source found):
#   (a) refit GWAS with more PCs (10-20) or per-cohort separately
#   (b) king --related; remove kinship > 0.05 (0.0884 for 2nd-degree)
#   (c) check case/control PCs separately
#   (d) check bivariate intercepts pairwise for sample overlap
#   (e) recompute biobank GWAS with sample-level relatedness exclusion
```

## Functional Category Partitioning

_modules: stratified-ldsc, baseline-ld, enrichment, tau, partitioning_

```bash
# Partitioned h2 with baseline-LD v2.2 model (Gazal 2017)
ldsc.py \
    --h2 trait.sumstats.gz \
    --ref-ld-chr 1000G_Phase3_baselineLD_v2.2_ldscores/baselineLD. \
    --frqfile-chr 1000G_Phase3_frq/1000G.EUR.QC. \
    --w-ld-chr 1000G_Phase3_weights_hm3_no_MHC/weights.hm3_noMHC. \
    --overlap-annot \
    --print-coefficients \
    --out trait_partitioned

# Bonferroni threshold: 0.05 / N_annot
# baseline-LD v2.2 is EUR-only; for non-EUR use baseline-LD-X (Atkinson 2021) or per-ancestry baseline-LD
# Test custom annotations marginal to baseline (baseline + new only); never test collinear annotations jointly
# Annotation size floor >= 0.5% of genome for tau estimation
```

## Cell-Type Prioritization

_modules: cell-type, h2-cts, chromatin, tissue-prioritization_

```bash
# Cell-type prioritization (Finucane 2018)
# Inputs: trait.sumstats.gz (munged), <cts>.ldcts manifest, baseline annotations, weights
ldsc.py \
    --h2-cts trait.sumstats.gz \
    --ref-ld-chr 1000G_EUR_Phase3_baseline/baseline. \
    --ref-ld-chr-cts Multi_tissue_chromatin.ldcts \
    --w-ld-chr weights_hm3_no_hla/weights. \
    --out trait_cts

# trait_cts.cell_type_results.txt: Name, Coefficient, Coefficient_std_error, Coefficient_P_value
# Bonferroni: 0.05 / nrow; ~2.5e-4 for ~200 tissues; top tissues are trait-relevant

# Custom cell-type LD scores from a chromatin BED:
ldsc.py --l2 --bfile <ref_plink> --annot <cell>.annot.gz --out <cell>_ldscore
# Then add a row to the .ldcts manifest: name, ldscore_prefix, control_ldscore_prefix
```

## Cross-Trait Genetic Correlation

_modules: genetic-correlation, rg, hdl, cross-trait-ldsc, sample-overlap_

```bash
# Cross-trait LDSC rg (use when sample overlap exists; intercept absorbs overlap)
ldsc.py \
    --rg trait1.sumstats.gz,trait2.sumstats.gz \
    --ref-ld-chr eur_w_ld_chr/ \
    --w-ld-chr eur_w_ld_chr/ \
    --out rg
# Output: rg, se, p, gcov_int (cross-trait intercept), h2_obs, h2_int per trait
# Non-zero gcov_int under known overlap is correct (absorber), not pathology
```

```r
# HDL rg (primary when samples non-overlapping <5%; ~60% lower variance than LDSC)
library(HDL)
gwas1 <- read.table('trait1.txt', header = TRUE, stringsAsFactors = FALSE)
gwas2 <- read.table('trait2.txt', header = TRUE, stringsAsFactors = FALSE)
LD.path <- 'UKB_array_SVD_eigen90_extraction'
rg_result <- HDL.rg(gwas1.df = gwas1, gwas2.df = gwas2, LD.path = LD.path,
                    Nref = 335265, output.file = 'hdl_rg.log',
                    eigen.cut = 'automatic')
# rg_result: rg, rg.se, p, h2_1, h2_2, gen.cov
# HDL UKB reference requires non-overlapping samples; if either GWAS is UKB, HDL is biased
```

## LDAK SumHer Reconciliation

_modules: ldak, sumher, model-reconciliation, ldak-thin_

```bash
# LDAK requires header: Predictor A1 A2 n Z (Z optional; can use beta + se instead)
# Reference LDAK-Thin tagging files at dougspeed.com/pre-computed-tagging-files
ldak --sum-hers trait_sumher \
    --summary trait_ldak.txt \
    --tagfile bld.ldak.thin.hapmap.gbr.tagging \
    --check-sums NO

# Partitioned with BLD-LDAK annotations (86 continuous annotations; dougspeed.com/bldldak)
# LDAK uses --annotation-number + --annotation-prefix (continuous) or
# --partition-number + --partition-prefix (binary); no --category-file flag
ldak --sum-hers trait_bld --summary trait_ldak.txt \
    --tagfile bld.ldak.thin.hapmap.gbr.tagging \
    --annotation-number 86 \
    --annotation-prefix BaselineLD/BaselineLD \
    --check-sums NO
# Tagging files are build/ancestry-specific; hg19 vs hg38 non-interchangeable
# Report BOTH LDSC and LDAK enrichment; >2x discordance = model-dependent (Gazal 2019, Hou 2019)
```

## Local Per-Locus Heritability

_modules: hess, local-h2, ldetect, per-locus, fine-mapping_

```bash
# HESS step 1: per-chromosome local h2 quadratic forms (run per chromosome)
for chr in {1..22}; do
    hess.py \
        --local-hsqg trait.sumstats.gz \
        --chrom $chr \
        --bfile 1000G_EUR_chr${chr} \
        --partition-file LDetect_EUR_chr${chr}.bed \
        --out hess_chr${chr}
done

# HESS step 2: aggregate across chromosomes and estimate h2
# Provide total h2 and SE from LDSC for the global constraint
hess.py \
    --prefix hess_chr \
    --out trait_local_h2 \
    --tot-hsqg <total_h2_estimate> <total_h2_SE>
# Require >= 1000 SNPs per locus; sparse loci give negative/unphysical h2 -> drop or merge
# LDetect partitions (Berisa & Pickrell 2016): bitbucket.org/nygcresearch/ldetect-data (EUR/EAS/AFR)
```
