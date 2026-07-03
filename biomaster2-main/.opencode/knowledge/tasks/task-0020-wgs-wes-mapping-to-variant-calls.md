---
id: task-0020
title: WGS/WES Mapping to Variant Calls
summary: '# WGS/WES Mapping to Variant Calls ## Overview Typical DNA sequence analysis
  involves three main phases: **Mapping**, **Improvement**, and **Variant Calling**.
  Below is a common workflow illustrating these steps for W...'
keywords:
- samtools
- WGS
- WES Mapping to Variant Calls
- '# WGS'
- '## Overview

  Typical DNA sequence analysis involves three main phases: **Mapping**'
- '**Improvement**'
- and **Variant Calling**. Below is a common workflow illustrating these steps for
  Whole Genome Sequencing (WGS) or Whole Exome Sequencing (WES)
- '## 1. Mapping'
- 1. **Reference Preparation**
- '```bash'
- bwa index <ref.fa>
- '```'
- Prepares a Burrows–Wheeler Transform (BWT) index
- required for BWA
- 2. **Aligning Reads with BWA-MEM**
- bwa mem -R '@RG\tID:foo\tSM:bar\tLB:library1' <ref.fa> <read1.fq> <read2.fq> > lane.sam
- The `-R` flag attaches read-group metadata (e.g
- sample name
- library). This data is crucial for downstream tools
- Output is in SAM format
- 3. **Fixmate**
- samtools fixmate -O bam <lane.sam> <lane_fixmate.bam>
- Cleans up pairing flags
- ensuring consistent FLAG and mate info
- 4. **Sort**
- samtools sort -O bam -o <lane_sorted.bam> -T <
- tmp
- lane_temp> <lane_fixmate.bam>
- Converts name-collated BAM to coordinate-sorted BAM for downstream steps
- '## 2. Improvement'
- '### 2.1 Indel Realignment (GATK)'
- Misalignment around INDELs can cause false
- BWA
path: .opencode/knowledge/tasks/task-0020-wgs-wes-mapping-to-variant-calls.md
origin_source: samtools
origin_page: 21
source_entry_index: 16
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: samtools
---

# WGS/WES Mapping to Variant Calls

## One-line description

# WGS/WES Mapping to Variant Calls ## Overview Typical DNA sequence analysis involves three main phases: **Mapping**, **Improvement**, and **Variant Calling**. Below is a common workflow illustrating these steps for W...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `samtools`
- Origin page: `21`
- Source entry index: `16`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0020`
- Analysis/tool category: `samtools`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
# WGS/WES Mapping to Variant Calls

## Overview
Typical DNA sequence analysis involves three main phases: **Mapping**, **Improvement**, and **Variant Calling**. Below is a common workflow illustrating these steps for Whole Genome Sequencing (WGS) or Whole Exome Sequencing (WES).

---

## 1. Mapping

1. **Reference Preparation**:
   ~~~bash
   bwa index <ref.fa>
   ~~~
   - Prepares a Burrows–Wheeler Transform (BWT) index, required for BWA.

2. **Aligning Reads with BWA-MEM**:
   ~~~bash
   bwa mem -R '@RG\tID:foo\tSM:bar\tLB:library1' <ref.fa> <read1.fq> <read2.fq> > lane.sam
   ~~~
   - The `-R` flag attaches read-group metadata (e.g., sample name, library). This data is crucial for downstream tools.
   - Output is in SAM format.

3. **Fixmate**:
   ~~~bash
   samtools fixmate -O bam <lane.sam> <lane_fixmate.bam>
   ~~~
   - Cleans up pairing flags, ensuring consistent FLAG and mate info.

4. **Sort**:
   ~~~bash
   samtools sort -O bam -o <lane_sorted.bam> -T </tmp/lane_temp> <lane_fixmate.bam>
   ~~~
   - Converts name-collated BAM to coordinate-sorted BAM for downstream steps.

---

## 2. Improvement

### 2.1 Indel Realignment (GATK)

Misalignment around INDELs can cause false variant calls. The GATK realignment step includes two commands:

~~~bash
# Step 1: Identify intervals needing realignment
java -Xmx2g -jar GenomeAnalysisTK.jar -T RealignerTargetCreator \
  -R <ref.fa> -I <lane.bam> -o <lane.intervals> --known <Mills1000G.b38.vcf>

# Step 2: Realign around those intervals
java -Xmx4g -jar GenomeAnalysisTK.jar -T IndelRealigner -R <ref.fa> \
  -I <lane.bam> -targetIntervals <lane.intervals> \
  --known <Mills1000G.b38.vcf> -o <lane_realigned.bam>
~~~

### 2.2 Base Quality Score Recalibration (GATK BQSR)

Reduces machine- or run-specific biases by adjusting base quality scores.

~~~bash
# Analyze covariates
java -Xmx4g -jar GenomeAnalysisTK.jar -T BaseRecalibrator \
  -R <ref.fa> -knownSites <dbsnp_142.b38.vcf> \
  -I <lane.bam> -o <lane_recal.table>

# Apply recalibration
java -Xmx2g -jar GenomeAnalysisTK.jar -T PrintReads -R <ref.fa> \
  -I <lane.bam> --BQSR <lane_recal.table> -o <lane_recal.bam>
~~~

### 2.3 Marking Duplicates & Merging Libraries

1. **Mark Duplicates**:
   ~~~bash
   java -Xmx2g -jar MarkDuplicates.jar VALIDATION_STRINGENCY=LENIENT \
     INPUT=<lane_1.bam> INPUT=<lane_2.bam> \
     OUTPUT=<library.bam>
   ~~~
   - Marks PCR/optical duplicates.

2. **Merge** libraries into a single sample-level BAM:
   ~~~bash
   samtools merge <sample.bam> <library1.bam> <library2.bam> <library3.bam>
   samtools index <sample.bam>
   ~~~

3. **(Optional) Realign Once More**:
   ~~~bash
   java -Xmx2g -jar GenomeAnalysisTK.jar -T RealignerTargetCreator ...
   java -Xmx4g -jar GenomeAnalysisTK.jar -T IndelRealigner ...
   samtools index <sample_realigned.bam>
   ~~~

---

## 3. Variant Calling

### 3.1 Generating BCF/VCF with bcftools

`mpileup` is used to gather per-base data, and `bcftools call` calls variants:

~~~bash
# One-step approach using a pipe
bcftools mpileup -Ou -f <ref.fa> <sample1.bam> <sample2.bam> <sample3.bam> | \
  bcftools call -vmO z -o <study.vcf.gz>
~~~

Alternatively, two-step:
~~~bash
# Step 1: produce BCF
bcftools mpileup -Ob -o <study.bcf> -f <ref.fa> <sample1.bam> <sample2.bam> <sample3.bam>

# Step 2: call variants
bcftools call -vmO z -o <study.vcf.gz> <study.bcf>
~~~

### 3.2 VCF Indexing & Statistics

~~~bash
tabix -p vcf <study.vcf.gz>

bcftools stats -F <ref.fa> -s - <study.vcf.gz> > <study.vcf.gz.stats>
mkdir plots
plot-vcfstats -p plots/ <study.vcf.gz.stats>
~~~

### 3.3 Filtering

~~~bash
bcftools filter -O z -o <study_filtered.vcf.gz> -s LOWQUAL \
  -i'%QUAL>10' <study.vcf.gz>
~~~

Filtering strategies depend heavily on the study’s goals, data quality, and coverage.

---

## Key Points
1. **Mapping**: Use BWA-MEM (index reference, align reads, fixmate, sort).
2. **Improvement**: Realign around indels, recalibrate base qualities, mark duplicates, and merge.
3. **Variant Calling**: Generate pileup and call variants (bcftools), index VCF, gather stats, and filter.
4. **Read Group Info** (`@RG`): Ensure correct `ID`, `SM`, and `LB` for GATK/bcftools compatibility.
5. **QC & Filtering**: Visualize with IGV, review alignment stats, apply appropriate variant filters.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
