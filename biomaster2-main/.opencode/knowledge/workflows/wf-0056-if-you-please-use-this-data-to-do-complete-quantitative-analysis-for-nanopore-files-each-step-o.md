---
id: wf-0056
title: 'IF you: Please use this data to do complete quantitative analysis for nanopore
  files. Each step o...'
summary: 'IF you: Please use this data to do complete quantitative analysis for nanopore
  files. Each step of the process has been organized into specific executable scripts(13
  steps). The bash tool is used. All the scripts are...'
keywords:
- nanopore
- workflow
- 'IF you: Please use this data to do complete quantitative analysis for nanopore
  files. Each step o'
- 'IF you: Please use this data to do complete quantitative'
- analysis for nanopore files. Each step of the process has been organized into specific
  executable scripts(13 steps). The bash tool is used. All the scripts are in the
  folder
- scripts
- The steps must be generated in strict order
- '1. basecaller.sh:

  do simplex basecalling'
- 'Input : a file folder containing nanopore files in fast5'
- 'pod5 format

  Output : a bam file.

  Usage

  Run the following in the container

  '
- 'basecaller.sh <pod5dir> <out>

  # pod5dir: Path of a file folder containing nanopore files in fast5'
- 'pod5 format.

  # out : name of output bam file'
- 2. basecall_sum.sh
- output a tab-separated file with read level sequencing information from the bam
  file generated during basecalling
- 'Input : basecaller’s output bam file'
- 'Output : a summary tsv file.

  Usage

  Run the following in the container

  '
- basecall_sum.sh <bam> <out>
- '# bam : basecaller’s output bam file.

  # out : name of output tsv file.

  3. bam2fq.sh'
- 'transfer bam file to fastq format.

  Input : basecaller’s output bam file'
- 'Output : a fastq file.

  Usage

  Run the following in the container

  '
- bam2fq.sh <numcore> <bam> <out>
- '# numcore : number of threads'
path: .opencode/knowledge/workflows/wf-0056-if-you-please-use-this-data-to-do-complete-quantitative-analysis-for-nanopore-files-each-step-o.md
origin_source: workflow
origin_page: 56
source_entry_index: 46
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: nanopore
---

# IF you: Please use this data to do complete quantitative analysis for nanopore files. Each step o...

## One-line description

IF you: Please use this data to do complete quantitative analysis for nanopore files. Each step of the process has been organized into specific executable scripts(13 steps). The bash tool is used. All the scripts are...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `56`
- Source entry index: `46`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0056`
- Analysis/tool category: `nanopore`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
IF you: Please use this data to do complete quantitative  analysis for nanopore files. Each step of the process has been organized into specific executable scripts(13 steps). The bash tool is used. All the scripts are in the folder ./scripts/. The steps must be generated in strict order. 
1. basecaller.sh:
do simplex basecalling. 
Input : a file folder containing nanopore files in fast5/pod5 format
Output : a bam file.
Usage
Run the following in the container
./scripts/basecaller.sh <pod5dir> <out>
# pod5dir: Path of a file folder containing nanopore files in fast5/pod5 format.
# out : name of output bam file.
 2. basecall_sum.sh:
 output a tab-separated file with read level sequencing information from the bam file generated during basecalling. 
Input : basecaller’s output bam file 
Output : a summary tsv file.
Usage
Run the following in the container
./scripts/basecall_sum.sh <bam> <out>  
# bam : basecaller’s output bam file.
# out : name of output tsv file.
3. bam2fq.sh:
 transfer bam file to fastq format.
Input : basecaller’s output bam file 
Output : a fastq file.
Usage
Run the following in the container
./scripts/bam2fq.sh <numcore> <bam> <out>  
# numcore : number of threads
# bam : basecaller’s output bam file.
# out : name of output fastq file. 
4. raw_plot.sh:
 plot QC imformation from the basecall fastq file(raw_plot).
Input : basecall fastq file 
Output : sevaral png file and a report html file containing QC imformation.
Usage
Run the following in the container
./scripts/raw_plot.sh <fastq> <outdir>  
# fastq : basecall fastq file.
# outdir : directory to store QC imformation files. 
5. filter.sh:
 filter low_quality reads in basecall fastq file.
Input : basecall fastq file 
Output : a filtered fastq file.
Usage
Run the following in the container
./scripts/filter.sh <fastq> <out>  
# fastq : basecall fastq file.
# out : name of filtered fastq file. 
6. host_removal.sh:
 remove host gene in filtered fastq file.
Input : filtered fastq file 
Output : a bam file.
Usage
Run the following in the container
./scripts/host_removal.sh <fa> <fastq> <out>  # fa:  host gene fasta file.
# fastq : filtered fastq file.
# out : name of output bam file. 
7. bam2fq.sh:
 transfer bam file to fastq format.
Input : host-gene-removal bam file 
Output : a fastq file.
Usage
Run the following in the container
./scripts/bam2fq.sh <numcore> <bam> <out>  
# numcore : number of threads
# bam : host-gene-removal bam file.
# out : name of output fastq file.  
8. filtered_plot.sh:
 plot QC imformation from the host-gene-removal fastq file(filtered_plot).
Input : host-gene-removal fastq file 
Output : sevaral png file and a report html file containing QC imformation.
Usage
Run the following in the container
./scripts/filtered_plot.sh <fastq> <outdir>  
# fastq : host-gene-removal fastq file.
# outdir : directory to store QC imformation files.  
9. map_fastq2_ref.sh:
Map host-gene-removal fastq file to reference genome(fa file). Generates sam file.
Input : a  host-gene-removal fastq file and a reference genome fa file
Output : a sam file 
Usage
Run the following in the container.
./scripts/map_fastq2_ref.sh <fq> <output_sam> <ref> <nThreads>
# fq :  host-gene-removal fastq file.
# output_sam : name of output sam file.
# ref : reference genome fa file
# nThreads : number of threads
 10. indexbam.sh:
index bam and generate statistics - coverage, error rate, number of reads.
Input: a sam file
Output: a sorted bam file
Usage
Run the following in the container
./scripts/indexbam.sh <nthread> <input_sam> <outputbam>
# nthread : number of threads to use
# input_sam : an input sam file
# outputbam : name of output bam file
 
11. alignment_stats.sh:
Get the alignment_stats report.
Input : the sorted bam file
Output : a alignment_stats txt file 
Usage
Run the following in the container.
./scripts/alignment_stats.sh <bam> <out> 
# bam :  the sorted bam file.
# out : name of alignment_stats report txt file.
# ref : reference genome fa file
# nThreads : number of threads  
12. quantififation.sh:
Generate transcripts and  gene_abundance tsv file from the sorted bam file.
Input : the sorted bam file
Output : a transcripts gtf file and a gene_abundance tsv file. 
Usage
Run the following in the container.
./scripts/quantififation.sh <bam> <transcripts_gtf> <out> 
# bam :  the sorted bam file. 
# transcripts_gtf :  name of output transcripts gtf file.
# out : name of output gene_abundance tsv file.
13. result_sum.sh:
 make a new diroctory to store all the readable result. 
Input : path to raw_plot dir, filterd_plot dir, alignment_stats report txt file, gene_abundance tsv file and basecall summary tsv file, a new diroctory path. 
Usage
Run the following in the container.
./scripts/result_sum.sh <dir1> <dir2> <alignment_stats> <gene_abundance> <basecall> <report_dir>
# dir1 : path to raw_plot QC imformation dir 
# dir2 : path to filtered_plot QC imformation dir
# alignment_stats : path to alignment_stats report txt file.
# gene_abundance : path to gene_abundance tsv file.
# basecall : path to  basecall summary tsv file. .
# report_dir : path of new diroctory to store the results.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
