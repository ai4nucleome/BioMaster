# Refhic Hic Loop Tad Annotation

## Overview

RefHiC is a reference-panel-guided deep-learning tool for annotating topological structures — chromatin loops and TAD boundaries — in Hi-C contact maps. By leveraging a pretrained model built on a reference panel of Hi-C samples, RefHiC robustly predicts loops and TAD boundaries even from low-coverage or low-quality data, where conventional tools struggle.

Inputs are Hi-C contact maps in `.cool` or `.bcool` (band-matrix cooler) format at **5 kb resolution only**. `.bcool` is RefHiC's space-saving format that discards contacts beyond 3 Mb; a standard `.cool` file is also accepted directly. Outputs are loop candidate scores (`.bedpe`), FDR-selected loops, TAD boundary scores (`.bed`), and TAD boundary annotations, plus optional pileup PNGs for sanity checking.

GPU is strongly recommended: prediction runs on CPU but is much slower, and model training is effectively impossible on CPU. The standard end-to-end workflow is: (1) install RefHiC and its PyTorch-based dependencies in a conda environment, (2) initialize the configuration and download/deploy a reference panel (default hg38 panel ~3 GB with 29 samples, or a mouse mm10 panel), (3) run loop annotation in two sub-steps — `loop pred` to score candidate loci from target and decoy maps, then `loop pool` for FDR-controlled loop selection, (4) run TAD annotation with `tad pred` to get boundary scores and extract left/right boundaries, and (5) perform sanity checks with `refhic util pileup` and interpret the output file formats. Use this skill when you have a 5 kb Hi-C contact map and want reference-guided loop/TAD annotation, especially for modest-coverage samples.

## Installation

Clone the RefHiC repository and create an isolated conda environment with the pinned dependencies. RefHiC depends on PyTorch (with CUDA support strongly recommended), plus several auxiliary libraries (torchmetrics, pytorch_ema, tensorboard, scikit-learn, scipy). After the environment is ready, install RefHiC itself in editable mode so the `refhic` command-line entry point becomes available. If the editable install fails, fall back to the setup.py build/install path. Installation requires network access and typically completes within a few minutes.

## Configuration and Reference Panel Setup

Before predicting, RefHiC must be initialized so that a reference panel and pretrained models are loaded into local configuration. The interactive `refhic config init` command offers two paths: (1) download the default reference panel (~3 GB, hg38, 29 samples) — the easiest and recommended route for human data; or (2) load a custom panel supplied as a zip of `.bcool` files plus a `meta.csv`. For mouse (mm10) data, download the mouse reference panel separately and deploy it via option (2). The reference panel and trained models are built for **5 kb resolution only**. You can later inspect or hand-edit the configuration with `refhic config edit`.

## Loop Annotation

Loop annotation is a two-step procedure. First, `refhic loop pred` scans a contact map and scores candidate loop loci, emitting candidates from both the target map and a permuted decoy map (the decoy is used downstream for FDR estimation). Second, `refhic loop pool` performs FDR-controlled selection on the candidate file to produce the final set of loops from the target data. For low-coverage or low-quality maps, raising the FDR alpha (e.g. to 0.1) retains more loops at the cost of more false positives. Device selection: leave `--cpu`/`--gpu` at default to use GPU, set `--cpu True` for CPU (much slower), or set `--gpu <index>` to pick a specific GPU.

## TAD Annotation

TAD annotation is a single prediction step. `refhic tad pred` computes per-locus left and right boundary scores across the requested chromosome and writes them to a `.bed` file. Each row reports the genomic bin, the left/right boundary scores (range -1 to 1), and 0/1 flags indicating whether a left and/or right boundary is called at that bin. Left and right boundary calls are then extracted into separate BED files with a simple awk filter. As with loops, raising alpha (e.g. to 0.1) selects more boundaries for low-coverage data at the cost of more false positives.

## Sanity Check and Output Interpretation

Because there is no ground truth for loops/TADs in real experiments, RefHiC provides a pileup utility to visually and quantitatively validate annotations. `refhic util pileup` averages the contact map around supplied foci (called loops or boundary positions) and writes a PNG; enabling the `--p2ll` option additionally computes the peak-to-lower-left ratio on the averaged contacts, which is especially informative for assessing loop quality. A clear focal enrichment in the pileup (high P2LL for loops; clear corner/insulation signal for boundaries) indicates reliable annotations, while a flat/noisy pileup suggests the calls may be spurious — often a sign to adjust alpha or check input data quality.
