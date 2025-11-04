# BioMaster Docker Guide

> ⚠️ **Experimental Feature**: Docker support has only been tested in limited scenarios and has not undergone extensive testing across different environments and use cases. Please report any issues you encounter.

## 📦 Docker File Structure

```
docker/
├── Dockerfile               # Main Dockerfile
├── biomaster-docker.yml     # Conda environment specification
├── docker-compose.yml       # Docker Compose configuration
├── docker-run.sh           # Convenience script to run BioMaster
├── docker-interactive.sh   # Interactive debugging script
└── install_env.sh          # Fallback environment installation script
```

## 🚀 Quick Start

### 1. Build the Image

```bash
# Run from project root directory
cd /path/to/BioMaster

# Using the script (recommended)
./docker/docker-run.sh

# Or manual build
docker build -f docker/Dockerfile -t biomaster-docker:latest .
```

**Note**: First-time build takes 15-30 minutes depending on your network speed and hardware.

### 2. Run the Container

```bash
# Run BioMaster (config file: config.yaml)
./docker/docker-run.sh config.yaml

# Using docker-compose
cd docker
docker-compose up
```

### 3. Interactive Mode

```bash
# Enter container for debugging
./docker/docker-interactive.sh

# Inside the container:
cd /work
python /app/run.py config.yaml
exit
```

## 📝 Environment Details

- **Image Name**: `biomaster-docker:latest`
- **Container Name**: `biomaster-runner`
- **Environment Name**: `biomaster-docker`
- **Python Version**: 3.11.14
- **Working Directory**: `/work` (mapped to host current directory)

## 🔧 Customization

### Modifying Conda Environment

Edit `docker/biomaster-docker.yml` file, then rebuild the image:

```bash
docker build -f docker/Dockerfile -t biomaster-docker:latest .
```

### Modifying Docker Configuration

Edit `docker/docker-compose.yml` or `docker/Dockerfile` as needed.

## 📂 Path Mapping

All paths in Docker are relative to your current directory:

```
Host Machine                  Container
├── config.yaml      ──────→  /work/config.yaml
├── data/            ──────→  /work/data/
│   └── file.h5ad              └── file.h5ad
└── output/          ──────→  /work/output/
    └── results/                └── results/
```

## 🐳 Common Docker Commands

```bash
# Check images
docker images | grep biomaster

# List running containers
docker ps

# View container logs
docker logs biomaster-runner

# Stop container
docker stop biomaster-runner

# Remove container
docker rm biomaster-runner

# Remove image
docker rmi biomaster-docker:latest

# Clean up all unused Docker resources
docker system prune -a
```

## 🔍 Troubleshooting

### Build fails during conda environment creation

The Dockerfile uses a multi-level fallback strategy:
1. First tries `mamba env create` (fastest)
2. Falls back to `conda env create --solver=libmamba`
3. Finally falls back to `install_env.sh` (manual package installation)

If all methods fail, check:
- Internet connection
- Available disk space (needs at least 20GB)
- Docker daemon resources (memory/CPU)

### Container cannot access host services

If you need to access services on the host machine (e.g., Ollama):
- Use `host.docker.internal` instead of `localhost` in your config
- Example: `http://host.docker.internal:11434`

### Permission issues with mounted volumes

The container runs as user `biouser`. If you encounter permission issues:
```bash
# On host machine
chmod -R 755 data/ output/
```

## 📚 More Information

For detailed usage instructions, see the main `README.md` in the project root directory.

## 📧 Support

If you encounter any issues with Docker deployment, please:
1. Check this documentation first
2. Review container logs: `docker logs biomaster-runner`
3. Open an issue on GitHub with detailed error messages

---

**Note**: This Docker implementation is experimental and actively being improved. Feedback and contributions are welcome!
