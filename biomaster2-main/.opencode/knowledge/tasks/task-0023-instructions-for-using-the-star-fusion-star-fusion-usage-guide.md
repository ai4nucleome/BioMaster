---
id: task-0023
title: Instructions for using the STAR-fusion:## STAR-Fusion Usage Guide
summary: Instructions for using the STAR-fusion:## STAR-Fusion Usage Guide This document
  consolidates notes on running **STAR-Fusion** for fusion transcript detection, either
  starting directly from FASTQ files or using an exis...
keywords:
- star-fusion
- STAR-Fusion
- Instructions for using the STAR-fusion:## STAR-Fusion Usage Guide
- This document consolidates notes on running **STAR-Fusion** for fusion transcript
  detection
- either starting directly from FASTQ files or using an existing STAR alignment (Kickstart
  mode). It also covers important parameters
- output format
- and integration with **FusionInspector**
- '### 1. Running STAR-Fusion'
- STAR-Fusion can be run in **two primary ways**
- 1. **Starting from FASTQ files (typical)**
- '**Paired-end FASTQ**'
- '```bash'
- STAR-Fusion \
- genome_lib_dir
- path
- to
- CTAT_resource_lib \
- left_fq reads_1.fq \
- right_fq reads_2.fq \
- output_dir star_fusion_outdir
- '```'
- '**Single-end FASTQ**'
- Here
- '`CTAT_resource_lib` is the path to the STAR-Fusion-compatible reference. STAR-Fusion
  internally runs the STAR aligner with recommended fusion-related parameters'
- 2. **Using an existing STAR alignment (Kickstart mode)**
- If you have already aligned reads with STAR and have a `Chimeric.out.junction` file
- you can feed that
- STAR
path: .opencode/knowledge/tasks/task-0023-instructions-for-using-the-star-fusion-star-fusion-usage-guide.md
origin_source: STAR-Fusion
origin_page: 24
source_entry_index: 19
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: star-fusion
---

# Instructions for using the STAR-fusion:## STAR-Fusion Usage Guide

## One-line description

Instructions for using the STAR-fusion:## STAR-Fusion Usage Guide This document consolidates notes on running **STAR-Fusion** for fusion transcript detection, either starting directly from FASTQ files or using an exis...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `STAR-Fusion`
- Origin page: `24`
- Source entry index: `19`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0023`
- Analysis/tool category: `star-fusion`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Instructions for using the STAR-fusion:## STAR-Fusion Usage Guide

This document consolidates notes on running **STAR-Fusion** for fusion transcript detection, either starting directly from FASTQ files or using an existing STAR alignment (Kickstart mode). It also covers important parameters, output format, and integration with **FusionInspector**.

---

### 1. Running STAR-Fusion

STAR-Fusion can be run in **two primary ways**:

1. **Starting from FASTQ files (typical)**
   
   **Paired-end FASTQ**:
   ~~~bash
   STAR-Fusion \
     --genome_lib_dir /path/to/CTAT_resource_lib \
     --left_fq reads_1.fq \
     --right_fq reads_2.fq \
     --output_dir star_fusion_outdir
   ~~~
   **Single-end FASTQ**:
   ~~~bash
   STAR-Fusion \
     --genome_lib_dir /path/to/CTAT_resource_lib \
     --left_fq reads_1.fq \
     --output_dir star_fusion_outdir
   ~~~
   Here, `CTAT_resource_lib` is the path to the STAR-Fusion-compatible reference. STAR-Fusion internally runs the STAR aligner with recommended fusion-related parameters.

2. **Using an existing STAR alignment (Kickstart mode)**
   
   If you have already aligned reads with STAR and have a `Chimeric.out.junction` file, you can feed that directly to STAR-Fusion:
   ~~~bash
   STAR-Fusion \
     --genome_lib_dir /path/to/CTAT_resource_lib \
     -J Chimeric.out.junction \
     --output_dir star_fusion_outdir
   ~~~
   This only works if you ran STAR with certain parameters (listed below) that enable chimeric read detection and generate the properly formatted `Chimeric.out.junction` file.

---

### 2. Running STAR for Fusion Detection

If you prefer to run STAR separately, be sure to include **key parameters** required by STAR-Fusion:

~~~bash
STAR --genomeDir /path/to/star_index \
     --readFilesIn reads_1.fq reads_2.fq \
     --outReadsUnmapped None \
     --twopassMode Basic \
     --readFilesCommand "gunzip -c" \  # or zcat if gzipped
     --outSAMstrandField intronMotif \
     --outSAMunmapped Within \
     --chimSegmentMin 12 \  # *** essential for chimeric read detection ***
     --chimJunctionOverhangMin 8 \
     --chimOutJunctionFormat 1 \  # *** required for STAR-Fusion ***
     --alignSJDBoverhangMin 10 \
     --alignMatesGapMax 100000 \
     --alignIntronMax 100000 \
     --alignSJstitchMismatchNmax 5 -1 5 5 \
     --outSAMattrRGline ID:GRPundef \
     --chimMultimapScoreRange 3 \
     --chimScoreJunctionNonGTAG -4 \
     --chimMultimapNmax 20 \
     --chimNonchimScoreDropMin 10 \
     --peOverlapNbasesMin 12 \
     --peOverlapMMp 0.1 \
     --alignInsertionFlush Right \
     --alignSplicedMateMapLminOverLmate 0 \
     --alignSplicedMateMapLmin 30
~~~

This creates `Chimeric.out.junction`, which STAR-Fusion can use via `-J Chimeric.out.junction`. Ensure `--chimOutJunctionFormat 1` is set so that STAR-Fusion can estimate FFPM values.

---

### 3. STAR-Fusion Outputs

After successful completion, STAR-Fusion writes results to the `star_fusion_outdir` (or chosen directory). The main outputs are:

1. **star-fusion.fusion_predictions.tsv**: A tab-delimited file listing each detected fusion event with supporting data. An abridged version (`.abridged.tsv`) omits explicit read identities.
2. **Columns of interest**:
   - **FusionName**: e.g. `GENE1--GENE2`.
   - **JunctionReadCount**: number of reads spanning the junction (split reads).
   - **SpanningFragCount**: number of read pairs where each mate maps to different genes.
   - **LargeAnchorSupport**: `YES_LDAS` if the split reads have ≥25 bases of unique alignment on both sides of the breakpoint.
   - **FFPM**: Fusion Fragments Per Million total reads (normalizes for library depth).
   - **SpliceType**: shows if breakpoints occur at known exon junctions.
   - **LeftGene/RightGene** and corresponding breakpoints.
   - **LeftBreakEntropy/RightBreakEntropy**: Shannon entropy near the breakpoint (range 0–2, with low entropy often less reliable).
   - **annots**: additional annotations, e.g. known fusions in cancer datasets, or whether the event is intrachromosomal or interchromosomal.

---

### 4. FusionInspector (In Silico Validation)

**FusionInspector** is included in STAR-Fusion for validating or refining predicted fusions:

- **--FusionInspector inspect**: re-map only the fusion-evidence reads to custom "fusion contigs," enabling quick inspection.
- **--FusionInspector validate**: re-map **all** reads to both the reference genome and the constructed fusion contigs, re-scoring fusions.
- **--denovo_reconstruct**: attempts to assemble fusion transcripts de novo using Trinity.
- **--examine_coding_effect**: determines coding in-frame/frameshift status and domain structure.

Example:
~~~bash
STAR-Fusion \
  --left_fq reads_1.fq.gz \
  --right_fq reads_2.fq.gz \
  --genome_lib_dir /path/to/CTAT_genome_lib \
  --FusionInspector validate \
  --denovo_reconstruct \
  --examine_coding_effect
~~~

This produces a `FusionInspector-validate/` subdirectory with refined predictions (`finspector.fusion_predictions.final`) and optional de novo–assembled contigs (`finspector.gmap_trinity_GG.fusions.fasta`).

---

### 5. Additional Details

- **Memory requirements**: Running STAR-Fusion from FASTQ typically needs ~40GB of RAM (STAR alignment). The post-processing steps themselves need far less.
- **CTAT resource library**: Must contain the genome plus specialized annotation files for known fusions, repeats, etc.
- **Filtering**: Low-support fusions can be noise; adjusting parameters like `--min_FFPM` can remove artifactual events.
- **Visualization**: Output files (contig BAM, bed files) can be loaded into IGV or used via an HTML-based viewer (e.g., igv-reports) for analyzing supporting read evidence.

---

### 6. Summary of Recommended Steps

1. **Build or download** a CTAT resource library (contains genome + fusion metadata).
2. **Run STAR-Fusion**
   - From **FASTQ**: specify `--left_fq [--right_fq]`.
   - Using **existing STAR alignment**: ensure recommended chimeric parameters, then feed `Chimeric.out.junction` via `-J`.
3. **Review outputs** in `star_fusion_outdir`, focusing on:
   - `star-fusion.fusion_predictions.tsv`/`.abridged.tsv`
   - Optional `FusionInspector-validate/` for more in-depth data.
4. **Use additional flags** like `--examine_coding_effect` or `--denovo_reconstruct` to deepen analysis.

With these steps and parameters, you can accurately detect and annotate fusion transcripts. FusionInspector can further validate or assemble the fusions for additional confidence, and outputs are easily viewed in IGV or other genomic viewers.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
