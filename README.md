<div align="center">
  <img src="./source/Biomaster.svg" width="96" height="96" alt="BioMaster logo" />

  <h1>BioMaster</h1>

  <p><strong>A knowledge-guided multi-agent system for automated bioinformatics workflow analysis</strong></p>

  <p>
    <a href="https://www.biorxiv.org/content/10.1101/2025.01.23.634608v1.abstract">
      <img src="https://img.shields.io/badge/bioRxiv-10.1101%2F2025.01.23.634608-brightgreen.svg" alt="bioRxiv DOI" />
    </a>
    <a href="#citation">
      <img src="https://img.shields.io/badge/Patterns-accepted-blue.svg" alt="Patterns accepted" />
    </a>
    <a href="#quick-start">
      <img src="https://img.shields.io/badge/version-v0.5-informational.svg" alt="BioMaster v0.5" />
    </a>
  </p>
</div>

## Overview

BioMaster is a multi-agent framework designed to translate natural-language biological analysis goals into executable, monitored, and validated bioinformatics workflows. It separates workflow design, command generation, runtime debugging, and output verification into distinct agent roles, and grounds these roles in curated workflow-level and tool-level knowledge.

This repository is the **v0.5 deployment-oriented release**. It is based on the v0.4 OpenCode-integrated implementation and adds a GitHub Pages-ready static site under `docs/` plus an organized `source/` directory for publication, website, and deployment assets.

The BioMaster manuscript, **"BioMaster: Multi-agent System for Automated Bioinformatics Analysis Workflow"**, has been accepted by *Patterns*. A preprint is available on bioRxiv.

## v0.5 at a Glance

| Area | v0.5 content |
| --- | --- |
| Paper context | README, citation, documentation pages, and manuscript figures aligned with the accepted *Patterns* manuscript |
| User interface | Modified OpenCode frontend with BioMaster and BioSkills management pages |
| Agent runtime | Plan, Execute, Debug, and Check agents following the deterministic v0.2 workflow skeleton |
| Knowledge layer | File-backed BioSkills library with SQLite cache generated from `.opencode/bioskills/` |
| Deployment assets | GitHub Pages-ready static site in `docs/` and curated figures in `source/` |
| Validation | BioSkills validation, SQLite sync, smoke tests, and pytest workflow coverage |

## Manuscript and Figures

- Preprint: <https://www.biorxiv.org/content/10.1101/2025.01.23.634608v1.abstract>
- Static website: `docs/index.html`
- Figure and deployment assets: `source/`
- Static site figures: `source/figures/`

The manuscript reports an evaluation over 49 bioinformatics tasks spanning 102 bioinformatics tools. Under the reported benchmark setting, BioMaster completed 47 of 49 tasks end to end, corresponding to a 95.9% workflow execution success rate. These results describe benchmarked workflow execution behavior and should not be interpreted as replacing expert biological review or interpretation.

## System Design

BioMaster uses a stepwise multi-agent workflow:

1. **Plan Agent**: converts a biological objective into a structured analysis plan with steps, expected inputs, expected outputs, and candidate tools.
2. **Execute Agent**: generates and runs tool-specific scripts for one approved step at a time.
3. **Debug Agent**: inspects execution failures and proposes bounded retry actions.
4. **Check Agent**: verifies required outputs and prevents downstream execution until the current step passes validation.

The current deployment keeps this agent skeleton stable while using the newer BioSkills and SQLite control layer:

- `opencode/` contains the modified OpenCode backend and web application.
- `.opencode/bioskills/` is the canonical BioSkills source.
- `.opencode/knowledge/biomaster_skills.db` is a generated cache and should not be committed.
- `docs/` contains the static public project site and can be selected directly as the GitHub Pages source.

## Repository Structure

```text
.
├── README.md
├── install.sh                    # first-time installer and dependency setup
├── run.sh                        # daily launcher with host/port/password options
├── docs/                         # GitHub Pages-ready static public site
├── source/                       # publication and deployment assets
│   ├── Biomaster.svg             # project logo
│   ├── UI.png                    # UI asset
│   ├── README.md                 # asset inventory and maintenance notes
│   └── figures/                  # manuscript and website figures
├── opencode/                     # modified OpenCode fork
│   └── packages/
│       ├── opencode/             # backend API, including BioSkills routes
│       └── app/                  # web frontend and BioSkills Library UI
├── examples/                     # smoke tests and example requests
├── tests/                        # pytest coverage
└── .opencode/                    # BioMaster OpenCode project configuration
    ├── agents/                   # plan, execute, debug, check, skiller, author, creator
    ├── commands/                 # biomaster-* command templates
    ├── bioskills/                # canonical file-backed BioSkills library
    ├── runtime/biomaster/        # Python runtime bridge and validation logic
    ├── tools/                    # BioSkills OpenCode tools
    └── knowledge/                # generated SQLite cache location
```

## Portability and Release Boundary

BioMaster v0.5 is designed to run from any checkout path. The installer and launcher derive all repository paths from the location of `install.sh` and `run.sh`; do not hard-code `/home/...`, `/Users/...`, or server-specific paths in project files.

Tracked release assets:

- `.opencode/`: BioMaster agents, commands, skill, BioSkills library, runtime bridge, and plugin package manifest.
- `opencode/`: the modified OpenCode backend/frontend source.
- `docs/` and `source/`: public site and manuscript-facing assets.
- `examples/` and `tests/`: lightweight fixtures and release validation.

Untracked/generated assets:

- `opencode/node_modules/` and `.opencode/node_modules/`
- `.logs/`
- `projects/` and `runs/`
- `.opencode/knowledge/biomaster_skills.db`
- `.opencode/bioskills/.index.db`
- local `data/` with large/private biological inputs

## Quick Start

The commands below assume that you are running them from the repository root after cloning the `v0.5` branch.

```bash
git clone -b v0.5 git@github.com:ai4nucleome/biomaster2.git BioMaster-v0.5
cd BioMaster-v0.5
```

If the repository has already been cloned, switch to the release branch first:

```bash
git fetch origin
git checkout v0.5
git pull --ff-only origin v0.5
```

### 1. Install and configure BioMaster

Use `install.sh` for the first deployment on a new machine. It installs or selects Bun, Node.js 22, a modern `node-gyp`, Python dependencies, OpenCode dependencies, BioMaster plugin dependencies, builds the BioMaster Web UI, and then validates the BioSkills index.

```bash
./install.sh
```

If dependency downloads are slow or the server has restricted npm access, use a closer registry and lower Bun's network concurrency:

```bash
BUN_REGISTRY=https://registry.npmmirror.com BUN_NETWORK_CONCURRENCY=12 ./install.sh
```

For a completely fresh dependency rebuild:

```bash
./install.sh --clean
```

Expected successful checks include:

```text
node v22.x
bun 1.x
Validated 185 BioSkills
```

### 2. Run BioMaster

```bash
./run.sh local
./run.sh status
```

Open:

```text
http://127.0.0.1:4096
```

`./run.sh` starts one OpenCode server process. The same port serves the Web UI, API, SSE, WebSocket, and BioSkills routes, so there is no separate frontend/backend deployment to manage.

### 3. What appears in OpenCode

When the BioMaster project root is selected, OpenCode automatically loads:

- the public skill `/biomaster` from `.opencode/skills/biomaster/SKILL.md`;
- workflow commands such as `/biomaster-start`, `/biomaster-run`, `/biomaster-plan`, `/biomaster-check`, `/biomaster-debug`, and `/biomaster-resume` from `.opencode/commands/`.

These entries are expected on every correctly deployed device. They are project-local BioMaster controls, not browser cache artifacts.

### 4. Start BioMaster on a remote server

For direct remote access, bind the web entrypoint to all interfaces and set a password. Do not reuse the example password below; generate a deployment-specific value:

```bash
export OPENCODE_SERVER_PASSWORD="$(openssl rand -base64 24)"
./run.sh remote --password "$OPENCODE_SERVER_PASSWORD"
./run.sh status --host 0.0.0.0
```

Generate the browser token on the server:

```bash
python3 - <<'PY'
import base64, os
password = os.environ["OPENCODE_SERVER_PASSWORD"]
print(base64.urlsafe_b64encode(f"opencode:{password}".encode()).decode().rstrip("="))
PY
```

Open BioMaster with the actual server IP address:

```text
http://<server-ip>:4096/?auth_token=<generated-token>
```

For safety, `run.sh` refuses `--host 0.0.0.0` unless a password is provided. For trusted isolated networks only, override this with `--unsafe`.

BioMaster v0.5 uses a **single server port** by default. The Web UI and API are served by the same OpenCode process.

To use a custom public port:

```bash
./run.sh stop --port 18080
./run.sh restart --host 0.0.0.0 --port 18080 --password "$OPENCODE_SERVER_PASSWORD"
```

Then open:

```text
http://<server-ip>:18080/?auth_token=<generated-token>
```

Use the same port in the browser. In the example above, `18080` serves both the Web UI and the OpenCode API.

### 5. Verify the running service

To verify that the running services come from this repository and not from another user's stale process:

```bash
./run.sh status --host 0.0.0.0 --port 18080
ss -ltnp | grep ':18080'
ps -fp "$(pgrep -f "opencode/packages/opencode/src/index.ts serve .*--port 18080" | head -1)"
```

The server command should point to this checkout's `opencode/packages/opencode/src/index.ts`.

To test the single server port:

```bash
curl http://127.0.0.1:18080/global/health
```

The expected response is similar to:

```json
{"healthy":true,"version":"local"}
```

BioMaster-specific checks through the same browser-facing port:

```bash
curl http://127.0.0.1:18080/command
curl "http://127.0.0.1:18080/bioskills?directory=$(pwd)"
```

The command endpoint should include `biomaster-start`, `biomaster-run`, and `biomaster-check`. The BioSkills endpoint should return the curated skills stored under `.opencode/bioskills/`.

### 6. Use an SSH tunnel when ports are blocked

On HPC or institutional servers, external ports may be blocked even when `./run.sh status` reports `http=200`. In that case, keep the service bound to localhost and forward only the BioMaster server port from your local machine:

```bash
# Server
./run.sh local

# Local machine
ssh -L 4096:127.0.0.1:4096 <user>@<server-ip>
```

Then open `http://127.0.0.1:4096` locally.

### 7. Logs and process control

Logs are written under `.logs/` by default and include the current username in the filename. This avoids permission conflicts on shared systems where temporary log files may belong to another user. Override the path only when needed:

```bash
SERVER_LOG=logs/server.log ./run.sh local
```

Useful launcher commands:

```bash
./run.sh local                         # start locally on 127.0.0.1:4096
./run.sh remote --password '<secret>'  # start remotely on 0.0.0.0:4096
./run.sh restart --port 18080          # restart with a custom server port
./run.sh stop                          # stop BioMaster
./run.sh status                        # show process IDs and HTTP status
./run.sh logs                          # show recent server logs
```

Common launcher options:

```bash
./run.sh local --port 18080
./run.sh remote --port 18080 --password '<secret>'
./run.sh restart --host 0.0.0.0 --port 18080 --password '<secret>'
```

### Deployment Troubleshooting

- **First deployment**: run `./install.sh` from the repository root. Use `./install.sh --clean` when moving between machines or after dependency corruption.
- **`cd opencode` fails after cloning**: confirm that the `v0.5` branch is checked out with `git checkout v0.5`.
- **`npm install -g node-gyp` or npm registry access times out**: update to the latest `install.sh` and rerun. The installer now prefers the `node-gyp` bundled with Node/npm and only contacts npm as a fallback. If a fallback install is still needed on a restricted network, use a reachable registry, for example `NPM_CONFIG_REGISTRY=https://registry.npmmirror.com ./install.sh`.
- **`bun install` is very slow**: run `BUN_REGISTRY=https://registry.npmmirror.com BUN_NETWORK_CONCURRENCY=12 ./install.sh`. The installer passes the registry to `bun install` and uses `--frozen-lockfile` when `bun.lock` is present.
- **`bun install` fails with `std::string_view` or old `node-gyp` errors**: run `./install.sh --clean`; the installer selects Node.js 22 and exports a modern `node-gyp`.
- **`.opencode` dependency install fails**: confirm `.opencode/package.json` exists, then run `./install.sh --clean`.
- **Browser shows a red disconnected indicator**: hard refresh the page, then confirm `./run.sh status` reports `server http=200` and `curl http://127.0.0.1:4096/global/health` returns healthy JSON.
- **Remote browser cannot open the page**: confirm that the firewall or cluster gateway allows the BioMaster server port, or use the SSH tunnel workflow above.
- **Health returns `401` when a password is set**: this indicates authentication is active. Use the BioMaster URL with the `auth_token` query parameter.
- **BioMaster commands are missing**: make sure the selected project directory is the repository root and that `.opencode/commands/` exists in that root.

## Static Site Deployment

The `docs/` directory is plain HTML, CSS, JavaScript, and static assets. It does not require a build step and is named to match GitHub Pages' `/docs` publishing option.

Preview locally:

```bash
cd docs
python3 -m http.server 8080
```

Then open:

```text
http://127.0.0.1:8080
```

Deployment options:

- **GitHub Pages**: set the Pages source to the `v0.5` branch and `/docs` folder.
- **Nginx/Apache**: copy the contents of `docs/` to the web root.
- **Vercel/Netlify**: deploy `docs/` as a static site.

## Using BioMaster

### BioMaster loading model

BioMaster is loaded as **project-level OpenCode configuration**, not as a global OpenCode plugin. In v0.5, the repository root is the BioMaster project root, and the runtime, agents, commands, and curated skills live under:

```text
.opencode/
```

Important subdirectories include:

- `.opencode/skills/`: OpenCode skills, including the primary `biomaster` skill.
- `.opencode/commands/`: slash commands such as `/biomaster-start`, `/biomaster-run`, and `/biomaster-check`.
- `.opencode/agents/`: BioMaster Plan, Execute, Debug, Check, and skill-management agents.
- `.opencode/bioskills/`: the canonical BioSkills knowledge library.

Because the configuration is project-local, BioMaster will not automatically load when running a globally installed OpenCode binary outside this checkout. Always start this repository's modified OpenCode runtime with:

```bash
./run.sh local
```

Do not use a globally installed command for BioMaster sessions:

```bash
opencode
npx opencode
```

When the UI asks for a project directory, open:

```text
<repository-root>
```

The repository root now contains `.opencode/`, so BioMaster commands and skills are available without selecting a nested project directory.

### BioMaster workflow interface

1. Start OpenCode with `./run.sh local`.
2. Open BioMaster at `http://127.0.0.1:4096` or `http://<server-ip>:4096`.
3. Select the BioMaster project directory when prompted:

   ```text
   <repository-root>
   ```

4. Use the BioMaster commands and agents through OpenCode:
   - `biomaster-plan` remains the primary workflow agent.
   - `biomaster-execute`, `biomaster-debug`, and `biomaster-check` handle step execution, error recovery, and output validation.
   - `biomaster-skiller`, `biomaster-skill-author`, and `biomaster-skill-creator` are available for BioSkills management but are not part of the normal execution loop.

### BioSkills Library

The BioSkills Library stores structured knowledge as files under:

```text
.opencode/bioskills/
```

Each curated skill contains:

- `SKILL.md`: metadata and compatibility information
- `macro.md`: high-level workflow or conceptual description
- `micro.md`: execution-level notes, commands, or tool guidance
- `steps.json`: structured step metadata

The SQLite database under `.opencode/knowledge/` is a generated cache. If it is missing, it is rebuilt by the runtime sync scripts and tests.

### Adding or updating skills

OpenCode skills are loaded from the current project configuration. If a new skill is created under `.opencode/skills/`, restart OpenCode or reopen the BioMaster project before expecting the skill to auto-trigger:

```bash
./run.sh local
```

For example, a skill created at:

```text
.opencode/skills/tcga_luad_deg_enrichment/SKILL.md
```

will be available in sessions whose project directory is `<repository-root>`.

### Troubleshooting BioMaster loading

If BioMaster appears missing in a new session, check the following before debugging the model prompt:

- The service was started with `./run.sh`, not a global `opencode` or `npx opencode` command.
- The selected project is `<repository-root>`.
- The browser is connected to the same `./run.sh` server process.
- `/global/health` on the BioMaster server port returns a healthy response.
- After adding new `.opencode/skills/*/SKILL.md` files, OpenCode was restarted or the project was reopened.

Open the same BioMaster server port in the browser and include `auth_token` when `OPENCODE_SERVER_PASSWORD` is set.

## Validation

Run the full validation suite before release or deployment:

```bash
make test
```

The test suite checks:

- BioSkills file validation
- SQLite synchronization from BioSkills
- smoke tests for BioMaster runtime behavior
- knowledge-control tests for the SQLite cache
- pytest coverage for agent prompts, workflow gates, runtime bridge behavior, and project context

Generated files should remain untracked:

- `node_modules/`
- `.opencode/knowledge/biomaster_skills.db`
- `.opencode/bioskills/.index.db`
- `projects/<slug>/`
- `runs/<run_id>/`
- Python caches such as `__pycache__/` and `.pytest_cache/`

`projects/` and `runs/` are runtime-created output directories. They are intentionally absent from a clean release checkout and are created on demand when BioMaster executes a workflow.

Large local datasets are not shipped in the release repository. Keep reproducible, lightweight fixtures under `examples/data/` or `examples/real_data/`; place private or large analysis inputs outside the repository or under an ignored local `data/` directory.

## Source Assets

`source/` stores materials used by the README, paper, and static site.

| Path | Purpose |
| --- | --- |
| `source/Biomaster.svg` | project logo |
| `source/UI.png` | interface or documentation asset |
| `source/figures/overview.png` | system overview figure |
| `source/figures/task-coverage.png` | benchmark task coverage figure |
| `source/figures/multistep-success.png` | multi-step workflow execution figure |
| `source/figures/reliability.png` | representative reliability/case-study figure |
| `source/figures/open-source-llms.png` | open-source LLM benchmark figure |
| `source/figures/manuscript-fig1.pdf` | manuscript figure source |
| `source/figures/reliability.svg` | vector reliability figure |
| `source/figures/open-source-llms.svg` | vector open-source LLM figure |

Keep figure claims consistent with the accepted manuscript and verified benchmark records. Prefer PNG/SVG for website deployment and preserve PDF/SVG originals when available.

## Version Notes

v0.5 is intended as a deployment and presentation version:

- uses a flattened single-root BioMaster project structure with `opencode/` retained as the embedded engine;
- adds the GitHub Pages-ready static site and manuscript-facing assets;
- keeps the v0.2-style Plan -> Execute -> Debug -> Check workflow discipline;
- organizes source assets for paper, documentation, and website reuse.

## Citation

Please cite the BioMaster manuscript when using this system:

```bibtex
@article{su2025biomaster,
  title   = {BioMaster: Multi-agent System for Automated Bioinformatics Analysis Workflow},
  author  = {Su, Houcheng and Feng, Junning and Lu, Yawen and Xu, Yucheng and Yang, Jinming and Lu, Haojie and Yang, Jixin and Yang, Xu and Xie, Sirui and Long, Weicai and Wang, Chengrui and Hou, Yusen and Zhu, Tingyu and Zhang, Yanlin},
  journal = {bioRxiv},
  year    = {2025},
  doi     = {10.1101/2025.01.23.634608}
}
```

The citation entry will be updated when the final *Patterns* publication metadata is available.

## Maintainer Checklist

- Keep `docs/` and `source/` separate from runtime-generated workflow outputs.
- Keep BioSkills source files in `.opencode/bioskills/`.
- Do not commit generated SQLite databases, BioSkills FTS indexes, dependency folders, or project run outputs.
- Keep only lightweight example fixtures in `examples/`; do not commit large `.h5ad` or private biological datasets.
- Review large biological data files before public release or migration to Git LFS.
- Re-run `make test` after modifying runtime code, agents, BioSkills schemas, or OpenCode BioSkills routes.
