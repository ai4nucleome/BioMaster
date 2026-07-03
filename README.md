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
| Deployment assets | GitHub Pages-ready static site in `docs/`, cleaned archive `docs.tar.gz`, and curated figures in `source/` |
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

- `biomaster2-main/.opencode/bioskills/` is the canonical BioSkills source.
- `biomaster2-main/.opencode/knowledge/biomaster_skills.db` is a generated cache and should not be committed.
- `opencode/` contains the modified OpenCode backend and web application.
- `docs/` contains the static public project site and can be selected directly as the GitHub Pages source.

## Repository Structure

```text
.
├── README.md
├── oc.sh                         # OpenCode backend/frontend launcher
├── docs/                         # GitHub Pages-ready static public site
├── docs.tar.gz                   # cleaned static site deployment archive
├── source/                       # publication and deployment assets
│   ├── Biomaster.svg             # project logo
│   ├── UI.png                    # UI asset
│   ├── README.md                 # asset inventory and maintenance notes
│   └── figures/                  # manuscript and website figures
├── opencode/                     # modified OpenCode fork
│   └── packages/
│       ├── opencode/             # backend API, including BioSkills routes
│       └── app/                  # web frontend and BioSkills Library UI
└── biomaster2-main/              # BioMaster OpenCode project
    ├── data/                     # demo datasets for test-mode workflows
    ├── examples/                 # smoke tests and example requests
    ├── tests/                    # pytest coverage
    └── .opencode/
        ├── agents/               # plan, execute, debug, check, skiller, author, creator
        ├── commands/             # biomaster-* command templates
        ├── bioskills/            # canonical file-backed BioSkills library
        ├── runtime/biomaster/    # Python runtime bridge and validation logic
        ├── tools/                # BioSkills OpenCode tools
        └── knowledge/            # generated SQLite cache location
```

## Quick Start

### 1. Install dependencies

```bash
cd /home/agent/BioMaster/biomaster-skill-v0.5

cd opencode
bun install
cd ..

cd biomaster2-main/.opencode
bun install
cd ../..
```

### 2. Start the local interface

```bash
cd /home/agent/BioMaster/biomaster-skill-v0.5
./oc.sh restart
```

Open:

```text
http://127.0.0.1:4444
```

### 3. Start on a remote server

```bash
cd /home/agent/BioMaster/biomaster-skill-v0.5
HOSTNAME_BIND=0.0.0.0 OPENCODE_SERVER_PASSWORD=agent ./oc.sh restart
```

Open the frontend with the actual server IP address:

```text
http://<server-ip>:4444/?auth_token=b3BlbmNvZGU6YWdlbnQ=
```

The example token corresponds to `opencode:agent`. For any public or shared deployment, replace the example password and avoid exposing an unauthenticated backend.

Useful launcher commands:

```bash
./oc.sh start      # start backend and frontend
./oc.sh stop       # stop backend and frontend
./oc.sh restart    # restart both services
./oc.sh status     # show process IDs and HTTP status
./oc.sh logs       # show recent backend/frontend logs
```

## Static Site Deployment

The `docs/` directory is plain HTML, CSS, JavaScript, and static assets. It does not require a build step and is named to match GitHub Pages' `/docs` publishing option.

Preview locally:

```bash
cd /home/agent/BioMaster/biomaster-skill-v0.5/docs
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
- **Archive transfer**: use `docs.tar.gz`, which is regenerated from `docs/` without macOS metadata files.

## Using BioMaster

### BioMaster workflow interface

1. Start OpenCode with `./oc.sh restart`.
2. Open the frontend at `http://127.0.0.1:4444` or `http://<server-ip>:4444`.
3. Select the BioMaster project directory when prompted:

   ```text
   /home/agent/BioMaster/biomaster-skill-v0.5/biomaster2-main
   ```

4. Use the BioMaster commands and agents through OpenCode:
   - `biomaster-plan` remains the primary workflow agent.
   - `biomaster-execute`, `biomaster-debug`, and `biomaster-check` handle step execution, error recovery, and output validation.
   - `biomaster-skiller`, `biomaster-skill-author`, and `biomaster-skill-creator` are available for BioSkills management but are not part of the normal execution loop.

### BioSkills Library

The BioSkills Library stores structured knowledge as files under:

```text
biomaster2-main/.opencode/bioskills/
```

Each curated skill contains:

- `SKILL.md`: metadata and compatibility information
- `macro.md`: high-level workflow or conceptual description
- `micro.md`: execution-level notes, commands, or tool guidance
- `steps.json`: structured step metadata

The SQLite database under `.opencode/knowledge/` is a generated cache. If it is missing, it is rebuilt by the runtime sync scripts and tests.

## Validation

Run the full validation suite before release or deployment:

```bash
cd /home/agent/BioMaster/biomaster-skill-v0.5/biomaster2-main
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
- Python caches such as `__pycache__/` and `.pytest_cache/`

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

- retains the v0.4 OpenCode/BioSkills runtime structure;
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
- Keep BioSkills source files in `biomaster2-main/.opencode/bioskills/`.
- Do not commit generated SQLite databases, BioSkills FTS indexes, dependency folders, or project run outputs.
- Review large biological data files before public release or migration to Git LFS.
- Re-run `make test` after modifying runtime code, agents, BioSkills schemas, or OpenCode BioSkills routes.
