---
id: task-0026
title: DESeq2 Differential Expression Analysis Tutorial
summary: '# DESeq2 Differential Expression Analysis Tutorial DESeq2 is an R package
  designed for normalization, visualization, and differential expression analysis
  of high-dimensional count data. It uses empirical Bayes techniq...'
keywords:
- deseq2
- DESeq2
- DESeq2 Differential Expression Analysis Tutorial
- '# DESeq2 Differential Expression Analysis Tutorial'
- DESeq2 is an R package designed for normalization
- visualization
- and differential expression analysis of high-dimensional count data. It uses empirical
  Bayes techniques to estimate log₂ fold changes and dispersion priors
- and then calculates their posterior values. Originally released in 2014 by Professor
  Michael Love from the University of North Carolina
- DESeq2 continues to be updated and is one of the most widely used tools for differential
  expression analysis
- '## 1. Installation'
- '### In R'
- Run the following commands in the R console or RStudio (for R version 4.2 and above)
- '```r

  if (!require("BiocManager"'
- quietly = TRUE))
- install.packages("BiocManager")
- 'BiocManager::install("DESeq2")

  ```'
- '### In a conda Environment'
- Use the following command
- '```bash

  conda install -c bioconda bioconductor-deseq2

  ```'
- '## 2. Workflow Overview'
- This tutorial covers the following steps
- 1. **Data Import and Preprocessing**
- Load the count matrix (e.g
- '`gene_count_matrix.csv`)'
- Perform data cleaning
- such as fixing gene names with extra information and removing invalid rows
- Filter out genes with low expression
path: .opencode/knowledge/tasks/task-0026-deseq2-differential-expression-analysis-tutorial.md
origin_source: DESeq2
origin_page: 27
source_entry_index: 22
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-conda
tool: deseq2
---

# DESeq2 Differential Expression Analysis Tutorial

## One-line description

# DESeq2 Differential Expression Analysis Tutorial DESeq2 is an R package designed for normalization, visualization, and differential expression analysis of high-dimensional count data. It uses empirical Bayes techniq...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `DESeq2`
- Origin page: `27`
- Source entry index: `22`
- Source subindex: `1`
- Canonical skill: `exec-conda`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-conda`
- Registry ID: `task-0026`
- Analysis/tool category: `deseq2`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
# DESeq2 Differential Expression Analysis Tutorial

DESeq2 is an R package designed for normalization, visualization, and differential expression analysis of high-dimensional count data. It uses empirical Bayes techniques to estimate log₂ fold changes and dispersion priors, and then calculates their posterior values. Originally released in 2014 by Professor Michael Love from the University of North Carolina, DESeq2 continues to be updated and is one of the most widely used tools for differential expression analysis.

---

## 1. Installation

### In R

Run the following commands in the R console or RStudio (for R version 4.2 and above):

~~~r
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

BiocManager::install("DESeq2")
~~~

### In a conda Environment

Use the following command:

~~~bash
conda install -c bioconda bioconductor-deseq2
~~~

---

## 2. Workflow Overview

This tutorial covers the following steps:

1. **Data Import and Preprocessing**: 
   - Load the count matrix (e.g., `gene_count_matrix.csv`).
   - Perform data cleaning, such as fixing gene names with extra information and removing invalid rows.
   - Filter out genes with low expression.

2. **Differential Expression Analysis**: 
   - Create group and sample information.
   - Build a `DESeqDataSet` object from the count matrix.
   - Perform normalization and statistical testing.
   - Extract and sort results by p-value and log₂ fold change, and filter significant genes.

3. **Visualization**: 
   - Display expression for a single gene.
   - Generate a heatmap of differentially expressed genes.
   - Create a volcano plot to visualize overall differential expression.

---

## 3. Data Import and Preprocessing

First, load the required R packages and read the expression count matrix. Assume the file `gene_count_matrix.csv` contains gene IDs as row names.

~~~r
# Load necessary libraries
library(DESeq2)
library(pheatmap)  # For heatmaps
library(ggplot2)   # For plotting

# Read the count matrix (set your working directory accordingly)
countData <- as.matrix(read.csv("gene_count_matrix.csv", row.names = "gene_id"))
~~~

**Note:**

- The gene names might include extra information, and there could be invalid rows. Use data cleaning functions in R as needed.
- Since many genes might show no expression (or zero counts), you can filter out these low-expression genes:

~~~r
countData <- countData[rowMeans(countData) > 1, ]  # Remove genes with very low expression
~~~

---

## 4. Differential Expression Analysis

### 4.1 Preparing Group Information

Assume you have three control samples and three osmotic-treated samples. Create a factor vector for the condition and a sample information data frame (`colData`) with row names matching the columns in `countData`.

~~~r
condition <- factor(c(rep("control", 3), rep("osmotic", 3)))
colData <- data.frame(row.names = colnames(countData), condition)
~~~

### 4.2 Creating the DESeqDataSet Object

Use the `DESeqDataSetFromMatrix` function to create the object:

~~~r
dds <- DESeqDataSetFromMatrix(countData = countData, colData = colData, design = ~ condition)
head(dds)  # View the structure of the DESeqDataSet
~~~

### 4.3 Normalization and Statistical Testing

Normalize the data and perform differential expression testing:

~~~r
dds1 <- DESeq(dds, fitType = 'mean', minReplicatesForReplace = 7, parallel = FALSE)
res <- results(dds1)
summary(res)
~~~

The output will display the number of upregulated and downregulated genes, along with counts for outliers and low-count genes.

### 4.4 Organizing and Filtering Results

Convert the results to a data frame, sort by p-value and log₂ fold change, and filter for significant genes (e.g., p-value < 0.05 and |log₂ fold change| ≥ 1):

~~~r
res1 <- data.frame(res, stringsAsFactors = FALSE, check.names = FALSE)
res1 <- res1[order(res1$pvalue, res1$log2FoldChange, decreasing = c(FALSE, TRUE)), ]

# Filter for upregulated and downregulated genes
res1_up <- res1[which(res1$log2FoldChange >= 1 & res1$pvalue < 0.05), ]
res1_down <- res1[which(res1$log2FoldChange <= -1 & res1$pvalue < 0.05), ]
res1_total <- rbind(res1_up, res1_down)
~~~

---

## 5. Visualization

### 5.1 Displaying a Single Gene's Expression

You can quickly visualize the expression of a specific gene using DESeq2's `plotCounts` function:

~~~r
plotCounts(dds1, gene = "AT4G38770", intgroup = "condition")
~~~

Alternatively, customize the plot using ggplot2:

~~~r
d <- data.frame(t(subset(countData, rownames(countData) == "AT4G38770")))
ggplot(d, aes(x = condition, y = AT4G38770, color = condition)) +
  geom_point(position = position_jitter(w = 0.2, h = 0)) +
  geom_text_repel(aes(label = rownames(d))) +
  theme_bw() +
  ggtitle("AT4G38770") +
  theme(plot.title = element_text(hjust = 0.5))
~~~

### 5.2 Creating a Heatmap

Use the pheatmap package to cluster and display the expression of differentially expressed genes:

~~~r
# Extract the differential genes from the count matrix
 df <- countData[intersect(rownames(countData), rownames(res1_total)), ]
 df2 <- as.matrix(df)
 pheatmap(df2,
          show_rownames = FALSE,
          show_colnames = TRUE,
          cluster_cols = FALSE,
          cluster_rows = TRUE,
          height = 10,
          scale = "row",
          fontsize = 10,
          angle_col = 45, 
          color = colorRampPalette(c("#8854d0", "#ffffff", "#fa8231"))(100),
          clustering_method = 'single'
 )
~~~

### 5.3 Drawing a Volcano Plot

Use ggplot2 to create a volcano plot that displays the log₂ fold changes against -log₁₀ (adjusted p-values):

~~~r
genes <- res1
# Assign colors based on upregulation, downregulation, or no significant change
 genes$color <- ifelse(genes$padj < 0.05 & abs(genes$log2FoldChange) >= 1,
                        ifelse(genes$log2FoldChange > 1, 'red', 'blue'),
                        'gray')
 color <- c(red = "red", gray = "gray", blue = "blue")

 p <- ggplot(genes, aes(log2FoldChange, -log10(padj), col = color)) +
   geom_point() +
   theme_bw() +
   scale_color_manual(values = color) +
   labs(x = "log2 (fold change)", y = "-log10 (q-value)") +
   geom_hline(yintercept = -log10(0.05), lty = 4, col = "grey", lwd = 0.6) +
   geom_vline(xintercept = c(-1, 1), lty = 4, col = "grey", lwd = 0.6) +
   theme(legend.position = "none",
         panel.grid = element_blank(),
         axis.title = element_text(size = 16),
         axis.text = element_text(size = 14)) +
   geom_text_repel(
     data = subset(genes, padj < 1e-100 & abs(genes$log2FoldChange) >= 10),
     aes(label = rownames(genes)),
     size = 5,
     box.padding = unit(0.35, "lines"),
     point.padding = unit(0.3, "lines")
   )
 p
~~~

---

## 6. A Complete DESeq2 Example in RStudio

Below is a complete example code that can be executed in RStudio:

~~~r
# Clear the workspace and set the working directory
rm(list = ls())
setwd('/XX/XX/XX')
if (!dir.exists('./01_DEGs')) {
  dir.create('./01_DEGs')
}
setwd('./01_DEGs/')

# Load necessary libraries
library(tidyverse)
library(DESeq2)

# Import the processed expression matrix (row names are gene symbols, columns are sample IDs)
dat <- read.csv('../../00_rawdata/GSE203346/dat.GSE203346_count.csv', check.names = FALSE, row.names = 1)

# Import the group information
colData <- read.csv('../../00_rawdata/GSE203346/group.GSE203346.csv')
colData$group <- factor(colData$group, levels = c("control", "disease"))
print(table(colData$group))
# Ensure the samples in the expression matrix match the group information
 dat <- dat[, colData$sample]

# Create the DESeqDataSet object
dds <- DESeqDataSetFromMatrix(countData = dat, colData = colData, design = ~ group)
# Filter out genes with low counts (genes with counts ≤ 1 in all samples)
dds <- dds[rownames(counts(dds)) > 1, ]
# Estimate size factors to normalize for sequencing depth
dds <- estimateSizeFactors(dds)

# Perform differential expression analysis
dds <- DESeq(dds)
res <- results(dds, contrast = c("group", "disease", "control"))
DEG <- as.data.frame(res)

# Add labels for differential expression (criteria: |log2FoldChange| ≥ 0.5 & p-value < 0.05)
DEG$change <- as.factor(
  ifelse(DEG$pvalue < 0.05 & abs(DEG$log2FoldChange) >= 0.5,
         ifelse(DEG$log2FoldChange > 0.5, 'Up', 'Down'), 'Not')
)
print(table(DEG$change))
DEG_write <- cbind(symbol = rownames(DEG), DEG)

# Filter for significantly differentially expressed genes
sig_diff <- subset(DEG, DEG$pvalue < 0.05 & abs(DEG$log2FoldChange) >= 0.5)
sig_diff_write <- cbind(symbol = rownames(sig_diff), sig_diff)

# Save the results
write.csv(DEG_write, file = 'DEG_all.csv')
write.csv(sig_diff_write, file = 'DEG_sig.csv')
~~~

**Explanation:**

- **Data Import:** The expression matrix and group information are imported, ensuring that the sample orders match.
- **DESeqDataSet Creation:** The count data, sample information, and experimental design (e.g., control vs. disease) are used to create a DESeqDataSet object.
- **Filtering & Normalization:** Lowly expressed genes are removed, and size factors are estimated to normalize the data.
- **Differential Expression:** The `DESeq` function performs the analysis, and results are extracted and organized.
- **Annotation & Saving:** Differential expression labels (Up, Down, Not) are added based on the criteria, and results are saved to CSV files for further analysis or visualization.

---

## 7. Summary

This tutorial provides a detailed guide for performing RNA-seq differential expression analysis using DESeq2. It covers:

- Data import and preprocessing to prepare count data for analysis.
- Normalization and statistical testing to identify differentially expressed genes.
- Visualization techniques including single-gene expression plots, heatmaps, and volcano plots.

By following these steps, researchers can construct a robust differential expression analysis pipeline and tailor parameters to suit their experimental design, ultimately drawing reliable biological conclusions.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
