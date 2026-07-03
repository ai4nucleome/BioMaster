---
id: task-0022
title: 'Instructions for using the STAR tool: Below is a more concise overview of
  STAR usage (sections 1....'
summary: 'Instructions for using the STAR tool: Below is a more concise overview of
  STAR usage (sections 1.2 through 14.25), preserving all key instructions. --- ##
  1.2 Basic Work Flow **STAR** involves two main steps: 1. **Gen...'
keywords:
- star
- STAR
- 'Instructions for using the STAR tool: Below is a more concise overview of STAR
  usage (sections 1'
- 'Instructions for using the STAR tool: Below is a more concise overview of STAR
  usage (sections 1.2 through 14.25)'
- preserving all key instructions
- '## 1.2 Basic Work Flow'
- '**STAR** involves two main steps'
- 1. **Generating genome indexes**
- 'Input: reference genome FASTA (one or more) and (optional but recommended) annotation
  GTF'
- 'Output: STAR-specific index files stored in a user-defined directory'
- 2. **Mapping reads to the genome**
- 'Input: the STAR index folder plus RNA-seq reads (FASTA'
- FASTQ)
- 'Output: alignment files (SAM'
- BAM)
- splice junctions
- unmapped reads
- logs
- etc
- '## 2. Generating Genome Indexes'
- '### 2.1 Basic Options'
- 'Example:

  ```

  STAR \'
- runThreadN <threads> \
- runMode genomeGenerate \
- genomeDir
- path
- to
- genomeDir \
- genomeFastaFiles
- genome.fa [more FASTAs...] \
- sjdbGTFfile
- annotations.gtf \
- 'sjdbOverhang <ReadLength - 1>

  ```

  - **--runThreadN**: number of threads.

  - **--runMode genomeGenerate**: tells STAR to build the genome index.

  - **--genomeDir**: output folder for index files.

  - **--genomeFastaFiles**: one or more uncompressed FASTA files.

  - **--sjdbGTFfile**: optional but strongly recommend'
path: .opencode/knowledge/tasks/task-0022-instructions-for-using-the-star-tool-below-is-a-more-concise-overview-of-star-usage-sections-1.md
origin_source: STAR
origin_page: 23
source_entry_index: 18
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: star
---

# Instructions for using the STAR tool: Below is a more concise overview of STAR usage (sections 1....

## One-line description

Instructions for using the STAR tool: Below is a more concise overview of STAR usage (sections 1.2 through 14.25), preserving all key instructions. --- ## 1.2 Basic Work Flow **STAR** involves two main steps: 1. **Gen...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `STAR`
- Origin page: `23`
- Source entry index: `18`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0022`
- Analysis/tool category: `star`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Instructions for using the STAR tool: Below is a more concise overview of STAR usage (sections 1.2 through 14.25), preserving all key instructions.

---

## 1.2 Basic Work Flow

**STAR** involves two main steps:

1. **Generating genome indexes**  
   - Input: reference genome FASTA (one or more) and (optional but recommended) annotation GTF.
   - Output: STAR-specific index files stored in a user-defined directory.

2. **Mapping reads to the genome**  
   - Input: the STAR index folder plus RNA-seq reads (FASTA/FASTQ).  
   - Output: alignment files (SAM/BAM), splice junctions, unmapped reads, logs, etc.

---

## 2. Generating Genome Indexes

### 2.1 Basic Options

Example:
~~~
STAR \
  --runThreadN <threads> \
  --runMode genomeGenerate \
  --genomeDir /path/to/genomeDir \
  --genomeFastaFiles /path/to/genome.fa [more FASTAs...] \
  --sjdbGTFfile /path/to/annotations.gtf \
  --sjdbOverhang <ReadLength - 1>
~~~
- **--runThreadN**: number of threads.
- **--runMode genomeGenerate**: tells STAR to build the genome index.
- **--genomeDir**: output folder for index files.
- **--genomeFastaFiles**: one or more uncompressed FASTA files.
- **--sjdbGTFfile**: optional but strongly recommended GTF.
- **--sjdbOverhang**: normally set to read length minus 1.

### 2.2 Advanced Notes

- **Include major chromosomes and unlocalized scaffolds**; skip patches/haplotypes unless needed.
- **Annotations must match genome FASTA** (naming consistency: e.g., both from Ensembl).
- **Small genomes**: scale down `--genomeSAindexNbases` (e.g., `min(14, log2(GenomeLength)/2 - 1)`).
- **Large references**: if >5000 scaffolds, reduce `--genomeChrBinNbits`.

---

## 3. Running Mapping Jobs

### 3.1 Basic Options

Example:
~~~
STAR \
  --runThreadN <threads> \
  --genomeDir /path/to/genomeDir \
  --readFilesIn /path/to/read1 [ /path/to/read2 ]
~~~
- **--genomeDir**: folder containing the STAR indexes.
- **--readFilesIn**: reads to map (paired-end requires read1 and read2).  
- If reads are gzipped: `--readFilesCommand zcat` (or similar) to decompress on the fly.

### 3.2 Other Key Options

- **Using annotations at mapping**: `--sjdbGTFfile <ann.gtf>` can be specified again here, even if not used when generating the index.
- **ENCODE-style defaults**: e.g., `--outFilterType BySJout`, `--alignSJoverhangMin 8`, etc.
- **Shared memory**: controlled by `--genomeLoad` (e.g. `LoadAndKeep`). May need adjusting system kernel parameters.

---

## 4. Output Files

- **Log.out**: main detailed log.  
- **Log.progress.out**: real-time stats.  
- **Log.final.out**: final mapping summary (unique/multi-mapping rates, splices, etc.).
- **Aligned.out.sam** or **Aligned.out.bam**: primary alignment file.
- **Aligned.sortedByCoord.out.bam**: coordinate-sorted BAM if `--outSAMtype BAM SortedByCoordinate`.
- **SJ.out.tab**: high-confidence splice junctions.

---

## 5. Chimeric/Fusion Alignments

- Enable detection with `--chimSegmentMin > 0`.
- Can output to the main BAM (`--chimOutType WithinBAM`) or a separate file (`Chimeric.out.sam` or `Chimeric.out.junction`).
- **STAR-Fusion** is recommended for robust fusion detection.

---

## 6. Output in Transcript Coordinates

- **--quantMode TranscriptomeSAM**: outputs `Aligned.toTranscriptome.out.bam` (used by tools like RSEM/eXpress).  
- By default, indels and soft-clips are disallowed in transcriptome alignments.

---

## 7. Counting Reads per Gene

- **--quantMode GeneCounts**: counts reads overlapping genes.  
- Output in `ReadsPerGene.out.tab` with four columns (unstranded, forward-strand, reverse-strand, etc.).

---

## 8. 2-pass Mapping

Improves novel junction discovery:
1. **Multi-sample**: run pass 1 for all samples, merge/collect junctions, then pass 2 using these junctions.
2. **Per-sample**: use `--twopassMode Basic`, so STAR auto-discovers junctions in pass 1 and re-maps in pass 2.

---

## 9. Merging Overlapping Paired-end Reads

- **--peOverlapNbasesMin**, **--peOverlapMMp**: merges mates if they overlap significantly, improving accuracy and enabling chimeric detection in the overlapped region.

---

## 10. Personal Variants

- **--varVCFfile**: specify a VCF (currently SNVs only) to mark overlap with genotype alleles in alignments.

---

## 11. WASP Filtering (Allele-Specific)

- **--waspOutputMode SAMtag**: adds `vW` to each alignment indicating whether it passes WASP filters.

---

## 12. Multimapping Chimeras

- **chimMultimapNmax > 0**: detects chimeric alignments that also multimap.
- Reported in `Chimeric.out.junction`.

---

## 13. STARsolo (Single-Cell RNA-seq)

- **--soloType Droplet**: for 10X/Drop-seq.  
- **--soloCBwhitelist**: file with valid barcodes.  
- Must specify cell barcode/UMI positions (e.g. `--soloCBstart`, `--soloUMIstart`).  
- Outputs barcodes.tsv, genes.tsv, matrix.mtx, etc. in a CellRanger-compatible format.

---

## 14. Description of All Options

STAR has extensive parameters grouped by function:
1. **Parameter Files**: load config from `--parametersFiles`.
2. **System**: shell settings.
3. **Run Parameters**: `--runMode`, `--runThreadN`, etc.
4. **Genome Parameters**: `--genomeDir`, `--genomeLoad`, etc.
5. **Genome Indexing**: `--genomeChrBinNbits`, etc.
6. **Splice Junctions Database**: `--sjdbGTFfile`, `--sjdbOverhang`.
7. **Variation**: `--varVCFfile`.
8. **Input Files**: `--readFilesIn`, etc.
9. **Read Parameters**: e.g., clipping, strand.
10. **Limits**: memory, buffers.
11. **General Output**: `--outFileNamePrefix`, etc.
12. **SAM/BAM Output**: `--outSAMtype`, `--outSAMattributes`.
13. **BAM Processing**: e.g. `--bamRemoveDuplicatesType`.
14. **Output Wiggle**: bedGraph/wiggle tracks.
15. **Filtering**: `--outFilterType`, `--outFilterMultimapNmax`.
16. **Splice-Junction Filtering**: `--outSJfilter*`.
17. **Scoring**: gap penalties.
18. **Alignments/Seeding**: `--alignIntronMin`, etc.
19. **Paired-End**: overlap merges.
20. **Windows/Anchors**: binning parameters.
21. **Chimeric**: `--chimOutType`, etc.
22. **Quantification**: `--quantMode`, `--quantTranscriptomeBan`.
23. **2-pass**: `--twopassMode`.
24. **WASP**: `--waspOutputMode`.
25. **STARsolo**: single-cell.

Defaults generally suffice, but advanced users can customize alignment scoring, filtering, shared-memory usage, chimeric detection, etc.  

---

### Summary

1. **Generate genome indexes**: runMode = genomeGenerate with FASTA + (optional) GTF.
2. **Map reads**: supply genomeDir, read files, possibly specifying on-the-fly annotations.
3. **Outputs**: logs, alignments (SAM/BAM), splice junctions (SJ.out.tab), chimeric reads, etc.
4. **Chimeric/fusions**: `--chimSegmentMin` > 0.
5. **Transcriptome**: `--quantMode TranscriptomeSAM` for transcriptome-based BAM.
6. **Gene counts**: `--quantMode GeneCounts`.
7. **2-pass mapping**: improved novel splice detection.
8. **Overlapping PE**: merges if mates overlap.
9. **Variants/WASP**: optional to tag personal SNPs or filter allele-specific reads.
10. **STARsolo**: droplet-based single-cell analysis.

This streamlined reference should help you efficiently configure and run STAR for standard RNA-seq, single-cell, fusion detection, or other specialized tasks.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
