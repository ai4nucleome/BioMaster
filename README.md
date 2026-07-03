# BioMaster on OpenCode — v0.3

BioMaster is a bioinformatics analysis agent system. This branch packages BioMaster
together with a modified [OpenCode](https://github.com/sst/opencode) platform that
provides both the agent backend and a web UI for managing a two-layer **BioSkills**
library (macro description layer + micro execution layer).

## Repository layout

```
.
├── oc.sh              # dev launcher for the backend + web frontend
├── opencode/          # modified OpenCode fork (backend server + SolidJS web app)
│   └── packages/
│       ├── opencode/  # backend HTTP API (incl. /bioskills routes)
│       └── app/       # SolidJS web app (incl. the BioSkills Library page)
└── biomaster2-main/   # BioMaster project
    └── .opencode/
        ├── agents/    # intake, plan, execute, debug, check, skiller,
        │              #   skill-author, skill-creator
        ├── tools/     # bioskills.ts (skill router), bioskills-author.ts
        ├── bioskills/ # file-backed BioSkills library (one folder per skill)
        └── bioskills-access.yaml  # role -> skill layer policy (integration interface)
```

## Prerequisites

- [Bun](https://bun.sh) (used as the runtime and package manager)
- A configured LLM provider / API key for OpenCode (see OpenCode docs)
- Optional: `python3` + `pdftotext` (poppler-utils) — enables PDF ingestion in the
  "New Skill → From a paper / URL / repo" flow

## Quick start

```bash
# 1. install dependencies
cd opencode && bun install && cd ..
cd biomaster2-main/.opencode && bun install && cd ../..

# 2. start backend (:4096) + web frontend (:4444)
./oc.sh start

# 3. open the web UI
#    http://127.0.0.1:4444
```

`oc.sh` binds the backend to the `biomaster2-main` project so the BioMaster agents,
tools, and BioSkills library are all available.

### oc.sh commands

```
./oc.sh start      # start backend + frontend
./oc.sh stop       # stop both
./oc.sh restart    # restart both
./oc.sh status     # show pids + HTTP health
./oc.sh logs       # tail recent backend/frontend logs
```

Default ports: backend `4096`, frontend `4444` (edit `oc.sh` to change).

## What's new in v0.3

- **Unified per-step skills**: each skill step shows its macro description with a
  collapsible micro execution section; muting a step hides both layers together.
- **BioSkills Library UI**: search + domain dropdown filter, a `customized` tag for
  user-added skills, and a domain dropdown (with "new domain") in the skill form.
- **New Skill options**: manual entry, "From a description (AI)", and
  "From a paper / URL / repo (AI)"; AI runs show a live conversation with a
  jump-to-skill button on completion.
- **skill-author / skill-creator agents**: curate/redivide raw material or synthesize
  new skills from an article / URL / GitHub repo / uploaded PDF.
- **skiller routing interface**: `biomaster-skiller` + `bioskills.ts` route the right
  layer (macro/micro/none) to each sub-agent; the agent<->skill wiring is centralized
  in `bioskills-access.yaml` (roles + aliases + default) so the agent graph can change
  without touching the tool or the skiller prompt.

## Notes

- Demo datasets under `biomaster2-main/data/` are included for test-mode runs.
- `node_modules/`, build output, and the generated BioSkills FTS index (`.index.db`)
  are not tracked; they are recreated by `bun install` / at runtime.
