## Installation

_modules: installation, conda, pytorch_

```bash
# Clone the repository
git clone https://github.com/BlanchetteLab/RefHiC.git
cd RefHiC

# Create a conda environment from the pinned requirements (Python 3.9)
conda create --name refhic --file requirements.txt python=3.9
conda activate refhic

# Install PyTorch matching your CUDA version (see https://pytorch.org/get-started/locally/)
# Example for CUDA 11.3:
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113

# Additional libraries required by RefHiC
pip install torchmetrics
pip install -U git+https://github.com/fadel/pytorch_ema
pip install tensorboard
pip install -U scikit-learn
pip install scipy==1.7.3

# Install RefHiC (editable mode, exposes the `refhic` CLI)
pip install --editable .

# Fallback if the editable install fails:
# python setup.py build && python setup.py install

# Verify the CLI is available
refhic --help
```

Note: RefHiC used LARS (torchlars) for contrastive pretraining but removed it due to compatibility issues. Contrastive pretraining now uses Adam by default; if you want LARS for custom training, install `pip install torchlars` and uncomment lines 6 and 10 in `pretrain.py`.

## Configuration and Reference Panel Setup

_modules: configuration, reference-panel, hg38, mm10_

```bash
# Initialize RefHiC (interactive prompt)
refhic config init
# At the prompt choose:
#   (1) download the default reference panel (~3GB, hg38, 29 samples)  [recommended for human]
#   (2) load your own panel (a zip containing .bcool files + meta.csv with header: sample,file)

# --- Mouse (mm10) panel ---
# Download the mouse reference panel, then run `refhic config init` and choose option (2):
wget http://repo.cs.mcgill.ca/PUB/blanchem/RefHiC/mouseRefPanel.zip
# unzip it, ensure meta.csv lists each sample with an absolute path in the `file` column,
# re-zip the .bcool files + meta.csv, then point option (2) at that zip.

# Inspect / manually edit the configuration if needed
refhic config edit
```

Key constraints:
- Reference panel and pretrained models are valid for **5 kb resolution** data only.
- For custom panels, `meta.csv` must have header `sample,file` and the `file` field must contain absolute paths to `.bcool` files.
- You can override the configured panel/model per-run with `--reference meta.csv` and `--modelState <model>` on the `pred` commands.

## Loop Annotation

_modules: loop-calling, fdr, prediction_

```bash
# --- Step 1: score candidate loops (target + decoy). ~10 min/chromosome on GPU.
refhic loop pred --chrom chr17 gm12878_500M.bcool gm12878_500M_chr17_loopCandidates.bedpe
# Options:
#   --chrom <chr>      chromosome to analyze
#   --cpu True         force CPU (slow)
#   --gpu <index>      select a specific GPU
#   --reference meta.csv     override configured reference panel
#   --modelState <model>     override configured model
# Input: .cool or .bcool at 5kb resolution. Output: candidate loops .bedpe

# --- Step 2: select loops via FDR control. ~1 min.
refhic loop pool gm12878_500M_chr17_loopCandidates.bedpe gm12878_500M_chr17_loop.bedpe
# For low-coverage/low-quality data, increase alpha to retain more loops:
#   refhic loop pool --alpha 0.1 gm12878_500M_chr17_loopCandidates.bedpe gm12878_500M_chr17_loop.bedpe
```

Output format (tab-separated, candidate file):
```
Chr1  Start1  End1  Chr2  Start2  End2  Score  IF  P2LL  Label
```
- `Score`: RefHiC loop score [0-1]
- `IF`: interaction frequency
- `P2LL`: peak-to-lower-left ratio (informational; not used by RefHiC)
- `Label`: whether the candidate came from the target or decoy set (consumed by `pool`)

Final loops file (`loop.bedpe`): same columns as above **without** the `Label` field (all retained loops are from the target).

## TAD Annotation

_modules: tad-annotation, boundary-detection, prediction_

```bash
# --- Predict TAD boundary scores. ~5 min/chromosome on GPU.
refhic tad pred --chrom chr17 gm12878_500M.bcool gm12878_500M_chr17_BoundaryScores.bed
# Options:
#   --chrom <chr>      chromosome to analyze
#   --cpu True         force CPU (slow)
#   --gpu <index>      select a specific GPU
#   --alpha <float>    FDR threshold; raise to 0.1+ for low-coverage data
#   --reference / --modelState   override configured panel/model
# Input: .cool or .bcool at 5kb resolution.

# --- Extract left and right boundaries from the boundary-score file.
# Column 5 = LeftBoundary flag; last column ($NF) = RightBoundary flag.
cat gm12878_500M_chr17_BoundaryScores.bed | awk '{if($5==1)print}'  > gm12878_500M_chr17_leftBoundary.bed
cat gm12878_500M_chr17_BoundaryScores.bed | awk '{if($NF==1)print}' > gm12878_500M_chr17_rightBoundary.bed
```

Output format — boundary scores file (7 columns, tab-separated, no header):
```
Chr  Start  End  LeftScore  LeftBoundary  RightScore  RightBoundary
```
- `LeftScore`/`RightScore`: boundary scores [-1 to 1]
- `LeftBoundary`/`RightBoundary`: 1 = boundary called, 0 = non-boundary

TADs can be derived by pairing consecutive left/right boundaries; the repository also provides a BED file listing TADs (one TAD per line) as an additional output.

## Sanity Check and Output Interpretation

_modules: pileup, sanity-check, interpretation, qc_

```bash
# --- Pileup around called loops (with P2LL computation). ~1 min.
refhic util pileup --p2ll True gm12878_500M_chr17_loop.bedpe gm12878_500M.bcool
# Produces: gm12878_500M_chr17_loop.bedpe_pileup.png

# --- Pileup around TAD boundaries. ~1 min each.
refhic util pileup gm12878_500M_chr17_leftBoundary.bed  gm12878_500M.bcool
refhic util pileup gm12878_500M_chr17_rightBoundary.bed gm12878_500M.bcool
# Produces: <input>_pileup.png for each
```

Interpretation guide:
- **Loops:** a bright, centered focal enrichment with high P2LL in the pileup PNG supports the called loops; a diffuse/flat pileup suggests false positives — consider tightening alpha or improving input coverage.
- **TAD boundaries:** the pileup should show a characteristic insulation/corner pattern at the boundary positions.
- **Low-coverage data:** if pileups are noisy, re-run `loop pool` / `tad pred` with a higher `--alpha` (e.g. 0.1) to trade specificity for sensitivity, then re-check pileups.
- **Output files summary:**
  - `*_loopCandidates.bedpe` — scored candidates (target + decoy, with Label)
  - `*_loop.bedpe` — final FDR-selected loops (no Label)
  - `*_BoundaryScores.bed` — per-bin left/right boundary scores and 0/1 calls
  - `*_leftBoundary.bed` / `*_rightBoundary.bed` — extracted boundary positions
  - `*_pileup.png` — averaged contact-map images for sanity checking
