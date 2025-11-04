#!/bin/bash
# BioMaster environment installation script (for Docker build)
# Fallback strategy if conda env create fails

set -e

ENV_FILE="/app/biomaster-docker.yml"
ENV_NAME="biomaster-docker"

# Initialize conda
source /opt/conda/etc/profile.d/conda.sh

echo "Using fallback strategy: installing core packages manually..."
echo "Creating base environment..."

# Create base Python environment
if command -v mamba &> /dev/null; then
    mamba create -y -n "$ENV_NAME" python=3.11.14 -c conda-forge
else
    conda create -y -n "$ENV_NAME" python=3.11.14 -c conda-forge
fi

# Activate environment
conda activate "$ENV_NAME"

echo "Installing core scientific packages..."

# Use mamba or conda to install core packages (step by step to avoid conflicts)
INSTALLER="conda"
if command -v mamba &> /dev/null; then
    INSTALLER="mamba"
fi

# 第一批：核心数值计算包
$INSTALLER install -y -c conda-forge -c bioconda \
    numpy=1.26.4 \
    pandas=2.3.3 \
    scipy=1.14.1 \
    scikit-learn=1.7.2 \
    numba=0.62.1 \
    llvmlite=0.45.1 || true

# 第二批：可视化包
$INSTALLER install -y -c conda-forge \
    matplotlib-base=3.10.7 \
    seaborn=0.13.2 \
    pillow=11.3.0 || true

# 第三批：单细胞分析包
$INSTALLER install -y -c conda-forge -c bioconda \
    scanpy=1.11.5 \
    squidpy=1.2.2 \
    anndata=0.9.1 \
    h5py=3.15.1 || true

# 第四批：数据处理包
$INSTALLER install -y -c conda-forge \
    dask=2025.10.0 \
    distributed=2025.10.0 \
    xarray=2025.10.1 \
    zarr=2.18.3 || true

# 第五批：图分析包
$INSTALLER install -y -c conda-forge \
    networkx=3.4.2 \
    python-igraph=0.11.9 \
    leidenalg=0.10.2 \
    umap-learn=0.5.9 || true

# 第六批：图像处理包
$INSTALLER install -y -c conda-forge \
    scikit-image=0.25.0 \
    tifffile=2025.10.16 \
    imagecodecs=2025.8.2 || true

# 第七批：其他工具包
$INSTALLER install -y -c conda-forge \
    statsmodels=0.14.5 \
    joblib=1.5.2 \
    tqdm=4.67.1 \
    pyyaml=6.0.3 \
    requests=2.32.3 || true

echo "Installing pip packages..."

# Install pip packages from requirements.txt
if [ -f "/app/requirements.txt" ]; then
    pip install --no-cache-dir -r /app/requirements.txt || true
fi

echo "✅ Environment creation completed!"

