---
id: task-0024
title: GO/KEGG enrichment analysis First, install the required packages.
summary: 'GO/KEGG enrichment analysis First, install the required packages. #source("https://bioconductor.org/biocLite.R")
  #biocLite("DOSE") #biocLite("topGO") #biocLite("clusterProfiler") #biocLite("pathview")
  Load the package...'
keywords:
- clusterprofiler
- GO
- KEGG enrichment analysis
- KEGG enrichment analysis First
- install the required packages
- '#source("https'
- bioconductor.org
- 'biocLite.R")

  #biocLite("DOSE")

  #biocLite("topGO")

  #biocLite("clusterProfiler")

  #biocLite("pathview")'
- Load the packages
- 'library(DOSE)

  library(org.Hs.eg.db)

  library(topGO)

  library(clusterProfiler)

  library(pathview)'
- Import the data. The raw data is a gene list with one column (with a header)
- data <- read.table("gene.list"
- 'header=TRUE)

  data$GeneName <- as.character(data$GeneName)'
- Convert gene names using org.Hs.eg.db
- transID = bitr(data$GeneName
- fromType = "SYMBOL"
- toType = c("ENSEMBL"
- '"ENTREZID")'
- 'OrgDb = "org.Hs.eg.db"

  )'
- Create folders to store the results
- 'dir.create("GO")

  dir.create("KEGG")'
- GO_CC annotation
- CC <- enrichGO(transID$ENTREZID
- '"org.Hs.eg.db"'
- keyType = "ENTREZID"
- ont = "CC"
- pvalueCutoff = 0.05
- pAdjustMethod = "BH"
- 'qvalueCutoff = 0.1

  )

  CC <- setReadable(CC'
- OrgDb = org.Hs.eg.db)
- svg(file = "
- GO_CC_Dotplot.svg"
- 'bg = "transparent")

  dotplot(CC'
- showCategory = 12
- colorBy = "pvalue"
- font.size = 8
- 'title = "GO_CC") # + theme(axis.text.y = element_text(angle = 45))

  dev.off()'
- GO_CC_Barplot.svg"
- bg = "transparent"
- clusterProfiler
path: .opencode/knowledge/tasks/task-0024-go-kegg-enrichment-analysis-first-install-the-required-packages.md
origin_source: GO/KEGG enrichment analysis
origin_page: 25
source_entry_index: 20
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: clusterprofiler
---

# GO/KEGG enrichment analysis First, install the required packages.

## One-line description

GO/KEGG enrichment analysis First, install the required packages. #source("https://bioconductor.org/biocLite.R") #biocLite("DOSE") #biocLite("topGO") #biocLite("clusterProfiler") #biocLite("pathview") Load the package...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `GO/KEGG enrichment analysis`
- Origin page: `25`
- Source entry index: `20`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0024`
- Analysis/tool category: `clusterprofiler`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
GO/KEGG enrichment analysis First, install the required packages.

#source("https://bioconductor.org/biocLite.R")
#biocLite("DOSE")
#biocLite("topGO")
#biocLite("clusterProfiler")
#biocLite("pathview")

Load the packages:

library(DOSE)
library(org.Hs.eg.db)
library(topGO)
library(clusterProfiler)
library(pathview)

Import the data. The raw data is a gene list with one column (with a header):

data <- read.table("gene.list", header=TRUE)
data$GeneName <- as.character(data$GeneName)

Convert gene names using org.Hs.eg.db:

transID = bitr(data$GeneName,
  fromType = "SYMBOL",
  toType = c("ENSEMBL", "ENTREZID"),
  OrgDb = "org.Hs.eg.db"
)

Create folders to store the results:

dir.create("GO")
dir.create("KEGG")

GO_CC annotation:

CC <- enrichGO(transID$ENTREZID,
  "org.Hs.eg.db",
  keyType = "ENTREZID",
  ont = "CC",
  pvalueCutoff = 0.05,
  pAdjustMethod = "BH",
  qvalueCutoff = 0.1
)
CC <- setReadable(CC, OrgDb = org.Hs.eg.db)

svg(file = "./GO/GO_CC_Dotplot.svg", bg = "transparent")
dotplot(CC, showCategory = 12, colorBy = "pvalue", font.size = 8, title = "GO_CC") # + theme(axis.text.y = element_text(angle = 45))
dev.off()

svg(file = "./GO/GO_CC_Barplot.svg", bg = "transparent")
barplot(CC, showCategory = 12, title = "GO_CC", font.size = 8)
dev.off()

svg(file = "./GO/GO_CC_Network.svg", bg = "transparent")
plotGOgraph(CC)
dev.off()

write.table(as.data.frame(CC@result), file = "./GO/GO_CC.xls", sep = "\t", row.names = F)

GO_MF annotation:

MF <- enrichGO(transID$ENTREZID, "org.Hs.eg.db", keyType = "ENTREZID", ont = "MF", pvalueCutoff = 0.05, pAdjustMethod = "BH", qvalueCutoff = 0.1)
MF <- setReadable(MF, OrgDb = org.Hs.eg.db)

svg(file = "./GO/GO_MF_Dotplot.svg", bg = "transparent")
dotplot(MF, showCategory = 12, colorBy = "pvalue", font.size = 8, title = "GO_MF") # + theme(axis.text.y = element_text(angle = 45))
dev.off()

svg(file = "./GO/GO_MF_Barplot.svg", bg = "transparent")
barplot(MF, showCategory = 12, title = "GO_MF", font.size = 8)
dev.off()

svg(file = "./GO/GO_MF_Network.svg", bg = "transparent")
plotGOgraph(MF)
dev.off()

write.table(as.data.frame(MF@result), file = "./GO/GO_MF.xls", sep = "\t", row.names = F)

GO_BP annotation:

BP <- enrichGO(transID$ENTREZID, "org.Hs.eg.db", keyType = "ENTREZID", ont = "BP", pvalueCutoff = 0.05, pAdjustMethod = "BH", qvalueCutoff = 0.1)
BP <- setReadable(BP, OrgDb = org.Hs.eg.db)

svg(file = "./GO/GO_BP_Dotplot.svg", bg = "transparent")
dotplot(BP, showCategory = 12, colorBy = "pvalue", font.size = 8, title = "GO_BP") # + theme(axis.text.y = element_text(angle = 45))
dev.off()

svg(file = "./GO/GO_BP_Barplot.svg", bg = "transparent")
barplot(BP, showCategory = 12, title = "GO_BP", font.size = 8)
dev.off()

svg(file = "./GO/GO_BP_Network.svg", bg = "transparent")
plotGOgraph(BP)
dev.off()

write.table(as.data.frame(BP@result), file = "./GO/GO_BP.xls", sep = "\t", row.names = F)

KEGG annotation:

kegg <- enrichKEGG(transID$ENTREZID, organism = "hsa", pvalueCutoff = 0.05, pAdjustMethod = "BH", qvalueCutoff = 0.1)
kegg <- setReadable(kegg, OrgDb = org.Hs.eg.db, keytype = "ENTREZID")

svg(file = "./KEGG/KEGG_Dotplot.svg", bg = "transparent")
dotplot(kegg, showCategory = 12, colorBy = "pvalue", font.size = 8, title = "KEGG") # + theme(axis.text.y = element_text(angle = 45))
dev.off()

svg(file = "./KEGG/KEGG_Barplot.svg", bg = "transparent")
barplot(kegg, showCategory = 12, title = "KEGG", font.size = 8)
dev.off()

write.table(as.data.frame(kegg@result), file = "./KEGG/kegg.xls", sep = "\t", row.names = F)

Create a directory for KEGG pathway maps:

dir.create("./KEGG/MAP")
kegg_df = as.data.frame(kegg)

for(i in kegg_df$ID){
  pathview(gene.data = transID$ENTREZID,
           pathway.id = i,
           species = "hsa",
           kegg.native = TRUE,
           kegg.dir = "./KEGG/MAP"
  )
}

print("TASK DONE")
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
