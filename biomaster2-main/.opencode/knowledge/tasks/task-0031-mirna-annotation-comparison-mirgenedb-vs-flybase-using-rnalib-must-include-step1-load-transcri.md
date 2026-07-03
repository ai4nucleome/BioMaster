---
id: task-0031
title: 'miRNA Annotation Comparison (MirGeneDB vs FlyBase) using rnalib must include:Step1:
  Load transcri...'
summary: 'miRNA Annotation Comparison (MirGeneDB vs FlyBase) using rnalib must include:Step1:
  Load transcriptome data from MirGeneDB and FlyBase. Description: Instantiate transcriptomes
  for MirGeneDB and FlyBase annotations. Ex...'
keywords:
- rnalib-annotation-workflow
- rnalib_annotation_workflow
- 'miRNA Annotation Comparison (MirGeneDB vs FlyBase) using rnalib must include:Step1:
  Load transcri'
- 'miRNA Annotation Comparison (MirGeneDB vs FlyBase) using rnalib must include:Step1:
  Load transcriptome data from MirGeneDB and FlyBase. Description: Instantiate transcriptomes
  for MirGeneDB and FlyBase annotations. Example snippet'
- 'cat << ''EOF'' > load_mirna_transcriptomes.py

  import rnalib as rna'
- t_mg = rna.Transcriptome(
- annotation_gff=rna.get_resource("mirgendb_dme_gff")
- annotation_flavour='mirgenedb')
- with tempfile.TemporaryDirectory() as tmpdir
- 'res = {"flybase_full": {'
- '"uri": "https'
- ftp.flybase.net
- releases
- FB2023_06
- dmel_r6.55
- gtf
- dmel-all-r6.55.gtf.gz"
- '"filename": "dmel-all-r6.55.gtf.gz"}}'
- rna.testdata.create_testdata(tmpdir
- res)
- t_fb = rna.Transcriptome(
- annotation_gff=rna.get_resource("flybase_full"
- tmpdir
- 'annotation_flavour=''flybase'')

  EOF'
- 'Step2: Exact and overlap-based annotation mapping. Description: Map MirGeneDB and
  FlyBase annotations based on exact location and overlap using rnalib iterators.
  Example code snippet'
- 'cat << ''EOF'' > mirna_annotation_mapping.py

  import rnalib as rna'
- '# Exact mapping

  mapping_exact = {name: t_mg_mir.get(mir'
- None) for mir
- name in t_fb_mir.items()}
- '# Overlap mapping

  mappin'
path: .opencode/knowledge/tasks/task-0031-mirna-annotation-comparison-mirgenedb-vs-flybase-using-rnalib-must-include-step1-load-transcri.md
origin_source: rnalib_annotation_workflow
origin_page: 32
source_entry_index: 27
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: rnalib-annotation-workflow
---

# miRNA Annotation Comparison (MirGeneDB vs FlyBase) using rnalib must include:Step1: Load transcri...

## One-line description

miRNA Annotation Comparison (MirGeneDB vs FlyBase) using rnalib must include:Step1: Load transcriptome data from MirGeneDB and FlyBase. Description: Instantiate transcriptomes for MirGeneDB and FlyBase annotations. Ex...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `rnalib_annotation_workflow`
- Origin page: `32`
- Source entry index: `27`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0031`
- Analysis/tool category: `rnalib-annotation-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
miRNA Annotation Comparison (MirGeneDB vs FlyBase) using rnalib must include:Step1: Load transcriptome data from MirGeneDB and FlyBase. Description: Instantiate transcriptomes for MirGeneDB and FlyBase annotations. Example snippet:

cat << 'EOF' > load_mirna_transcriptomes.py
import rnalib as rna

t_mg = rna.Transcriptome(
    annotation_gff=rna.get_resource("mirgendb_dme_gff"),
    annotation_flavour='mirgenedb')

with tempfile.TemporaryDirectory() as tmpdir:
    res = {"flybase_full": {
        "uri": "https://ftp.flybase.net/releases/FB2023_06/dmel_r6.55/gtf/dmel-all-r6.55.gtf.gz",
        "filename": "dmel-all-r6.55.gtf.gz"}}
    rna.testdata.create_testdata(tmpdir, res)
    t_fb = rna.Transcriptome(
        annotation_gff=rna.get_resource("flybase_full", tmpdir, res),
        annotation_flavour='flybase')
EOF

Step2: Exact and overlap-based annotation mapping. Description: Map MirGeneDB and FlyBase annotations based on exact location and overlap using rnalib iterators. Example code snippet:

cat << 'EOF' > mirna_annotation_mapping.py
import rnalib as rna

# Exact mapping
mapping_exact = {name: t_mg_mir.get(mir, None) for mir, name in t_fb_mir.items()}

# Overlap mapping
mapping_overlap = {}
with rna.it(rna.it(t_fb_mir), anno_its=rna.it(t_mg_mir)) as it:
    for loc, (fb_mir, mg_mir) in it:
        mapping_overlap[fb_mir] = [x.data for x in mg_mir]
EOF

Step3: Visualize annotations with IGV browser. Description: Export selected annotations to BED format and display in IGV browser. Example snippet:

cat << 'EOF' > igv_browser_display.py
import rnalib as rna
import tempfile, igv_notebook

with tempfile.TemporaryDirectory() as tmpdir:
    bed_file = f"{tmpdir}/annotations.bed"
    with open(bed_file, 'wt') as out:
        rna.it({
            'hpRNA:CR46343': t_fb['hpRNA:CR46343'],
            'gene_Dme-Mir-997_3p*': t_mg['gene_Dme-Mir-997_3p*'],
            'gene_Dme-Mir-997_5p': t_mg['gene_Dme-Mir-997_5p']
        }).to_bed(out)
    igv_notebook.init()
    browser = igv_notebook.Browser({
        "genome": "dm6",
        "tracks": [{"name": "BED", "url": bed_file, "format": "bed"}]
    }).search('hpRNA:CR46343')
EOF

Tools Used: rnalib, Python, IGV Browser (igv_notebook)
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
