---
id: task-0030
title: 'Transcriptome Annotation Comparison (Gencode vs Chess) using rnalib must include:Step1:
  Set test...'
summary: 'Transcriptome Annotation Comparison (Gencode vs Chess) using rnalib must
  include:Step1: Set test data directory. Description: Define the global test data
  path for rnalib by monkey-patching `rna.__RNALIB_TESTDATA__`. G...'
keywords:
- rnalib-annotation-workflow
- rnalib_annotation_workflow
- 'Transcriptome Annotation Comparison (Gencode vs Chess) using rnalib must include:Step1:
  Set test'
- 'Transcriptome Annotation Comparison (Gencode vs Chess) using rnalib must include:Step1:
  Set test data directory. Description: Define the global test data path for rnalib
  by monkey-patching `rna.__RNALIB_TESTDATA__`. Generate necessary resources if missing
  by calling `rna.testdata.create_testdata`. Python code snippet'
- 'cat << ''EOF'' > setup_testdata.py

  import rnalib as rna

  rna.__RNALIB_TESTDATA__ = "rnalib_testdata'
- '"

  rna.testdata.create_testdata(rna.__RNALIB_TESTDATA'
- (rna.testdata.test_resources
- 'rna.testdata.large_test_resources))

  EOF'
- 'Step2: Load transcriptome data. Description: Instantiate `rna.Transcriptome` objects
  for Gencode and Chess annotations using canonical GRCh38 chromosomes and gene-type
  filtering (''protein_coding''). Use latest gene symbols via `gene_name_alias_file`.
  Example code'
- 'cat << ''EOF'' > load_transcriptomes.py

  import rnalib as rna

  alias_txt = rna.get_resource("gene_aliases")

  gencode_gff = rna.get_resource("full_gencode_gff")

  chess_gff = rna.get_resource("full_chess_gtf")'
- txfilter = rna.TranscriptFilter(). \
- include_gene_types({'protein_coding'}). \
- include_chromosomes(rna.CANONICAL_CHROMOSOMES['GRCh38'])
- t_gc = rna.Transcriptome(
- annotation_g
path: .opencode/knowledge/tasks/task-0030-transcriptome-annotation-comparison-gencode-vs-chess-using-rnalib-must-include-step1-set-test.md
origin_source: rnalib_annotation_workflow
origin_page: 31
source_entry_index: 26
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: rnalib-annotation-workflow
---

# Transcriptome Annotation Comparison (Gencode vs Chess) using rnalib must include:Step1: Set test...

## One-line description

Transcriptome Annotation Comparison (Gencode vs Chess) using rnalib must include:Step1: Set test data directory. Description: Define the global test data path for rnalib by monkey-patching `rna.__RNALIB_TESTDATA__`. G...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `rnalib_annotation_workflow`
- Origin page: `31`
- Source entry index: `26`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0030`
- Analysis/tool category: `rnalib-annotation-workflow`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Transcriptome Annotation Comparison (Gencode vs Chess) using rnalib must include:Step1: Set test data directory. Description: Define the global test data path for rnalib by monkey-patching `rna.__RNALIB_TESTDATA__`. Generate necessary resources if missing by calling `rna.testdata.create_testdata`. Python code snippet:

cat << 'EOF' > setup_testdata.py
import rnalib as rna
rna.__RNALIB_TESTDATA__ = "rnalib_testdata/"
rna.testdata.create_testdata(rna.__RNALIB_TESTDATA__, (rna.testdata.test_resources, rna.testdata.large_test_resources))
EOF

Step2: Load transcriptome data. Description: Instantiate `rna.Transcriptome` objects for Gencode and Chess annotations using canonical GRCh38 chromosomes and gene-type filtering ('protein_coding'). Use latest gene symbols via `gene_name_alias_file`. Example code:

cat << 'EOF' > load_transcriptomes.py
import rnalib as rna
alias_txt = rna.get_resource("gene_aliases")
gencode_gff = rna.get_resource("full_gencode_gff")
chess_gff = rna.get_resource("full_chess_gtf")

txfilter = rna.TranscriptFilter(). \
    include_gene_types({'protein_coding'}). \
    include_chromosomes(rna.CANONICAL_CHROMOSOMES['GRCh38'])

t_gc = rna.Transcriptome(
    annotation_gff=gencode_gff,
    annotation_flavour='gencode',
    copied_fields=['gene_type', 'transcript_type'],
    gene_name_alias_file=alias_txt,
    feature_filter=txfilter)

t_ch = rna.Transcriptome(
    annotation_gff=chess_gff,
    annotation_flavour='chess',
    copied_fields=['gene_type'],
    gene_name_alias_file=alias_txt,
    feature_filter=txfilter)
EOF

Step3: Perform annotation comparison. Description: Use `rna.cmp_sets` to identify shared and unique genes. Example snippet:

cat << 'EOF' > compare_annotations.py
import rnalib as rna
shared, uniq_gc, uniq_ch = rna.cmp_sets({x.gene_name for x in t_gc.genes}, {x.gene_name for x in t_ch.genes})
EOF

Step4: Detailed gene coordinate comparison. Description: Utilize `rna.AnnotationIterator` to systematically identify differences in gene coordinates and names. Compute histograms for differences in start/end coordinates and visualize using matplotlib. Example code:

cat << 'EOF' > detailed_comparison.py
import rnalib as rna
from collections import Counter
import matplotlib.pyplot as plt

stats, hist_start, hist_end = Counter(), Counter(), Counter()
with rna.AnnotationIterator(
    rna.TranscriptomeIterator(t_gc, feature_types='gene'),
    rna.TranscriptomeIterator(t_ch, feature_types='gene')) as it:
    for gene_gc, dat in it:
        # coordinate comparison logic
        pass  # full implementation omitted for brevity
EOF

Tools Used: rnalib package, Python, matplotlib
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
