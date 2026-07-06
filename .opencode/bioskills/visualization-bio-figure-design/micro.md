## Setup & Input Parsing

_modules: setup, input-parsing, validation_

```text
# Required inputs (pipe-delimited or structured)
topic: [research topic]
task_system: [task system]
dataset_catalog: [dataset catalog]
metric_system: [metric system]
analysis_system: [analysis system]
target_journal: [optional, default nat-communications]
```

```markdown
# Validation checklist
- [ ] Every task in task_system has >=1 dataset in dataset_catalog
- [ ] Every task has >=1 metric in metric_system
- [ ] analysis_system covers all tasks intended for main figures
- [ ] target_journal figure conventions noted (panel style / color / count)
```

## Design Figure 1 (Framework Overview)

_modules: figure1, framework, overview_

```markdown
## Figure 1: Framework Overview
- Panel a: method / model overview
- Panel b: data or modality overview
- Panel c: task overview
- Panel d: metric overview
- Panel e: analysis overview
- Caption intent: [one-sentence framing of the whole paper]
```

# Design rules for Figure 1
- Conceptual only; no raw result plots
- One coherent visual logic across all five panels
- Must map to the manuscript's central claim

## Design Figures 2-N (Task-Driven Application Figures)

_modules: application-figures, task-driven, quantitative-evaluation, biological-validation_

```markdown
## Figure 2: [Task 1]
- Panel a: data flow / experimental setup
- Panel b: quantitative evaluation (metric: ___)
- Panel c: quantitative evaluation (metric: ___)
- Panel d: quantitative evaluation (metric: ___)
- Panel e: qualitative / biological validation
- Caption intent: [claim this figure supports]

## Figure 3: [Task 2]
- Panel a: data flow / experimental setup
- Panel b-d: quantitative evaluation
- Panel e+: qualitative / biological validation
- Caption intent: [claim this figure supports]
```

# Design rules for application figures
- One major task per figure
- Every panel tied to a concrete task + metric
- Quantitative panels before biological-validation panels
- If a panel does not support the figure's claim, move it to supplementary

## Plan Supplementary Figures

_modules: supplementary, ablation, robustness_

```markdown
## Supplementary Figures
- Supplementary Figure 1: [ablation: ___]
- Supplementary Figure 2: [robustness check: ___]
- Supplementary Figure 3: [extra markers / extended dataset: ___]
- Supplementary Figure 4: [alternative parameter settings: ___]
```

# Allocation rules
- Move any panel not tied to a main claim here
- One purpose per supplementary figure
- Keep ablations and robustness checks separate from result figures

## Draft Captions & Assemble Output

_modules: caption, claims, output-assembly_

```markdown
# Figure Designs

## Figure 1: Framework Overview
- Panel a: ...
- Panel b: ...
- Panel c: ...
- Panel d: ...
- Panel e: ...
- Caption intent: ...

## Figure 2: [Task 1]
- Panel a-e: ...
- Caption intent: ...

## Supplementary Figures
- Supplementary Figure 1: ...
- Supplementary Figure 2: ...

## Design Notes
- visual consistency: [color/style/panel-size rules]
- panel ordering logic: [why panels are in this order]
- expected take-home message per figure: [one line per figure]

## Next Step
- Use the figure plan to draft manuscript text in Step 7
```

# Caption plan template (per figure)
- What each panel shows: ___
- What claim it supports: ___
- What dataset it uses: ___
- What metric / biological conclusion it demonstrates: ___
