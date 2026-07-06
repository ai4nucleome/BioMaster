# Multi Omics Database Access

## Overview

Workflow for retrieving public omics datasets, sequences, annotations, and literature-linked biological resources from repositories such as NCBI GEO/SRA, UniProt, Reactome, and PubMed. Given accessions, identifiers, or free-text query terms (with optional species or database constraints), it selects the right repository, runs reproducible queries, normalizes the returned metadata onto stable identifiers, downloads only the needed records, and exports accession tables plus provenance for downstream use. Use this skill whenever the task is downloading or querying public bioinformatics databases, resolving accessions or search terms into data assets, or pulling external references for GEO, SRA, UniProt, Reactome, or PubMed. Expected inputs are accessions or identifiers, query terms, and optional species or database constraints. Expected outputs are downloaded datasets, linked metadata tables, and query result summaries with recorded database versions and access dates.

## Pick the right database

Select the target repository based on what the task needs: raw sequencing reads go to SRA, processed expression datasets to GEO DataSets, protein sequences and annotations to UniProt, pathways to Reactome, and literature to PubMed. Choosing the correct database up front avoids wasted queries and ensures the returned records match the user goal.

## Query reproducibly

Run the search against the chosen database using stable identifiers or query terms, and capture the database name, search term, filters, result count, returned identifiers, and access date. Recording these parameters makes the retrieval reproducible and lets downstream steps join on the exact identifiers that were returned.

## Normalize returned metadata

Fetch summary records for the returned identifiers and reshape them into a tidy table with one row per accession and stable, consistently named columns such as accession, title, sample count, platform, and release date. Drop records missing a stable accession and de-duplicate so downstream workflows can join cleanly on accession IDs.

## Download only needed assets

Retrieve the actual data records for the filtered accession list rather than performing a bulk dump, fetching each record by accession and writing it to a data directory. Narrow, accession-scoped retrieval keeps the download small and avoids pulling oversized collections when a subset solves the task.

## Export usable references

Write the normalized accession metadata table, a retrieval provenance record covering database, query term, parameters, and access date, and a concise query result summary to a results directory. These artifacts give downstream steps stable IDs to join on and a traceable record of where the data came from.
