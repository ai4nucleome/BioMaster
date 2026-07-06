## annotation-validation.md

# LaminDB Annotation & Validation

This document covers data curation, validation, schema management, and annotation best practices in LaminDB.

## Overview

LaminDB's curation process ensures datasets are both validated and queryable through three essential steps:

1. **Validation**: Confirming datasets match desired schemas
2. **Standardization**: Fixing inconsistencies like typos and mapping synonyms
3. **Annotation**: Linking datasets to metadata entities for queryability

## Schema Design

Schemas define expected data structure, types, and validation rules. LaminDB supports three main schema approaches:

### 1. Flexible Schema

Validates only columns matching Feature registry names, allowing additional metadata:

```python
import lamindb as ln

# Create flexible schema
schema = ln.Schema(
    name="valid_features",
    itype=ln.Feature  # Validates against Feature registry
).save()

# Any column matching a Feature name will be validated
# Additional columns are permitted but not validated
```

### 2. Minimal Required Schema

Specifies essential columns while permitting extra metadata:

```python
# Define required features
required_features = [
    ln.Feature.get(name="cell_type"),
    ln.Feature.get(name="tissue"),
    ln.Feature.get(name="donor_id")
]

# Create schema with required features
schema = ln.Schema(
    name="minimal_immune_schema",
    features=required_features,
    flexible=True  # Allows additional columns
).save()
```

### 3. Strict Schema

Enforces complete control over data structure:

```python
# Define all allowed features
all_features = [
    ln.Feature.get(name="cell_type"),
    ln.Feature.get(name="tissue"),
    ln.Feature.get(name="donor_id"),
    ln.Feature.get(name="disease")
]

# Create strict schema
schema = ln.Schema(
    name="strict_immune_schema",
    features=all_features,
    flexible=False  # No additional columns allowed
).save()
```

## DataFrame Curation Workflow

The typical curation process involves six key steps:

### Step 1-2: Load Data and Establish Registries

```python
import pandas as pd
import lamindb as ln

# Load data
df = pd.read_csv("experiment.csv")

# Define and save features
ln.Feature(name="cell_type", dtype=str).save()
ln.Feature(name="tissue", dtype=str).save()
ln.Feature(name="gene_count", dtype=int).save()
ln.Feature(name="experiment_date", dtype="date").save()

# Populate valid values (if using controlled vocabulary)
import bionty as bt
bt.CellType.import_source()
bt.Tissue.import_source()
```

### Step 3: Create Schema

```python
# Link features to schema
features = [
    ln.Feature.get(name="cell_type"),
    ln.Feature.get(name="tissue"),
    ln.Feature.get(name="gene_count"),
    ln.Feature.get(name="experiment_date")
]

schema = ln.Schema(
    name="experiment_schema",
    features=features,
    flexible=True
).save()
```

### Step 4: Initialize Curator and Validate

```python
# Initialize curator
curator = ln.curators.DataFrameCurator(df, schema)

# Validate dataset
validation = curator.validate()

# Check validation results
if validation:
    print("✓ Validation passed")
else:
    print("✗ Validation failed")
    curator.non_validated  # See problematic fields
```

### Step 5: Fix Validation Issues

#### Standardize Values

```python
# Fix typos and synonyms in categorical columns
curator.cat.standardize("cell_type")
curator.cat.standardize("tissue")

# View standardization mapping
curator.cat.inspect_standardize("cell_type")
```

#### Map to Ontologies

```python
# Map values to ontology terms
curator.cat.add_ontology("cell_type", bt.CellType)
curator.cat.add_ontology("tissue", bt.Tissue)

# Look up public ontologies for unmapped terms
curator.cat.lookup(public=True).cell_type  # Interactive lookup
```

#### Add New Terms

```python
# Add new valid terms to registry
curator.cat.add_new_from("cell_type")

# Or manually create records
new_cell_type = bt.CellType(name="my_novel_cell_type").save()
```

#### Rename Columns

```python
# Rename columns to match feature names
df = df.rename(columns={"celltype": "cell_type"})

# Re-initialize curator with fixed DataFrame
curator = ln.curators.DataFrameCurator(df, schema)
```

### Step 6: Save Curated Artifact

```python
# Save with schema linkage
artifact = curator.save_artifact(
    key="experiments/curated_data.parquet",
    description="Validated and annotated experimental data"
)

# Verify artifact has schema
artifact.schema  # Returns the schema object
artifact.describe()  # Shows validation status
```

## AnnData Curation

For composite structures like AnnData, use "slots" to validate different components:

### Defining AnnData Schemas

```python
# Create schemas for different slots
obs_schema = ln.Schema(
    name="cell_metadata",
    features=[
        ln.Feature.get(name="cell_type"),
        ln.Feature.get(name="tissue"),
        ln.Feature.get(name="donor_id")
    ]
).save()

var_schema = ln.Schema(
    name="gene_ids",
    features=[ln.Feature.get(name="ensembl_gene_id")]
).save()

# Create composite AnnData schema
anndata_schema = ln.Schema(
    name="scrna_schema",
    otype="AnnData",
    slots={
        "obs": obs_schema,
        "var.T": var_schema  # .T indicates transposition
    }
).save()
```

### Curating AnnData Objects

```python
import anndata as ad

# Load AnnData
adata = ad.read_h5ad("data.h5ad")

# Initialize curator
curator = ln.curators.AnnDataCurator(adata, anndata_schema)

# Validate all slots
validation = curator.validate()

# Fix issues by slot
curator.cat.standardize("obs", "cell_type")
curator.cat.add_ontology("obs", "cell_type", bt.CellType)
curator.cat.standardize("var.T", "ensembl_gene_id")

# Save curated artifact
artifact = curator.save_artifact(
    key="scrna/validated_data.h5ad",
    description="Curated single-cell RNA-seq data"
)
```

## MuData Curation

MuData supports multi-modal data through modality-specific slots:

```python
# Define schemas for each modality
rna_obs_schema = ln.Schema(name="rna_obs_schema", features=[...]).save()
protein_obs_schema = ln.Schema(name="protein_obs_schema", features=[...]).save()

# Create MuData schema
mudata_schema = ln.Schema(
    name="multimodal_schema",
    otype="MuData",
    slots={
        "rna:obs": rna_obs_schema,
        "protein:obs": protein_obs_schema
    }
).save()

# Curate
curator = ln.curators.MuDataCurator(mdata, mudata_schema)
curator.validate()
```

## SpatialData Curation

For spatial transcriptomics data:

```python
# Define spatial schema
spatial_schema = ln.Schema(
    name="spatial_schema",
    otype="SpatialData",
    slots={
        "tables:cell_metadata.obs": cell_schema,
        "attrs:bio": bio_metadata_schema
    }
).save()

# Curate
curator = ln.curators.SpatialDataCurator(sdata, spatial_schema)
curator.validate()
```

## TileDB-SOMA Curation

For scalable array-backed data:

```python
# Define SOMA schema
soma_schema = ln.Schema(
    name="soma_schema",
    otype="tiledbsoma",
    slots={
        "obs": obs_schema,
        "ms:RNA.T": var_schema  # measurement:modality.T
    }
).save()

# Curate
curator = ln.curators.TileDBSOMACurator(soma_exp, soma_schema)
curator.validate()
```

## Feature Validation

### Data Type Validation

```python
# Define typed features
ln.Feature(name="age", dtype=int).save()
ln.Feature(name="weight", dtype=float).save()
ln.Feature(name="is_treated", dtype=bool).save()
ln.Feature(name="collection_date", dtype="date").save()

# Coerce types during validation
ln.Feature(name="age_str", dtype=int, coerce_dtype=True).save()  # Auto-convert strings to int
```

### Value Validation

```python
# Validate against allowed values
cell_type_feature = ln.Feature(name="cell_type", dtype=str).save()

# Link to registry for controlled vocabulary
cell_type_feature.link_to_registry(bt.CellType)

# Now validation checks against CellType registry
curator = ln.curators.DataFrameCurator(df, schema)
curator.validate()  # Errors if cell_type values not in registry
```

## Standardization Strategies

### Using Public Ontologies

```python
# Look up standardized terms from public sources
curator.cat.lookup(public=True).cell_type

# Returns auto-complete object with public ontology terms
# User can select correct term interactively
```

### Synonym Mapping

```python
# Add synonyms to records
t_cell = bt.CellType.get(name="T cell")
t_cell.add_synonym("T lymphocyte")
t_cell.add_synonym("T-cell")

# Now standardization maps synonyms automatically
curator.cat.standardize("cell_type")
# "T lymphocyte" → "T cell"
# "T-cell" → "T cell"
```

### Custom Standardization

```python
# Manual mapping
mapping = {
    "TCell": "T cell",
    "t cell": "T cell",
    "T-cells": "T cell"
}

# Apply mapping
df["cell_type"] = df["cell_type"].map(lambda x: mapping.get(x, x))
```

## Handling Validation Errors

### Common Issues and Solutions

**Issue: Column not in schema**
```python
# Solution 1: Rename column
df = df.rename(columns={"old_name": "feature_name"})

# Solution 2: Add feature to schema
new_feature = ln.Feature(name="new_column", dtype=str).save()
schema.features.add(new_feature)
```

**Issue: Invalid values**
```python
# Solution 1: Standardize
curator.cat.standardize("column_name")

# Solution 2: Add new valid values
curator.cat.add_new_from("column_name")

# Solution 3: Map to ontology
curator.cat.add_ontology("column_name", bt.Registry)
```

**Issue: Data type mismatch**
```python
# Solution 1: Convert data type
df["column"] = df["column"].astype(int)

# Solution 2: Enable coercion in feature
feature = ln.Feature.get(name="column")
feature.coerce_dtype = True
feature.save()
```

## Schema Versioning

Schemas can be versioned like other records:

```python
# Create initial schema
schema_v1 = ln.Schema(name="experiment_schema", features=[...]).save()

# Update schema with new features
schema_v2 = ln.Schema(
    name="experiment_schema",
    features=[...],  # Updated list
    version="2"
).save()

# Link artifacts to specific schema versions
artifact.schema = schema_v2
artifact.save()
```

## Querying Validated Data

Once data is validated and annotated, it becomes queryable:

```python
# Find all validated artifacts
ln.Artifact.filter(is_valid=True).to_dataframe()

# Find artifacts with specific schema
ln.Artifact.filter(schema=schema).to_dataframe()

# Query by annotated features
ln.Artifact.filter(cell_type="T cell", tissue="blood").to_dataframe()

# Include features in results
ln.Artifact.filter(is_valid=True).to_dataframe(include="features")
```

## Best Practices

1. **Define features first**: Create Feature registry before curation
2. **Use public ontologies**: Leverage bt.lookup(public=True) for standardization
3. **Start flexible**: Use flexible schemas initially, tighten as understanding grows
4. **Document slots**: Clearly specify transposition (.T) in composite schemas
5. **Standardize early**: Fix typos and synonyms before validation
6. **Validate incrementally**: Check each slot separately for composite structures
7. **Version schemas**: Track schema changes over time
8. **Add synonyms**: Register common variations to simplify future curation
9. **Coerce types cautiously**: Enable dtype coercion only when safe
10. **Test on samples**: Validate small subsets before full dataset curation

## Advanced: Custom Validators

Create custom validation logic:

```python
def validate_gene_expression(df):
    """Custom validator for gene expression values."""
    # Check non-negative
    if (df < 0).any().any():
        return False, "Negative expression values found"

    # Check reasonable range
    if (df > 1e6).any().any():
        return False, "Unreasonably high expression values"

    return True, "Valid"

# Apply during curation
is_valid, message = validate_gene_expression(df)
if not is_valid:
    print(f"Validation failed: {message}")
```

## Tracking Curation Provenance

```python
# Curated artifacts track curation lineage
ln.track()  # Start tracking

# Perform curation
curator = ln.curators.DataFrameCurator(df, schema)
curator.validate()
curator.cat.standardize("cell_type")
artifact = curator.save_artifact(key="curated.parquet")

ln.finish()  # Complete tracking

# View curation lineage
artifact.run.describe()  # Shows curation transform
artifact.view_lineage()  # Visualizes curation process
```

---

## core-concepts.md

# LaminDB Core Concepts

This document covers the fundamental concepts and building blocks of LaminDB: Artifacts, Records, Runs, Transforms, Features, and data lineage tracking.

## Artifacts

Artifacts represent datasets in various formats (DataFrames, AnnData, SpatialData, Parquet, Zarr, etc.). They serve as the primary data objects in LaminDB.

### Creating and Saving Artifacts

**From file:**
```python
import lamindb as ln

# Save a file as artifact
ln.Artifact("sample.fasta", key="sample.fasta").save()

# With description
artifact = ln.Artifact(
    "data/analysis.h5ad",
    key="experiments/scrna_batch1.h5ad",
    description="Single-cell RNA-seq batch 1"
).save()
```

**From DataFrame:**
```python
import pandas as pd

df = pd.read_csv("data.csv")
artifact = ln.Artifact.from_dataframe(
    df,
    key="datasets/processed_data.parquet",
    description="Processed experimental data"
).save()
```

**From AnnData:**
```python
import anndata as ad

adata = ad.read_h5ad("data.h5ad")
artifact = ln.Artifact.from_anndata(
    adata,
    key="scrna/experiment1.h5ad",
    description="scRNA-seq data with QC"
).save()
```

### Retrieving Artifacts

```python
# By key
artifact = ln.Artifact.get(key="sample.fasta")

# By UID
artifact = ln.Artifact.get("aRt1Fact0uid000")

# By filter
artifact = ln.Artifact.filter(suffix=".h5ad").first()
```

### Accessing Artifact Content

```python
# Get cached local path
local_path = artifact.cache()

# Load into memory
data = artifact.load()  # Returns DataFrame, AnnData, etc.

# Streaming access (for large files)
with artifact.open() as f:
    # Read incrementally
    chunk = f.read(1000)
```

### Artifact Metadata

```python
# View all metadata
artifact.describe()

# Access specific metadata
artifact.size          # File size in bytes
artifact.suffix        # File extension
artifact.created_at    # Timestamp
artifact.created_by    # User who created it
artifact.run          # Associated run
artifact.transform    # Associated transform
artifact.version      # Version string
```

## Records

Records represent experimental entities: samples, perturbations, instruments, cell lines, and any other metadata entities. They support hierarchical relationships through type definitions.

### Creating Records

```python
# Define a type
sample_type = ln.Record(name="Sample", is_type=True).save()

# Create instances of that type
ln.Record(name="P53mutant1", type=sample_type).save()
ln.Record(name="P53mutant2", type=sample_type).save()
ln.Record(name="WT-control", type=sample_type).save()
```

### Searching Records

```python
# Text search
ln.Record.search("p53").to_dataframe()

# Filter by fields
ln.Record.filter(type=sample_type).to_dataframe()

# Get specific record
record = ln.Record.get(name="P53mutant1")
```

### Hierarchical Relationships

```python
# Establish parent-child relationships
parent_record = ln.Record.get(name="P53mutant1")
child_record = ln.Record(name="P53mutant1-replicate1", type=sample_type).save()
child_record.parents.add(parent_record)

# Query relationships
parent_record.children.to_dataframe()
child_record.parents.to_dataframe()
```

## Runs & Transforms

These capture computational lineage. A **Transform** represents a reusable analysis step (notebook, script, or function), while a **Run** documents a specific execution instance.

### Basic Tracking Workflow

```python
import lamindb as ln

# Start tracking (beginning of notebook/script)
ln.track()

# Your analysis code
data = ln.Artifact.get(key="input.csv").load()
# ... perform analysis ...
result.to_csv("output.csv")
artifact = ln.Artifact("output.csv", key="output.csv").save()

# Finish tracking (end of notebook/script)
ln.finish()
```

### Tracking with Parameters

```python
ln.track(params={
    "learning_rate": 0.01,
    "batch_size": 32,
    "epochs": 100,
    "downsample": True
})

# Query runs by parameters
ln.Run.filter(params__learning_rate=0.01).to_dataframe()
ln.Run.filter(params__downsample=True).to_dataframe()
```

### Tracking with Projects

```python
# Associate with project
ln.track(project="Cancer Drug Screen 2025")

# Query by project
project = ln.Project.get(name="Cancer Drug Screen 2025")
ln.Artifact.filter(projects=project).to_dataframe()
ln.Run.filter(project=project).to_dataframe()
```

### Function-Level Tracking

Use the `@ln.tracked()` decorator for fine-grained lineage:

```python
@ln.tracked()
def preprocess_data(input_key: str, output_key: str, normalize: bool = True) -> None:
    """Preprocess raw data and save result."""
    # Load input (automatically tracked)
    artifact = ln.Artifact.get(key=input_key)
    data = artifact.load()

    # Process
    if normalize:
        data = (data - data.mean()) / data.std()

    # Save output (automatically tracked)
    ln.Artifact.from_dataframe(data, key=output_key).save()

# Each call creates a separate Transform and Run
preprocess_data("raw/batch1.csv", "processed/batch1.csv", normalize=True)
preprocess_data("raw/batch2.csv", "processed/batch2.csv", normalize=False)
```

### Accessing Lineage Information

```python
# From artifact to run
artifact = ln.Artifact.get(key="output.csv")
run = artifact.run
transform = run.transform

# View details
run.describe()          # Run metadata
transform.describe()    # Transform metadata

# Access inputs
run.inputs.to_dataframe()

# Visualize lineage graph
artifact.view_lineage()
```

## Features

Features define typed metadata fields for validation and querying. They enable structured annotation and searching.

### Defining Features

```python
from datetime import date

# Numeric feature
ln.Feature(name="gc_content", dtype=float).save()
ln.Feature(name="read_count", dtype=int).save()

# Date feature
ln.Feature(name="experiment_date", dtype=date).save()

# Categorical feature
ln.Feature(name="cell_type", dtype=str).save()
ln.Feature(name="treatment", dtype=str).save()
```

### Annotating Artifacts with Features

```python
# Single values
artifact.features.add_values({
    "gc_content": 0.55,
    "experiment_date": "2025-10-31"
})

# Using feature registry records
gc_content_feature = ln.Feature.get(name="gc_content")
artifact.features.add(gc_content_feature)
```

### Querying by Features

```python
# Filter by feature value
ln.Artifact.filter(gc_content=0.55).to_dataframe()
ln.Artifact.filter(experiment_date="2025-10-31").to_dataframe()

# Comparison operators
ln.Artifact.filter(read_count__gt=1000000).to_dataframe()
ln.Artifact.filter(gc_content__gte=0.5, gc_content__lte=0.6).to_dataframe()

# Check for presence of annotation
ln.Artifact.filter(cell_type__isnull=False).to_dataframe()

# Include features in output
ln.Artifact.filter(treatment="DMSO").to_dataframe(include="features")
```

### Nested Dictionary Features

For complex metadata stored as dictionaries:

```python
# Access nested values
ln.Artifact.filter(study_metadata__detail1="123").to_dataframe()
ln.Artifact.filter(study_metadata__assay__type="RNA-seq").to_dataframe()
```

## Data Lineage Tracking

LaminDB automatically captures execution context and relationships between data, code, and runs.

### What Gets Tracked

- **Source code**: Script/notebook content and git commit
- **Environment**: Python packages and versions
- **Input artifacts**: Data loaded during execution
- **Output artifacts**: Data created during execution
- **Execution metadata**: Timestamps, user, parameters
- **Computational dependencies**: Transform relationships

### Viewing Lineage

```python
# Visualize full lineage graph
artifact.view_lineage()

# View captured metadata
artifact.describe()

# Access related entities
artifact.run              # The run that created it
artifact.run.transform    # The transform (code) used
artifact.run.inputs       # Input artifacts
artifact.run.report       # Execution report
```

### Querying Lineage

```python
# Find all outputs from a transform
transform = ln.Transform.get(name="preprocessing.py")
ln.Artifact.filter(transform=transform).to_dataframe()

# Find all artifacts from a specific user
user = ln.User.get(handle="researcher123")
ln.Artifact.filter(created_by=user).to_dataframe()

# Find artifacts using specific inputs
input_artifact = ln.Artifact.get(key="raw/data.csv")
runs = ln.Run.filter(inputs=input_artifact)
ln.Artifact.filter(run__in=runs).to_dataframe()
```

## Versioning

LaminDB manages artifact versioning automatically when source data or code changes.

### Automatic Versioning

```python
# First version
artifact_v1 = ln.Artifact("data.csv", key="experiment/data.csv").save()

# Modify and save again - creates new version
# (modify data.csv)
artifact_v2 = ln.Artifact("data.csv", key="experiment/data.csv").save()
```

### Working with Versions

```python
# Get latest version (default)
artifact = ln.Artifact.get(key="experiment/data.csv")

# View all versions
artifact.versions.to_dataframe()

# Get specific version
artifact_v1 = artifact.versions.filter(version="1").first()

# Compare versions
v1_data = artifact_v1.load()
v2_data = artifact.load()
```

## Best Practices

1. **Use meaningful keys**: Structure keys hierarchically (e.g., `project/experiment/sample.h5ad`)
2. **Add descriptions**: Help future users understand artifact contents
3. **Track consistently**: Call `ln.track()` at the start of every analysis
4. **Define features upfront**: Create feature registry before annotation
5. **Use typed features**: Specify dtypes for better validation
6. **Leverage versioning**: Don't create new keys for minor changes
7. **Document transforms**: Add docstrings to tracked functions
8. **Set projects**: Group related work for easier organization and access control
9. **Query efficiently**: Use filters before loading large datasets
10. **Visualize lineage**: Use `view_lineage()` to understand data provenance

---

## data-management.md

# LaminDB Data Management

This document covers querying, searching, filtering, and streaming data in LaminDB, as well as best practices for organizing and accessing datasets.

## Registry Overview

View available registries and their contents:

```python
import lamindb as ln

# View all registries across modules
ln.view()

# View latest 100 artifacts
ln.Artifact.to_dataframe()

# View other registries
ln.Transform.to_dataframe()
ln.Run.to_dataframe()
ln.User.to_dataframe()
```

## Lookup for Quick Access

For registries with fewer than 100k records, `Lookup` objects enable convenient auto-complete:

```python
# Create lookup
records = ln.Record.lookup()

# Access by name (auto-complete enabled in IDEs)
experiment_1 = records.experiment_1
sample_a = records.sample_a

# Works with biological ontologies too
import bionty as bt
cell_types = bt.CellType.lookup()
t_cell = cell_types.t_cell
```

## Retrieving Single Records

### Using get()

Retrieve exactly one record (errors if zero or multiple matches):

```python
# By UID
artifact = ln.Artifact.get("aRt1Fact0uid000")

# By field
artifact = ln.Artifact.get(key="data/experiment.h5ad")
user = ln.User.get(handle="researcher123")

# By ontology ID (for bionty)
cell_type = bt.CellType.get(ontology_id="CL:0000084")
```

### Using one() and one_or_none()

```python
# Get exactly one from QuerySet (errors if 0 or >1)
artifact = ln.Artifact.filter(key="data.csv").one()

# Get one or None (errors if >1)
artifact = ln.Artifact.filter(key="maybe_data.csv").one_or_none()

# Get first match
artifact = ln.Artifact.filter(suffix=".h5ad").first()
```

## Filtering Data

The `filter()` method returns a QuerySet for flexible retrieval:

```python
# Basic filtering
artifacts = ln.Artifact.filter(suffix=".h5ad")
artifacts.to_dataframe()

# Multiple conditions (AND logic)
artifacts = ln.Artifact.filter(
    suffix=".h5ad",
    created_by=user
)

# Comparison operators
ln.Artifact.filter(size__gt=1e6).to_dataframe()           # Greater than
ln.Artifact.filter(size__gte=1e6).to_dataframe()          # Greater than or equal
ln.Artifact.filter(size__lt=1e9).to_dataframe()           # Less than
ln.Artifact.filter(size__lte=1e9).to_dataframe()          # Less than or equal

# Range queries
ln.Artifact.filter(size__gte=1e6, size__lte=1e9).to_dataframe()
```

## Text and String Queries

```python
# Exact match
ln.Artifact.filter(description="Experiment 1").to_dataframe()

# Contains (case-sensitive)
ln.Artifact.filter(description__contains="RNA").to_dataframe()

# Case-insensitive contains
ln.Artifact.filter(description__icontains="rna").to_dataframe()

# Starts with
ln.Artifact.filter(key__startswith="experiments/").to_dataframe()

# Ends with
ln.Artifact.filter(key__endswith=".csv").to_dataframe()

# IN list
ln.Artifact.filter(suffix__in=[".h5ad", ".csv", ".parquet"]).to_dataframe()
```

## Feature-Based Queries

Query artifacts by their annotated features:

```python
# Filter by feature value
ln.Artifact.filter(cell_type="T cell").to_dataframe()
ln.Artifact.filter(treatment="DMSO").to_dataframe()

# Include features in output
ln.Artifact.filter(treatment="DMSO").to_dataframe(include="features")

# Nested dictionary access
ln.Artifact.filter(study_metadata__assay="RNA-seq").to_dataframe()
ln.Artifact.filter(study_metadata__detail1="123").to_dataframe()

# Check annotation status
ln.Artifact.filter(cell_type__isnull=False).to_dataframe()  # Has annotation
ln.Artifact.filter(treatment__isnull=True).to_dataframe()    # Missing annotation
```

## Traversing Related Registries

Django's double-underscore syntax enables queries across related tables:

```python
# Find artifacts by creator handle
ln.Artifact.filter(created_by__handle="researcher123").to_dataframe()
ln.Artifact.filter(created_by__handle__startswith="test").to_dataframe()

# Find artifacts by transform name
ln.Artifact.filter(transform__name="preprocess.py").to_dataframe()

# Find artifacts measuring specific genes
ln.Artifact.filter(feature_sets__genes__symbol="CD8A").to_dataframe()
ln.Artifact.filter(feature_sets__genes__ensembl_gene_id="ENSG00000153563").to_dataframe()

# Find runs with specific parameters
ln.Run.filter(params__learning_rate=0.01).to_dataframe()
ln.Run.filter(params__downsample=True).to_dataframe()

# Find artifacts from specific project
project = ln.Project.get(name="Cancer Study")
ln.Artifact.filter(projects=project).to_dataframe()
```

## Ordering Results

```python
# Order by field (ascending)
ln.Artifact.filter(suffix=".h5ad").order_by("created_at").to_dataframe()

# Order descending
ln.Artifact.filter(suffix=".h5ad").order_by("-created_at").to_dataframe()

# Multiple order fields
ln.Artifact.order_by("-created_at", "size").to_dataframe()
```

## Advanced Logical Queries

### OR Logic

```python
from lamindb import Q

# OR condition
artifacts = ln.Artifact.filter(
    Q(suffix=".jpg") | Q(suffix=".png")
).to_dataframe()

# Complex OR with multiple conditions
artifacts = ln.Artifact.filter(
    Q(suffix=".h5ad", size__gt=1e6) | Q(suffix=".csv", size__lt=1e3)
).to_dataframe()
```

### NOT Logic

```python
# Exclude condition
artifacts = ln.Artifact.filter(
    ~Q(suffix=".tmp")
).to_dataframe()

# Complex exclusion
artifacts = ln.Artifact.filter(
    ~Q(created_by__handle="testuser")
).to_dataframe()
```

### Combining AND, OR, NOT

```python
# Complex query
artifacts = ln.Artifact.filter(
    (Q(suffix=".h5ad") | Q(suffix=".csv")) &
    Q(size__gt=1e6) &
    ~Q(created_by__handle__startswith="test")
).to_dataframe()
```

## Search Functionality

Full-text search across registry fields:

```python
# Basic search
ln.Artifact.search("iris").to_dataframe()
ln.User.search("smith").to_dataframe()

# Search in specific registry
bt.CellType.search("T cell").to_dataframe()
bt.Gene.search("CD8").to_dataframe()
```

## Working with QuerySets

QuerySets are lazy - they don't hit the database until evaluated:

```python
# Create query (no database hit)
qs = ln.Artifact.filter(suffix=".h5ad")

# Evaluate in different ways
df = qs.to_dataframe()        # As pandas DataFrame
list_records = list(qs)       # As Python list
count = qs.count()            # Count only
exists = qs.exists()          # Boolean check

# Iteration
for artifact in qs:
    print(artifact.key, artifact.size)

# Slicing
first_10 = qs[:10]
next_10 = qs[10:20]
```

## Chaining Filters

```python
# Build query incrementally
qs = ln.Artifact.filter(suffix=".h5ad")
qs = qs.filter(size__gt=1e6)
qs = qs.filter(created_at__year=2025)
qs = qs.order_by("-created_at")

# Execute
results = qs.to_dataframe()
```

## Streaming Large Datasets

For datasets too large to fit in memory, use streaming access:

### Streaming Files

```python
# Open file stream
artifact = ln.Artifact.get(key="large_file.csv")

with artifact.open() as f:
    # Read in chunks
    chunk = f.read(10000)  # Read 10KB
    # Process chunk
```

### Array Slicing

For array-based formats (Zarr, HDF5, AnnData):

```python
# Get backing file without loading
artifact = ln.Artifact.get(key="large_data.h5ad")
adata = artifact.backed()  # Returns backed AnnData

# Slice specific portions
subset = adata[:1000, :]  # First 1000 cells
genes_of_interest = adata[:, ["CD4", "CD8A", "CD8B"]]

# Stream batches
for i in range(0, adata.n_obs, 1000):
    batch = adata[i:i+1000, :]
    # Process batch
```

### Iterator Access

```python
# Process large collections incrementally
artifacts = ln.Artifact.filter(suffix=".fastq.gz")

for artifact in artifacts.iterator(chunk_size=10):
    # Process 10 at a time
    path = artifact.cache()
    # Analyze file
```

## Aggregation and Statistics

```python
# Count records
ln.Artifact.filter(suffix=".h5ad").count()

# Distinct values
ln.Artifact.values_list("suffix", flat=True).distinct()

# Aggregation (requires Django ORM knowledge)
from django.db.models import Sum, Avg, Max, Min

# Total size of all artifacts
ln.Artifact.aggregate(Sum("size"))

# Average artifact size by suffix
ln.Artifact.values("suffix").annotate(avg_size=Avg("size"))
```

## Caching and Performance

```python
# Check cache location
ln.settings.cache_dir

# Configure cache
lamin cache set /path/to/cache

# Clear cache for specific artifact
artifact.delete_cache()

# Get cached path (downloads if needed)
path = artifact.cache()

# Check if cached
if artifact.is_cached():
    path = artifact.cache()
```

## Organizing Data with Keys

Best practices for structuring keys:

```python
# Hierarchical organization
ln.Artifact("data.h5ad", key="project/experiment/batch1/data.h5ad").save()
ln.Artifact("data.h5ad", key="scrna/2025/oct/sample_001.h5ad").save()

# Browse by prefix
ln.Artifact.filter(key__startswith="scrna/2025/oct/").to_dataframe()

# Version in key (alternative to built-in versioning)
ln.Artifact("data.h5ad", key="data/processed/v1/final.h5ad").save()
ln.Artifact("data.h5ad", key="data/processed/v2/final.h5ad").save()
```

## Collections

Group related artifacts into collections:

```python
# Create collection
collection = ln.Collection(
    [artifact1, artifact2, artifact3],
    name="scRNA-seq batch 1-3",
    description="Complete dataset across three batches"
).save()

# Access collection members
for artifact in collection.artifacts:
    print(artifact.key)

# Query collections
ln.Collection.filter(name__contains="batch").to_dataframe()
```

## Best Practices

1. **Use filters before loading**: Query metadata before accessing file contents
2. **Leverage QuerySets**: Build queries incrementally for complex conditions
3. **Stream large files**: Don't load entire datasets into memory unnecessarily
4. **Structure keys hierarchically**: Makes browsing and filtering easier
5. **Use search for discovery**: When you don't know exact field values
6. **Cache strategically**: Configure cache location based on storage capacity
7. **Index features**: Define features upfront for efficient feature-based queries
8. **Use collections**: Group related artifacts for dataset-level operations
9. **Order results**: Sort by creation date or other fields for consistent retrieval
10. **Check existence**: Use `exists()` or `one_or_none()` to avoid errors

## Common Query Patterns

```python
# Recent artifacts
ln.Artifact.order_by("-created_at")[:10].to_dataframe()

# My artifacts
me = ln.setup.settings.user
ln.Artifact.filter(created_by=me).to_dataframe()

# Large files
ln.Artifact.filter(size__gt=1e9).order_by("-size").to_dataframe()

# This month's data
from datetime import datetime
ln.Artifact.filter(
    created_at__year=2025,
    created_at__month=10
).to_dataframe()

# Validated datasets with specific features
ln.Artifact.filter(
    is_valid=True,
    cell_type__isnull=False
).to_dataframe(include="features")
```

---

## integrations.md

# LaminDB Integrations

This document covers LaminDB integrations with workflow managers, MLOps platforms, visualization tools, and other third-party systems.

## Overview

LaminDB supports extensive integrations across data storage, computational workflows, machine learning platforms, and visualization tools, enabling seamless incorporation into existing data science and bioinformatics pipelines.

## Data Storage Integrations

### Local Filesystem

```python
import lamindb as ln

# Initialize with local storage
lamin init --storage ./mydata

# Save artifacts to local storage
artifact = ln.Artifact("data.csv", key="local/data.csv").save()

# Load from local storage
data = artifact.load()
```

### AWS S3

```python
# Initialize with S3 storage
lamin init --storage s3://my-bucket/path \
  --db postgresql://user:pwd@host:port/db

# Artifacts automatically sync to S3
artifact = ln.Artifact("data.csv", key="experiments/data.csv").save()

# Transparent S3 access
data = artifact.load()  # Downloads from S3 if not cached
```

### S3-Compatible Services

Support for MinIO, Cloudflare R2, and other S3-compatible endpoints:

```python
# Initialize with custom S3 endpoint
lamin init --storage 's3://bucket?endpoint_url=http://minio.example.com:9000'

# Configure credentials
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
```

### Google Cloud Storage

```python
# Install GCP extras
pip install 'lamindb[gcp]'

# Initialize with GCS
lamin init --storage gs://my-bucket/path \
  --db postgresql://user:pwd@host:port/db

# Artifacts sync to GCS
artifact = ln.Artifact("data.csv", key="experiments/data.csv").save()
```

### HTTP/HTTPS (Read-Only)

```python
# Access remote files without copying
artifact = ln.Artifact(
    "https://example.com/data.csv",
    key="remote/data.csv"
).save()

# Stream remote content
with artifact.open() as f:
    data = f.read()
```

### HuggingFace Datasets

```python
# Access HuggingFace datasets
from datasets import load_dataset

dataset = load_dataset("squad", split="train")

# Register as LaminDB artifact
artifact = ln.Artifact.from_dataframe(
    dataset.to_pandas(),
    key="hf/squad_train.parquet",
    description="SQuAD training data from HuggingFace"
).save()
```

## Workflow Manager Integrations

### Nextflow

Track Nextflow pipeline execution and outputs:

```python
# In your Nextflow process script
import lamindb as ln

# Initialize tracking
ln.track()

# Your Nextflow process logic
input_artifact = ln.Artifact.get(key="${input_key}")
data = input_artifact.load()

# Process data
result = process_data(data)

# Save output
output_artifact = ln.Artifact.from_dataframe(
    result,
    key="${output_key}"
).save()

ln.finish()
```

**Nextflow config example:**
```nextflow
process ANALYZE {
    input:
    val input_key

    output:
    path "result.csv"

    script:
    """
    #!/usr/bin/env python
    import lamindb as ln
    ln.track()
    artifact = ln.Artifact.get(key="${input_key}")
    # Process and save
    ln.finish()
    """
}
```

### Snakemake

Integrate LaminDB into Snakemake workflows:

```python
# In Snakemake rule
rule process_data:
    input:
        "data/input.csv"
    output:
        "data/output.csv"
    run:
        import lamindb as ln

        ln.track()

        # Load input artifact
        artifact = ln.Artifact.get(key="inputs/data.csv")
        data = artifact.load()

        # Process
        result = analyze(data)

        # Save output
        result.to_csv(output[0])
        ln.Artifact(output[0], key="outputs/result.csv").save()

        ln.finish()
```

### Redun

Track Redun task execution:

```python
from redun import task
import lamindb as ln

@task()
@ln.tracked()
def process_dataset(input_key: str, output_key: str):
    """Redun task with LaminDB tracking."""
    # Load input
    artifact = ln.Artifact.get(key=input_key)
    data = artifact.load()

    # Process
    result = transform(data)

    # Save output
    ln.Artifact.from_dataframe(result, key=output_key).save()

    return output_key

# Redun automatically tracks lineage alongside LaminDB
```

## MLOps Platform Integrations

### Weights & Biases (W&B)

Combine W&B experiment tracking with LaminDB data management:

```python
import wandb
import lamindb as ln

# Initialize both
wandb.init(project="my-project", name="experiment-1")
ln.track(params={"learning_rate": 0.01, "batch_size": 32})

# Load training data
train_artifact = ln.Artifact.get(key="datasets/train.parquet")
train_data = train_artifact.load()

# Train model
model = train_model(train_data)

# Log to W&B
wandb.log({"accuracy": 0.95, "loss": 0.05})

# Save model in LaminDB
import joblib
joblib.dump(model, "model.pkl")
model_artifact = ln.Artifact(
    "model.pkl",
    key="models/experiment-1.pkl",
    description=f"Model from W&B run {wandb.run.id}"
).save()

# Link W&B run ID
model_artifact.features.add_values({"wandb_run_id": wandb.run.id})

ln.finish()
wandb.finish()
```

### MLflow

Integrate MLflow model tracking with LaminDB:

```python
import mlflow
import lamindb as ln

# Start runs
mlflow.start_run()
ln.track()

# Log parameters to both
params = {"max_depth": 5, "n_estimators": 100}
mlflow.log_params(params)
ln.context.params = params

# Load data from LaminDB
data_artifact = ln.Artifact.get(key="datasets/features.parquet")
X = data_artifact.load()

# Train and log model
model = train_model(X)
mlflow.sklearn.log_model(model, "model")

# Save to LaminDB
import joblib
joblib.dump(model, "model.pkl")
model_artifact = ln.Artifact(
    "model.pkl",
    key=f"models/{mlflow.active_run().info.run_id}.pkl"
).save()

mlflow.end_run()
ln.finish()
```

### HuggingFace Transformers

Track model fine-tuning with LaminDB:

```python
from transformers import Trainer, TrainingArguments
import lamindb as ln

ln.track(params={"model": "bert-base", "epochs": 3})

# Load training data
train_artifact = ln.Artifact.get(key="datasets/train_tokenized.parquet")
train_dataset = train_artifact.load()

# Configure trainer
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

# Train
trainer.train()

# Save model to LaminDB
trainer.save_model("./model")
model_artifact = ln.Artifact(
    "./model",
    key="models/bert_finetuned",
    description="BERT fine-tuned on custom dataset"
).save()

ln.finish()
```

### scVI-tools

Single-cell analysis with scVI and LaminDB:

```python
import scvi
import lamindb as ln

ln.track()

# Load data
adata_artifact = ln.Artifact.get(key="scrna/raw_counts.h5ad")
adata = adata_artifact.load()

# Setup scVI
scvi.model.SCVI.setup_anndata(adata, layer="counts")

# Train model
model = scvi.model.SCVI(adata)
model.train()

# Save latent representation
adata.obsm["X_scvi"] = model.get_latent_representation()

# Save results
result_artifact = ln.Artifact.from_anndata(
    adata,
    key="scrna/scvi_latent.h5ad",
    description="scVI latent representation"
).save()

ln.finish()
```

## Array Store Integrations

### TileDB-SOMA

Scalable array storage with cellxgene support:

```python
import tiledbsoma as soma
import lamindb as ln

# Create SOMA experiment
uri = "tiledb://my-namespace/experiment"

with soma.Experiment.create(uri) as exp:
    # Add measurements
    exp.add_new_collection("RNA")

    # Register in LaminDB
    artifact = ln.Artifact(
        uri,
        key="cellxgene/experiment.soma",
        description="TileDB-SOMA experiment"
    ).save()

# Query with SOMA
with soma.Experiment.open(uri) as exp:
    obs = exp.obs.read().to_pandas()
```

### DuckDB

Query artifacts with DuckDB:

```python
import duckdb
import lamindb as ln

# Get artifact
artifact = ln.Artifact.get(key="datasets/large_data.parquet")

# Query with DuckDB (without loading full file)
path = artifact.cache()
result = duckdb.query(f"""
    SELECT cell_type, COUNT(*) as count
    FROM read_parquet('{path}')
    GROUP BY cell_type
    ORDER BY count DESC
""").to_df()

# Save query result
result_artifact = ln.Artifact.from_dataframe(
    result,
    key="analysis/cell_type_counts.parquet"
).save()
```

## Visualization Integrations

### Vitessce

Create interactive visualizations:

```python
from vitessce import VitessceConfig
import lamindb as ln

# Load spatial data
artifact = ln.Artifact.get(key="spatial/visium_slide.h5ad")
adata = artifact.load()

# Create Vitessce configuration
vc = VitessceConfig.from_object(adata)

# Save configuration
import json
config_file = "vitessce_config.json"
with open(config_file, "w") as f:
    json.dump(vc.to_dict(), f)

# Register configuration
config_artifact = ln.Artifact(
    config_file,
    key="visualizations/spatial_config.json",
    description="Vitessce visualization config"
).save()
```

## Schema Module Integrations

### Bionty (Biological Ontologies)

```python
import bionty as bt

# Import biological ontologies
bt.CellType.import_source()
bt.Gene.import_source(organism="human")

# Use in data curation
cell_types = bt.CellType.from_values(adata.obs.cell_type)
```

### WetLab

Track wet lab experiments:

```python
# Install wetlab module
pip install 'lamindb[wetlab]'

# Use wetlab registries
import lamindb_wetlab as wetlab

# Track experiments, samples, protocols
experiment = wetlab.Experiment(name="RNA-seq batch 1").save()
```

### Clinical Data (OMOP)

```python
# Install clinical module
pip install 'lamindb[clinical]'

# Use OMOP common data model
import lamindb_clinical as clinical

# Track clinical data
patient = clinical.Patient(patient_id="P001").save()
```

## Git Integration

### Sync with Git Repositories

```python
# Configure git sync
export LAMINDB_SYNC_GIT_REPO=https://github.com/user/repo.git

# Or programmatically
ln.settings.sync_git_repo = "https://github.com/user/repo.git"

# Set development directory
lamin settings set dev-dir .

# Scripts tracked with git commits
ln.track()  # Automatically captures git commit hash
# ... your code ...
ln.finish()

# View git information
transform = ln.Transform.get(name="analysis.py")
transform.source_code  # Shows code at git commit
transform.hash        # Git commit hash
```

## Enterprise Integrations

### Benchling

Sync with Benchling registries (requires team/enterprise plan):

```python
# Configure Benchling connection (contact LaminDB team)
# Syncs schemas and data from Benchling registries

# Access synced Benchling data
# Details available through enterprise support
```

## Custom Integration Patterns

### REST API Integration

```python
import requests
import lamindb as ln

ln.track()

# Fetch from API
response = requests.get("https://api.example.com/data")
data = response.json()

# Convert to DataFrame
import pandas as pd
df = pd.DataFrame(data)

# Save to LaminDB
artifact = ln.Artifact.from_dataframe(
    df,
    key="api/fetched_data.parquet",
    description="Data fetched from external API"
).save()

artifact.features.add_values({"api_url": response.url})

ln.finish()
```

### Database Integration

```python
import sqlalchemy as sa
import lamindb as ln

ln.track()

# Connect to external database
engine = sa.create_engine("postgresql://user:pwd@host:port/db")

# Query data
query = "SELECT * FROM experiments WHERE date > '2025-01-01'"
df = pd.read_sql(query, engine)

# Save to LaminDB
artifact = ln.Artifact.from_dataframe(
    df,
    key="external_db/experiments_2025.parquet",
    description="Experiments from external database"
).save()

ln.finish()
```

## Croissant Metadata

Export datasets with Croissant metadata format:

```python
# Create artifact with rich metadata
artifact = ln.Artifact.from_dataframe(
    df,
    key="datasets/published_data.parquet",
    description="Published dataset with Croissant metadata"
).save()

# Export Croissant metadata (requires additional configuration)
# Enables dataset discovery and interoperability
```

## Best Practices for Integrations

1. **Track consistently**: Use `ln.track()` in all integrated workflows
2. **Link IDs**: Store external system IDs (W&B run ID, MLflow experiment ID) as features
3. **Centralize data**: Use LaminDB as single source of truth for data artifacts
4. **Sync parameters**: Log parameters to both LaminDB and ML platforms
5. **Version together**: Keep code (git), data (LaminDB), and experiments (ML platform) in sync
6. **Cache strategically**: Configure appropriate cache locations for cloud storage
7. **Use feature sets**: Link ontology terms from Bionty to artifacts
8. **Document integrations**: Add descriptions explaining integration context
9. **Test incrementally**: Verify integration with small datasets first
10. **Monitor lineage**: Use `view_lineage()` to ensure integration tracking works

## Troubleshooting Common Issues

**Issue: S3 credentials not found**
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

**Issue: GCS authentication failure**
```bash
gcloud auth application-default login
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

**Issue: Git sync not working**
```bash
# Ensure git repo is set
lamin settings get sync-git-repo

# Ensure you're in git repo
git status

# Commit changes before tracking
git add .
git commit -m "Update analysis"
ln.track()
```

**Issue: MLflow artifacts not syncing**
```python
# Save explicitly to both systems
mlflow.log_artifact("model.pkl")
ln.Artifact("model.pkl", key="models/model.pkl").save()
```

---

## ontologies.md

# LaminDB Ontology Management

This document covers biological ontology management in LaminDB through the Bionty plugin, including accessing, searching, and annotating data with standardized biological terms.

## Overview

LaminDB integrates the `bionty` plugin to manage standardized biological ontologies, enabling consistent metadata curation and data annotation across research projects. Bionty provides access to 20+ curated biological ontologies covering genes, proteins, cell types, tissues, diseases, and more.

## Available Ontologies

LaminDB provides access to multiple curated ontology sources:

| Registry | Ontology Source | Description |
|----------|----------------|-------------|
| **Gene** | Ensembl | Genes across organisms (human, mouse, etc.) |
| **Protein** | UniProt | Protein sequences and annotations |
| **CellType** | Cell Ontology (CL) | Standardized cell type classifications |
| **CellLine** | Cell Line Ontology (CLO) | Cell line annotations |
| **Tissue** | Uberon | Anatomical structures and tissues |
| **Disease** | Mondo, DOID | Disease classifications |
| **Phenotype** | Human Phenotype Ontology (HPO) | Phenotypic abnormalities |
| **Pathway** | Gene Ontology (GO) | Biological pathways and processes |
| **ExperimentalFactor** | Experimental Factor Ontology (EFO) | Experimental variables |
| **DevelopmentalStage** | Various | Developmental stages across organisms |
| **Ethnicity** | HANCESTRO | Human ancestry ontology |
| **Drug** | DrugBank | Drug compounds |
| **Organism** | NCBItaxon | Taxonomic classifications |

## Installation and Import

```python
# Install bionty (included with lamindb)
pip install lamindb

# Import
import lamindb as ln
import bionty as bt
```

## Importing Public Ontologies

Populate your registry with a public ontology source:

```python
# Import Cell Ontology
bt.CellType.import_source()

# Import organism-specific genes
bt.Gene.import_source(organism="human")
bt.Gene.import_source(organism="mouse")

# Import tissues
bt.Tissue.import_source()

# Import diseases
bt.Disease.import_source(source="mondo")  # Mondo Disease Ontology
bt.Disease.import_source(source="doid")   # Disease Ontology
```

## Searching and Accessing Records

### Keyword Search

```python
# Search cell types
bt.CellType.search("T cell").to_dataframe()
bt.CellType.search("gamma-delta").to_dataframe()

# Search genes
bt.Gene.search("CD8").to_dataframe()
bt.Gene.search("TP53").to_dataframe()

# Search diseases
bt.Disease.search("cancer").to_dataframe()

# Search tissues
bt.Tissue.search("brain").to_dataframe()
```

### Auto-Complete Lookup

For registries with fewer than 100k records:

```python
# Create lookup object
cell_types = bt.CellType.lookup()

# Access by name (auto-complete in IDEs)
t_cell = cell_types.t_cell
hsc = cell_types.hematopoietic_stem_cell

# Similarly for other registries
genes = bt.Gene.lookup()
cd8a = genes.cd8a
```

### Exact Field Matching

```python
# By ontology ID
cell_type = bt.CellType.get(ontology_id="CL:0000798")
disease = bt.Disease.get(ontology_id="MONDO:0004992")

# By name
cell_type = bt.CellType.get(name="T cell")
gene = bt.Gene.get(symbol="CD8A")

# By Ensembl ID
gene = bt.Gene.get(ensembl_gene_id="ENSG00000153563")
```

## Ontological Hierarchies

### Exploring Relationships

```python
# Get a cell type
gdt_cell = bt.CellType.get(ontology_id="CL:0000798")  # gamma-delta T cell

# View direct parents
gdt_cell.parents.to_dataframe()

# View all ancestors recursively
ancestors = []
current = gdt_cell
while current.parents.exists():
    parent = current.parents.first()
    ancestors.append(parent)
    current = parent

# View direct children
gdt_cell.children.to_dataframe()

# View all descendants recursively
gdt_cell.query_children().to_dataframe()
```

### Visualizing Hierarchies

```python
# Visualize parent hierarchy
gdt_cell.view_parents()

# Include children in visualization
gdt_cell.view_parents(with_children=True)

# Get all related terms for visualization
t_cell = bt.CellType.get(name="T cell")
t_cell.view_parents(with_children=True)  # Shows T cell subtypes
```

## Standardizing and Validating Data

### Validation

Check if terms exist in the ontology:

```python
# Validate cell types
bt.CellType.validate(["T cell", "B cell", "invalid_cell"])
# Returns: [True, True, False]

# Validate genes
bt.Gene.validate(["CD8A", "TP53", "FAKEGENE"], organism="human")
# Returns: [True, True, False]

# Check which terms are invalid
terms = ["T cell", "fat cell", "neuron", "invalid_term"]
invalid = [t for t, valid in zip(terms, bt.CellType.validate(terms)) if not valid]
print(f"Invalid terms: {invalid}")
```

### Standardization with Synonyms

Convert non-standard terms to validated names:

```python
# Standardize cell type names
bt.CellType.standardize(["fat cell", "blood forming stem cell"])
# Returns: ['adipocyte', 'hematopoietic stem cell']

# Standardize genes
bt.Gene.standardize(["BRCA-1", "p53"], organism="human")
# Returns: ['BRCA1', 'TP53']

# Handle mixed valid/invalid terms
terms = ["T cell", "T lymphocyte", "invalid"]
standardized = bt.CellType.standardize(terms)
# Returns standardized names where possible
```

### Loading Validated Records

```python
# Load records from values (including synonyms)
records = bt.CellType.from_values(["fat cell", "blood forming stem cell"])

# Returns list of CellType records
for record in records:
    print(record.name, record.ontology_id)

# Use with gene symbols
genes = bt.Gene.from_values(["CD8A", "CD8B"], organism="human")
```

## Annotating Datasets

### Annotating AnnData

```python
import anndata as ad
import lamindb as ln

# Load example data
adata = ad.read_h5ad("data.h5ad")

# Validate and retrieve matching records
cell_types = bt.CellType.from_values(adata.obs.cell_type)

# Create artifact with annotations
artifact = ln.Artifact.from_anndata(
    adata,
    key="scrna/annotated_data.h5ad",
    description="scRNA-seq data with validated cell type annotations"
).save()

# Link ontology records to artifact
artifact.feature_sets.add_ontology(cell_types)
```

### Annotating DataFrames

```python
import pandas as pd

# Create DataFrame with biological entities
df = pd.DataFrame({
    "cell_type": ["T cell", "B cell", "NK cell"],
    "tissue": ["blood", "spleen", "liver"],
    "disease": ["healthy", "lymphoma", "healthy"]
})

# Validate and standardize
df["cell_type"] = bt.CellType.standardize(df["cell_type"])
df["tissue"] = bt.Tissue.standardize(df["tissue"])

# Create artifact
artifact = ln.Artifact.from_dataframe(
    df,
    key="metadata/sample_info.parquet"
).save()

# Link ontology records
cell_type_records = bt.CellType.from_values(df["cell_type"])
tissue_records = bt.Tissue.from_values(df["tissue"])

artifact.feature_sets.add_ontology(cell_type_records)
artifact.feature_sets.add_ontology(tissue_records)
```

## Managing Custom Terms and Hierarchies

### Adding Custom Terms

```python
# Register new term not in public ontology
my_celltype = bt.CellType(name="my_novel_T_cell_subtype").save()

# Establish parent-child relationship
parent = bt.CellType.get(name="T cell")
my_celltype.parents.add(parent)

# Verify relationship
my_celltype.parents.to_dataframe()
parent.children.to_dataframe()  # Should include my_celltype
```

### Adding Synonyms

```python
# Add synonyms for standardization
hsc = bt.CellType.get(name="hematopoietic stem cell")
hsc.add_synonym("HSC")
hsc.add_synonym("blood stem cell")
hsc.add_synonym("hematopoietic progenitor")

# Set abbreviation
hsc.set_abbr("HSC")

# Now standardization works with synonyms
bt.CellType.standardize(["HSC", "blood stem cell"])
# Returns: ['hematopoietic stem cell', 'hematopoietic stem cell']
```

### Creating Custom Hierarchies

```python
# Build custom cell type hierarchy
immune_cell = bt.CellType.get(name="immune cell")

# Add custom subtypes
my_subtype1 = bt.CellType(name="custom_immune_subtype_1").save()
my_subtype2 = bt.CellType(name="custom_immune_subtype_2").save()

# Link to parent
my_subtype1.parents.add(immune_cell)
my_subtype2.parents.add(immune_cell)

# Create sub-subtypes
my_subsubtype = bt.CellType(name="custom_sub_subtype").save()
my_subsubtype.parents.add(my_subtype1)

# Visualize custom hierarchy
immune_cell.view_parents(with_children=True)
```

## Multi-Organism Support

For organism-aware registries like Gene:

```python
# Set global organism
bt.settings.organism = "human"

# Validate human genes
bt.Gene.validate(["TCF7", "CD8A"], organism="human")

# Load genes for specific organism
human_genes = bt.Gene.from_values(["CD8A", "TP53"], organism="human")
mouse_genes = bt.Gene.from_values(["Cd8a", "Trp53"], organism="mouse")

# Search organism-specific genes
bt.Gene.search("CD8", organism="human").to_dataframe()
bt.Gene.search("Cd8", organism="mouse").to_dataframe()

# Switch organism context
bt.settings.organism = "mouse"
genes = bt.Gene.from_source(symbol="Ap5b1")
```

## Public Ontology Lookup

Access terms from public ontologies without importing:

```python
# Interactive lookup in public sources
cell_types_public = bt.CellType.lookup(public=True)

# Access public terms
hepatocyte = cell_types_public.hepatocyte

# Import specific term
hepatocyte_local = bt.CellType.from_source(name="hepatocyte")

# Or import by ontology ID
specific_cell = bt.CellType.from_source(ontology_id="CL:0000182")
```

## Version Tracking

LaminDB automatically tracks ontology versions:

```python
# View current source versions
bt.Source.filter(currently_used=True).to_dataframe()

# Check which source a record derives from
cell_type = bt.CellType.get(name="hepatocyte")
cell_type.source  # Returns Source metadata

# View source details
source = cell_type.source
print(source.name)        # e.g., "cl"
print(source.version)     # e.g., "2023-05-18"
print(source.url)         # Ontology URL
```

## Ontology Integration Workflows

### Workflow 1: Validate Existing Data

```python
# Load data with biological annotations
adata = ad.read_h5ad("uncurated_data.h5ad")

# Validate cell types
validation = bt.CellType.validate(adata.obs.cell_type)

# Identify invalid terms
invalid_idx = [i for i, v in enumerate(validation) if not v]
invalid_terms = adata.obs.cell_type.iloc[invalid_idx].unique()
print(f"Invalid cell types: {invalid_terms}")

# Fix invalid terms manually or with standardization
adata.obs["cell_type"] = bt.CellType.standardize(adata.obs.cell_type)

# Re-validate
validation = bt.CellType.validate(adata.obs.cell_type)
assert all(validation), "All terms should now be valid"
```

### Workflow 2: Curate and Annotate

```python
import lamindb as ln

ln.track()  # Start tracking

# Load data
df = pd.read_csv("experimental_data.csv")

# Standardize using ontologies
df["cell_type"] = bt.CellType.standardize(df["cell_type"])
df["tissue"] = bt.Tissue.standardize(df["tissue"])

# Create curated artifact
artifact = ln.Artifact.from_dataframe(
    df,
    key="curated/experiment_2025_10.parquet",
    description="Curated experimental data with ontology-validated annotations"
).save()

# Link ontology records
artifact.feature_sets.add_ontology(bt.CellType.from_values(df["cell_type"]))
artifact.feature_sets.add_ontology(bt.Tissue.from_values(df["tissue"]))

ln.finish()  # Complete tracking
```

### Workflow 3: Cross-Organism Gene Mapping

```python
# Get human genes
human_genes = ["CD8A", "CD8B", "TP53"]
human_records = bt.Gene.from_values(human_genes, organism="human")

# Find mouse orthologs (requires external mapping)
# LaminDB doesn't provide built-in ortholog mapping
# Use external tools like Ensembl BioMart or homologene

mouse_orthologs = ["Cd8a", "Cd8b", "Trp53"]
mouse_records = bt.Gene.from_values(mouse_orthologs, organism="mouse")
```

## Querying Ontology-Annotated Data

```python
# Find all datasets with specific cell type
t_cell = bt.CellType.get(name="T cell")
ln.Artifact.filter(feature_sets__cell_types=t_cell).to_dataframe()

# Find datasets measuring specific genes
cd8a = bt.Gene.get(symbol="CD8A", organism="human")
ln.Artifact.filter(feature_sets__genes=cd8a).to_dataframe()

# Query across ontology hierarchy
# Find all datasets with T cell or T cell subtypes
t_cell_subtypes = t_cell.query_children()
ln.Artifact.filter(
    feature_sets__cell_types__in=t_cell_subtypes
).to_dataframe()
```

## Best Practices

1. **Import ontologies first**: Call `import_source()` before validation
2. **Use standardization**: Leverage synonym mapping to handle variations
3. **Validate early**: Check terms before creating artifacts
4. **Set organism context**: Specify organism for gene-related queries
5. **Add custom synonyms**: Register common variations in your domain
6. **Use public lookup**: Access `lookup(public=True)` for term discovery
7. **Track versions**: Monitor ontology source versions for reproducibility
8. **Build hierarchies**: Link custom terms to existing ontology structures
9. **Query hierarchically**: Use `query_children()` for comprehensive searches
10. **Document mappings**: Track custom term additions and relationships

## Common Ontology Operations

```python
# Check if term exists
exists = bt.CellType.filter(name="T cell").exists()

# Count terms in registry
n_cell_types = bt.CellType.filter().count()

# Get all terms with specific parent
immune_cells = bt.CellType.filter(parents__name="immune cell")

# Find orphan terms (no parents)
orphans = bt.CellType.filter(parents__isnull=True)

# Get recently added terms
from datetime import datetime, timedelta
recent = bt.CellType.filter(
    created_at__gte=datetime.now() - timedelta(days=7)
)
```

---

## setup-deployment.md

# LaminDB Setup & Deployment

This document covers installation, configuration, instance management, storage options, and deployment strategies for LaminDB.

## Installation

### Basic Installation

```bash
# Install LaminDB
pip install lamindb

# Or with pip3
pip3 install lamindb
```

### Installation with Extras

Install optional dependencies for specific functionality:

```bash
# Google Cloud Platform support
pip install 'lamindb[gcp]'

# Flow cytometry formats
pip install 'lamindb[fcs]'

# Array storage and streaming (Zarr support)
pip install 'lamindb[zarr]'

# AWS S3 support (usually included by default)
pip install 'lamindb[aws]'

# Multiple extras
pip install 'lamindb[gcp,zarr,fcs]'
```

### Module Plugins

```bash
# Biological ontologies (Bionty)
pip install bionty

# Wet lab functionality
pip install lamindb-wetlab

# Clinical data (OMOP CDM)
pip install lamindb-clinical
```

### Verify Installation

```python
import lamindb as ln
print(ln.__version__)

# Check available modules
import bionty as bt
print(bt.__version__)
```

## Authentication

### Creating an Account

1. Visit https://lamin.ai
2. Sign up for a free account
3. Navigate to account settings to generate an API key

### Logging In

```bash
# Login with API key
lamin login

# You'll be prompted to enter your API key
# API key is stored locally at ~/.lamin/
```

### Authentication Details

**Data Privacy:** LaminDB authentication only collects basic metadata (email, user information). Your actual data remains private and is not sent to LaminDB servers.

**Local vs Cloud:** Authentication is required even for local-only usage to enable collaboration features and instance management.

## Instance Initialization

### Local SQLite Instance

For local development and small datasets:

```bash
# Initialize in current directory
lamin init --storage ./mydata

# Initialize in specific directory
lamin init --storage /path/to/data

# Initialize with specific modules
lamin init --storage ./mydata --modules bionty

# Initialize with multiple modules
lamin init --storage ./mydata --modules bionty,wetlab
```

### Cloud Storage with SQLite

Use cloud storage but local SQLite database:

```bash
# AWS S3
lamin init --storage s3://my-bucket/path

# Google Cloud Storage
lamin init --storage gs://my-bucket/path

# S3-compatible (MinIO, Cloudflare R2)
lamin init --storage 's3://bucket?endpoint_url=http://endpoint:9000'
```

### Cloud Storage with PostgreSQL

For production deployments:

```bash
# S3 + PostgreSQL
lamin init --storage s3://my-bucket/path \
  --db postgresql://user:password@hostname:5432/dbname \
  --modules bionty

# GCS + PostgreSQL
lamin init --storage gs://my-bucket/path \
  --db postgresql://user:password@hostname:5432/dbname \
  --modules bionty
```

### Instance Naming

```bash
# Specify instance name
lamin init --storage ./mydata --name my-project

# Default name uses directory name
lamin init --storage ./mydata  # Instance name: "mydata"
```

## Connecting to Instances

### Connect to Your Own Instance

```bash
# By name
lamin connect my-project

# By full path
lamin connect account_handle/my-project
```

### Connect to Shared Instance

```bash
# Connect to someone else's instance
lamin connect other-user/their-project

# Requires appropriate permissions
```

### Switching Between Instances

```bash
# List available instances
lamin info

# Switch instance
lamin connect another-instance

# Close current instance
lamin close
```

## Storage Configuration

### Local Storage

**Advantages:**
- Fast access
- No internet required
- Simple setup

**Setup:**
```bash
lamin init --storage ./data
```

### AWS S3 Storage

**Advantages:**
- Scalable
- Collaborative
- Durable

**Setup:**
```bash
# Set credentials
export AWS_ACCESS_KEY_ID=your_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Initialize
lamin init --storage s3://my-bucket/project-data \
  --db postgresql://user:pwd@host:5432/db
```

**S3 Permissions Required:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket/*",
        "arn:aws:s3:::my-bucket"
      ]
    }
  ]
}
```

### Google Cloud Storage

**Setup:**
```bash
# Authenticate
gcloud auth application-default login

# Or use service account
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Initialize
lamin init --storage gs://my-bucket/project-data \
  --db postgresql://user:pwd@host:5432/db
```

### S3-Compatible Storage

For MinIO, Cloudflare R2, or other S3-compatible services:

```bash
# MinIO example
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin

lamin init --storage 's3://my-bucket?endpoint_url=http://minio.example.com:9000'

# Cloudflare R2 example
export AWS_ACCESS_KEY_ID=your_r2_access_key
export AWS_SECRET_ACCESS_KEY=your_r2_secret_key

lamin init --storage 's3://bucket?endpoint_url=https://account-id.r2.cloudflarestorage.com'
```

## Database Configuration

### SQLite (Default)

**Advantages:**
- No separate database server
- Simple setup
- Good for development

**Limitations:**
- Not suitable for concurrent writes
- Limited scalability

**Setup:**
```bash
# SQLite is default
lamin init --storage ./data
# Database stored at ./data/.lamindb/
```

### PostgreSQL

**Advantages:**
- Production-ready
- Concurrent access
- Better performance at scale

**Setup:**
```bash
# Full connection string
lamin init --storage s3://bucket/path \
  --db postgresql://username:password@hostname:5432/database

# With SSL
lamin init --storage s3://bucket/path \
  --db "postgresql://user:pwd@host:5432/db?sslmode=require"
```

**PostgreSQL Versions:** Compatible with PostgreSQL 12+

### Database Schema Management

```bash
# Check current schema version
lamin migrate check

# Upgrade schema
lamin migrate deploy

# View migration history
lamin migrate history
```

## Cache Configuration

### Cache Directory

LaminDB maintains a local cache for cloud files:

```python
import lamindb as ln

# View cache location
print(ln.settings.cache_dir)
```

### Configure Cache Location

```bash
# Set cache directory
lamin cache set /path/to/cache

# View current cache settings
lamin cache get
```

### System-Wide Cache (Multi-User)

For shared systems with multiple users:

```bash
# Create system settings file
sudo mkdir -p /system/settings
sudo nano /system/settings/system.env
```

Add to `system.env`:
```bash
lamindb_cache_path=/shared/cache/lamindb
```

Ensure permissions:
```bash
sudo chmod 755 /shared/cache/lamindb
sudo chown -R shared-user:shared-group /shared/cache/lamindb
```

### Cache Management

```python
import lamindb as ln

# Clear cache for specific artifact
artifact = ln.Artifact.get(key="data.h5ad")
artifact.delete_cache()

# Check if artifact is cached
if artifact.is_cached():
    print("Already cached")

# Manually clear entire cache
import shutil
shutil.rmtree(ln.settings.cache_dir)
```

## Settings Management

### View Current Settings

```python
import lamindb as ln

# User settings
print(ln.setup.settings.user)
# User(handle='username', email='user@email.com', name='Full Name')

# Instance settings
print(ln.setup.settings.instance)
# Instance(name='my-project', storage='s3://bucket/path')
```

### Configure Settings

```bash
# Set development directory for relative keys
lamin settings set dev-dir /path/to/project

# Configure git sync
lamin settings set sync-git-repo https://github.com/user/repo.git

# View all settings
lamin settings
```

### Environment Variables

```bash
# Cache directory
export LAMIN_CACHE_DIR=/path/to/cache

# Settings directory
export LAMIN_SETTINGS_DIR=/path/to/settings

# Git sync
export LAMINDB_SYNC_GIT_REPO=https://github.com/user/repo.git
```

## Instance Management

### Viewing Instance Information

```bash
# Current instance info
lamin info

# List all instances
lamin ls

# View instance details
lamin instance details
```

### Instance Collaboration

```bash
# Set instance visibility (requires LaminHub)
lamin instance set-visibility public
lamin instance set-visibility private

# Invite collaborators (requires LaminHub)
lamin instance invite user@email.com
```

### Instance Migration

```bash
# Backup instance
lamin backup create

# Restore from backup
lamin backup restore backup_id

# Export instance metadata
lamin export instance-metadata.json
```

### Deleting Instances

```bash
# Delete instance (preserves data, removes metadata)
lamin delete --force instance-name

# This only removes the LaminDB metadata
# Actual data in storage location remains
```

## Production Deployment Patterns

### Pattern 1: Local Development → Cloud Production

**Development:**
```bash
# Local development
lamin init --storage ./dev-data --modules bionty
```

**Production:**
```bash
# Cloud production
lamin init --storage s3://prod-bucket/data \
  --db postgresql://user:pwd@db-host:5432/prod-db \
  --modules bionty \
  --name production
```

**Migration:** Export artifacts from dev, import to prod
```python
# Export from dev
artifacts = ln.Artifact.filter().all()
for artifact in artifacts:
    artifact.export("/tmp/export/")

# Switch to prod
lamin connect production

# Import to prod
for file in Path("/tmp/export/").glob("*"):
    ln.Artifact(str(file), key=file.name).save()
```

### Pattern 2: Multi-Region Deployment

Deploy instances in multiple regions for data sovereignty:

```bash
# US instance
lamin init --storage s3://us-bucket/data \
  --db postgresql://user:pwd@us-db:5432/db \
  --name us-production

# EU instance
lamin init --storage s3://eu-bucket/data \
  --db postgresql://user:pwd@eu-db:5432/db \
  --name eu-production
```

### Pattern 3: Shared Storage, Personal Instances

Multiple users, shared data:

```bash
# Shared storage with user-specific DB
lamin init --storage s3://shared-bucket/data \
  --db postgresql://user1:pwd@host:5432/user1_db \
  --name user1-workspace

lamin init --storage s3://shared-bucket/data \
  --db postgresql://user2:pwd@host:5432/user2_db \
  --name user2-workspace
```

## Performance Optimization

### Database Performance

```python
# Use connection pooling for PostgreSQL
# Configure in database server settings

# Optimize queries with indexes
# LaminDB creates indexes automatically for common queries
```

### Storage Performance

```bash
# Use appropriate storage classes
# S3: STANDARD for frequent access, INTELLIGENT_TIERING for mixed access

# Configure multipart upload thresholds
export AWS_CLI_FILE_IO_BANDWIDTH=100MB
```

### Cache Optimization

```python
# Pre-cache frequently used artifacts
artifacts = ln.Artifact.filter(key__startswith="reference/")
for artifact in artifacts:
    artifact.cache()  # Download to cache

# Use backed mode for large arrays
adata = artifact.backed()  # Don't load into memory
```

## Security Best Practices

1. **Credentials Management:**
   - Use environment variables, not hardcoded credentials
   - Use IAM roles on AWS/GCP instead of access keys
   - Rotate credentials regularly

2. **Access Control:**
   - Use PostgreSQL for multi-user access control
   - Configure storage bucket policies
   - Enable audit logging

3. **Network Security:**
   - Use SSL/TLS for database connections
   - Use VPCs for cloud deployments
   - Restrict IP addresses when possible

4. **Data Protection:**
   - Enable encryption at rest (S3, GCS)
   - Use encryption in transit (HTTPS, SSL)
   - Implement backup strategies

## Monitoring and Maintenance

### Health Checks

```python
import lamindb as ln

# Check database connection
try:
    ln.Artifact.filter().count()
    print("✓ Database connected")
except Exception as e:
    print(f"✗ Database error: {e}")

# Check storage access
try:
    test_artifact = ln.Artifact("test.txt", key="healthcheck.txt").save()
    test_artifact.delete(permanent=True)
    print("✓ Storage accessible")
except Exception as e:
    print(f"✗ Storage error: {e}")
```

### Logging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# LaminDB operations will produce detailed logs
```

### Backup Strategy

```bash
# Regular database backups (PostgreSQL)
pg_dump -h hostname -U username -d database > backup_$(date +%Y%m%d).sql

# Storage backups (S3 versioning)
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled

# Metadata export
lamin export metadata_backup.json
```

## Troubleshooting

### Common Issues

**Issue: Cannot connect to instance**
```bash
# Check instance exists
lamin ls

# Verify authentication
lamin login

# Re-connect
lamin connect instance-name
```

**Issue: Storage permissions denied**
```bash
# Check AWS credentials
aws s3 ls s3://your-bucket/

# Check GCS credentials
gsutil ls gs://your-bucket/

# Verify IAM permissions
```

**Issue: Database connection error**
```bash
# Test PostgreSQL connection
psql postgresql://user:pwd@host:5432/db

# Check database version compatibility
lamin migrate check
```

**Issue: Cache full**
```python
# Clear cache
import lamindb as ln
import shutil
shutil.rmtree(ln.settings.cache_dir)

# Set larger cache location
lamin cache set /larger/disk/cache
```

## Upgrade and Migration

### Upgrading LaminDB

```bash
# Upgrade to latest version
pip install --upgrade lamindb

# Upgrade database schema
lamin migrate deploy
```

### Schema Compatibility

Check the compatibility matrix to ensure your database schema version is compatible with your installed LaminDB version.

### Breaking Changes

Major version upgrades may require migration:

```bash
# Check for breaking changes
lamin migrate check

# Review migration plan
lamin migrate plan

# Execute migration
lamin migrate deploy
```

## Best Practices

1. **Start local, scale cloud**: Develop locally, deploy to cloud for production
2. **Use PostgreSQL for production**: SQLite is only for development
3. **Configure appropriate cache**: Size cache based on working set
4. **Enable versioning**: Use S3/GCS versioning for data protection
5. **Monitor costs**: Track storage and compute costs in cloud deployments
6. **Document configuration**: Keep infrastructure-as-code for reproducibility
7. **Test backups**: Regularly verify backup and restore procedures
8. **Set up monitoring**: Implement health checks and alerting
9. **Use modules strategically**: Only install needed plugins to reduce complexity
10. **Plan for scale**: Consider concurrent users and data growth
