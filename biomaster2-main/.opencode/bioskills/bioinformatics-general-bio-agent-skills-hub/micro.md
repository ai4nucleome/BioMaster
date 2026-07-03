## Search the index to find candidate skills

_modules: search, index, routing, skill-discovery_

```python
import pandas as pd

# Authoritative v3 index. Prefer a local copy if this skill bundles one; else read from GitHub raw.
INDEX_URL = "https://raw.githubusercontent.com/BioTender-max/awesome-bio-agent-skills/main/bioskill_index_v3.csv"
df = pd.read_csv(INDEX_URL)   # 1,676 rows

def search_skills(query, category=None, source=None, top=15):
    """Keyword search over name+description+category+source. Returns candidate skills."""
    q = query.lower()
    hay = (df["skill_name"].fillna("") + " | " +
           df["description"].fillna("") + " | " +
           df["category"].fillna("") + " | " +
           df["source_repo"].fillna("")).str.lower()
    hits = df[hay.str.contains(q, regex=False)].copy()
    if category:
        hits = hits[hits["category"] == category]
    if source:
        hits = hits[hits["source_repo"] == source]
    # rank: name match first, then description match
    hits["_name_hit"] = hits["skill_name"].str.lower().str.contains(q, regex=False)
    hits = hits.sort_values(["_name_hit", "file_count"], ascending=[False, False])
    return hits[["skill_name", "category", "source_repo", "archive_path", "description"]].head(top)

print(search_skills("variant calling").to_string(index=False))
```

Key parameters: `query` (keyword, matched case-insensitively as a substring), `category` (optional filter by category key, e.g. `genomics`, `single-cell`), `source` (optional filter by source_repo), `top` (number of candidates to return, default 15).

## Fetch the chosen skill's SKILL.md

_modules: fetch, skill-retrieval, github-raw_

```python
import urllib.request

archive_path = "bioskills/clair3-variants"   # from the search result
url = f"https://raw.githubusercontent.com/BioTender-max/awesome-bio-agent-skills/main/skills/{archive_path}/SKILL.md"
skill_md = urllib.request.urlopen(url, timeout=30).read().decode()
print(skill_md)   # read it, then follow its instructions
```

Key parameter: `archive_path` (the path under skills/ returned by the search, e.g. `bioskills/clair3-variants`). Fetch timeout is 30s. The raw URL pattern is `https://raw.githubusercontent.com/BioTender-max/awesome-bio-agent-skills/main/skills/<archive_path>/SKILL.md`.

## Offline / bulk / private fallback (clone)

_modules: clone, offline, mirror, fallback_

```bash
# Standard (international)
git clone https://github.com/BioTender-max/awesome-bio-agent-skills.git
cp -r awesome-bio-agent-skills/skills/<archive_path>/ /path/to/your/agent/skills/

# China-accelerated (ghfast.top mirror) — prepend the mirror to the GitHub URL;
# works for cloning this or any source repo (https://ghfast.top/https://github.com/<owner>/<repo>.git)
git clone https://ghfast.top/https://github.com/BioTender-max/awesome-bio-agent-skills.git
cp -r awesome-bio-agent-skills/skills/<archive_path>/ /path/to/your/agent/skills/
```

Key parameter: `<archive_path>` (the path under skills/ from the search result). Replace `/path/to/your/agent/skills/` with the target agent's skills directory.
