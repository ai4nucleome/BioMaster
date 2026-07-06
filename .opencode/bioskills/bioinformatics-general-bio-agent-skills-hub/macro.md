# Bioinformatics General Bio Agent Skills Hub

## Overview

A router/index skill over 1,676 deduplicated biomedical AI agent skills, aggregated and deduplicated from 20 open-source repositories into 15 categories (genomics, transcriptomics, single-cell, proteomics, clinical, multi-omics, database-query, bioinformatics-general, and others). Each underlying skill is a self-contained SKILL.md folder compatible with Claude-based agent frameworks.

Use this skill whenever a user needs a bioinformatics or biomedical task — genomics, transcriptomics, single-cell, proteomics, protein design, clinical, epigenomics, multi-omics, pathway, metagenomics, database queries, visualization, or workflows — and you need to discover and invoke a specialized skill rather than implement the analysis from scratch.

Inputs: a natural-language description of the desired bioinformatics/biomedical task. Outputs: a ranked list of candidate skills from the index, the single best-matching skill's SKILL.md content fetched on demand, and (optionally) a local copy of the skill folder for offline/bulk/private use.

This skill does NOT duplicate the 1,676 skills. It tells the agent how to (1) search the machine-readable index, (2) locate the single best-matching skill, (3) fetch that skill's SKILL.md from GitHub on demand, and (4) follow it. A git clone fallback (including a China-accelerated mirror) is provided for offline, bulk, or private-network access. The authoritative machine-readable index is a CSV with 1,676 rows and columns skill_name, folder_name, source_repo, category, description, file_count, and archive_path (the path under skills/ used to fetch a skill later).

## Search the index to find candidate skills

Search the authoritative machine-readable index (a CSV with 1,676 rows) to find candidate skills matching the user's task. The index columns are skill_name, folder_name, source_repo, category, description, file_count, and archive_path, where archive_path is the path under skills/ used to fetch the skill in the next step. Search across skill_name, description, category, and source_repo together, since descriptions contain rich 'Use when...' text. Present ranked candidates with their category and archive_path so the right one can be chosen. Rank by name match first, then by file_count. If nothing matches, broaden the query with a synonym, or filter by category and browse that category's README section. The 15 categories include genomics, biology-other, proteomics, clinical, single-cell, transcriptomics, bioinformatics-general, multi-omics, and database-query, among others.

## Fetch the chosen skill's SKILL.md

Once a candidate's archive_path is chosen from the search results, fetch that skill's SKILL.md on demand from the GitHub raw endpoint. Read the fetched content and follow its instructions. Some skills ship supporting files such as scripts/ or references/; if those are needed, list the folder via the GitHub API or clone the repository (next step).

## Offline / bulk / private fallback (clone)

If the raw fetch is unavailable, or all supporting files are wanted, clone the repository and copy the chosen skill folder into the agent's skills directory. A China-accelerated mirror (ghfast.top) is available by prepending the mirror to the GitHub URL; this works for cloning this repository or any source repo. Use this fallback for offline, bulk, or private-network access.
