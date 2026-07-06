# Clinical Query Opentarget

## Overview

Query the OpenTargets Platform GraphQL API (v4) to retrieve drug-target-disease associations, therapeutic evidence, and clinical drug metadata.

**Inputs:** Gene names (resolved to Ensembl IDs), disease names (resolved to EFO IDs), or directly supplied Ensembl/EFO identifiers.

**Outputs:** JSON responses containing association scores (with per-datasource breakdowns), known drugs with mechanism of action and clinical phase/status, and entity metadata (approved symbols, names, descriptions).

**When to use:** User asks about drug targets for a disease, disease-gene associations, drugs targeting a specific gene, target validation evidence, or drug-disease associations. Triggers on terms like "opentarget", "drug target", "target validation", "disease association", "therapeutic target", "drug for disease".

**Workflow stages:** (1) set up an HTTP helper against the OpenTargets GraphQL endpoint; (2) search and resolve entity names to stable IDs; (3) query bidirectional target-disease associations with scores; (4) look up known drugs, mechanisms of action, and clinical trial phases for a target.

## API Setup & Query Helper

Establish the HTTP helper that posts GraphQL queries to the OpenTargets Platform v4 endpoint. This helper is reused by every subsequent query step. It accepts a GraphQL query string and an optional variables dict, posts JSON to the API, raises on HTTP errors, and returns the parsed JSON response.

## Entity Search & Resolution

Search OpenTargets by free-text name to resolve gene targets (to Ensembl IDs) and diseases (to EFO IDs). Both searches use the platform's unified search endpoint filtered to a single entity type, returning the top hits with their stable IDs, names, and descriptions. Common EFO IDs for frequent diseases are provided as a quick-reference shortcut so users can skip the search step when the disease is already known.

## Target-Disease Associations

Query bidirectional target-disease associations with overall association scores and per-datasource score breakdowns. Given an Ensembl target ID, retrieve its top associated diseases; given an EFO disease ID, retrieve its top associated targets. Each row returns the partner entity's stable ID and approved name plus an aggregate score (0-1) and component-level scores from individual evidence datasources (genetics, literature, drugs, animal models, etc.).

## Drug & Clinical Trial Lookup

Retrieve known drugs for a target, including each drug's identifier and name, mechanism of action, clinical development phase, approval status, and the disease the drug is being investigated for. This step supports target-validation and drug-repurposing questions by linking a gene target to its therapeutic pipeline.
