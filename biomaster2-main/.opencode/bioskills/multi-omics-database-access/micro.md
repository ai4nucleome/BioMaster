## Pick the right database

_modules: database-selection, repository-mapping_

```python
# Map task type -> target repository / API base URL
DATABASE_MAP = {
    "raw sequencing":       ("SRA",      "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"),
    "processed expression":("GEO/GDS",  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"),
    "protein sequence":    ("UniProt",  "https://rest.uniprot.org/uniprotkb/"),
    "pathways":             ("Reactome", "https://reactome.org/ContentService/"),
    "literature":           ("PubMed",   "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"),
}

task = "processed expression"          # set from the user goal
db, base_url = DATABASE_MAP[task]
print(db, base_url)
```

## Query reproducibly

_modules: query, eutils, esearch, provenance_

```python
import requests, datetime

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
params = {
    "db": "gds",                 # GEO DataSets; use "sra" / "pubmed" as needed
    "term": "single cell liver",
    "retmode": "json",
    "retmax": 20,
}
resp = requests.get(EUTILS, params=params)
resp.raise_for_status()
hits = resp.json()["esearchresult"]

provenance = {
    "database": params["db"],
    "term": params["term"],
    "retmax": params["retmax"],
    "access_date": datetime.date.today().isoformat(),
    "count": hits.get("count"),
    "idlist": hits.get("idlist", []),
}
print(provenance)
```

## Normalize returned metadata

_modules: metadata-normalization, id-mapping, pandas_

```python
import requests, pandas as pd

ids = provenance["idlist"]
summ = requests.get(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
    params={"db": "gds", "id": ",".join(ids), "retmode": "json"},
).json()["result"]

rows = []
for uid in ids:
    rec = summ.get(uid, {})
    rows.append({
        "gds_id": rec.get("Id"),
        "accession": rec.get("Accession"),
        "title": rec.get("title"),
        "summary": rec.get("Summary"),
        "n_samples": rec.get("n_samples"),
        "platform": rec.get("GPL"),
        "release_date": rec.get("PDAT"),
    })
meta = pd.DataFrame(rows)
meta = meta.dropna(subset=["accession"]).drop_duplicates("accession")
print(meta.head())
```

## Download only needed assets

_modules: download, efetch, filtered-retrieval_

```python
import requests, os

os.makedirs("data", exist_ok=True)
# Download only the records in the filtered accession list, not a bulk dump
for acc in meta["accession"].head(5):           # narrow subset
    r = requests.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params={"db": "gds", "id": acc, "rettype": "full", "retmode": "text"},
    )
    r.raise_for_status()
    with open(f"data/{acc}.txt", "w") as fh:
        fh.write(r.text)
    print("saved", acc, len(r.text), "bytes")
```

## Export usable references

_modules: export, provenance, metadata-tables_

```python
import json, os

os.makedirs("results", exist_ok=True)
# Accession + metadata table for downstream joins
meta.to_csv("results/accession_metadata.tsv", sep="\t", index=False)
# Provenance record (database, query, parameters, access date)
with open("results/retrieval_provenance.json", "w") as fh:
    json.dump(provenance, fh, indent=2)
# Concise query result summary
summary = meta[["accession", "title", "n_samples", "release_date"]]
summary.to_csv("results/query_summary.tsv", sep="\t", index=False)
print("wrote", os.listdir("results"))
```
