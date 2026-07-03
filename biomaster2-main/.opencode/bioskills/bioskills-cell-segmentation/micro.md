## Preparation & Image Loading

_modules: image-loading, version-check, channel-selection_

import tifffile
import numpy as np

# Load processed multi-channel image (channels ordered by panel)
img = tifffile.imread('processed.tiff')

# Identify channels by index based on the panel
nuclear_channel = img[0]    # e.g., DNA1
membrane_channel = img[1]   # e.g., CD45

# Reference versions: Cellpose 3.0+, anndata 0.10+, matplotlib 3.8+,
# numpy 1.26+, pandas 2.2+, scanpy 1.10+, steinbock 0.16+
# Verify before use:
#   pip show <package>                       # Python package version
#   <tool> --version && <tool> --help        # CLI version + flags
# On ImportError/AttributeError/TypeError, introspect the installed API
# (help(module.function)) and adapt the call rather than retrying.

## Cell Segmentation

_modules: cellpose, deepcell, mesmer, steinbock, segmentation, nuclei-expansion_

from cellpose import models
from skimage.segmentation import expand_labels

# --- Option A: Nuclear-only segmentation (Cellpose 'nuclei') ---
model = models.Cellpose(model_type='nuclei', gpu=True)
masks, flows, styles, diams = model.eval(
    nuclear_channel,
    diameter=30,            # average nucleus diameter in pixels
    flow_threshold=0.4,
    cellprob_threshold=0.0,
)
print(f'Cells segmented: {masks.max()}')

# --- Option B: Whole-cell segmentation (Cellpose 'cyto2') ---
# Build 2-channel input [membrane, nuclear]
img_input = np.stack([membrane_channel, nuclear_channel])
model = models.Cellpose(model_type='cyto2', gpu=True)
masks, flows, styles, diams = model.eval(
    img_input,
    channels=[1, 2],        # [membrane, nuclear]
    diameter=50,
    flow_threshold=0.4,
)

# --- Option C: Mesmer (DeepCell) ---
from deepcell.applications import Mesmer
app = Mesmer()
deepcell_input = np.stack([nuclear_channel, membrane_channel], axis=-1)
deepcell_input = np.expand_dims(deepcell_input, axis=0)  # (batch, H, W, 2)
predictions = app.predict(
    deepcell_input,
    image_mpp=1.0,                  # microns per pixel
    compartment='whole-cell',       # or 'nuclear'
)
masks = predictions[0, :, :, 0]

# --- Option D: steinbock CLI (run in shell) ---
# steinbock segment cellpose --img processed --model cyto2 --channelwise \
#     --nuclear-channel 0 --membrane-channel 1 -o masks
# steinbock segment deepcell --img processed --nuclear-channel 0 \
#     --membrane-channel 1 -o masks

# --- Optional: expand nuclear masks to approximate whole cells ---
expanded_masks = expand_labels(masks, distance=10)

## Single-Cell Data Extraction

_modules: regionprops, intensity-extraction, morphology_

from skimage import measure
import pandas as pd

def extract_single_cell_data(img, masks, channel_names):
    '''Extract mean intensity per cell per channel plus morphology.'''
    props = measure.regionprops(masks)
    cell_data, intensities = [], []

    for prop in props:
        cell_data.append({
            'cell_id': prop.label,
            'area': prop.area,
            'centroid_x': prop.centroid[1],
            'centroid_y': prop.centroid[0],
            'eccentricity': prop.eccentricity,
        })
        cell_mask = masks == prop.label
        intensities.append([img[c][cell_mask].mean()
                            for c in range(len(channel_names))])

    cell_df = pd.DataFrame(cell_data)
    intensity_df = pd.DataFrame(intensities, columns=channel_names)
    return cell_df, intensity_df

cell_info, intensities = extract_single_cell_data(img, masks, channel_names)
print(f'Extracted data for {len(cell_info)} cells')

## Quality Control

_modules: qc, visualization, statistics_

import matplotlib.pyplot as plt

def qc_segmentation(img, masks, nuclear_channel_idx=0):
    '''Visualize segmentation quality and report area statistics.'''
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(img[nuclear_channel_idx], cmap='gray')
    axes[0].set_title('Nuclear Channel')
    axes[1].imshow(masks, cmap='tab20')
    axes[1].set_title(f'Segmentation ({masks.max()} cells)')
    axes[2].imshow(img[nuclear_channel_idx], cmap='gray')
    axes[2].contour(masks, colors='red', linewidths=0.5)
    axes[2].set_title('Overlay')
    for ax in axes:
        ax.axis('off')
    plt.tight_layout()
    plt.savefig('segmentation_qc.png', dpi=150)
    plt.close()

    props = measure.regionprops(masks)
    areas = [p.area for p in props]
    print(f'Cells: {len(props)}')
    print(f'Area: mean={np.mean(areas):.1f}, median={np.median(areas):.1f}')

qc_segmentation(img, masks)

## Export & Save

_modules: export, anndata, tiff, csv_

import tifffile
import anndata as ad

# Save labeled mask
tifffile.imwrite('cell_masks.tiff', masks.astype(np.uint16))

# Save per-cell tables
cell_info.to_csv('cell_info.csv', index=False)
intensities.to_csv('cell_intensities.csv', index=False)

# Assemble AnnData with spatial coordinates
adata = ad.AnnData(X=intensities.values)
adata.var_names = channel_names
adata.obs = cell_info
adata.obsm['spatial'] = cell_info[['centroid_x', 'centroid_y']].values
adata.write('imc_segmented.h5ad')
