---
id: task-0040
title: To run PureCLIP in basic mode, it requires BAM and BAI files, the reference
  genome and a specifie...
summary: 'To run PureCLIP in basic mode, it requires BAM and BAI files, the reference
  genome and a specified output file: ```bash pureclip -i aligned.prepro.R2.bam -bai
  aligned.prepro.R2.bam.bai -g ref.hg19.fa -iv ''chr1;chr2;ch...'
keywords:
- pureclip
- To run PureCLIP in basic mode
- it requires BAM and BAI files
- the reference genome and a specifie
- the reference genome and a specified output file
- '```bash

  pureclip -i aligned.prepro.R2.bam -bai aligned.prepro.R2.bam.bai -g ref.hg19.fa
  -iv ''chr1'
- chr2
- chr3
- ''' -nt 10 -o PureCLIP.crosslink_sites.bed

  ```'
- With `-iv` the chromosomes (or transcripts) can be specified that will be used to
  learn the parameters of PureCLIP’s HMM. This reduces the memory consumption and
  runtime
- '### Input Control Mode

  To run PureCLIP with input control data'
- ''' -nt 10 -o PureCLIP.crosslink_sites

  ```'
- '### CL-Motif Scores

  To address crosslinking sequence bias'
- CL-motif scores can be incorporated
- '#### Compute CL-Motif Scores:

  ```bash

  wget -O motifs.txt https'
- raw.githubusercontent.com
- skrakau
- PureCLIP_data
- master
- common_CL-motifs
- 'dreme.w10.k4.txt

  wget -O motifs.xml https'
- 'dreme.w10.k4.xml

  compute_CLmotif_scores.sh ref.hg19.fa aligned.prepro.R2.bam motifs.xml motifs.txt
  fimo_clmotif_occurences.bed

  ```'
- '#### Run PureCLIP with CL-Motif:

  ```bash

  pureclip -i aligned.pr'
path: .opencode/knowledge/tasks/task-0040-to-run-pureclip-in-basic-mode-it-requires-bam-and-bai-files-the-reference-genome-and-a-specifie.md
origin_source: pureclip
origin_page: 41
source_entry_index: 36
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: pureclip
---

# To run PureCLIP in basic mode, it requires BAM and BAI files, the reference genome and a specifie...

## One-line description

To run PureCLIP in basic mode, it requires BAM and BAI files, the reference genome and a specified output file: ```bash pureclip -i aligned.prepro.R2.bam -bai aligned.prepro.R2.bam.bai -g ref.hg19.fa -iv 'chr1;chr2;ch...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `pureclip`
- Origin page: `41`
- Source entry index: `36`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0040`
- Analysis/tool category: `pureclip`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
To run PureCLIP in basic mode, it requires BAM and BAI files, the reference genome and a specified output file:

~~~bash
pureclip -i aligned.prepro.R2.bam -bai aligned.prepro.R2.bam.bai -g ref.hg19.fa -iv 'chr1;chr2;chr3;' -nt 10 -o PureCLIP.crosslink_sites.bed
~~~

With `-iv` the chromosomes (or transcripts) can be specified that will be used to learn the parameters of PureCLIP’s HMM. This reduces the memory consumption and runtime. 

### Input Control Mode
To run PureCLIP with input control data:

~~~bash
pureclip -i aligned.prepro.R2.bam -bai aligned.prepro.R2.bam.bai -g ref.hg19.fa -iv 'chr1;chr2;chr3;' -nt 10 -o PureCLIP.crosslink_sites
~~~

### CL-Motif Scores
To address crosslinking sequence bias, CL-motif scores can be incorporated.

#### Compute CL-Motif Scores:
~~~bash
wget -O motifs.txt https://raw.githubusercontent.com/skrakau/PureCLIP_data/master/common_CL-motifs/dreme.w10.k4.txt
wget -O motifs.xml https://raw.githubusercontent.com/skrakau/PureCLIP_data/master/common_CL-motifs/dreme.w10.k4.xml
compute_CLmotif_scores.sh ref.hg19.fa aligned.prepro.R2.bam motifs.xml motifs.txt fimo_clmotif_occurences.bed
~~~

#### Run PureCLIP with CL-Motif:
~~~bash
pureclip -i aligned.prepro.R2.bam -bai aligned.prepro.R2.bam.bai -g ref.hg19.fa -o PureCLIP.crosslink_sites.cov_CLmotifs.bed -nt 10 -iv 'chr1;chr2;chr3;' -nim 4 -fis fimo_clmotif_occurences.bed
~~~

### Output
- **Crosslink sites**: BED6 with chr, start, end, state, score, strand.
- **Binding regions** (optional): merged crosslink sites with scores if `-or` and `-dm` provided.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
