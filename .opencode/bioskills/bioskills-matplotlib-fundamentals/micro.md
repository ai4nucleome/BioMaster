## Setup & Configuration

_modules: rcparams, configuration, fonts, version-check_

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# rcParams for publication compliance
mpl.rcParams.update({
    'pdf.fonttype': 42,                 # TrueType -- searchable PDFs
    'ps.fonttype': 42,                  # TrueType in EPS
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 7,                     # Nature requires 5-7 pt body text
    'axes.labelsize': 7,
    'axes.titlesize': 8,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
    'legend.fontsize': 6,
    'figure.dpi': 100,                  # display
    'savefig.dpi': 300,                 # save
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
    'axes.linewidth': 0.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'lines.linewidth': 1.0,
    'patch.linewidth': 0.5,
})

# Version compatibility check (tested: matplotlib 3.8+, seaborn 0.13+,
# numpy 1.26+, pandas 2.2+). On ImportError/AttributeError/TypeError,
# introspect the installed package and adapt the example to the actual API.
#   pip show <package>   then   help(module.function)
```

## Figure & Axes Creation

_modules: figure, axes, subplots, constrained-layout, figsize_

```python
import matplotlib.pyplot as plt

# Single axes -- 89mm x 70mm (Nature single column) converted to inches
fig, ax = plt.subplots(figsize=(89/25.4, 70/25.4),
                       constrained_layout=True)
ax.scatter(x, y, c='#0072B2', s=10, alpha=0.7, edgecolors='none', rasterized=True)
ax.set_xlabel('PC1 (45%)')
ax.set_ylabel('PC2 (12%)')
ax.spines[['top', 'right']].set_visible(False)
fig.savefig('scatter.pdf')

# Grid of axes -- 180mm double column
fig, axes = plt.subplots(2, 3, figsize=(180/25.4, 100/25.4),
                         constrained_layout=True)
for ax, (label, panel_data) in zip(axes.flat, data.items()):
    ax.plot(panel_data['x'], panel_data['y'])
    ax.set_title(label, fontsize=8)
```

## Plotting Common Chart Types

_modules: scatter, line, bar, boxplot, histogram, heatmap, rasterization_

```python
# Scatter -- always rasterized for >1000 points
ax.scatter(x, y, c=values, cmap='viridis', s=8, alpha=0.6,
           edgecolors='none', rasterized=True)
plt.colorbar(ax.collections[0], ax=ax, label='Expression', shrink=0.8)

# Line
ax.plot(x, y1, color='#0072B2', label='Control', linewidth=1)
ax.plot(x, y2, color='#D55E00', label='Treatment', linewidth=1)
ax.fill_between(x, y_low, y_high, color='#0072B2', alpha=0.2)
ax.legend(frameon=False, fontsize=6)

# Bar
ax.bar(categories, values, color='#0072B2', edgecolor='black', linewidth=0.5)

# Box / violin (prefer seaborn for these -- see distribution-plots)
ax.boxplot([group_a, group_b, group_c], labels=['A', 'B', 'C'],
           patch_artist=True, boxprops=dict(facecolor='#0072B2', alpha=0.7))

# Histogram
ax.hist(values, bins=30, color='#0072B2', edgecolor='white', linewidth=0.5)

# Heatmap (prefer seaborn for clustered; see heatmaps-clustering)
im = ax.imshow(matrix, cmap='RdBu_r', aspect='auto', vmin=-vmax, vmax=vmax)
plt.colorbar(im, ax=ax, label='Z-score')
```

## seaborn Integration

_modules: seaborn, axes-level, facetgrid, objects-grammar_

```python
import seaborn as sns

# seaborn shares the matplotlib Figure/Axes -- pass ax= argument
fig, ax = plt.subplots(figsize=(4, 3), constrained_layout=True)
sns.scatterplot(data=df, x='log_fold_change', y='neg_log_p',
                hue='significance', palette=['#999999', '#0072B2', '#D55E00'],
                s=10, alpha=0.7, ax=ax, rasterized=True)

# seaborn 0.13+ objects grammar interface (ggplot-like)
import seaborn.objects as so
(so.Plot(df, x='log_fold_change', y='neg_log_p')
   .add(so.Dots(pointsize=2), color='significance')
   .scale(color=['#999999', '#0072B2', '#D55E00']))

# Return-type gotcha:
#   axes-level (scatterplot, boxplot, barplot) -> return Axes, use ax.set_xlabel
#   figure-level (displot, relplot, catplot)   -> return FacetGrid,
#                                                  use g.set_axis_labels(x, y)
```

## Axis Formatting & Color

_modules: axis-formatting, ticks, scales, color-palette, cvd-safe, diverging_

```python
# Log scale
ax.set_yscale('log')

# Scientific notation
from matplotlib.ticker import ScalarFormatter
ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))

# Date axis
import matplotlib.dates as mdates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Tick frequency
ax.set_xticks(np.arange(0, 10, 2))
ax.set_xticklabels(['A', 'B', 'C'], rotation=45, ha='right')

# Grid
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

# CVD-safe categorical
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']

# Perceptually-uniform sequential (Crameri batlow / viridis cividis)
from cmcrameri import cm as cmc
plt.imshow(data, cmap=cmc.batlow)
plt.imshow(data, cmap='viridis')                          # built-in

# Diverging symmetric for LFC / z-score
vmax = np.quantile(np.abs(data), 0.99)
plt.imshow(data, cmap='RdBu_r', vmin=-vmax, vmax=vmax)   # symmetric
```

## Saving & Export

_modules: savefig, export, pdf, png, tiff, svg, dpi_

```python
# PDF for vector text + raster scatter (best of both)
fig.savefig('figure.pdf', dpi=300, bbox_inches='tight')

# PNG for raster (web, presentations)
fig.savefig('figure.png', dpi=300, bbox_inches='tight')

# TIFF for some journals
fig.savefig('figure.tiff', dpi=300, pil_kwargs={'compression': 'tiff_lzw'})

# SVG for editable vector
fig.savefig('figure.svg', bbox_inches='tight')

# Per-element rasterization: rasterized=True on scatter only;
# axes and text stay vector. Global control:
fig.set_rasterization_zorder(0)
```

## Troubleshooting Failure Modes

_modules: troubleshooting, fonts, layout, rasterization, debugging_

```python
# Fix: Type-3 fonts rejected by journals
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
# verify:  pdffonts figure.pdf  -> should show 'TrueType'

# Fix: tight_layout fails on complex grids (colorbars / shared axes)
fig, ax = plt.subplots(constrained_layout=True)   # not plt.tight_layout()
# or after creation:  fig.set_constrained_layout(True)

# Fix: pyplot state-machine mislabels multi-subplot
ax.set_xlabel('...')          # explicit axes reference, NOT plt.xlabel

# Fix: 50 MB PDF from vector scatter at large N
ax.scatter(x, y, rasterized=True)   # per-element; axes/text stay vector

# Fix: seaborn FacetGrid vs Axes return-type confusion
g = sns.displot(...)
g.set_axis_labels('x', 'y')        # FacetGrid -- NOT g.set_xlabel
# or switch to axes-level:  sns.histplot(ax=ax)  -> returns Axes

# Fix: figsize in inches when mm was intended
figsize=(89/25.4, 70/25.4)        # convert mm -> inches

# Fix: colorbar over-fills the axes
plt.colorbar(im, ax=ax, shrink=0.6, aspect=20)
# or:  from mpl_toolkits.axes_grid1 import make_axes_locatable

# Error / symptom -> Cause -> Solution quick table:
# | PDF rejected by journal       | Type-3 fonts            | pdf.fonttype=42                  |
# | Subplots overlap              | No constrained_layout   | plt.subplots(constrained_layout=True) |
# | Wrong subplot labeled         | pyplot state-machine    | ax.set_xlabel explicitly         |
# | 50 MB PDF                     | Vector scatter at large N | rasterized=True on scatter     |
# | Figure too big                | mm interpreted as inches | Divide by 25.4                  |
# | Colorbar dominates            | Default size            | shrink=0.6, aspect=20            |
# | seaborn .set_xlabel fails     | FacetGrid not Axes      | g.set_axis_labels(x, y)          |
# | Axes spine missing            | Wrong API               | ax.spines[['top','right']].set_visible(False) |
```
