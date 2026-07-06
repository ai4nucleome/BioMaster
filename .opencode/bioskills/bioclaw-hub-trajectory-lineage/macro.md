# Bioclaw Hub Trajectory Lineage

## Overview

Workflow for pseudotime, lineage branching, and state-transition analysis in single-cell data. This pipeline takes a processed single-cell object (with a coherent embedding and cluster annotations) and optional time or perturbation metadata, then infers developmental trajectories, assigns pseudotime values, identifies branch-specific lineage states, and reports dynamic gene programs along the progression. Use this skill when the user asks for pseudotime, lineage branching, developmental progression, or dynamic gene programs, and the data already has a meaningful embedding and cell-type or cluster labels. The workflow produces pseudotime assignments, branch or lineage state labels, and lists of genes that vary along pseudotime or across branches. Outputs should be organized into `results/` (tables and serialized objects), `figures/` (plots and static exports), and `qc/` (validation artifacts).

## Check Topology Assumptions

Validate that the embedding and cluster relationships support a trajectory-style interpretation. Examine the neighborhood graph and embedding to confirm that clusters form a continuous progression rather than disconnected islands. Compute a diffusion map or force-directed layout to reveal the underlying manifold structure. Generate a QC plot showing cluster positions in the embedding to visually assess whether a trajectory model is appropriate.

## Pick Roots and Branches

Define the root state(s) and expected branching structure using prior biological knowledge or metadata. Use known marker genes, time-point metadata, or a user-specified cell type as the starting point. For root selection, compute a root-cell score based on marker expression or use the earliest time point. Document the assumptions made about root placement and branch structure, as these choices strongly influence downstream pseudotime and lineage assignments.

## Infer Trajectories

Compute pseudotime or lineage paths along the manifold. Use diffusion pseudotime (DPT) via scanpy for a single-root trajectory, or RNA velocity via scvelo when spliced/unspliced counts are available. Verify that the inferred pseudotime aligns with known marker gene trends (e.g., progenitor markers decreasing, differentiated markers increasing along pseudotime). For branching trajectories, identify branch points in the diffusion map or velocity stream plot.

## Identify Dynamic Features

Report genes or gene modules that vary significantly along pseudotime or across branches. Use scanpy's differential expression along pseudotime groups or a generalised additive model (GAM) approach to find temporally dynamic genes. For branching trajectories, identify branch-specific marker genes that distinguish lineage paths. Produce a ranked table of dynamic genes with their pseudotime correlation or branch specificity scores.

## Visualize with Context

Overlay the inferred trajectories on the embedding (UMAP, diffusion map, or force-directed layout) and summarize branch-specific biology. Produce a pseudotime heatmap of the top dynamic genes ordered along the trajectory. Generate a final summary figure that combines the trajectory overlay, pseudotime coloring, and key marker gene expression to communicate the biological progression clearly.
