## Setup & API Configuration

_modules: setup, api-config, organism-codes_

```python
import requests

BASE_URL = "https://rest.kegg.jp"

# API pattern: https://rest.kegg.jp/<operation>/<argument>
# Operations:
#   list  -> /list/pathway/hsa        enumerate all pathways for an organism
#   find  -> /find/pathway/cancer     keyword search
#   get   -> /get/hsa:672             fetch a single record (gene/pathway)
#   link  -> /link/genes/hsa00010     cross-reference (genes in a pathway)
#   conv  -> /conv/genes/ncbi-geneid:672  convert between ID systems

# Organism codes
ORGANISM_CODES = {
    "hsa": "Human",
    "mmu": "Mouse",
    "rno": "Rat",
    "dme": "Fly",
    "sce": "Yeast",
    "eco": "E. coli",
}
```

## Pathway Discovery

_modules: pathway-search, pathway-list, keyword-query_

```python
# Find pathways by keyword
# Replaces generic 'map' prefix with the organism code for organism-specific IDs
def find_pathways(keyword, organism="hsa"):
    url = f"{BASE_URL}/find/pathway/{keyword}"
    r = requests.get(url)
    lines = r.text.strip().split('\n')
    results = []
    for line in lines:
        if line:
            parts = line.split('\t')
            pid = parts[0].replace("map", organism) if organism else parts[0]
            results.append({"id": pid, "name": parts[1] if len(parts) > 1 else ""})
    return results

# List all pathways for an organism
def list_pathways(organism="hsa"):
    url = f"{BASE_URL}/list/pathway/{organism}"
    r = requests.get(url)
    return r.text

# Example
pathways = find_pathways("apoptosis")
for p in pathways[:5]:
    print(f"{p['id']}: {p['name']}")
```

## Pathway Details & Gene Retrieval

_modules: pathway-details, pathway-genes, link-operation_

```python
# Get full pathway details (plain-text record)
def get_pathway(pathway_id):
    url = f"{BASE_URL}/get/{pathway_id}"
    r = requests.get(url)
    return r.text

# Get all genes linked to a pathway
# Returns KEGG gene IDs, e.g. hsa:672, hsa:7157
def get_pathway_genes(pathway_id):
    url = f"{BASE_URL}/link/genes/{pathway_id}"
    r = requests.get(url)
    genes = []
    for line in r.text.strip().split('\n'):
        if line:
            parts = line.split('\t')
            if len(parts) >= 2:
                genes.append(parts[1])
    return genes

# Example
details = get_pathway("hsa04210")  # apoptosis
genes = get_pathway_genes("hsa04210")
print(f"{len(genes)} genes in apoptosis pathway")
```

## Gene Lookup & ID Conversion

_modules: gene-lookup, id-conversion, conv-operation_

```python
# Get gene info by KEGG gene ID (e.g. hsa:672 for BRCA1)
def get_gene(kegg_gene_id):
    url = f"{BASE_URL}/get/{kegg_gene_id}"
    r = requests.get(url)
    return r.text

# Find genes by name within an organism
def find_gene(gene_name, organism="hsa"):
    url = f"{BASE_URL}/find/{organism}/{gene_name}"
    r = requests.get(url)
    return r.text

# Convert between ID systems (KEGG <-> NCBI Gene ID)
# Example: ncbi-geneid:672 -> hsa:672
def convert_ids(source_db, source_id):
    url = f"{BASE_URL}/conv/genes/{source_db}:{source_id}"
    r = requests.get(url)
    return r.text

# Examples
brca1 = get_gene("hsa:672")
found = find_gene("BRCA1")
kegg_id = convert_ids("ncbi-geneid", "672")
```
