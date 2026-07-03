# Database Query Uniprot

## Overview

This skill provides local access to the UniProt REST API (https://rest.uniprot.org) for protein sequence and annotation retrieval — no Modal deployment is needed, all operations run via HTTP requests. Inputs are either a known UniProt accession (e.g., P00533) or a search query such as a gene name with an optional organism ID (e.g., 9606 for human). Outputs include FASTA sequences, full JSON entries, domain boundaries, natural sequence variants, PDB cross-references, and search result lists. Use this skill when: (1) looking up protein sequences by accession, (2) finding functional annotations, (3) getting domain boundaries, (4) finding homologs and variants, or (5) cross-referencing to PDB structures. For structure retrieval use the pdb skill; for sequence design use proteinmpnn. Downstream, retrieved sequences can feed into esm for embeddings or colabfold for structure prediction.

## Fetch Sequence by Accession

Retrieve a protein sequence for a known UniProt accession. Supports FASTA format (header line plus sequence) via curl or Python requests, and full JSON format when annotations are needed alongside the sequence. This is the entry point when an accession such as P00533 is already known.

## Retrieve Annotations & Domain Boundaries

Fetch the full UniProt entry as JSON and extract structured annotations. The full entry exposes the recommended protein name and feature lists; Domain features can be parsed to obtain domain names with start/end residue positions (e.g., the EGFR kinase domain spanning residues 712-979).

## Search UniProt Entries

Find UniProt entries by query such as a gene name, optionally filtered by organism ID (e.g., 9606 for human). Returns a list of matching entries from which the primary accession can be taken. For sequence-similarity discovery, UniProt's BLAST service is available as an alternative to the text search.

## Cross-References & Sequence Variants

Extract cross-references to external databases (notably PDB structures, with method and chain metadata) and natural sequence variants from the full entry JSON. Useful for linking a sequence to available experimental structures and for cataloging known mutations.

## Target Selection Workflow

End-to-end composite workflow chaining the previous steps: search for a protein by name, take the top result's primary accession, fetch its domain boundaries, and find available PDB structures to inform downstream structure-based design. This is the typical use case for selecting a design target.
