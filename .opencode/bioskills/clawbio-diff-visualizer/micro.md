## Input Detection & Validation

_modules: input-detection, validation_

```bash
# Auto-detect from an upstream rnaseq-de directory
python skills/diff-visualizer/diff_visualizer.py \
  --input output/rnaseq_run --output diffviz_report

# Auto-detect from an upstream scrna-orchestrator directory
python skills/diff-visualizer/diff_visualizer.py \
  --input output/scrna_run --output diffviz_report

# Direct bulk DE table (auto-detected from columns)
python skills/diff-visualizer/diff_visualizer.py \
  --input de_results.csv --output diffviz_report

# Direct scRNA table (explicit --mode scrna)
python skills/diff-visualizer/diff_visualizer.py \
  --mode scrna --input contrastive_markers_full.csv --output diffviz_report

# Via ClawBio runner
python clawbio.py run diffviz --input de_results.csv --output diffviz_report
```

Required column schemas by input type:
- Bulk DE table: `gene`, `log2FoldChange`, plus `padj` or `pvalue`
- scRNA contrast table: `names`, `scores`
- scRNA within-cluster contrast table: `cluster`, `comparison_id`, `group1`, `group2`, `names`, `scores`
- scRNA cluster markers table: `cluster`, `names`, `scores`
- Optional bulk counts: gene rows × sample columns, first column = gene id
- Optional bulk metadata: must contain `sample_id`
- Optional AnnData: expression matrix with gene names in `var_names`

## Bulk Differential Visualization

_modules: volcano, ma-plot, heatmap, bar-chart_

```bash
# Bulk DE table — volcano + top-gene bars (+ MA plot if supported)
python skills/diff-visualizer/diff_visualizer.py \
  --input de_results.csv --output diffviz_report

# Bulk directory with optional heatmap inputs (counts + metadata)
python skills/diff-visualizer/diff_visualizer.py \
  --input output/rnaseq_run --counts counts.csv --metadata metadata.csv \
  --output diffviz_report
```

Figures produced (written to `figures/`):
- `volcano.png` — log2FoldChange vs -log10(padj)
- `top_genes_bar.png` — top ranked genes by effect size
- `ma_plot.png` — log2FoldChange vs mean expression (optional)
- `top_genes_heatmap.png` — top genes across samples (requires counts + metadata)

## scRNA Marker Visualization

_modules: contrast-volcano, marker-bars, dotplot, umap_

```bash
# scRNA contrast table — contrast volcanoes + marker ranking bars
python skills/diff-visualizer/diff_visualizer.py \
  --mode scrna --input contrastive_markers_full.csv --output diffviz_report

# scRNA within-cluster contrast table — within-cluster comparison panels
python skills/diff-visualizer/diff_visualizer.py \
  --mode scrna --input within_cluster_contrastive_markers_full.csv \
  --output diffviz_report

# scRNA cluster markers table — marker ranking bars
python skills/diff-visualizer/diff_visualizer.py \
  --mode scrna --input markers_top.csv --output diffviz_report

# scRNA with AnnData enhancement (dotplot, heatmap, UMAP feature panel)
python skills/diff-visualizer/diff_visualizer.py \
  --mode scrna --input contrastive_markers_full.csv --adata cells.h5ad \
  --output diffviz_report
```

Figures produced (written to `figures/`):
- `contrast_volcano.png` — dataset-level contrast volcano
- `top_markers_bar.png` — top markers by score
- `marker_rank_bars.png` — marker ranking across clusters
- `marker_dotplot.png` — marker dotplot (requires AnnData)
- `marker_heatmap.png` — marker heatmap (requires AnnData)
- `umap_feature_panel.png` — UMAP feature panel (requires AnnData)

## Report & Reproducibility

_modules: report, reproducibility, html_

```bash
# Report assembly is automatic on every run; no extra flags needed.
python skills/diff-visualizer/diff_visualizer.py \
  --input de_results.csv --output diffviz_report

# Demo runs (bulk and scRNA) for quick verification
python skills/diff-visualizer/diff_visualizer.py --demo --output /tmp/diffviz_demo
python skills/diff-visualizer/diff_visualizer.py --demo --mode scrna --output /tmp/diffviz_scrna_demo
python clawbio.py run diffviz --demo
```

Output structure written to the output directory:
```text
output_directory/
├── report.md
├── report.html
├── result.json
├── figures/            # all rendered PNGs
├── tables/             # top_genes.csv, significant_genes.csv,
│                       # top_markers.csv, top_markers_by_cluster.csv
└── reproducibility/
    ├── commands.sh
    ├── environment.yml
    └── checksums.sha256
```
