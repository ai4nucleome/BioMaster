# Visualization Bio Figure Design

## Overview

This workflow designs the figures of a computational biology / bioinformatics manuscript panel by panel, producing a structured markdown figure-design document that feeds directly into manuscript writing. It is run after the analysis system is complete and before drafting manuscript text.

Inputs: (1) research topic, (2) task system (the set of tasks the method addresses), (3) dataset catalog, (4) metric system, (5) analysis system, and optionally (6) target journal (default: nat-communications).

Outputs: a markdown document containing Figure 1 (framework/method overview), Figures 2-N (one major task per figure, with quantitative evaluation before biological validation), supplementary figures (ablations, robustness, extended data), per-figure caption plans, and design notes on visual consistency and take-home messages.

When to use: when the analysis is done and you need to plan the visual narrative of the paper so that figure order matches the manuscript story, every panel ties to a concrete task and metric, and reviewer-facing clarity is prioritized over decorative complexity.

Design principles enforced throughout: one main claim per figure; quantitative evidence before broad interpretation; biological validation visible rather than hidden; figure order matches the manuscript story; do not overload a main figure if a supplementary figure can carry the extra material.

## Setup & Input Parsing

Parse and validate the five required inputs (topic, task_system, dataset_catalog, metric_system, analysis_system) plus the optional target_journal. Confirm that every planned figure will map to at least one task, dataset, and metric, so no figure is left without supporting evidence. If a target journal is specified, note its figure conventions (panel style, color, count limits) to respect during design.

## Design Figure 1 (Framework Overview)

Design Figure 1 as the method/framework overview that makes the full manuscript logic visible in a single figure. Plan five panels: (a) method/model overview, (b) data or modality overview, (c) task overview, (d) metric overview, (e) analysis overview. Keep Figure 1 conceptual and clean; its goal is to communicate the paper framing, not to present results.

## Design Figures 2-N (Task-Driven Application Figures)

Design each application figure around exactly one major task. Structure every application figure consistently: panel a for data flow or experimental setup, panels b-d for quantitative evaluation, panel e or later for qualitative or biological validation. Tie every panel to a concrete task and metric so the paper stays organized around claims rather than around plots. Quantitative evidence must appear before broad interpretation, and biological validation must be visible.

## Plan Supplementary Figures

Allocate supplementary figures for material that supports the main claims but does not belong in the main figures: ablations, robustness checks, extra markers, extended datasets, and alternative parameter settings. Do not overload a main figure if a supplementary figure can carry the extra material. List each supplementary figure with a one-line purpose.

## Draft Captions & Assemble Output

For every figure (main and supplementary), draft a caption plan that states what each panel shows, what claim it supports, what dataset it uses, and what metric or biological conclusion it demonstrates. Then assemble all figure designs into the final markdown output, adding design notes on visual consistency, panel ordering logic, and the expected take-home message per figure. The assembled document is the handoff to manuscript text drafting.
