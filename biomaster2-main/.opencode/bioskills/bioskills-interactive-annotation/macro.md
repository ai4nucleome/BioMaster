# Bioskills Interactive Annotation

## Overview

This workflow enables interactive manual annotation of cell types in imaging mass cytometry (IMC) and other multiplexed imaging data using napari-based visualization. It takes a multi-channel image stack of shape (C, H, W) and a corresponding integer cell segmentation mask as inputs, and lets the user paint cell-type labels onto cells while guided by marker-channel overlays. The annotated cells are extracted into a per-cell feature table (mean marker intensities plus integer labels) that can serve as training data for downstream classifiers. A semi-automated step then propagates a small set of manual labels to all unannotated cells using a k-nearest-neighbors classifier on standardized marker intensities, with class-probability confidence scores to flag uncertain assignments for review. Finally, per-cell-type validation montages sample annotated cells for manual quality control. Use this workflow when you need curated ground-truth labels for training phenotyping classifiers or for validating automated cell-typing results. Reference examples were tested with matplotlib 3.8+, numpy 1.26+, pandas 2.2+, and scikit-learn 1.4+; if installed versions differ, introspect the actual API (e.g. `pip show <package>` then `help(module.function)`) and adapt the patterns rather than retrying on ImportError/AttributeError/TypeError.

## Viewer Setup & Marker Visualization

Set up a napari viewer loaded with the multi-channel image stack, the cell segmentation mask, and an empty annotation label layer. Each marker channel is added as a separate image layer (initially hidden, grayscale, additive blending) so the user can toggle channels on demand. A helper builds RGB overlays of selected marker combinations (for example CD3/CD45 for T cells, panCK for tumor) by min-max normalizing each channel and summing weighted color contributions, making it easier to identify cell types visually during annotation. A cell-type mapping dictionary defines the integer label-to-name convention used throughout the workflow.

## Interactive Annotation Widgets

Add magicgui-powered dock widgets to the napari viewer to streamline annotation. One widget annotates the currently selected cell (by matching the segmentation layer's selected_label) with a chosen cell-type integer, updating the annotation label layer in place. A second widget exports the current annotations to CSV by iterating over segmentation labels, taking the median annotation value within each cell mask, and writing cell_id/cell_type pairs. These widgets turn napari into a lightweight annotation tool without leaving the viewer.

## Batch Annotation Workflow

Extend the single-image annotation setup to a batch session over many image/segmentation file pairs. For each sample, the viewer is cleared and repopulated with that sample's channels, segmentation mask, and either a previously saved annotation mask or a fresh empty one. The session pauses for the user to annotate interactively, then stores the resulting annotation mask keyed by sample name, allowing annotation to be resumed across runs.

## Training Data Extraction

Convert the painted annotation mask into a per-cell feature table suitable for classifier training. For every cell ID in the segmentation mask, the function reads the annotation values inside that cell's mask, assigns the cell type as the median non-zero annotation, and computes the mean intensity of each marker channel over the cell. The resulting DataFrame (cell_id, cell_type, mean marker intensities) is saved to CSV and summarized by cell-type counts.

## Semi-Automated Annotation

Propagate a small set of manual annotations to all unannotated cells using marker-expression similarity. A k-nearest-neighbors classifier (k=5) is trained on the standardized marker intensities of manually annotated cells, then predicts labels and class probabilities for the remaining cells. The maximum class probability is reported as a confidence score; cells above a threshold (e.g. 0.8) are treated as high-confidence assignments, while low-confidence cells are flagged for manual review.

## Annotation Validation

Generate per-cell-type validation montages for manual quality control. For each cell type, a random sample of up to 20 cells is drawn; for each sampled cell, the bounding box (with padding) of its mask is cropped from every marker channel and arranged into a grid of thumbnails. The resulting figure is saved per cell type so the user can visually confirm that annotated cells match the expected marker profile.
