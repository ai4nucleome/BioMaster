## API Setup & Query Helper

_modules: api, graphql, http, setup_

```python
import requests
import json

OPENTARGETS_URL = "https://api.platform.opentargets.org/api/v4/graphql"

def query_opentargets(graphql_query, variables=None):
    """Post a GraphQL query to the OpenTargets Platform API.

    Args:
        graphql_query: GraphQL query string.
        variables: optional dict of query variables.

    Returns:
        Parsed JSON response dict.
    """
    payload = {"query": graphql_query, "variables": variables or {}}
    r = requests.post(
        OPENTARGETS_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    r.raise_for_status()
    return r.json()
```

## Entity Search & Resolution

_modules: search, target-resolution, disease-resolution, efo, ensembl_

```python
# Search for a target (gene) by name -> resolve to Ensembl ID
def search_target(gene_name):
    query = '''
    query searchTarget($name: String!) {
      search(queryString: $name, entityNames: ["target"], page: {index: 0, size: 5}) {
        hits { id name description entity }
      }
    }'''
    return query_opentargets(query, {"name": gene_name})

# Search for a disease by name -> resolve to EFO ID
def search_disease(disease_name):
    query = '''
    query searchDisease($name: String!) {
      search(queryString: $name, entityNames: ["disease"], page: {index: 0, size: 5}) {
        hits { id name description entity }
      }
    }'''
    return query_opentargets(query, {"name": disease_name})

# Common Disease IDs (EFO) — quick reference, skip search when known:
#   Alzheimer's disease : EFO_0000249
#   Breast cancer       : EFO_0000305
#   Type 2 diabetes     : EFO_0001360
#   Parkinson's disease : EFO_0002508

# Usage: take hits[0]["id"] as the resolved Ensembl/EFO ID for downstream steps.
```

## Target-Disease Associations

_modules: associations, target-disease, scoring, evidence_

```python
# Diseases associated with a target (Ensembl ID)
def target_diseases(ensembl_id, size=10):
    query = '''
    query targetDiseases($ensemblId: String!, $size: Int!) {
      target(ensemblId: $ensemblId) {
        id approvedSymbol approvedName
        associatedDiseases(page: {index: 0, size: $size}) {
          count
          rows { disease { id name } score
            datasourceScores { componentId score } }
        }
      }
    }'''
    return query_opentargets(query, {"ensemblId": ensembl_id, "size": size})

# Targets associated with a disease (EFO ID)
def disease_targets(disease_id, size=10):
    query = '''
    query diseaseTargets($diseaseId: String!, $size: Int!) {
      disease(efoId: $diseaseId) {
        id name
        associatedTargets(page: {index: 0, size: $size}) {
          count
          rows { target { id approvedSymbol approvedName } score }
        }
      }
    }'''
    return query_opentargets(query, {"diseaseId": disease_id, "size": size})

# Tip: inspect datasourceScores to break down evidence by source
# (e.g. genetic_association, literature, known_drug, animal_model).
```

## Drug & Clinical Trial Lookup

_modules: drugs, clinical-trials, mechanism-of-action, target-validation_

```python
# Known drugs for a target (Ensembl ID)
def target_drugs(ensembl_id):
    query = '''
    query targetDrugs($ensemblId: String!) {
      target(ensemblId: $ensemblId) {
        id approvedSymbol
        knownDrugs(size: 10) {
          count
          rows { drug { id name } mechanismOfAction phase status
            disease { id name } }
        }
      }
    }'''
    return query_opentargets(query, {"ensemblId": ensembl_id})

# End-to-end example: top drug targets for Alzheimer's disease
result = search_disease("Alzheimer")
hits = result.get("data", {}).get("search", {}).get("hits", [])
if hits:
    disease_id = hits[0]["id"]
    targets = disease_targets(disease_id, size=5)
    disease = targets.get("data", {}).get("disease", {})
    print(f"Disease: {disease.get('name')} ({disease.get('id')})")
    for row in disease.get("associatedTargets", {}).get("rows", []):
        t = row["target"]
        print(f"  {t['approvedSymbol']} ({t['approvedName']}) — score: {row['score']:.3f}")
```
