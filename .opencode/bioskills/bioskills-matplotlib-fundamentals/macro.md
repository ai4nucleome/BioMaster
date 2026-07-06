# Bioskills Matplotlib Fundamentals

## Overview

This workflow produces publication-ready figures in Python using matplotlib's object-oriented Figure/Axes API, optionally layered with seaborn. Inputs are numeric arrays, pandas DataFrames, or matrices (e.g., expression values, PCA/UMAP embeddings, fold-changes, z-scored heatmaps). Outputs are journal-compliant figure files (PDF/PNG/TIFF/SVG) with Type-42 TrueType fonts, CVD-safe palettes, constrained_layout alignment, and rasterized point layers for large scatter. Use it whenever a figure must meet journal submission standards (Nature, IEEE, ACM) or when building reproducible multi-panel figures; the pyplot state-machine is reserved for notebook scratch only. The ordered stages are: configure rcParams and verify versions, create the figure/axes scaffolding, draw common chart types, integrate seaborn, format axes and color, save/export, and troubleshoot common failure modes.

## Setup & Configuration

Configure matplotlib rcParams for publication compliance before drawing anything. First verify that installed package versions match the tested references (matplotlib 3.8+, seaborn 0.13+, numpy 1.26+, pandas 2.2+); if versions differ, introspect the installed API with pip show and help() rather than retrying on Import/Attribute/TypeErrors. The three modern defaults to enforce are: the object-oriented Figure/Axes API (not the pyplot state-machine), constrained_layout for automatic axis alignment (replacing tight_layout, default since matplotlib 3.6), and Type-42 (TrueType) font embedding so PDFs are searchable and accepted by Nature, IEEE, and ACM (default Type-3 PostScript glyphs are rejected). Set font sizes to journal scales (5-7 pt body, 8 pt titles), line and spine widths to ~0.5 pt, display DPI to 100 and save DPI to 300.

## Figure & Axes Creation

Build the figure scaffolding with the object-oriented API. Create single or grid axes via plt.subplots with constrained_layout=True and figsize specified in inches; convert millimetres with /25.4 for journal column widths (89 mm single column, 180 mm double column). Always hold explicit Axes references (fig, ax) so labels and styling target the correct subplot, and never rely on pyplot's 'current axes' in multi-panel figures, which becomes order-dependent and mislabels subplots.

## Plotting Common Chart Types

Draw the data using the appropriate Axes method. Rasterize scatter calls (rasterized=True) whenever the point count exceeds ~1000 to keep PDFs small while axes and text stay vector. Use fill_between for confidence bands, patch_artist boxplots for filled boxes, and imshow with aspect='auto' for heatmaps. Prefer seaborn for clustered heatmaps and distribution plots (cross-referenced in related skills), but the core chart types below are handled directly on Axes.

## seaborn Integration

Layer seaborn on top of matplotlib by passing an explicit ax= argument so the plot lands on the intended Axes. Distinguish axes-level functions (scatterplot, boxplot, barplot, which return Axes and accept ax=) from figure-level functions (displot, relplot, catplot, which return a FacetGrid and need set_axis_labels rather than set_xlabel). seaborn 0.13+ also offers the objects grammar (so.Plot) for ggplot-like layered composition with explicit scales.

## Axis Formatting & Color

Format axes (log scales, scientific notation, date axes, tick frequency and rotated labels, grids) and choose color palettes deliberately. Use the Okabe-Ito CVD-safe categorical palette for groups, perceptually-uniform sequential maps (viridis, cividis, Crameri batlow) for continuous magnitude, and symmetric diverging maps (RdBu_r with vmin=-vmax) for signed quantities like log-fold-change or z-scores. See the color-palettes skill for the full palette decision tree.

## Saving & Export

Export the figure in the format the target demands. PDF gives vector text plus raster scatter (best for publication), PNG for web and presentations, TIFF with LZW compression for journals that require it, and SVG for editable vector. Always pass dpi=300 and bbox_inches='tight'. Keep rasterization per-element (on scatter only) so axes and text remain crisp vector on zoom; use fig.set_rasterization_zorder(0) for global control when mixing vector and raster layers.

## Troubleshooting Failure Modes

Diagnose and fix the common publication-figure failure modes. Type-3 font rejection (set pdf.fonttype=42 and ps.fonttype=42, verify with pdffonts showing TrueType), tight_layout failures on complex grids with colorbars or shared axes (switch to constrained_layout=True), pyplot state-machine mislabeling in multi-subplots (use explicit ax.set_xlabel), 50 MB PDFs from vector scatter at large N (rasterized=True on the scatter call), seaborn FacetGrid vs Axes return-type confusion (set_axis_labels for FacetGrid, set_xlabel for Axes, or switch to axes-level histplot), figsize-in-inches-when-mm-intended (divide by 25.4), and colorbar over-fill (shrink=0.6, aspect=20, or make_axes_locatable for fine control). The error table below maps each symptom to its cause and fix.
