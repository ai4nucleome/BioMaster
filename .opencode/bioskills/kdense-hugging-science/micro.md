## flagship-resources.md

# Flagship resources by domain

Sensible "if in doubt, start here" picks per scientific domain. These are the resources users most often want when they describe a task in plain language. Always confirm with the live catalog (`fetch_catalog.py topic <slug>`) before final recommendation — the catalog evolves and there may be something newer.

The catalog is the source of truth. Treat this file as a fast cheatsheet, not a directory.

## Biology / Genomics

**DNA foundation models**
- `arcinstitute/evo2_40b` — 40B-param DNA LM, 9.3T nucleotide pretraining; zero-shot variant effect prediction, sequence generation. Huge — use Inference Providers or a Space.
- `arcinstitute/evo2_7b` — 7B instruction-tuned variant; runs on a single 24 GB GPU.

**Protein language models**
- `facebook/esm2_t33_650M_UR50D` — 650M ESM2; standard for embeddings, structure prediction, mutation scoring. Strong default.
- Smaller ESM2 variants (`*_t30_150M_*`, `*_t12_35M_*`) for laptop/CPU use.

**Single-cell / transcriptomics**
- `arcinstitute/Stack-Large` (STACK) — single-cell foundation model with in-context learning across cell types.
- `Merck/TEDDY` — 116M single-cell foundation models for genomics + drug discovery.

**Antibodies**
- `opig/OAS` — Observed Antibody Space, ~1B antibody sequences. The standard antibody ML dataset.

**Bioacoustics / ecology**
- `EarthSpeciesProject/NatureLM-audio` — first audio-LM for animal vocalizations.
- `EarthSpeciesProject/esp-aves2-sl-beats-all` — self-supervised bioacoustic encoder.

**Genomic corpora**
- `arcinstitute/opengenome2` — curated prokaryotic + eukaryotic sequences for foundation-model pretraining.

## Chemistry / Drug discovery

- `SandboxAQ/AQAffinity` — drug-target affinity prediction.
- **SAIR dataset** — 1M+ protein-ligand co-structures (see SandboxAQ blog post in catalog).
- For SMILES/molecular tasks: check the catalog `chemistry` topic for current best — molecular foundation models change frequently.

## Materials science

- **LeMaterial** — large open materials database (see catalog blog post 2024-12-10).
- Crystal structure foundation models, perovskite datasets — fetch `topic materials-science` for the live list. Many ship `pymatgen.Structure` objects rather than tensors.

## Physics

- PDE-solver datasets (`topic physics --filter datasets`) — magnetohydrodynamics, fluid dynamics, plasma.
- Physics-Informed Neural Networks (PINN) — methodology covered in catalog blog posts.

## Climate / Earth science / Weather

- Weather-foundation-model entries under `topic climate` — these are often huge multi-modal models with structured atmospheric inputs (geopotential, temperature on multiple pressure levels).
- Satellite imagery / remote sensing models under `topic earth-science`.

## Medicine / Pathology

- `hugging-science/breast-cancer-detector-2` — image classification baseline from the org itself.
- Pathology + radiology foundation models — fetch `topic medicine`. Many are gated; check the model card for access requirements.

## Mathematics / Scientific reasoning

- **Kimina-Prover** family — large theorem-proving models. Likely needs Inference Providers.
- `topic scientific-reasoning` for LLM-as-scientific-assistant work, paper QA, multi-step reasoning evals.

## Astronomy

- Galaxy survey datasets (e.g., `hugging-science/mmu_legacysurvey_dr10_south_21`) — image-heavy, FITS format, may need `astropy`.
- Astronomical foundation models — fetch `topic astronomy`.

## Cross-domain interactive demos (Spaces)

- `hugging-science/boltzgen-demo` — protein/peptide/nanobody binder design (the marquee demo).
- `hugging-science/dataset-quest` — discover and submit scientific datasets.
- `hugging-science/science-release-heatmap` — visualize who's publishing AI4Science resources.

## How to use this list

1. User describes a task → match to a domain row above.
2. Fetch the live topic file with `fetch_catalog.py topic <slug>` and confirm the recommended resource still exists / is current.
3. Read the resource's HF card for input format, license, access requirements.
4. Follow `using-datasets.md` / `using-models.md` / `using-spaces.md` for the actual code.
5. If a related blog post is listed in the catalog, cite it when explaining methodology.

If nothing in this cheatsheet fits, run `fetch_catalog.py search "<keyword>"` against the full index. The catalog has hundreds of entries this file doesn't enumerate.

---

## topics-and-slugs.md

# Topic slugs and entry schema

The Hugging Science catalog organizes scientific resources across **17 topics**. Each has a markdown file at `https://huggingscience.co/topics/<slug>.md`. Slugs are lowercase and hyphenated.

## Topic slugs and what each covers

| Slug | What's in here |
|---|---|
| `astronomy` | Galaxy/stellar surveys, cosmology, exoplanets, telescope imagery, foundation models for astronomical data |
| `benchmark` | Cross-domain evaluation suites — useful when comparing methods or running standard tests |
| `biology` | Protein/DNA/single-cell data and models, antibodies, bioacoustics, microbiome — broad biology umbrella |
| `biotechnology` | Synthetic biology, fermentation, applied genetic engineering data |
| `chemistry` | Molecules, reactions, drug discovery, SMILES corpora, DFT data, ligand-protein interactions |
| `climate` | Weather forecasting, climate models, atmospheric data, storm/flood prediction |
| `conservation` | Wildlife monitoring, biodiversity, camera-trap and bioacoustic models |
| `earth-science` | Remote sensing, satellite imagery, geospatial foundation models |
| `ecology` | Species distribution, ecosystem dynamics, biogeography (overlaps with conservation/biology) |
| `energy` | Battery materials, fusion plasma, grid simulation, renewables modeling |
| `engineering` | CAD, mechanical/structural simulation, robotics datasets |
| `genomics` | DNA language models, variant effect, single-cell, phylogenetics (overlaps heavily with biology) |
| `materials-science` | Crystal structures, band gaps, catalysts, perovskites, alloys, materials foundation models |
| `mathematics` | Theorem proving, formal math, mathematical reasoning datasets |
| `medicine` | Pathology, radiology, clinical NLP, drug-disease, EHR (overlaps with biology/chemistry) |
| `physics` | PDE solvers, fluid/plasma simulation, particle physics, physics-informed ML |
| `scientific-reasoning` | LLMs for scientific QA, paper understanding, multi-step scientific reasoning |

## Cross-domain reality

Most real tasks span multiple slugs. Pull all relevant ones rather than guessing:

- "Drug discovery" → `chemistry`, `biology`, `medicine`
- "Protein structure prediction" → `biology`, `chemistry`
- "Weather forecasting model" → `climate`, `earth-science`, `physics`
- "Single-cell foundation model" → `biology`, `genomics`, `medicine`
- "Battery electrolyte design" → `materials-science`, `chemistry`, `energy`
- "Bioacoustic species ID" → `biology`, `ecology`, `conservation`

When in doubt, fall back to `python scripts/fetch_catalog.py search "<keyword>"` against the full catalog.

## Entry schema

Each catalog entry is an H3 block with bulleted metadata followed by a description. Three flavors:

### Datasets
```
### org/dataset-name
- **Type**: <category, e.g. "Genomics", "Pathology", "PDE Simulation">
- **Tags**: <comma-separated topic tags>
- **HuggingFace**: https://huggingface.co/datasets/org/dataset-name

<one-line description>
```

### Models
```
### Model Display Name
- **Type**: <category, e.g. "Protein Language Model", "Materials Foundation Model">
- **Tags**: <comma-separated topic tags>
- **HuggingFace**: https://huggingface.co/org/model-id

<one-line description>
```

### Blog posts
```
### Post Title
- **Author**: <username>
- **Date**: <YYYY-MM-DD>
- **Tags**: <comma-separated>
- **Link**: <URL — usually huggingface.co/blog/...>

<one-line description>
```

## Endpoints

- `https://huggingscience.co/llms.txt` — compact site index
- `https://huggingscience.co/llms-full.txt` — every entry, every domain (this is the file to fetch when you want to grep across the whole catalog)
- `https://huggingscience.co/topics/<slug>.md` — one domain
- `https://huggingscience.co/feed.xml` — RSS for new entries

The `fetch_catalog.py` script wraps these and adds parsing, filtering, and JSON output. Prefer the script for structured access; use raw `WebFetch`/`curl` only if the script fails.

---

## using-datasets.md

# Using scientific datasets from the catalog

Hugging Science dataset entries always link to a Hugging Face Hub dataset (`huggingface.co/datasets/<org>/<name>`). You load them with the standard `datasets` library. The interesting part is what makes scientific datasets *different* from typical NLP/vision datasets — that's what this file is about.

## Install

Use `uv` for all installs:

```bash
uv pip install datasets huggingface_hub      # in an active venv
# or, project-style:
uv add datasets huggingface_hub
# one-off:
uv run --with datasets python my_script.py
```

For private/gated datasets, authenticate via `HF_TOKEN`. **Prefer loading from `.env`:**

```bash
# .env (in project root, gitignored)
HF_TOKEN=hf_...
```

```python
from dotenv import load_dotenv
load_dotenv()                # picks up HF_TOKEN before any HF call
from datasets import load_dataset
ds = load_dataset("opig/OAS")
```

If `python-dotenv` isn't installed: `uv add python-dotenv` (or `uv pip install python-dotenv`).

A surprising number of biomedical datasets are gated (clinical PHI proxies, antibody repertoires from named patients). Check the dataset card before assuming open access.

## Default loading pattern

```python
from datasets import load_dataset

ds = load_dataset("arcinstitute/opengenome2")
print(ds)            # see splits and columns
print(ds["train"][0]) # peek at one row
```

## Use streaming for large datasets — by default

Many scientific corpora are 10 GB to many TB. `load_dataset(..., streaming=True)` returns an `IterableDataset` that pulls shards on demand instead of materializing the whole thing on disk:

```python
ds = load_dataset("arcinstitute/opengenome2", split="train", streaming=True)
for example in ds.take(10):
    ...
```

Rule of thumb: if the dataset card mentions billions of tokens, millions of images, or "TB", default to streaming and only switch to full download when the user explicitly wants offline reproducibility.

## Inspect schema before assuming columns

Generic datasets have predictable columns (`text`, `label`, `image`). Scientific datasets often don't. Before writing preprocessing code, look at one example:

```python
sample = next(iter(load_dataset("opig/OAS", split="train", streaming=True)))
print(sample.keys())
```

Common surprises:
- **Genomics**: columns can be `sequence`, `species`, `taxonomy`, `accession` rather than `text`.
- **Materials**: rows may contain serialized `pymatgen` `Structure` objects or CIF strings — not numeric tensors.
- **Imaging**: medical/astronomy images can be FITS, DICOM, or NIfTI rather than PNG/JPEG. The `image` column may be raw bytes that need a domain-specific decoder.
- **Time series / signals**: EEG, audio, weather often have variable-length arrays under a column like `signal` or `array`; the dtype matters (`float16` vs `float32`) for memory.

## Splits and subsets

- Many scientific datasets ship multiple **configs** (e.g., `load_dataset("Merck/TEDDY", "single_cell")`). If `load_dataset` errors with "Please pick a config", read the dataset card or run `get_dataset_config_names("...")`.
- Some have non-standard split names (`pretrain`, `held_out_species`, `test_chr1`). Don't assume `train/validation/test`.

## Filtering and subsetting

For very large datasets, prefer `filter` on a streaming iterator over downloading and slicing:

```python
ds = load_dataset("opig/OAS", split="train", streaming=True)
human_only = ds.filter(lambda ex: ex.get("species") == "human")
```

To convert a streaming subset into an in-memory dataset for training:

```python
from datasets import Dataset
subset = Dataset.from_list(list(human_only.take(10_000)))
```

## Train/eval handoff to `transformers`

Once shaped correctly, scientific datasets feed `Trainer`/`SFTTrainer` like any other. The bridge is usually a tokenizer or feature extractor that's specific to the domain:

- DNA: tokenizer from the matching DNA model (e.g., `AutoTokenizer.from_pretrained("arcinstitute/evo2_7b", trust_remote_code=True)`).
- Proteins: `AutoTokenizer.from_pretrained("facebook/esm2_t33_650M_UR50D")`.
- SMILES: usually a character-level or BPE tokenizer; check the model card.

If a model and dataset come from the same org, their tokenizers/preprocessors are usually compatible by design — that's a strong signal to pair them.

## Caveats specific to scientific data

- **License**: Some datasets are CC-BY-NC (research only). Check before any commercial deployment suggestion.
- **Versioning**: Major scientific datasets revise their splits over time. Pin a `revision=` if reproducibility matters.
- **Preprocessing must match training**: For foundation models, the catalog's blog posts often document the *exact* preprocessing used in pretraining (tokenizer config, normalization). When fine-tuning, replicate it — small mismatches (e.g., reverse complement augmentation for DNA) can wreck downstream performance.

---

## using-models.md

# Using scientific models from the catalog

Hugging Science model entries link to standard Hugging Face Hub repos. There are three sensible execution paths. Pick based on model size and whether the user is doing one-off inference or a long batch job.

## Decision: where to run the model

| Path | When to use | What it costs |
|---|---|---|
| **Local with `transformers`** | Models ≤ ~7B params, user has a GPU or wants offline use, or doing fine-tuning | Disk + VRAM; free |
| **HF Inference API (serverless)** | Quick one-off inference on smaller hosted models, no GPU needed | Free tier exists, then pay-per-call |
| **HF Inference Providers** | Very large models (Evo-2 40B, Kimina-Prover 72B), or when you need throughput | Pay-per-token; routed to third-party providers |
| **HF Space (gradio_client)** | The model has an interactive demo and you want easy structured I/O without managing weights | Free if Space is public; see `using-spaces.md` |

Always check the model card first — some entries are *only* available as Spaces (no public weights), and some are gated and require approval before download.

## Local with `transformers`

Use `uv` for installs:

```bash
uv pip install transformers torch accelerate python-dotenv    # in an active venv
# or project-style:
uv add transformers torch accelerate python-dotenv
```

For gated models, put the token in `.env` rather than running `huggingface-cli login`:

```
# .env (gitignored)
HF_TOKEN=hf_...
```

```python
from dotenv import load_dotenv
load_dotenv()    # reads HF_TOKEN before any HF call

from transformers import AutoModel, AutoTokenizer

model_id = "facebook/esm2_t33_650M_UR50D"
tok = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

inputs = tok("MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ", return_tensors="pt")
embeddings = model(**inputs).last_hidden_state
```

### `trust_remote_code=True` is normal here

A large fraction of scientific models — Evo-2, many Nucleotide Transformer variants, single-cell foundation models, several materials models — ship custom modeling code in their repo. `transformers` will refuse to load them without `trust_remote_code=True`:

```python
model = AutoModel.from_pretrained("arcinstitute/evo2_7b", trust_remote_code=True)
```

Tell the user when you set this flag and why. It executes Python from the repo, so the user should trust the org. The catalog only lists reputable orgs (Arc Institute, Meta/Facebook AI, EleutherAI, SandboxAQ, Merck, etc.), but the user gets to make the call.

### Sizing the GPU

Rough memory for inference at fp16 (very approximate — quantization changes this):

- 35M–650M params (most ESM2 variants): runs on a laptop GPU or even CPU.
- 1B–7B (Evo-2 7B, Nucleotide Transformer 2.5B, STACK Large): single 24 GB GPU is fine.
- 40B+ (Evo-2 40B, Kimina-Prover): needs multi-GPU or A100/H100; almost always better via Inference Providers unless the user has the hardware.

For training/fine-tuning, multiply by ~3–4× for activations and optimizer state.

## HF Inference API (serverless)

Fast for tiny one-off jobs without setting up a GPU. The model has to be supported on the serverless tier (smaller models, popular pipelines).

```bash
uv pip install huggingface_hub python-dotenv     # or: uv add huggingface_hub python-dotenv
```

Put your token in `.env` rather than exporting per-shell:

```
# .env (gitignored)
HF_TOKEN=hf_...
```

```python
from dotenv import load_dotenv
load_dotenv()    # InferenceClient reads HF_TOKEN from env

from huggingface_hub import InferenceClient

client = InferenceClient(model="facebook/esm2_t33_650M_UR50D")
result = client.feature_extraction("MKTAYIAKQR")
```

The serverless API supports tasks like `feature_extraction`, `text_generation`, `image_classification`, `token_classification`. For non-standard scientific tasks (e.g., DNA sequence generation), you may need Inference Providers or local execution instead.

## HF Inference Providers

For very large models or when you want production throughput. Inference Providers route requests to vetted backends (Together, Fireworks, Replicate, Sambanova, etc.) that host frontier models.

```python
from huggingface_hub import InferenceClient

client = InferenceClient(provider="together", model="arcinstitute/evo2_40b")
output = client.text_generation("ATCGGCTA", max_new_tokens=64)
```

Check the model card for which providers host it. Not every catalog model is available — many are research-only and only hosted by their authors as a Space.

## After loading: standard pipelines apply

Once the model is loaded, scientific models behave like any other `transformers` model — you embed sequences, generate, classify, or fine-tune. The unique steps are:

1. **Use the matching tokenizer/feature extractor.** Don't try to feed protein sequences to a DNA tokenizer; the alphabets are different and the model will silently produce garbage.
2. **Match the preprocessing from pretraining.** For fine-tuning, the catalog's blog posts often spell out exact preprocessing recipes (special tokens, normalization, augmentation). Read them before training.
3. **Mind the output head.** Many scientific foundation models are masked-LM by default; classification or regression downstream tasks usually need an extra head layered on `model.last_hidden_state`.

## When you can't run a model anywhere

Some catalog models are demo-only — the authors host a Space but never published weights. In that case:

- See `using-spaces.md` and call the Space via `gradio_client`.
- Or surface this constraint to the user and offer the next-best fully-open alternative from the same topic file.

---

## using-spaces.md

# Using Hugging Science Spaces (interactive demos)

A **Hugging Face Space** is a hosted web app — usually Gradio or Streamlit — that wraps a model behind a UI. The `hugging-science` org maintains ~27 of these, and many catalog entries point to a Space rather than (or in addition to) raw weights. Spaces are the fastest way to get scientific output without managing models or GPUs yourself.

Spaces are not just web pages — every Gradio Space exposes a programmatic API. You can call them from Python with `gradio_client` and parse the result as a normal Python value.

## When to call a Space (vs. running the model locally)

Reach for a Space when:
- The user wants a one-shot result, not a fine-tuning loop.
- The model is huge (40B+) and the user has no GPU.
- The model has private weights and the Space is the only public interface.
- The Space already implements complex orchestration (tokenization, sampling, post-processing) you'd otherwise reimplement.

Reach for local execution instead when:
- You'll call it many times in a loop (Spaces have rate limits and queues).
- You're fine-tuning, batching at scale, or need offline reproducibility.
- The Space is private/gated and you can't get access.

## Setup

```bash
uv pip install gradio_client python-dotenv    # or: uv add gradio_client python-dotenv
```

For private/gated Spaces, store the token in `.env` and load it at startup:

```
# .env (gitignored)
HF_TOKEN=hf_...
```

```python
from dotenv import load_dotenv
load_dotenv()    # gradio_client picks up HF_TOKEN automatically
```

## The general pattern

```python
from gradio_client import Client

client = Client("hugging-science/<space-name>")

# Find the API endpoints exposed by this Space:
print(client.view_api())

# Call the endpoint named in view_api(), e.g. "/predict":
result = client.predict(
    "argument_one",
    42,
    api_name="/predict",
)
print(result)
```

`view_api()` is the discovery step — it prints every exposed endpoint with parameter names and types. Always run it once when wrapping a new Space; the function signature varies between Spaces and isn't always obvious from the UI.

## Worked example: BoltzGen (protein/peptide/nanobody binder design)

BoltzGen is one of the flagship Spaces in the `hugging-science` org. It generates designed binders against a target protein.

```python
from gradio_client import Client, file

client = Client("hugging-science/boltzgen-demo")
print(client.view_api())   # inspect first

# Typical call shape (verify against view_api() — endpoint names evolve):
result = client.predict(
    target_pdb=file("/path/to/target.pdb"),
    binder_type="protein",         # or "peptide", "nanobody"
    n_designs=8,
    api_name="/generate",
)
# result is usually a list of generated sequences/structures or a path
# to a downloadable file inside the Space's tmp dir.
```

When the Space returns a file path, `gradio_client` downloads the file to a local temp location and returns the path — handy for pipelines that need the actual output (`.pdb`, `.fasta`).

## File inputs

Many scientific Spaces take structured file inputs (PDB, CIF, FASTA, NIfTI, FITS). Wrap them with `gradio_client.file(...)`:

```python
from gradio_client import file
result = client.predict(file("target.pdb"), api_name="/predict")
```

Don't pass raw paths as strings — Gradio uploads files differently from text and the type wrapper signals which is which.

## Other notable Spaces in `hugging-science`

These are good defaults to know about. Always check `view_api()` for the current signature.

| Space | Purpose |
|---|---|
| `hugging-science/boltzgen-demo` | Protein / peptide / nanobody binder design |
| `hugging-science/anatomy-of-boltzgen` | Educational walkthrough of BoltzGen architecture |
| `hugging-science/dataset-quest` | Browse and submit community scientific datasets |
| `hugging-science/science-release-heatmap` | Visualize AI4Science contributors across orgs and domains |
| `hugging-science/HuggingMod` | Community moderation tooling |

The full live list lives at `huggingface.co/hugging-science` (Spaces tab). If a Space name 404s, the org may have renamed it — search the org page or check the catalog entry.

## Rate limits and queue behavior

Free Spaces share a community GPU queue. For interactive use this is fine; for any kind of batching:

- Expect occasional `queue is full` or timeout errors. Add retry-with-backoff.
- For large workloads, duplicate the Space into your own account (the "Duplicate" button on the Space page) to get private compute.
- Or: run the underlying model locally if weights are public — usually preferable for >10s of calls.

## When the Space has no API

A small minority of Spaces disable the API or are Streamlit-based without a clean programmatic interface. In that case, fall back to local model execution (`using-models.md`) or surface the limitation to the user — don't try to scrape the UI.
