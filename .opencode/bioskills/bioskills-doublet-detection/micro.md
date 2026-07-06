## Data Loading & Channel Verification

_modules: data-loading, fcs, channel-check_

```r
library(flowCore)
library(ggcyto)

# Load FCS files into a flowSet
fs <- read.flowSet(list.files('data/', pattern = '\\.fcs$', full.names = TRUE))

# Inspect available scatter channels to choose a method
available <- colnames(fs[[1]])
print(available)

# Verify package versions match the reference (flowCore 2.14+, ggplot2 3.5+)
packageVersion('flowCore')
packageVersion('ggplot2')
```

## Scatter-Based Singlet Gating

_modules: singlet-gating, fsc, ssc, flowDensity, ratio_

```r
library(flowDensity)

# --- Manual rectangular gate on FSC-A vs FSC-H ---
singlet_gate <- rectangleGate(
    filterId = 'singlets',
    'FSC-A' = c(50000, 250000),
    'FSC-H' = c(50000, 250000)
)

# Polygon gate following the singlet diagonal
singlet_polygon <- polygonGate(
    filterId = 'singlets',
    .gate = data.frame(
        'FSC-A' = c(50000, 250000, 250000, 50000),
        'FSC-H' = c(40000, 200000, 260000, 60000)
    )
)

singlets <- Subset(fs, singlet_gate)
autoplot(fs[[1]], 'FSC-A', 'FSC-H') + geom_gate(singlet_gate)

# --- FSC-A/FSC-W width variant (some instruments provide FSC-W) ---
if ('FSC-W' %in% colnames(fs[[1]])) {
    singlet_gate_w <- rectangleGate(
        filterId = 'singlets',
        'FSC-A' = c(50000, 250000),
        'FSC-W' = c(50000, 100000)  # lower width = singlets
    )
    singlets <- Subset(fs, singlet_gate_w)
}

# --- SSC-based gating for cell types where FSC discriminates poorly ---
ssc_singlet_gate <- rectangleGate(
    filterId = 'ssc_singlets',
    'SSC-A' = c(10000, 200000),
    'SSC-H' = c(10000, 200000)
)
combined_gate <- singlet_gate & ssc_singlet_gate
singlets <- Subset(fs, combined_gate)

# --- Automated singlet gating with flowDensity ---
singlet_result <- flowDensity(
    fs[[1]],
    channels = c('FSC-A', 'FSC-H'),
    position = c(TRUE, TRUE),
    gates = c(NA, NA)
)
singlets <- getflowFrame(singlet_result)
pct_singlets <- nrow(singlets) / nrow(fs[[1]]) * 100
cat('Singlets:', round(pct_singlets, 1), '%\n')

# --- Ratio-based detection (FSC-A / FSC-H) ---
calculate_fsc_ratio <- function(ff) {
    fsc_a <- exprs(ff)[, 'FSC-A']
    fsc_h <- exprs(ff)[, 'FSC-H']
    ratio <- fsc_a / (fsc_h + 1)  # avoid division by zero
    return(ratio)
}
for (i in 1:length(fs)) {
    ratio <- calculate_fsc_ratio(fs[[i]])
    fs[[i]] <- cbind2(fs[[i]], ratio)
    colnames(fs[[i]])[ncol(fs[[i]])] <- 'FSC_ratio'
}
ratio_cutoff <- quantile(exprs(fs[[1]])[, 'FSC_ratio'], 0.95)
singlet_gate_ratio <- rectangleGate(filterId = 'singlets', 'FSC_ratio' = c(0, ratio_cutoff))
```

## CyTOF Doublet Detection

_modules: cytof, catalyst, dna-content, event-length_

```r
library(CATALYST)

# Build SCE from CyTOF data
sce <- prepData(fs, panel, md)

# Event-length method: doublets have longer event lengths
if ('Event_length' %in% rownames(sce)) {
    event_length <- assay(sce)['Event_length', ]
    singlet_idx <- event_length < quantile(event_length, 0.95)
    sce_singlets <- sce[, singlet_idx]
    cat('Removed', sum(!singlet_idx), 'doublets based on event length\n')
}

# DNA intercalator method: doublets have ~2x DNA content
if (all(c('DNA1', 'DNA2') %in% rownames(sce))) {
    dna_total <- assay(sce)['DNA1', ] + assay(sce)['DNA2', ]
    dna_cutoff <- quantile(dna_total, 0.95)
    singlet_idx <- dna_total < dna_cutoff
    sce_singlets <- sce[, singlet_idx]
}
```

## Regression-Based Doublet Detection

_modules: regression, residuals, catalyst, doublet-rate_

```r
library(CATALYST)

# Load and prepare data with arcsinh transformation
sce <- prepData(fs, panel, md, transform = TRUE, cofactor = 5)

# Marker-based doublet removal (if available)
sce <- filterSCE(sce, !is_doublet(sce))

# Custom regression-based detection on FSC
fsc_a <- colData(sce)$FSC_A
fsc_h <- colData(sce)$FSC_H

fit <- lm(fsc_a ~ fsc_h)
residuals <- abs(fsc_a - predict(fit))
threshold <- quantile(residuals, 0.95)

colData(sce)$doublet <- residuals > threshold
sce_singlets <- sce[, !colData(sce)$doublet]

cat('Doublet rate:', round(mean(colData(sce)$doublet) * 100, 1), '%\n')
```

## Batch Processing & Quality Control

_modules: batch-processing, qc, flowAI, fsApply_

```r
library(flowAI)

# Comprehensive QC: flow rate, signal acquisition, dynamic range anomalies
fs_qc <- flow_auto_qc(
    fs,
    folder_results = 'flowAI_results',
    fcs_QC = TRUE,
    fcs_highQ = TRUE
)

# Doublet-detection function for batch use
detect_doublets <- function(ff, method = 'fsc') {
    if (method == 'fsc') {
        fsc_a <- exprs(ff)[, 'FSC-A']
        fsc_h <- exprs(ff)[, 'FSC-H']
        fit <- lm(fsc_a ~ fsc_h)
        residuals <- abs(fsc_a - predict(fit))
        threshold <- quantile(residuals, 0.95)
        singlet_idx <- residuals <= threshold
    } else if (method == 'ratio') {
        ratio <- exprs(ff)[, 'FSC-A'] / (exprs(ff)[, 'FSC-H'] + 1)
        singlet_idx <- ratio < quantile(ratio, 0.95)
    }
    return(ff[singlet_idx, ])
}

# Apply across all samples
fs_singlets <- fsApply(fs, detect_doublets, method = 'fsc')

doublet_rates <- sapply(1:length(fs), function(i) {
    1 - nrow(fs_singlets[[i]]) / nrow(fs[[i]])
})
cat('Mean doublet rate:', round(mean(doublet_rates) * 100, 1), '%\n')
```

## Visualization & Reporting

_modules: visualization, ggplot2, reporting_

```r
library(ggplot2)

# Build plotting data with doublet classification
plot_data <- data.frame(
    FSC_A = exprs(fs[[1]])[, 'FSC-A'],
    FSC_H = exprs(fs[[1]])[, 'FSC-H']
)
fit <- lm(FSC_A ~ FSC_H, data = plot_data)
plot_data$residual <- abs(plot_data$FSC_A - predict(fit))
plot_data$doublet <- plot_data$residual > quantile(plot_data$residual, 0.95)

ggplot(plot_data, aes(x = FSC_H, y = FSC_A, color = doublet)) +
    geom_point(alpha = 0.3, size = 0.5) +
    scale_color_manual(values = c('gray', 'red')) +
    theme_bw() +
    labs(title = 'Doublet Detection', x = 'FSC-H', y = 'FSC-A')
ggsave('doublet_detection.png', width = 8, height = 6)
```
