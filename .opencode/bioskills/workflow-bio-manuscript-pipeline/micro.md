## Input Parsing & Project Setup

_modules: input-parsing, project-setup, validation_

```text
# Required input template
 topic: [research topic]
 base_work:
   - paper: [related paper link]
   - code: [related code repository]
 innovation: [one-sentence innovation summary]
 - algorithmic novelty: [core method novelty]
 - tasks: [task1, task2, task3, ...]
 - data: [dataset source or type]
 - benchmark: [evaluation benchmark]
 - metrics: [metric1, metric2, ...]
 - biological analyses: [how biological significance will be shown]
 demo_data: [demo dataset link]
 target_journal: [optional, default nat-communications]
 num_refine_rounds: [optional, default 2]
```

```python
# Execution outline
parsed = parse_input_template(user_input)
validate_required_fields(parsed, required=["topic", "base_work", "innovation", "demo_data"])
apply_defaults(parsed, target_journal="nat-communications", num_refine_rounds=2)
workspace = setup_group_workspace(parsed["topic"])
# Extract key signals for downstream phases
topic_signal = parsed["topic"]            # -> innovation search
base_work_signal = parsed["base_work"]    # -> literature analysis
innovation_signal = parsed["innovation"]  # -> proposal generation
write_artifact(workspace, "PARSED_INPUT.json", parsed)
```

## Innovation & Literature Analysis

_modules: literature-analysis, innovation-assessment, gap-analysis_

```python
# Execution outline
related_work = survey_literature(topic_signal, base_work_signal)
gap_analysis = identify_research_gaps(related_work, innovation_signal)
novelty_assessment = assess_algorithmic_novelty(
    innovation_signal["algorithmic_novelty"],
    related_work,
)
task_eval = evaluate_tasks(innovation_signal["tasks"], innovation_signal["benchmark"])
metric_eval = evaluate_metrics(innovation_signal["metrics"])
bio_plan = plan_biological_analyses(innovation_signal["biological_analyses"])
innovation_report = {
    "related_work": related_work,
    "gap_analysis": gap_analysis,
    "novelty_assessment": novelty_assessment,
    "task_evaluation": task_eval,
    "metric_evaluation": metric_eval,
    "biological_analysis_plan": bio_plan,
}
write_artifact(workspace, "INNOVATION_ANALYSIS.md", innovation_report)
```

## Research Proposal Generation

_modules: proposal-generation, research-planning_

```python
# Execution outline
proposal = generate_research_proposal(
    parsed_input=parsed,
    innovation_report=innovation_report,
    target_journal=parsed["target_journal"],
)
# Proposal sections
# - Research question & motivation
# - Methodological approach (algorithmic novelty)
# - Experimental design (tasks, data, benchmark)
# - Evaluation strategy (metrics)
# - Expected biological findings
# - Publication targeting (journal scope & fit)
write_artifact(workspace, "FINAL_PROPOSAL.md", proposal)
```

## Figure Design

_modules: figure-design, visualization-planning_

```python
# Execution outline
figure_plan = design_figures(
    proposal=proposal,
    tasks=innovation_signal["tasks"],
    bio_plan=bio_plan,
    target_version="v3",
)
# Typical figure allocation:
#  Figure 2: method overview / architecture
#  Figure 3: main task results (e.g., integration / mapping)
#  Figure 4: benchmark comparison
#  Figure 5: biological analysis (markers / pathways)
#  Figure 6: neighborhood / boundary case studies
#  Figure 7: additional ablations or downstream analyses
for fig in figure_plan:
    fig["panels"] = define_panels(fig, data_source=innovation_signal["data"])
    fig["visualization"] = choose_visualization(fig["panels"])
write_artifact(workspace, "FIGURE_DESIGN_v3.md", figure_plan)
```

## Manuscript Text Drafting

_modules: manuscript-drafting, scientific-writing_

```python
# Execution outline
manuscript = {}
manuscript["introduction"] = draft_introduction(
    gap_analysis, novelty_assessment, proposal
)
manuscript["results"] = draft_results(
    figure_plan, task_eval, metric_eval, bio_plan
)
manuscript["discussion"] = draft_discussion(
    bio_plan, novelty_assessment, limitations=True
)
manuscript["methods"] = draft_methods(
    innovation_signal["algorithmic_novelty"],
    innovation_signal["data"],
    innovation_signal["benchmark"],
    innovation_signal["metrics"],
)
write_artifact(workspace, "MANUSCRIPT_TEXT_v2.md", manuscript)
```

## Presentation & Summary Generation

_modules: presentation, summary-generation_

```python
# Execution outline
ppt = generate_presentation(
    proposal=proposal,
    figure_plan=figure_plan,
    audience="lab_meeting",
)
write_artifact(workspace, "PROGRESS_PPT.md", ppt)  # or .pptx outline

exec_summary = write_exec_summary(
    inputs=parsed,
    artifacts=[
        "INNOVATION_ANALYSIS.md",
        "FINAL_PROPOSAL.md",
        "FIGURE_DESIGN_v3.md",
        "MANUSCRIPT_TEXT_v2.md",
        "PROGRESS_PPT.md",
    ],
    status="complete",
)
write_artifact(workspace, "FINAL_EXEC_SUMMARY.md", exec_summary)

# For integration-focused runs only:
if integration_run:
    write_artifact(workspace, "INTEGRATION_TEST_REPORT.md", integration_report)
```

## Iterative Refinement

_modules: iterative-refinement, reviewer-feedback_

```python
# Execution outline
rounds = parsed["num_refine_rounds"]  # default 2
artifacts = {
    "proposal": proposal,
    "figures": figure_plan,
    "manuscript": manuscript,
}
for r in range(1, rounds + 1):
    review = reviewer_style_critique(
        artifacts,
        focus=["novelty", "rigor", "clarity", "biological_significance"],
        target_journal=parsed["target_journal"],
    )
    artifacts = revise_artifacts(artifacts, review)
    write_artifact(workspace, f"REFINE_ROUND_{r}_REVIEW.md", review)
# Write final refined versions
write_artifact(workspace, "FINAL_PROPOSAL.md", artifacts["proposal"])
write_artifact(workspace, "FIGURE_DESIGN_v3.md", artifacts["figures"])
write_artifact(workspace, "MANUSCRIPT_TEXT_v2.md", artifacts["manuscript"])
```
