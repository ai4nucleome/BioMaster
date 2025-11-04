# BioMaster Dockerfile
# Production-ready Docker image with all dependencies

FROM continuumio/miniconda3:latest

# 防止Python写.pyc文件并启用无缓冲日志
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CONDA_AUTO_UPDATE_CONDA=false \
    CONDA_AUTO_ACTIVATE_BASE=true

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      git \
      ca-certificates \
      wget \
      bzip2 \
      libgl1-mesa-glx \
      libglib2.0-0 \
      bash \
      pkg-config \
      libcairo2-dev \
      libpango1.0-dev \
      libgdk-pixbuf2.0-dev \
      libffi-dev \
      libssl-dev \
      libxml2-dev \
      libxslt1-dev \
      zlib1g-dev \
      libjpeg-dev \
      libpng-dev \
      libfreetype6-dev \
      libx11-dev \
      libxext-dev \
      libxrender-dev \
      libxt-dev \
      libhdf5-dev \
      libnetcdf-dev \
      libgdal-dev \
      libproj-dev \
      libgeos-dev \
      libudunits2-dev \
      libv8-dev && \
    rm -rf /var/lib/apt/lists/*

# Configure conda channels
RUN conda config --set show_channel_urls false && \
    conda config --add channels defaults && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    conda config --add channels https://repo.anaconda.com/pkgs/main && \
    conda config --add channels https://repo.anaconda.com/pkgs/r && \
    conda config --set channel_priority flexible

# Install mamba (faster dependency resolver)
RUN conda install -y mamba -n base -c conda-forge

# 创建工作目录
WORKDIR /app

# Copy environment file and project files
COPY docker/biomaster-docker.yml /app/biomaster-docker.yml
COPY requirements.txt /app/requirements.txt
COPY . /app

# Create non-root user
RUN useradd -m -s /bin/bash biouser

# Copy installation script
COPY docker/install_env.sh /app/install_env.sh
RUN chmod +x /app/install_env.sh

# Create biomaster-docker environment (multi-level fallback strategy)
# Note: This runs as root user before switching to biouser
RUN /bin/bash -c "\
    source /opt/conda/etc/profile.d/conda.sh && \
    if ! mamba env create -f /app/biomaster-docker.yml -n biomaster-docker 2>&1; then \
        echo 'mamba failed, trying conda with libmamba solver...' && \
        if ! conda env create -f /app/biomaster-docker.yml -n biomaster-docker --solver=libmamba 2>&1; then \
            echo 'conda failed, using fallback script...' && \
            /app/install_env.sh; \
        fi; \
    fi && \
    if [ ! -f /opt/conda/envs/biomaster-docker/bin/python3.11 ]; then \
        echo 'ERROR: Environment creation failed - python not found' && \
        exit 1; \
    fi && \
    echo 'Environment created successfully' && \
    /opt/conda/envs/biomaster-docker/bin/python3.11 --version"

# Create necessary directories
RUN mkdir -p /app/output /app/data /app/chroma_db /app/doc /app/graph_db /app/hybrid_db

# Set directory permissions
RUN chown -R biouser:biouser /app && \
    chown -R biouser:biouser /opt/conda

# Switch to non-root user
USER biouser

# Initialize conda for biouser
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate biomaster-docker" >> ~/.bashrc

# Working directory (mapped to host current directory)
WORKDIR /work

# Environment variables
ENV CONFIG_PATH=config.yaml \
    PATH="/opt/conda/envs/biomaster-docker/bin:/opt/conda/bin:${PATH}" \
    CONDA_DEFAULT_ENV=biomaster-docker

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD /opt/conda/envs/biomaster-docker/bin/python3.11 -c "import sys,os; sys.exit(0 if os.path.exists(os.environ.get('CONFIG_PATH','config.yaml')) else 1)"

# Run BioMaster with biomaster-docker environment
# Use python3.11 directly to avoid symlink issues
ENTRYPOINT ["/opt/conda/envs/biomaster-docker/bin/python3.11", "/app/run.py"]
CMD ["config.yaml"]

