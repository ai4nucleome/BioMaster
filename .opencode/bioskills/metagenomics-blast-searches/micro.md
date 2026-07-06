## Program Selection

_modules: program-selection, blastn, blastp, word-size_

from Bio.Blast import NCBIWWW, NCBIXML
from Bio import SeqIO

# Program decision (query vs database molecule):
#   blastn       DNA->DNA    word=11   general DNA similarity
#   megablast    DNA->DNA    word=28   high-identity (>=95%): primers, contamination
#   dc-megablast DNA->DNA    word=11   cross-species mRNA (discontiguous, gapped, sensitive)
#   blastp       Prot->Prot  word=3    general protein homology (6 also valid)
#   blastx       DNA->Prot   word=3    translated query vs protein DB; ORF discovery
#   tblastn      Prot->DNA   word=3    protein query vs translated DB; unannotated CDS
#   tblastx      DNA->DNA    word=3    both translated; most expensive cross-species coding
#   psiblast     Prot->Prot  word=3    iterative PSSM remote homology (see remote-homology)

# Core call signature (program chosen here, db + sequence in later steps):
# handle = NCBIWWW.qblast(program, db, sequence, ...)

## Database Selection

_modules: database-selection, reproducibility, refseq, metagenomic-db_

# Database choice (db= argument to qblast / -db on the CLI):
#   nt              non-redundant nucleotide (GenBank+EMBL+DDBJ) ~250GB  NOT stable (daily)
#   nr              non-redundant protein ~300GB                       NOT stable (daily)
#   refseq_select   one curated rep per species (RNA+protein) small     versioned/stable
#   refseq_rna      RefSeq mRNA ~10GB                                  stable
#   refseq_protein  RefSeq protein small                               stable
#   swissprot       UniProt Swiss-Prot (reviewed) small                stable (monthly)
#   pdb             protein structures small                           stable
#   refseq_genomic  RefSeq genomic huge                                stable
#   env_nr/env_nt   environmental (metagenomic) huge                   stable

# Reproducibility rule: never publish results from nt/nr without recording
# the snapshot date (and ideally archiving a frozen copy). Default to
# refseq_select for cross-species homology; escalate to nt/nr only when
# curated coverage is insufficient.

## Parameter Configuration

_modules: parameters, composition-based-statistics, hitlist-size, max-target-seqs_

# Composition-Based Statistics (composition_based_statistics=):
#   0  off                                  almost never
#   1  F&S 2002 score adjustment            legacy compatibility
#   2  Yu&Altschul 2005 conditional         DEFAULT since BLAST+ 2.2.17; correct for most cases
#   3  universal statistics                 short queries (<30 aa) where mode 2 over-corrects

# max_target_seqs TRAP (Shah et al. 2019, Bioinformatics 35:1613):
#   max_target_seqs is an EARLY-TERMINATION heuristic, NOT a 'top N' filter.
#   max_target_seqs=10 can return different hits than max_target_seqs=500
#   then filtering to top 10 by E-value.
# CORRECT PATTERN: set hitlist_size large, post-filter in Python (see Step 5).
handle = NCBIWWW.qblast(
    program='blastp',
    db='refseq_select',
    sequence=query_seq,
    hitlist_size=1000,                  # large; let the search consider many hits
    # composition_based_statistics=3,   # set to 3 for protein queries < 30 aa
    # expect=0.001,                     # E-value threshold
)
# Word size inherits program defaults (see Step 1); override only with reason
# (lower for sensitivity, raise for speed on near-identical DNA). For protein
# with compositional bias keep CBS=2 and consider hard-masking with SEG.

## Submit and Poll

_modules: submission, rid, polling, rate-limiting_

import time
from Bio.Blast import NCBIWWW

# Submit; qblast returns a handle backed by an RID. By default NCBIWWW.qblast
# blocks until the search is ready. NCBI rate-limit ethic: one search at a
# time, polite polling, no parallelism. No API key required for remote BLAST.
handle = NCBIWWW.qblast(program='blastn', db='refseq_rna', sequence=query_seq)

# For explicit RID control / non-blocking use, capture the RID from the
# submission response and poll NCBI's status endpoint until ready, then fetch
# results. Keep poll intervals polite (seconds, not sub-second).

# Equivalent CLI (emits XML, outfmt 5):
#   blastn -remote -db nt -query seq.fa -out hits.xml -outfmt 5

## Parse and Interpret Results

_modules: parsing, ncbixml, e-value, bit-score, filtering_

from Bio.Blast import NCBIXML

blast_record = NCBIXML.read(handle)      # single query -> one record
# For multiple queries use NCBIXML.parse(handle) and iterate.

# E-value interpretation (Karlin-Altschul, BLOSUM62 protein):
#   E < 1e-50        bit > 200    strong; almost certainly homologous
#   1e-50..1e-10     100-200      significant; likely homolog
#   1e-10..1e-3      50-100       marginal; check identity + coverage
#   0.01..10         30-50        possible remote homolog; needs profile method
#   E > 10           bit < 30     random; not meaningful
#
# E = K*m*n*exp(-lambda*S): same alignment vs a 100x larger DB -> 100x larger E.
# Cross-database E-value comparison is MEANINGLESS. Use bit-score (DB-size
# normalized) as the cross-database metric.

# Post-filter to top N by E-value (correct alternative to max_target_seqs):
top_hits = sorted(
    blast_record.alignments,
    key=lambda aln: aln.hsps[0].expect
)[:10]

# For marginal protein remote homology (E ~1e-3..1e-1), escalate to profile
# methods: PSI-BLAST, jackhmmer, HHblits, Foldseek (see remote-homology skill).
