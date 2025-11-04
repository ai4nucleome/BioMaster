#!/bin/bash
# BioMaster Docker Run Script
# All paths (./data/, ./output/, config.yaml, etc.) are relative to current directory

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}BioMaster Docker Startup Script${NC}"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Get config file path (default: config.yaml)
CONFIG_FILE="${1:-config.yaml}"

# Get current working directory (directory where docker is called)
CURRENT_DIR=$(pwd)

echo -e "${BLUE}Current working directory: ${CURRENT_DIR}${NC}"
echo -e "${BLUE}Config file: ${CONFIG_FILE}${NC}"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}⚠️  Warning: Config file $CONFIG_FILE not found${NC}"
    echo "Will use default config file path (may be inside container)"
fi

# Create necessary directories if they don't exist
echo -e "${BLUE}Creating necessary directories...${NC}"
mkdir -p output data chroma_db graph_db hybrid_db doc

# Check if image exists
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

if ! docker image inspect biomaster-docker:latest &> /dev/null; then
    echo -e "${YELLOW}Image biomaster-docker:latest not found, building...${NC}"
    echo -e "${BLUE}This may take 15-20 minutes, please wait...${NC}"
    echo -e "${BLUE}Installing all required packages...${NC}"
    docker build -f "$SCRIPT_DIR/Dockerfile" -t biomaster-docker:latest "$PROJECT_ROOT"
    echo -e "${GREEN}✅ Image build completed!${NC}"
fi

# Create volumes if they don't exist
echo -e "${BLUE}Creating Docker volumes...${NC}"
docker volume create biomaster_conda_pkgs 2>/dev/null || true

# Clean up old container if exists
if docker ps -a --format '{{.Names}}' | grep -q "^biomaster-runner$"; then
    echo -e "${YELLOW}Cleaning up old container...${NC}"
    docker rm -f biomaster-runner 2>/dev/null || true
fi

# Run container
echo -e "${GREEN}Starting BioMaster container...${NC}"
echo -e "${BLUE}Mount directory mapping:${NC}"
echo -e "  - ${CURRENT_DIR} -> /work"
echo -e "  - ${CURRENT_DIR}/output -> /work/output"
echo -e "  - ${CURRENT_DIR}/data -> /work/data"
echo -e "  - ${CURRENT_DIR}/chroma_db -> /work/chroma_db"
echo ""

docker run --rm \
    --name biomaster-runner \
    -v "${CURRENT_DIR}":/work \
    -v "${CURRENT_DIR}/output":/work/output \
    -v "${CURRENT_DIR}/data":/work/data \
    -v "${CURRENT_DIR}/chroma_db":/work/chroma_db \
    -v "${CURRENT_DIR}/graph_db":/work/graph_db \
    -v "${CURRENT_DIR}/hybrid_db":/work/hybrid_db \
    -v "${CURRENT_DIR}/doc":/work/doc \
    -v biomaster_conda_pkgs:/opt/conda/pkgs \
    -e CONFIG_PATH="$CONFIG_FILE" \
    -e OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://host.docker.internal:11434}" \
    -e PATH="/opt/conda/envs/biomaster-docker/bin:/opt/conda/bin:${PATH}" \
    -e CONDA_DEFAULT_ENV=biomaster-docker \
    --add-host host.docker.internal:host-gateway \
    biomaster-docker:latest "$CONFIG_FILE"

echo ""
echo -e "${GREEN}✅ BioMaster execution completed!${NC}"
echo -e "${BLUE}📁 Output files saved to: ${CURRENT_DIR}/output${NC}"
echo -e "${BLUE}💾 Installed packages are cached in Docker volume for faster subsequent runs${NC}"

