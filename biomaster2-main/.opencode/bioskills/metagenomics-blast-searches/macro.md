# Metagenomics Blast Searches

## Overview

Run remote BLAST searches against NCBI servers to identify unknown sequences or find homologs. Inputs: a query sequence (DNA or protein) plus a choice of BLAST program and NCBI database. Outputs: an XML hit table parsed into per-hit E-values, bit-scores, identities, and alignments. Best for one-off identification of a few sequences; for more than ~50 sequences switch to local BLAST or DIAMOND/MMseqs2. The workflow walks through the three consequential decisions (program, database, parameters), submits the query via Bio.Blast.NCBIWWW, polls the Request ID (RID) until completion, then parses and interprets results using Karlin-Altschul E-values and database-size-normalized bit-scores. It avoids the common max_target_seqs misuse (Shah et al. 2019) and guides reproducible database choice (prefer versioned refseq_select/swissprot over the daily-changing nt/nr). Tested with BioPython 1.83+ and NCBI BLAST+ 2.15+; if installed versions differ, introspect the actual API (pip show biopython; help(NCBIWWW.qblast); blastn -version) and adapt rather than retrying on ImportError/AttributeError/TypeError.

## Program Selection

Choose the BLAST program based on the query and target molecule types, since the program defines word-size defaults and the overall search strategy. blastn, megablast, and dc-megablast cover DNA-vs-DNA: megablast (word 28) for high-identity cases such as PCR primer or contamination checks at >=95% identity, dc-megablast (discontiguous, word 11) for sensitive cross-species mRNA, and default blastn (word 11) for general DNA similarity. blastp handles protein-vs-protein, blastx translates a DNA query against a protein database (ORF discovery), tblastn searches a protein query against a translated database (finding unannotated CDS), tblastx translates both sides for the most expensive cross-species coding similarity, and psiblast performs iterative PSSM-based remote homology. The most common misuse is running default blastn or megablast for cross-species DNA where dc-megablast is the correct, sensitive choice.

## Database Selection

Choose the NCBI database based on the trade-off between coverage and reproducibility. nt and nr are comprehensive but change daily, so they are unsuitable for publication reproducibility unless the snapshot date is recorded or a frozen copy is archived. refseq_select (one curated representative per species), refseq_rna, refseq_protein, swissprot, and pdb are versioned and stable. Default to refseq_select for cross-species homology and escalate to nt or nr only when curated coverage is insufficient. Environmental metagenomic databases env_nr and env_nt are available for metagenomic queries and are stable.

## Parameter Configuration

Configure search parameters: word size (inherits program defaults but tunable), composition-based statistics (CBS) to control compositional-bias inflation, and hitlist_size. Critically, do NOT use max_target_seqs as a 'top N hits' filter, because it is an early-termination heuristic that changes which hits the search ever considers, not which it ultimately reports (Shah et al. 2019). The correct pattern is to set hitlist_size large (1000+) and post-filter to the top N by E-value or bit-score in Python. For protein queries under 30 amino acids, use CBS mode 3 (universal statistics) because the default mode 2 over-corrects; for known compositional bias such as coiled-coil or signal-peptide regions, keep CBS=2 and consider hard-masking with SEG.

## Submit and Poll

Submit the query to NCBI's remote BLAST server via NCBIWWW.qblast, which returns a handle backed by a Request ID (RID), and poll until the search completes. NCBI's rate-limit ethic applies: run one search at a time, wait politely between polls, and avoid parallelism. No API key is required for remote BLAST itself. The equivalent CLI path is blastn with the -remote flag and -outfmt 5 to emit XML.

## Parse and Interpret Results

Parse the returned XML with NCBIXML.read into per-hit records, then interpret significance using Karlin-Altschul E-values and bit-scores. E-value depends on database size (E = K*m*n*exp(-lambda*S)), so the same alignment against a 100x larger database yields a 100x larger E-value; cross-database E-value comparison is therefore meaningless, and bit-score (database-size normalized) is the correct cross-database metric. Apply the post-filter from the parameter step to select the top N hits by E-value or bit-score. For marginal protein remote homology (E roughly 1e-3 to 1e-1), escalate to profile methods such as PSI-BLAST, jackhmmer, HHblits, or Foldseek.
