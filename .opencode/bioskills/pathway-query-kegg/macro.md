# Pathway Query Kegg

## Overview

A workflow for querying the KEGG REST API to discover biological pathways, retrieve pathway details and gene lists, and look up gene information with ID conversion. The KEGG REST API follows a simple pattern: `https://rest.kegg.jp/<operation>/<argument>`. Inputs are keywords, pathway IDs (e.g. hsa00010), gene names or KEGG gene IDs (e.g. hsa:672), and organism codes (e.g. hsa for human). Outputs are pathway lists, pathway detail records, gene lists per pathway, and gene info records. Use this workflow when a user asks about metabolic or signaling pathways (glycolysis, apoptosis, etc.), wants to find which pathways a gene participates in, needs KEGG pathway IDs, wants pathway gene lists, or needs to convert between KEGG and external gene IDs.

## Setup & API Configuration

Establish the KEGG REST API base URL and understand the operation/argument pattern that all subsequent steps rely on. The API lives at https://rest.kegg.jp and exposes operations such as list (enumerate), find (keyword search), get (fetch a record), link (cross-reference), and conv (ID conversion). Organism codes select the species context: hsa for Human, mmu for Mouse, rno for Rat, dme for Fly, sce for Yeast, and eco for E. coli. These codes are substituted into pathway and gene IDs (e.g. hsa00010 for human glycolysis).

## Pathway Discovery

Discover pathways either by keyword search or by listing all pathways for a given organism. Keyword search returns matching pathway IDs and names; the generic map prefix in results is replaced with the organism code so IDs are organism-specific. Listing all pathways returns the complete catalog for an organism. This is the entry point when a user names a biological process (e.g. apoptosis, glycolysis) or wants to browse available pathways.

## Pathway Details & Gene Retrieval

Given a pathway ID, fetch the full pathway detail record and retrieve the list of genes that participate in that pathway. The get operation returns the complete KEGG record (description, class, modules, etc.) as plain text. The link operation cross-references the pathway to its member genes, returning KEGG gene IDs (e.g. hsa:672). Use this when a user has a pathway ID and wants its contents or member genes.

## Gene Lookup & ID Conversion

Look up individual genes by KEGG gene ID or by name within an organism, and convert between KEGG gene IDs and external database IDs (e.g. NCBI Gene ID). The get operation fetches a full gene record; the find operation searches an organism's gene set by name; the conv operation translates between ID systems. Use this when a user has a gene symbol or external ID and needs its KEGG record, or wants to map NCBI/UniProt IDs to KEGG.
