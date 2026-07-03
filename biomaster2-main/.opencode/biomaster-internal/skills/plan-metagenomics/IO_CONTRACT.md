# IO Contract: metagenomics

## Inputs
- test mode: built-in demonstration OTU/taxonomy/metadata tables
- formal mode: OTU table (counts), taxonomy table, sample metadata CSV/TSV

## Outputs
- phyloseq object (`ps.rds`)
- core microbiota figure (`core_microbiota.pdf`)
- composition bar plot (`composition.pdf`)
- alpha diversity table and figures (`alpha_diversity.csv`, `alpha_*.pdf`)
- PCA table and biplot (`pca_components.csv`, `pca_biplot.pdf`)
- dissimilarity matrix, ANOSIM, PERMANOVA results (`dist_matrix.csv`, `anosim.txt`, `permanova.txt`)
- ordination object and figure (`ordination.rds`, `ordination.pdf`)
- marker table and effect-size bar plot (`marker_table.csv`, `marker_bar.pdf`)
