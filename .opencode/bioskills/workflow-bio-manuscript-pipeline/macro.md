# Workflow Bio Manuscript Pipeline

## Overview

This end-to-end manuscript pipeline transforms a structured research project description into a complete, journal-ready manuscript planning package. Given a research topic, related base work (papers and code), a structured innovation summary, demo data, and optional target journal / refinement settings, the pipeline produces a lab-meeting presentation (PPT), a full research proposal (FINAL_PROPOSAL), detailed task-wise figure designs (Figure 2-7), and manuscript text sections (Introduction, Results, Discussion, Methods). The pipeline runs in two phases: system building (input parsing, innovation analysis, proposal generation, figure design, manuscript drafting, presentation) followed by iterative reviewer-style refinement for a configurable number of rounds. Use this workflow when you have a concrete research idea with supporting literature and demo data and want to produce a structured, publication-oriented planning package. Inputs follow a structured template with required fields (topic, base_work, innovation with subfields, demo_data) and optional fields (target_journal defaulting to nat-communications, num_refine_rounds defaulting to 2). All intermediate and final artifacts are written to the group workspace so that downstream sibling manuscript skills can consume them as context. At the end of each substantial run, a human-readable execution summary is also produced.

## Input Parsing & Project Setup

Parse the structured project input template and validate all required fields. Extract the research topic for innovation search, base_work (paper and code links) for literature analysis, and the structured innovation summary with its subfields: algorithmic novelty, tasks, data, benchmark, metrics, and biological analyses. Capture optional settings: target_journal (default nat-communications) and num_refine_rounds (default 2). Set up the group workspace directory structure and prepare to write intermediate artifacts that downstream sibling skills will consume as context.

## Innovation & Literature Analysis

Using the parsed topic and base_work references, survey related literature and assess the project's algorithmic novelty against existing work. Identify the research gaps the project addresses, evaluate the proposed tasks, data sources, benchmark setup, and metrics for completeness and rigor. Map out how the biological analyses (marker genes, pathway enrichment, neighborhood preservation, tissue-boundary case studies, etc.) will demonstrate biological significance. Produce a structured innovation assessment that feeds into proposal generation.

## Research Proposal Generation

Generate a full research proposal (FINAL_PROPOSAL) that synthesizes the innovation analysis into a coherent research plan. The proposal covers the research question, methodological approach, experimental design, benchmark strategy, expected biological findings, and publication targeting for the chosen journal. This artifact serves as the foundation for figure design and manuscript drafting in subsequent steps.

## Figure Design

Design detailed task-wise figures (Figure 2 through Figure 7) that visualize the method, results, and biological analyses. Each figure corresponds to a specific task or analysis stage, with panel-level descriptions, data sources, and visualization choices. The figure designs are iterated to version 3 (v3) to reflect the refined proposal and innovation assessment, ensuring each figure directly supports a manuscript claim.

## Manuscript Text Drafting

Draft the core manuscript text sections: Introduction, Results, Discussion, and Methods. The Introduction frames the research gap and contribution; the Results present findings organized by task and figure; the Discussion interprets biological significance and limitations; the Methods detail the algorithmic approach, data, and evaluation. The draft reaches version 2 (v2) by incorporating the proposal and figure designs.

## Presentation & Summary Generation

Generate a lab-meeting or progress presentation (PPT) summarizing the project for internal review. Additionally, write a concise human-readable execution summary (FINAL_EXEC_SUMMARY.md) documenting the pipeline run, its inputs, and the artifacts produced. For integration-focused runs, also write an INTEGRATION_TEST_REPORT.md. These artifacts capture the pipeline's outputs and facilitate handoff to collaborators or downstream sibling skills.

## Iterative Refinement

Run reviewer-style feedback loops for the configured number of refinement rounds (num_refine_rounds, default 2). In each round, critique the proposal, figures, and manuscript text from a reviewer's perspective, identifying weaknesses in novelty, rigor, clarity, or biological significance, and revise the artifacts accordingly. The refinement loop improves the overall quality and publication readiness of the manuscript planning package before final delivery.
