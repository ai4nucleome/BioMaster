---
name: "multi-omics-database-access"
description: "Workflow for retrieving public omics datasets, sequences, annotations, and literature-linked biological resources from repositories such as NCBI GEO/SRA, UniProt, Reactome, and PubMed."
domain: "multi-omics"
primary_tool: "requests"
methods: ["requests","pandas","NCBI E-utilities","UniProt","Reactome","PubMed"]
macro_tags: []
micro_tags: ["requests","pandas","NCBI E-utilities","UniProt","Reactome","PubMed","database-selection","repository-mapping","query","eutils","esearch","provenance","metadata-normalization","id-mapping","download","efetch","filtered-retrieval","export","metadata-tables"]
source: "bioclaw_hub/database-access"
status: "active"
enabled: true
custom: false
---

# Multi Omics Database Access
