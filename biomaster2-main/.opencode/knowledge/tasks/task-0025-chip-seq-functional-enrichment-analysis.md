---
id: task-0025
title: CHIP-seq Functional enrichment analysis
summary: CHIP-seq Functional enrichment analysis Once we have obtained the annotated
  nearest genes, we can perform functional enrichment analysis to identify predominant
  biological themes among these genes by incorporating bio...
keywords:
- clusterprofiler
- CHIP-seq Functional enrichment
- CHIP-seq Functional enrichment analysis
- 'CHIP-seq Functional enrichment analysis

  Once we have obtained the annotated nearest genes'
- we can perform functional enrichment analysis to identify predominant biological
  themes among these genes by incorporating biological knowledge provided by biological
  ontologies. For instance
- Gene Ontology (GO) (Ashburner et al. 2000) annotates genes to biological processes
- molecular functions
- and cellular components in a directed acyclic graph structure
- Kyoto Encyclopedia of Genes and Genomes (KEGG) (Kanehisa et al. 2004) annotates
  genes to pathways
- Disease Ontology (DO) (Schriml et al. 2011) annotates genes with human disease association
- and Reactome (Croft et al. 2013) annotates genes to pathways and reactions
- ChIPseeker also provides a function
- seq2gene
- for linking genomic regions to genes in a many-to-many mapping. It considers the
  host gene (exon
- intron)
- promoter region
- and flanking gene from intergenic regions that may be under cis-regulation. This
  function is designed to link both coding and non-coding genomic regions to coding
  genes and facilitate functional analysis
- Enrichment analysis is a widely used approach to identify biological themes. Several
  Bioconductor packag
- clusterProfiler
path: .opencode/knowledge/tasks/task-0025-chip-seq-functional-enrichment-analysis.md
origin_source: CHIP-seq Functional enrichment
origin_page: 26
source_entry_index: 21
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: clusterprofiler
---

# CHIP-seq Functional enrichment analysis

## One-line description

CHIP-seq Functional enrichment analysis Once we have obtained the annotated nearest genes, we can perform functional enrichment analysis to identify predominant biological themes among these genes by incorporating bio...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `CHIP-seq Functional enrichment`
- Origin page: `26`
- Source entry index: `21`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0025`
- Analysis/tool category: `clusterprofiler`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
CHIP-seq Functional enrichment analysis
Once we have obtained the annotated nearest genes, we can perform functional enrichment analysis to identify predominant biological themes among these genes by incorporating biological knowledge provided by biological ontologies. For instance, Gene Ontology (GO) (Ashburner et al. 2000) annotates genes to biological processes, molecular functions, and cellular components in a directed acyclic graph structure; Kyoto Encyclopedia of Genes and Genomes (KEGG) (Kanehisa et al. 2004) annotates genes to pathways; Disease Ontology (DO) (Schriml et al. 2011) annotates genes with human disease association; and Reactome (Croft et al. 2013) annotates genes to pathways and reactions.

ChIPseeker also provides a function, seq2gene, for linking genomic regions to genes in a many-to-many mapping. It considers the host gene (exon/intron), promoter region, and flanking gene from intergenic regions that may be under cis-regulation. This function is designed to link both coding and non-coding genomic regions to coding genes and facilitate functional analysis.

Enrichment analysis is a widely used approach to identify biological themes. Several Bioconductor packages have been developed to investigate whether the number of selected genes associated with a particular biological term is larger than expected. These include DOSE (Yu et al. 2015) for Disease Ontology, ReactomePA for Reactome pathway analysis, and clusterProfiler (Yu et al. 2012) for Gene Ontology and KEGG enrichment analysis.

library(ReactomePA)

pathway1 <- enrichPathway(as.data.frame(peakAnno)$geneId)
head(pathway1, 2)
##                          ID        Description GeneRatio   BgRatio RichFactor
## R-HSA-9830369 R-HSA-9830369 Kidney development    19/499  46/11146  0.4130435
## R-HSA-9758941 R-HSA-9758941       Gastrulation    27/499 125/11146  0.2160000
##               FoldEnrichment    zScore       pvalue     p.adjust       qvalue
## R-HSA-9830369       9.226017 12.102741 2.252177e-14 2.360281e-11 2.351747e-11
## R-HSA-9758941       4.824721  9.309385 5.773075e-12 3.025091e-09 3.014153e-09
##                                                                                                                                                   geneID
## R-HSA-9830369                                          2625/5076/7490/652/6495/2303/3975/6928/10736/5455/7849/3237/6092/2122/255743/2296/3400/28514/2138
## R-HSA-9758941 5453/5692/5076/5080/7546/3169/652/5015/2303/5717/3975/2627/5714/344022/7849/5077/2637/7022/8320/7545/6657/4487/51176/2296/28514/2626/64321
##               Count
## R-HSA-9830369    19
## R-HSA-9758941    27
gene <- seq2gene(peak, tssRegion = c(-1000, 1000), flankDistance = 3000, TxDb = txdb)
pathway2 <- enrichPathway(gene)
head(pathway2, 2)
##                          ID        Description GeneRatio   BgRatio RichFactor
## R-HSA-9830369 R-HSA-9830369 Kidney development    17/408  46/11146  0.3695652
## R-HSA-9758941 R-HSA-9758941       Gastrulation    24/408 125/11146  0.1920000
##               FoldEnrichment    zScore       pvalue     p.adjust       qvalue
## R-HSA-9830369      10.096014 12.049721 1.806589e-13 1.765037e-10 1.709604e-10
## R-HSA-9758941       5.245176  9.303549 1.834131e-11 8.959732e-09 8.678338e-09
##                                                                                                                                    geneID
## R-HSA-9830369                                      2625/5076/3227/652/6495/2303/3975/3237/6092/2122/255743/7490/6928/7849/5455/2296/28514
## R-HSA-9758941 5453/5692/5076/7546/3169/652/2303/5717/3975/2627/5714/344022/2637/8320/7545/7020/2626/5080/5015/7849/51176/2296/64321/28514
##               Count
## R-HSA-9830369    17
## R-HSA-9758941    24
dotplot(pathway2)
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
