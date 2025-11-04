#!/bin/bash
# BioMaster Docker Interactive Script
# Enter container for debugging or manual operations

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}BioMaster Docker Interactive Container${NC}"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Get current working directory
CURRENT_DIR=$(pwd)

echo -e "${BLUE}Current working directory: ${CURRENT_DIR}${NC}"

# Check if image exists
if ! docker image inspect biomaster-docker:latest &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: Image biomaster-docker:latest not found${NC}"
    echo "Please run ./docker-run.sh first to build the image"
    exit 1
fi

# Create volumes if they don't exist
docker volume create biomaster_conda_pkgs 2>/dev/null || true

# Run interactive container
echo -e "${GREEN}Starting interactive container...${NC}"
echo -e "${BLUE}Tip: All paths inside container are relative to /work directory${NC}"
echo -e "${BLUE}Use 'exit' to leave the container${NC}"
echo ""

docker run --rm -it \
    --name biomaster-interactive \
    -v "${CURRENT_DIR}":/work \
    -v "${CURRENT_DIR}/output":/work/output \
    -v "${CURRENT_DIR}/data":/work/data \
    -v "${CURRENT_DIR}/chroma_db":/work/chroma_db \
    -v "${CURRENT_DIR}/graph_db":/work/graph_db \
    -v "${CURRENT_DIR}/hybrid_db":/work/hybrid_db \
    -v "${CURRENT_DIR}/doc":/work/doc \
    -v biomaster_conda_pkgs:/opt/conda/pkgs \
    -e PATH="/opt/conda/envs/biomaster-docker/bin:/opt/conda/bin:${PATH}" \
    -e CONDA_DEFAULT_ENV=biomaster-docker \
    --entrypoint /bin/bash \
    biomaster-docker:latest \
    -c "source /opt/conda/etc/profile.d/conda.sh && conda activate biomaster-docker && cd /work && exec bash"

