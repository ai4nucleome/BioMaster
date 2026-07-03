## census_schema.md

# CZ CELLxGENE Census Data Schema Reference

## Overview

The CZ CELLxGENE Census is a versioned collection of single-cell data built on the TileDB-SOMA framework. This reference documents the data structure, available metadata fields, and query syntax.

## High-Level Structure

The Census is organized as a `SOMACollection` with two main components:

### 1. census_info
Summary information including:
- **summary**: Build date, cell counts, dataset statistics
- **datasets**: All datasets from CELLxGENE Discover with metadata
- **summary_cell_counts**: Cell counts stratified by metadata categories

### 2. census_data
Organism-specific `SOMAExperiment` objects:
- **"homo_sapiens"**: Human single-cell data
- **"mus_musculus"**: Mouse single-cell data

## Data Structure Per Organism

Each organism experiment contains:

### obs (Cell Metadata)
Cell-level annotations stored as a `SOMADataFrame`. Access via:
```python
census["census_data"]["homo_sapiens"].obs
```

### ms["RNA"] (Measurement)
RNA measurement data including:
- **X**: Data matrices with layers:
  - `raw`: Raw count data
  - `normalized`: (if available) Normalized counts
- **var**: Gene metadata
- **feature_dataset_presence_matrix**: Sparse boolean array showing which genes were measured in each dataset

## Cell Metadata Fields (obs)

### Required/Core Fields

**Identity & Dataset:**
- `soma_joinid`: Unique integer identifier for joins
- `dataset_id`: Source dataset identifier
- `is_primary_data`: Boolean flag (True = unique cell, False = duplicate across datasets)

**Cell Type:**
- `cell_type`: Human-readable cell type name
- `cell_type_ontology_term_id`: Standardized ontology term (e.g., "CL:0000236")

**Tissue:**
- `tissue`: Specific tissue name
- `tissue_general`: Broader tissue category (useful for grouping)
- `tissue_ontology_term_id`: Standardized ontology term

**Assay:**
- `assay`: Sequencing technology used
- `assay_ontology_term_id`: Standardized ontology term

**Disease:**
- `disease`: Disease status or condition
- `disease_ontology_term_id`: Standardized ontology term

**Donor:**
- `donor_id`: Unique donor identifier
- `sex`: Biological sex (male, female, unknown)
- `self_reported_ethnicity`: Ethnicity information
- `development_stage`: Life stage (adult, child, embryonic, etc.)
- `development_stage_ontology_term_id`: Standardized ontology term

**Organism:**
- `organism`: Scientific name (Homo sapiens, Mus musculus)
- `organism_ontology_term_id`: Standardized ontology term

**Technical:**
- `suspension_type`: Sample preparation type (cell, nucleus, na)

## Gene Metadata Fields (var)

Access via:
```python
census["census_data"]["homo_sapiens"].ms["RNA"].var
```

**Available Fields:**
- `soma_joinid`: Unique integer identifier for joins
- `feature_id`: Ensembl gene ID (e.g., "ENSG00000161798")
- `feature_name`: Gene symbol (e.g., "FOXP2")
- `feature_length`: Gene length in base pairs

## Value Filter Syntax

Queries use Python-like expressions for filtering. The syntax is processed by TileDB-SOMA.

### Comparison Operators
- `==`: Equal to
- `!=`: Not equal to
- `<`, `>`, `<=`, `>=`: Numeric comparisons
- `in`: Membership test (e.g., `feature_id in ['ENSG00000161798', 'ENSG00000188229']`)

### Logical Operators
- `and`, `&`: Logical AND
- `or`, `|`: Logical OR

### Examples

**Single condition:**
```python
value_filter="cell_type == 'B cell'"
```

**Multiple conditions with AND:**
```python
value_filter="cell_type == 'B cell' and tissue_general == 'lung' and is_primary_data == True"
```

**Using IN for multiple values:**
```python
value_filter="tissue in ['lung', 'liver', 'kidney']"
```

**Complex condition:**
```python
value_filter="(cell_type == 'neuron' or cell_type == 'astrocyte') and disease != 'normal'"
```

**Filtering genes:**
```python
var_value_filter="feature_name in ['CD4', 'CD8A', 'CD19']"
```

## Data Inclusion Criteria

The Census includes all data from CZ CELLxGENE Discover meeting:

1. **Species**: Human (*Homo sapiens*) or mouse (*Mus musculus*)
2. **Technology**: Approved sequencing technologies for RNA
3. **Count Type**: Raw counts only (no processed/normalized-only data)
4. **Metadata**: Standardized following CELLxGENE schema
5. **Both spatial and non-spatial data**: Includes traditional and spatial transcriptomics

## Important Data Characteristics

### Duplicate Cells
Cells may appear across multiple datasets. Use `is_primary_data == True` to filter for unique cells in most analyses.

### Count Types
The Census includes:
- **Molecule counts**: From UMI-based methods
- **Full-gene sequencing read counts**: From non-UMI methods
These may need different normalization approaches.

### Versioning
Census releases are versioned (e.g., "2023-07-25", "stable"). Always specify version for reproducible analysis:
```python
census = cellxgene_census.open_soma(census_version="2023-07-25")
```

## Dataset Presence Matrix

Access which genes were measured in each dataset:
```python
presence_matrix = census["census_data"]["homo_sapiens"].ms["RNA"]["feature_dataset_presence_matrix"]
```

This sparse boolean matrix helps understand:
- Gene coverage across datasets
- Which datasets to include for specific gene analyses
- Technical batch effects related to gene coverage

## SOMA Object Types

Core TileDB-SOMA objects used:
- **DataFrame**: Tabular data (obs, var)
- **SparseNDArray**: Sparse matrices (X layers, presence matrix)
- **DenseNDArray**: Dense arrays (less common)
- **Collection**: Container for related objects
- **Experiment**: Top-level container for measurements
- **SOMAScene**: Spatial transcriptomics scenes
- **obs_spatial_presence**: Spatial data availability

---

## common_patterns.md

# Common Query Patterns and Best Practices

## Query Pattern Categories

### 1. Exploratory Queries (Metadata Only)

Use when exploring available data without loading expression matrices.

**Pattern: Get unique cell types in a tissue**
```python
import cellxgene_census

with cellxgene_census.open_soma() as census:
    cell_metadata = cellxgene_census.get_obs(
        census,
        "homo_sapiens",
        value_filter="tissue_general == 'brain' and is_primary_data == True",
        column_names=["cell_type"]
    )
    unique_cell_types = cell_metadata["cell_type"].unique()
    print(f"Found {len(unique_cell_types)} unique cell types")
```

**Pattern: Count cells by condition**
```python
cell_metadata = cellxgene_census.get_obs(
    census,
    "homo_sapiens",
    value_filter="disease != 'normal' and is_primary_data == True",
    column_names=["disease", "tissue_general"]
)
counts = cell_metadata.groupby(["disease", "tissue_general"]).size()
```

**Pattern: Explore dataset information**
```python
# Access datasets table
datasets = census["census_info"]["datasets"].read().concat().to_pandas()

# Filter for specific criteria
covid_datasets = datasets[datasets["disease"].str.contains("COVID", na=False)]
```

### 2. Small-to-Medium Queries (AnnData)

Use `get_anndata()` when results fit in memory (typically < 100k cells).

**Pattern: Tissue-specific cell type query**
```python
adata = cellxgene_census.get_anndata(
    census=census,
    organism="Homo sapiens",
    obs_value_filter="cell_type == 'B cell' and tissue_general == 'lung' and is_primary_data == True",
    obs_column_names=["assay", "disease", "sex", "donor_id"],
)
```

**Pattern: Gene-specific query with multiple genes**
```python
marker_genes = ["CD4", "CD8A", "CD19", "FOXP3"]

# First get gene IDs
gene_metadata = cellxgene_census.get_var(
    census, "homo_sapiens",
    value_filter=f"feature_name in {marker_genes}",
    column_names=["feature_id", "feature_name"]
)
gene_ids = gene_metadata["feature_id"].tolist()

# Query with gene filter
adata = cellxgene_census.get_anndata(
    census=census,
    organism="Homo sapiens",
    var_value_filter=f"feature_id in {gene_ids}",
    obs_value_filter="cell_type == 'T cell' and is_primary_data == True",
)
```

**Pattern: Multi-tissue query**
```python
adata = cellxgene_census.get_anndata(
    census=census,
    organism="Homo sapiens",
    obs_value_filter="tissue_general in ['lung', 'liver', 'kidney'] and is_primary_data == True",
    obs_column_names=["cell_type", "tissue_general", "dataset_id"],
)
```

**Pattern: Disease-specific query**
```python
adata = cellxgene_census.get_anndata(
    census=census,
    organism="Homo sapiens",
    obs_value_filter="disease == 'COVID-19' and tissue_general == 'lung' and is_primary_data == True",
)
```

### 3. Large Queries (Out-of-Core Processing)

Use `axis_query()` for queries that exceed available RAM.

**Pattern: Iterative processing**
```python
import pyarrow as pa

# Create query
query = census["census_data"]["homo_sapiens"].axis_query(
    measurement_name="RNA",
    obs_query=soma.AxisQuery(
        value_filter="tissue_general == 'brain' and is_primary_data == True"
    ),
    var_query=soma.AxisQuery(
        value_filter="feature_name in ['FOXP2', 'TBR1', 'SATB2']"
    )
)

# Iterate through X matrix in chunks
iterator = query.X("raw").tables()
for batch in iterator:
    # Process batch (a pyarrow.Table)
    # batch has columns: soma_data, soma_dim_0, soma_dim_1
    process_batch(batch)
```

**Pattern: Incremental statistics (mean/variance)**
```python
# Using Welford's online algorithm
n = 0
mean = 0
M2 = 0

iterator = query.X("raw").tables()
for batch in iterator:
    values = batch["soma_data"].to_numpy()
    for x in values:
        n += 1
        delta = x - mean
        mean += delta / n
        delta2 = x - mean
        M2 += delta * delta2

variance = M2 / (n - 1) if n > 1 else 0
```

### 4. PyTorch Integration (Machine Learning)

Use `experiment_dataloader()` for training models.

**Pattern: Create training dataloader**
```python
from cellxgene_census.experimental.ml import experiment_dataloader
import torch

with cellxgene_census.open_soma() as census:
    # Create dataloader
    dataloader = experiment_dataloader(
        census["census_data"]["homo_sapiens"],
        measurement_name="RNA",
        X_name="raw",
        obs_value_filter="tissue_general == 'liver' and is_primary_data == True",
        obs_column_names=["cell_type"],
        batch_size=128,
        shuffle=True,
    )

    # Training loop
    for epoch in range(num_epochs):
        for batch in dataloader:
            X = batch["X"]  # Gene expression
            labels = batch["obs"]["cell_type"]  # Cell type labels
            # Train model...
```

**Pattern: Train/test split**
```python
from cellxgene_census.experimental.ml import ExperimentDataset

# Create dataset from query
dataset = ExperimentDataset(
    experiment_axis_query,
    layer_name="raw",
    obs_column_names=["cell_type"],
    batch_size=128,
)

# Split data
train_dataset, test_dataset = dataset.random_split(
    split=[0.8, 0.2],
    seed=42
)

# Create loaders
train_loader = experiment_dataloader(train_dataset)
test_loader = experiment_dataloader(test_dataset)
```

### 5. Integration Workflows

**Pattern: Scanpy integration**
```python
import scanpy as sc

# Load data
adata = cellxgene_census.get_anndata(
    census=census,
    organism="Homo sapiens",
    obs_value_filter="cell_type == 'neuron' and is_primary_data == True",
)

# Standard scanpy workflow
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
sc.pl.umap(adata, color=["cell_type", "tissue_general"])
```

**Pattern: Multi-dataset integration**
```python
# Query multiple datasets separately
datasets_to_integrate = ["dataset_id_1", "dataset_id_2", "dataset_id_3"]

adatas = []
for dataset_id in datasets_to_integrate:
    adata = cellxgene_census.get_anndata(
        census=census,
        organism="Homo sapiens",
        obs_value_filter=f"dataset_id == '{dataset_id}' and is_primary_data == True",
    )
    adatas.append(adata)

# Integrate using scanorama, harmony, or other tools
import scanpy.external as sce
sce.pp.scanorama_integrate(adatas)
```

## Best Practices

### 1. Always Filter for Primary Data
Unless specifically analyzing duplicates, always include `is_primary_data == True`:
```python
obs_value_filter="cell_type == 'B cell' and is_primary_data == True"
```

### 2. Specify Census Version
For reproducible analysis, always specify the Census version:
```python
census = cellxgene_census.open_soma(census_version="2023-07-25")
```

### 3. Use Context Manager
Always use the context manager to ensure proper cleanup:
```python
with cellxgene_census.open_soma() as census:
    # Your code here
```

### 4. Select Only Needed Columns
Minimize data transfer by selecting only required metadata columns:
```python
obs_column_names=["cell_type", "tissue_general", "disease"]  # Not all columns
```

### 5. Check Dataset Presence for Gene Queries
When analyzing specific genes, check which datasets measured them:
```python
presence = cellxgene_census.get_presence_matrix(
    census,
    "homo_sapiens",
    var_value_filter="feature_name in ['CD4', 'CD8A']"
)
```

### 6. Use tissue_general for Broader Queries
`tissue_general` provides coarser groupings than `tissue`, useful for cross-tissue analyses:
```python
# Better for broad queries
obs_value_filter="tissue_general == 'immune system'"

# Use specific tissue when needed
obs_value_filter="tissue == 'peripheral blood mononuclear cell'"
```

### 7. Combine Metadata Exploration with Expression Queries
First explore metadata to understand available data, then query expression:
```python
# Step 1: Explore
metadata = cellxgene_census.get_obs(
    census, "homo_sapiens",
    value_filter="disease == 'COVID-19'",
    column_names=["cell_type", "tissue_general"]
)
print(metadata.value_counts())

# Step 2: Query based on findings
adata = cellxgene_census.get_anndata(
    census=census,
    organism="Homo sapiens",
    obs_value_filter="disease == 'COVID-19' and cell_type == 'T cell' and is_primary_data == True",
)
```

### 8. Memory Management for Large Queries
For large queries, check estimated size before loading:
```python
# Get cell count first
metadata = cellxgene_census.get_obs(
    census, "homo_sapiens",
    value_filter="tissue_general == 'brain' and is_primary_data == True",
    column_names=["soma_joinid"]
)
n_cells = len(metadata)
print(f"Query will return {n_cells} cells")

# If too large, use out-of-core processing or further filtering
```

### 9. Leverage Ontology Terms for Consistency
When possible, use ontology term IDs instead of free text:
```python
# More reliable than cell_type == 'B cell' across datasets
obs_value_filter="cell_type_ontology_term_id == 'CL:0000236'"
```

### 10. Batch Processing Pattern
For systematic analyses across multiple conditions:
```python
tissues = ["lung", "liver", "kidney", "heart"]
results = {}

for tissue in tissues:
    adata = cellxgene_census.get_anndata(
        census=census,
        organism="Homo sapiens",
        obs_value_filter=f"tissue_general == '{tissue}' and is_primary_data == True",
    )
    # Perform analysis
    results[tissue] = analyze(adata)
```

## Common Pitfalls to Avoid

1. **Not filtering for is_primary_data**: Leads to counting duplicate cells
2. **Loading too much data**: Use metadata queries to estimate size first
3. **Not using context manager**: Can cause resource leaks
4. **Inconsistent versioning**: Results not reproducible without specifying version
5. **Overly broad queries**: Start with focused queries, expand as needed
6. **Ignoring dataset presence**: Some genes not measured in all datasets
7. **Wrong count normalization**: Be aware of UMI vs read count differences
