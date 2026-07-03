# Bioskills Cell Segmentation

## Overview

Cell segmentation workflow for Imaging Mass Cytometry (IMC) and other multiplexed imaging data. It takes a processed multi-channel TIFF image (e.g., produced by a data-preprocessing skill) containing nuclear and membrane markers, and produces a labeled integer cell mask, a per-cell expression matrix, and an AnnData object with spatial coordinates ready for downstream phenotyping and spatial analysis.

Inputs: a processed multi-channel TIFF (channels ordered by panel, e.g. nuclear DNA1 first, membrane CD45 second) and a list of channel names. Outputs: a uint16 labeled mask TIFF, per-cell morphology and intensity CSVs, and an H5AD AnnData with intensities in X, channel names as var_names, morphology in obs, and centroid coordinates in obsm['spatial'].

Use this skill when you need to identify individual cell boundaries in multiplexed imaging data. It supports deep-learning segmentation (Cellpose 'nuclei' for nuclear-only, Cellpose 'cyto2' for whole-cell with nuclear+membrane channels, and Mesmer/DeepCell for whole-cell or nuclear prediction) as well as pipeline-based segmentation via the steinbock CLI. If only nuclear masks are available, labels can be expanded to approximate whole-cell boundaries.

Reference versions: Cellpose 3.0+, anndata 0.10+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, steinbock 0.16+. Before running, verify installed versions match; if they differ, introspect the installed API (pip show / help / --version / --help) and adapt the example rather than retrying on ImportError, AttributeError, or TypeError. Related skills: data-preprocessing (prepare images before segmentation), phenotyping (classify segmented cells), spatial-analysis (analyze cell spatial relationships).

## Preparation & Image Loading

Load the processed multi-channel TIFF and identify the nuclear (e.g., DNA1) and membrane (e.g., CD45) channels by index according to the panel. This step also establishes the version-compatibility contract: the reference examples assume Cellpose 3.0+, anndata 0.10+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, and steinbock 0.16+. If installed versions differ, introspect the actual API (pip show for Python packages, --version/--help for CLIs, help(module.function) for signatures) and adapt the calls rather than retrying blindly on ImportError, AttributeError, or TypeError.

## Cell Segmentation

Produce a labeled integer mask in which every cell has a unique ID. Choose a method based on the data and goal: Cellpose 'nuclei' for nuclear-only segmentation from a single nuclear channel; Cellpose 'cyto2' for whole-cell segmentation using a two-channel [membrane, nuclear] input; Mesmer (DeepCell) for whole-cell or nuclear prediction from a (batch, H, W, 2) input; or the steinbock CLI for pipeline-based Cellpose/DeepCell segmentation. Key parameters include the expected diameter (typical nucleus ~30 px, whole cell ~50 px), flow_threshold (~0.4), cellprob_threshold, and image_mpp (microns per pixel) for Mesmer. If only nuclear masks are available, expand the labels by a fixed distance to approximate whole-cell boundaries.

## Single-Cell Data Extraction

Convert the labeled mask and multi-channel image stack into a per-cell expression matrix together with morphological features. Iterate over regionprops of the label mask; for each cell compute the mean intensity of every channel within its pixels and collect morphology (area, centroid x/y, eccentricity). The result is two DataFrames: a cell-info table keyed by cell_id and an intensity table whose columns are the channel names.

## Quality Control

Visually and statistically assess segmentation quality before downstream use. Generate a three-panel figure showing the nuclear channel, the labeled mask, and an overlay of red mask contours on the nuclear channel. Report the total cell count and the area distribution (mean and median). Inspect for over- or under-segmentation and, if needed, revisit the diameter, flow_threshold, or cellprob_threshold parameters from the segmentation step.

## Export & Save

Persist segmentation outputs for downstream phenotyping and spatial analysis. Save the labeled mask as a uint16 TIFF, the cell-info and per-channel intensity tables as CSVs, and assemble a combined AnnData object with intensities in X, channel names as var_names, cell morphology in obs, and centroid coordinates in obsm['spatial']; write the AnnData to an H5AD file.
