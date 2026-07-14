<div align="center">
  <img src="./source/Biomaster.svg" width="96" height="96" alt="BioMaster logo" />

  <h1>BioMaster</h1>

  <p><strong>A knowledge-guided multi-agent system for automated bioinformatics workflow analysis</strong></p>

  <p>
    <a href="https://doi.org/10.1016/j.patter.2026.101611">
      <img src="https://img.shields.io/badge/Patterns-10.1016%2Fj.patter.2026.101611-blue.svg" alt="Patterns DOI" />
    </a>
    <a href="https://github.com/ai4nucleome/biomaster2/tree/2.0-alpha1">
      <img src="https://img.shields.io/badge/release-2.0--alpha1-informational.svg" alt="BioMaster 2.0-alpha1" />
    </a>
    <a href="#quick-start">
      <img src="https://img.shields.io/badge/interface-OpenCode-6f42c1.svg" alt="OpenCode interface" />
    </a>
  </p>
</div>

## Overview

BioMaster is a knowledge-guided multi-agent system that translates natural-language biological analysis goals into executable, monitored, and validated bioinformatics workflows. Dedicated Plan, Execute, Debug, and Check agents coordinate through a deterministic workflow, with role-isolated BioSkills and SQLite-backed retrieval.

This repository contains the OpenCode-integrated **2.0-alpha1 release branch**, including the BioMaster runtime, web interface, curated BioSkills library, automated validation, and GitHub Pages assets.

The peer-reviewed BioMaster article is published in *Patterns*: [BioMaster: Multi-agent system for automated bioinformatics analysis workflow](https://doi.org/10.1016/j.patter.2026.101611).

## At a Glance

| Area | Content |
| --- | --- |
| Paper | *Patterns* (2026), article 101611, DOI [`10.1016/j.patter.2026.101611`](https://doi.org/10.1016/j.patter.2026.101611) |
| User interface | Modified OpenCode frontend with BioMaster and BioSkills management pages |
| Agent runtime | Plan, Execute, Debug, and Check agents following a deterministic workflow skeleton |
| Knowledge layer | File-backed BioSkills library with SQLite cache generated from `.opencode/bioskills/` |
| Deployment assets | GitHub Pages-ready static site in `docs/` and curated figures in `source/` |
| Validation | BioSkills validation, SQLite sync, smoke tests, and pytest workflow coverage |

## Publication and Figures

- Published article: <https://doi.org/10.1016/j.patter.2026.101611>
- Preprint: <https://doi.org/10.1101/2025.01.23.634608>
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

- `BioMaster/` contains the renamed embedded BioMaster/OpenCode engine source, including the backend and web application.
- `.opencode/bioskills/` is the canonical BioSkills source.
- `.opencode/knowledge/biomaster_skills.db` is a generated cache and should not be committed.
- `docs/` contains the static public project site and can be selected directly as the GitHub Pages source.

## Repository Structure

```text
.
├── README.md
├── VERSION.md                    # release-candidate scope and validation checklist
├── CONTRIBUTING.md               # contributor and maintenance guidance
├── Makefile                      # validation, indexing, testing, and cleanup targets
├── requirements.txt              # Python runtime/test dependencies
├── pyproject.toml                # Python package and pytest configuration
├── install.sh                    # first-time installer and dependency setup
├── run.sh                        # daily launcher with host/port/password options
├── .github/workflows/            # lightweight repository CI
├── docs/                         # GitHub Pages-ready static public site
├── source/                       # publication and deployment assets
│   ├── Biomaster.svg             # project logo
│   ├── UI.png                    # UI asset
│   ├── README.md                 # asset inventory and maintenance notes
│   └── figures/                  # manuscript and website figures
├── BioMaster/                    # renamed embedded BioMaster/OpenCode engine
│   └── packages/
│       ├── opencode/             # backend API, including BioSkills routes
│       └── app/                  # web frontend and BioSkills Library UI
├── examples/                     # smoke tests and example requests
└── .opencode/                    # BioMaster OpenCode project configuration
    ├── agents/                   # plan, execute, debug, check, skiller, author, creator
    ├── commands/                 # biomaster-* command templates
    ├── bioskills/                # canonical file-backed BioSkills library
    ├── runtime/biomaster/        # Python runtime bridge and validation logic
    ├── tools/                    # BioSkills OpenCode tools
    └── knowledge/                # generated SQLite cache location
```

## Portability and Release Boundary

BioMaster is designed to run from any checkout path. The installer and launcher derive all repository paths from the location of `install.sh` and `run.sh`; do not hard-code `/home/...`, `/Users/...`, or server-specific paths in project files.

Tracked release assets:

- `.opencode/`: BioMaster agents, commands, skill, BioSkills library, runtime bridge, and plugin package manifest.
- `BioMaster/`: the modified OpenCode backend/frontend source.
- `docs/` and `source/`: public site and manuscript-facing assets.
- `examples/`: lightweight smoke tests and usage fixtures.

Untracked/generated assets:

- `BioMaster/node_modules/` and `.opencode/node_modules/`
- `.logs/`
- `projects/` and `runs/`
- `.opencode/knowledge/biomaster_skills.db`
- `.opencode/bioskills/.index.db`
- local `data/` with large/private biological inputs

## Quick Start

### Requirements

- Linux or macOS
- Git and `curl`
- Python 3.10+
- Node.js 22+ and Bun 1.x (the installer can provision compatible versions)
- Bioinformatics tools and reference data required by the analysis you request

The commands below install the `2.0-alpha1` branch:

```bash
git clone --branch 2.0-alpha1 https://github.com/ai4nucleome/biomaster2.git BioMaster
cd BioMaster
./install.sh
```

If the repository is already cloned:

```bash
git fetch origin
git checkout 2.0-alpha1
git pull --ff-only origin 2.0-alpha1
./install.sh
```

### 1. Install and configure BioMaster

`install.sh` installs or selects Bun and Node.js 22, installs Python and OpenCode dependencies, builds the Web UI, and validates the BioSkills index. Re-running it is safe when updating the checkout.

```bash
./install.sh
```

If dependency downloads are slow or the server has restricted npm access, use a closer registry and lower Bun's network concurrency:

```bash
BUN_REGISTRY=https://registry.npmmirror.com BUN_NETWORK_CONCURRENCY=12 ./install.sh
```

If the server uses a custom HTTPS certificate chain, prefer the system CA store or provide a CA bundle:

```bash
NODE_USE_SYSTEM_CA=1 ./install.sh
BUN_CAFILE=/path/to/your-ca-bundle.pem ./install.sh
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

### 3. Run your first workflow

1. Open `http://127.0.0.1:4096`.
2. Select the cloned repository root as the project.
3. Start with one of:

   ```text
   /biomaster-start
   /biomaster-start Analyze tumor heterogeneity in my scRNA-seq dataset
   /biomaster Analyze tumor heterogeneity in my scRNA-seq dataset
   ```

4. Choose **Test mode**, **Formal analysis**, or **Custom objective** when prompted.
5. For formal analysis, provide the objective first, then the input paths, sample metadata, groups, and required phenotype or clinical tables.
6. Review the generated `projects/<project_slug>/PLAN.yaml`.
7. Approve execution and run `/biomaster-run`. BioMaster executes one step at a time through Execute → Debug → Check.
8. Use `/biomaster-resume` to continue an existing project, `/biomaster-check` to re-check outputs, or `/biomaster-debug` after a failed step.

Outputs are written under `projects/<project_slug>/`:

```text
PLAN.yaml           structured analysis plan
PROJECT_LOG.yaml    audited step history and evidence
CHECK_REPORT.yaml   per-step verification results
REPORT.md           final human-readable report
OPENCODE_VIEW.md    compact project view for the UI
scripts/            generated step scripts
steps/              execution logs and step results
artifacts/          analysis artifacts
```

BioMaster will not enter reporting while a required check is failing or incomplete. Generated commands and biological conclusions should still be reviewed by a qualified analyst before clinical or production use.

### 4. Available commands

When the BioMaster project root is selected, OpenCode automatically loads:

- the public skill `/biomaster` from `.opencode/skills/biomaster/SKILL.md`;
- workflow commands such as `/biomaster-start`, `/biomaster-run`, `/biomaster-plan`, `/biomaster-check`, `/biomaster-debug`, and `/biomaster-resume` from `.opencode/commands/`.

| Command | Purpose |
| --- | --- |
| `/biomaster <goal>` | Load BioMaster and describe an analysis goal conversationally |
| `/biomaster-start [goal]` | Start mode selection and create or select a project |
| `/biomaster-plan <goal>` | Build a SQLite-grounded `PLAN.yaml` after routing |
| `/biomaster-run` | Execute the next eligible plan step |
| `/biomaster-check` | Verify step outputs and refresh reports |
| `/biomaster-debug` | Diagnose a failed step and prepare a bounded retry |
| `/biomaster-resume` | Continue or review an existing project |

These commands are project-local controls and appear only when the repository root is selected.

### 5. Start BioMaster on a remote server

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

BioMaster uses a **single server port** by default. The Web UI and API are served by the same OpenCode process.

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

### 6. Verify the running service

To verify that the running services come from this repository and not from another user's stale process:

```bash
./run.sh status --host 0.0.0.0 --port 18080
ss -ltnp | grep ':18080'
ps -fp "$(pgrep -f "BioMaster/packages/opencode/src/index.ts serve .*--port 18080" | head -1)"
```

The server command should point to this checkout's `BioMaster/packages/opencode/src/index.ts`.

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

### 7. Use an SSH tunnel when ports are blocked

On HPC or institutional servers, external ports may be blocked even when `./run.sh status` reports `http=200`. In that case, keep the service bound to localhost and forward only the BioMaster server port from your local machine:

```bash
# Server
./run.sh local

# Local machine
ssh -L 4096:127.0.0.1:4096 <user>@<server-ip>
```

Then open `http://127.0.0.1:4096` locally.

### 8. Logs and process control

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
- **`BioMaster/` engine directory is missing after cloning**: confirm that the selected release branch was checked out and pulled successfully.
- **`npm install -g node-gyp` or npm registry access times out**: update to the latest `install.sh` and rerun. The installer now prefers the `node-gyp` bundled with Node/npm and only contacts npm as a fallback. If a fallback install is still needed on a restricted network, use a reachable registry, for example `NPM_CONFIG_REGISTRY=https://registry.npmmirror.com ./install.sh`.
- **`bun install` is very slow**: run `BUN_REGISTRY=https://registry.npmmirror.com BUN_NETWORK_CONCURRENCY=12 ./install.sh`. The installer passes the registry to `bun install` and uses `--frozen-lockfile` when `bun.lock` is present.
- **`bun install` fails with `ERR_TLS_CERT_ALTNAME_INVALID`**: the registry certificate does not match the hostname seen by this server. First try `NODE_USE_SYSTEM_CA=1 BUN_REGISTRY=https://registry.npmjs.org ./install.sh` or `NODE_USE_SYSTEM_CA=1 BUN_REGISTRY=https://registry.npmmirror.com ./install.sh`. If your institution provides a CA bundle, use `BUN_CAFILE=/path/to/ca-bundle.pem ./install.sh`. If the cluster rewrites HTTPS certificates incorrectly and no CA bundle is available, use `BUN_REGISTRY=http://registry.npmmirror.com ./install.sh` only inside a trusted network.
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

- **GitHub Pages**: set the Pages source to the selected release branch and `/docs` folder.
- **Nginx/Apache**: copy the contents of `docs/` to the web root.
- **Vercel/Netlify**: deploy `docs/` as a static site.

## Using BioMaster

### BioMaster loading model

BioMaster is loaded as **project-level OpenCode configuration**, not as a global OpenCode plugin. The repository root is the BioMaster project root, and the runtime, agents, commands, and curated skills live under:

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

### Agent and Skill isolation

The Plan Agent remains the visible conversation owner. Worker agents are invoked for individual workflow stages, and Skill bodies are isolated by role:

| Skill class | Authorized agents |
| --- | --- |
| Workflow / `plan-*` | `biomaster-plan` only |
| Execution / `exec-*` | `biomaster-execute`, `biomaster-debug`, `biomaster-check` |
| Skill-management catalog | `biomaster-skiller`, `biomaster-skill-author`, `biomaster-skill-creator` receive metadata only |

Unknown agents are denied by default. Agent identity, phase, SQLite `allowed_agents`, and the Skill-level `enabled` state are checked before Skill content is inserted into a prompt.

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

The SQLite database under `.opencode/knowledge/` is a generated cache. If it is missing or stale, it is rebuilt from the file-backed library. Turning a Skill off in the BioSkills page immediately marks it unavailable to Agent and SQLite retrieval while keeping the disabled card visible. Click the same toggle to activate it again.

### Adding or updating skills

Use the BioSkills page for interactive creation and editing, or use the scaffold command:

```bash
make skill-add ARGS='my-tool --target execute --description "Run my analysis tool" --metadata-value my-tool'
make knowledge-seed
```

Internal BioSkills belong under:

```text
.opencode/bioskills/<skill-name>/
```

Do not add internal workflow or execution knowledge under `.opencode/skills/`; that directory intentionally exposes only the public `/biomaster` entry point. New `plan-*` Skills are restricted to Plan, while new `exec-*` Skills are restricted to Execute, Debug, and Check.

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
- runtime smoke tests, knowledge-control tests, and compliance checks

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

Keep figure claims consistent with the published article and verified benchmark records. Prefer PNG/SVG for website deployment and preserve PDF/SVG originals when available.

## Version Notes

The `2.0-alpha1` branch is the OpenCode-integrated alpha release accompanying the published project:

- uses a flattened single-root BioMaster project structure with `BioMaster/` retained as the embedded engine;
- adds the GitHub Pages-ready static site and manuscript-facing assets;
- enforces the Plan → Execute → Debug → Check workflow with runtime gates;
- isolates workflow and execution Skill bodies by Agent role;
- synchronizes Skill activation state across the UI, file library, and SQLite cache;
- organizes source assets for paper, documentation, and website reuse.

## Citation

Please cite the BioMaster manuscript when using this system:

```bibtex
@article{su2026biomaster,
  title     = {BioMaster: Multi-agent system for automated bioinformatics analysis workflow},
  author    = {Su, Houcheng and Feng, Junning and Lu, Yawen and Xu, Yucheng and Yang, Jinming and Lu, Haojie and Yang, Jixin and Yang, Xu and Xie, Sirui and Long, Weicai and Wang, Chengrui and Hou, Yusen and Zhu, Tingyu and Zhang, Yanlin},
  journal   = {Patterns},
  year      = {2026},
  pages     = {101611},
  publisher = {Elsevier},
  doi       = {10.1016/j.patter.2026.101611}
}
```

GitHub also exposes this metadata through [`CITATION.cff`](CITATION.cff).

## Maintainer Checklist

- Keep `docs/` and `source/` separate from runtime-generated workflow outputs.
- Keep BioSkills source files in `.opencode/bioskills/`.
- Do not commit generated SQLite databases, BioSkills FTS indexes, dependency folders, or project run outputs.
- Keep only lightweight example fixtures in `examples/`; do not commit large `.h5ad` or private biological datasets.
- Review large biological data files before public release or migration to Git LFS.
- Re-run `make test` after modifying runtime code, agents, BioSkills schemas, or OpenCode BioSkills routes.
