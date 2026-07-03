## Fetch Sequence by Accession

_modules: sequence-retrieval, fasta, accession_

```bash
# FASTA format
curl "https://rest.uniprot.org/uniprotkb/P00533.fasta"

# JSON format with annotations
curl "https://rest.uniprot.org/uniprotkb/P00533.json"
```

```python
import requests

def get_uniprot_sequence(accession):
    """Fetch sequence from UniProt."""
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.fasta"
    response = requests.get(url)
    if response.ok:
        lines = response.text.strip().split('\n')
        header = lines[0]
        sequence = ''.join(lines[1:])
        return header, sequence
    return None, None
```

Key endpoints: `/uniprotkb/{id}.fasta` (FASTA sequence), `/uniprotkb/{id}.json` (full entry JSON).

## Retrieve Annotations & Domain Boundaries

_modules: annotation, domain-boundaries, features_

```python
def get_uniprot_entry(accession):
    """Fetch full UniProt entry as JSON."""
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    response = requests.get(url)
    return response.json() if response.ok else None

entry = get_uniprot_entry("P00533")
print(f"Protein: {entry['proteinDescription']['recommendedName']['fullName']['value']}")
```

```python
def get_domains(accession):
    """Extract domain annotations."""
    entry = get_uniprot_entry(accession)
    domains = []
    for feature in entry.get('features', []):
        if feature['type'] == 'Domain':
            domains.append({
                'name': feature.get('description', ''),
                'start': feature['location']['start']['value'],
                'end': feature['location']['end']['value']
            })
    return domains

# Example: EGFR domains
domains = get_domains("P00533")
# [{'name': 'Kinase', 'start': 712, 'end': 979}, ...]
```

Parse `entry['features']` filtering by `type == 'Domain'`; read positions from `location.start.value` / `location.end.value`.

## Search UniProt Entries

_modules: search, gene-name, organism-filter, blast_

```python
def search_uniprot(query, organism=None, limit=10):
    """Search UniProt by query."""
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": query,
        "format": "json",
        "size": limit
    }
    if organism:
        params["query"] += f" AND organism_id:{organism}"
    response = requests.get(url, params=params)
    return response.json()['results']

# Search for human EGFR
results = search_uniprot("EGFR", organism=9606)
```

For sequence-similarity search use the UniProt BLAST service at https://www.uniprot.org/blast (no local code path provided in source).

Key endpoints: `/uniprotkb/search` (search entries), `/uniprotkb/stream` (batch download).

## Cross-References & Sequence Variants

_modules: cross-reference, pdb, natural-variants_

```python
def get_pdb_references(accession):
    """Get PDB structures for UniProt entry."""
    entry = get_uniprot_entry(accession)
    pdbs = []
    for xref in entry.get('uniProtKBCrossReferences', []):
        if xref['database'] == 'PDB':
            pdbs.append({
                'pdb_id': xref['id'],
                'method': xref.get('properties', [{}])[0].get('value', ''),
                'chains': xref.get('properties', [{}])[1].get('value', '')
            })
    return pdbs

# Example: PDB structures for EGFR
pdbs = get_pdb_references("P00533")
```

```python
def get_sequence_variants(accession):
    """Get natural variants from UniProt."""
    entry = get_uniprot_entry(accession)
    variants = []
    for feature in entry.get('features', []):
        if feature['type'] == 'Natural variant':
            variants.append({
                'position': feature['location']['start']['value'],
                'original': feature.get('alternativeSequence', {}).get('originalSequence', ''),
                'variant': feature.get('alternativeSequence', {}).get('alternativeSequences', [''])[0],
                'description': feature.get('description', '')
            })
    return variants
```

PDB refs live in `entry['uniProtKBCrossReferences']` (filter `database == 'PDB'`); variants in `entry['features']` (filter `type == 'Natural variant'`).

## Target Selection Workflow

_modules: target-selection, workflow, end-to-end_

```python
# 1. Find protein by name
results = search_uniprot("insulin receptor", organism=9606)

# 2. Get accession
accession = results[0]['primaryAccession']  # e.g., P06213

# 3. Get domains
domains = get_domains(accession)

# 4. Find PDB structure
pdbs = get_pdb_references(accession)

# 5. Download best structure for design (delegated to the pdb skill)
```

Troubleshooting notes: verify accession format (e.g., P00533) when an entry is not found; add a delay between requests to respect rate limits; use the `/uniprotkb/stream` endpoint with pagination for large downloads.
