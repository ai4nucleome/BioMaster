---
name: "metagenomics-blast-searches"
description: "Run remote BLAST searches against NCBI servers via Bio.Blast.NCBIWWW: pick the correct program and database, configure parameters (word size, composition-based statistics, hitlist_size), submit and poll the RID, then parse and interpret hits using Karlin-Altschul E-values and bit-scores. Avoids the max_target_seqs misuse (Shah et al. 2019)."
domain: "metagenomics"
primary_tool: "Bio.Blast.NCBIWWW"
methods: ["Bio.Blast.NCBIWWW","NCBIXML","blastn-remote"]
macro_tags: []
micro_tags: ["Bio.Blast.NCBIWWW","NCBIXML","blastn-remote","program-selection","blastn","blastp","word-size","database-selection","reproducibility","refseq","metagenomic-db","parameters","composition-based-statistics","hitlist-size","max-target-seqs","submission","rid","polling","rate-limiting","parsing","ncbixml","e-value","bit-score","filtering"]
source: "bioskills/blast-searches"
status: "active"
enabled: true
custom: false
---

# Metagenomics Blast Searches
