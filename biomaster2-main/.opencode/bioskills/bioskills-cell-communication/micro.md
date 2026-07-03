## Setup & Database Loading

_modules: setup, database, ligand-receptor_

```r
library(CellChat)
library(Seurat)
library(nichenetr)
library(tidyverse)

# --- CellChat: attach ligand-receptor database ---
# Create CellChat object from Seurat with cell type labels
cellchat <- createCellChat(object = seurat_obj, group.by = 'cell_type')

# Choose species database
CellChatDB <- CellChatDB.human  # or CellChatDB.mouse
cellchat@DB <- CellChatDB

# Optional: subset to a signaling category (e.g. secreted signaling)
CellChatDB.use <- subsetDB(CellChatDB, search = 'Secreted Signaling')
cellchat@DB <- CellChatDB.use

# --- NicheNet: load precomputed networks ---
ligand_target_matrix <- readRDS('ligand_target_matrix.rds')
lr_network <- readRDS('lr_network.rds')
weighted_networks <- readRDS('weighted_networks.rds')
```

```python
import liana as li
import scanpy as sc

# --- LIANA: load AnnData with cell type labels ---
adata = sc.read_h5ad('adata.h5ad')
# 'cell_type' column in adata.obs is required; 'consensus' resource ships with LIANA
```

## CellChat Communication Inference

_modules: cellchat, communication-probability, aggregation_

```r
# Preprocessing: subset data and identify overexpressed genes/interactions
cellchat <- subsetData(cellchat)
cellchat <- identifyOverExpressedGenes(cellchat)
cellchat <- identifyOverExpressedInteractions(cellchat)

# Compute communication probability (trimean is conservative; use type='truncatedMean' for more interactions)
cellchat <- computeCommunProb(cellchat, type = 'triMean')
cellchat <- filterCommunication(cellchat, min.cells = 10)

# Infer pathway-level communication and aggregate into a network
cellchat <- computeCommunProbPathway(cellchat)
cellchat <- aggregateNet(cellchat)
```

## CellChat Visualization & Pathway Analysis

_modules: visualization, pathway-analysis, signaling-roles_

```r
# --- Network-level visualization ---
# Circle plots: interaction count and strength
netVisual_circle(cellchat@net$count, vertex.weight = groupSize, weight.scale = TRUE,
                 label.edge = FALSE, title.name = 'Number of interactions')
netVisual_circle(cellchat@net$weight, vertex.weight = groupSize, weight.scale = TRUE,
                 label.edge = FALSE, title.name = 'Interaction strength')

# Heatmap of interactions
netVisual_heatmap(cellchat, color.heatmap = 'Reds')

# Pathway-specific views (e.g. WNT)
netVisual_aggregate(cellchat, signaling = 'WNT', layout = 'circle')
netVisual_aggregate(cellchat, signaling = 'WNT', layout = 'chord')

# Bubble plot of L-R pairs from selected sources to targets
netVisual_bubble(cellchat, sources.use = c(1, 2), targets.use = c(3, 4),
                 remove.isolate = FALSE)

# Chord diagram for specific ligand-receptor pairs
netVisual_chord_gene(cellchat, sources.use = 1, targets.use = c(2, 3, 4),
                     lab.cex = 0.5, legend.pos.x = 10)

# --- Signaling role / pathway analysis ---
# Compute centrality on pathway-level network
cellchat <- netAnalysis_computeCentrality(cellchat, slot.name = 'netP')

# Signaling role heatmap per pathway
netAnalysis_signalingRole_heatmap(cellchat, signaling = c('WNT', 'TGFb', 'BMP'))

# Dominant senders/receivers
netAnalysis_signalingRole_scatter(cellchat)

# Rank and compare pathway contributions (with statistics)
rankNet(cellchat, mode = 'comparison', stacked = TRUE, do.stat = TRUE)
```

## CellChat Condition Comparison

_modules: comparison, differential, multi-condition_

```r
# Build per-condition CellChat objects (run full inference pipeline on each)
cellchat_ctrl <- createCellChat(subset(seurat_obj, condition == 'control'), group.by = 'cell_type')
cellchat_treat <- createCellChat(subset(seurat_obj, condition == 'treatment'), group.by = 'cell_type')
# ... apply subsetData / identifyOverExpressed* / computeCommunProb / computeCommunProbPathway / aggregateNet to both ...

# Merge for comparison
cellchat_list <- list(Control = cellchat_ctrl, Treatment = cellchat_treat)
cellchat_merged <- mergeCellChat(cellchat_list, add.names = names(cellchat_list))

# Compare total interactions and strength
compareInteractions(cellchat_merged, show.legend = FALSE)

# Differential interaction visualizations
netVisual_diffInteraction(cellchat_merged, weight.scale = TRUE)
netVisual_heatmap(cellchat_merged)

# Pathway-level comparison across conditions
rankNet(cellchat_merged, mode = 'comparison', stacked = TRUE)
```

## NicheNet Ligand Activity Analysis

_modules: nichenet, ligand-activity, target-genes_

```r
# Define sender and receiver cell types
sender_celltypes <- c('Macrophage', 'Dendritic')
receiver <- 'T_cell'

# Get expressed genes (pct threshold for fraction of cells expressing)
expressed_genes_sender <- get_expressed_genes(sender_celltypes, seurat_obj, pct = 0.10)
expressed_genes_receiver <- get_expressed_genes(receiver, seurat_obj, pct = 0.10)

# Gene set of interest: DE genes in receiver (e.g. activated vs naive)
geneset_oi <- FindMarkers(seurat_obj, ident.1 = 'activated_T', ident.2 = 'naive_T') %>%
    filter(p_val_adj < 0.05, avg_log2FC > 0.5) %>% rownames()

background_genes <- expressed_genes_receiver

# Define potential ligands from expressed ligands/receptors and the L-R network
ligands <- lr_network %>% pull(from) %>% unique()
expressed_ligands <- intersect(ligands, expressed_genes_sender)

receptors <- lr_network %>% pull(to) %>% unique()
expressed_receptors <- intersect(receptors, expressed_genes_receiver)

potential_ligands <- lr_network %>%
    filter(from %in% expressed_ligands & to %in% expressed_receptors) %>%
    pull(from) %>% unique()

# Predict ligand activities (Pearson correlation of predicted vs observed target effects)
ligand_activities <- predict_ligand_activities(
    geneset = geneset_oi,
    background_expressed_genes = background_genes,
    ligand_target_matrix = ligand_target_matrix,
    potential_ligands = potential_ligands
)

# Top prioritized ligands
best_ligands <- ligand_activities %>% top_n(20, pearson) %>% arrange(-pearson) %>% pull(test_ligand)

# --- Visualization ---
# Ligand-target heatmap
active_ligand_target_links <- best_ligands %>%
    lapply(get_weighted_ligand_target_links, geneset_oi, ligand_target_matrix, n = 200) %>%
    bind_rows() %>% drop_na()

vis_ligand_target <- prepare_ligand_target_visualization(
    ligand_target_df = active_ligand_target_links,
    ligand_target_matrix = ligand_target_matrix,
    cutoff = 0.33
)

p_ligand_target <- vis_ligand_target %>%
    make_heatmap_ggplot('Prioritized ligands', 'Target genes',
                        color = 'purple', legend_position = 'top')

# Ligand-receptor heatmap
lr_network_top <- lr_network %>%
    filter(from %in% best_ligands & to %in% expressed_receptors) %>%
    distinct(from, to)

vis_ligand_receptor <- get_exprs_avg(seurat_obj, 'cell_type') %>%
    inner_join(lr_network_top, by = c('gene' = 'to'))

p_ligand_receptor <- vis_ligand_receptor %>%
    make_heatmap_ggplot('Ligands', 'Receptors', color = 'mediumvioletred')

# Ligand expression by cell type
p_ligand_expression <- DotPlot(seurat_obj, features = best_ligands, cols = 'RdYlBu') +
    RotatedAxis()
```

## LIANA Analysis & Tensor Decomposition

_modules: liana, rank-aggregation, tensor-decomposition_

```python
import liana as li
import scanpy as sc

adata = sc.read_h5ad('adata.h5ad')

# --- Consensus rank aggregation across multiple methods ---
li.mt.rank_aggregate(adata, groupby='cell_type', resource_name='consensus',
                     expr_prop=0.1, verbose=True)

# Retrieve and filter significant interactions
liana_results = adata.uns['liana_res']
sig_interactions = liana_results[liana_results['liana_rank'] < 0.01]

# Dot plot of interactions from selected source to target groups
li.pl.dotplot(adata, colour='magnitude_rank', size='specificity_rank',
              source_groups=['Macrophage'], target_groups=['T_cell'])

# --- Multi-sample tensor decomposition ---
# Re-run rank aggregation with use_raw=False for consistent scaling across samples
li.mt.rank_aggregate(adata, groupby='cell_type', resource_name='consensus',
                     use_raw=False, verbose=True)

# Build the communication tensor across samples
li.multi.build_tensor(adata, sample_key='sample', groupby='cell_type',
                      ligand_key='ligand_complex', receptor_key='receptor_complex')

# Decompose into factors (each factor = a signaling program)
li.multi.decompose_tensor(adata, n_components=5)

# Visualize factor loadings (e.g. factor 0)
li.pl.factor_loadings(adata, factor_idx=0)
```
