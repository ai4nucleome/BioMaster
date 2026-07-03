## Expression Data Integration

_modules: expression-loading, normalization, gpr-mapping_

```python
import numpy as np
import pandas as pd

def load_expression_data(filepath, gene_col='gene_id', expr_col='TPM'):
    '''Load and normalize expression data.

    Accepts RNA-seq counts (TPM, FPKM), microarray intensities, or proteomics
    abundances. Returns a dict mapping gene_id -> normalized expression in [0, 1].
    '''
    df = pd.read_csv(filepath)

    expr = df[expr_col].values
    # Log-transform if the dynamic range is very high
    if expr.max() / expr.mean() > 100:
        expr = np.log2(expr + 1)

    # Normalize to 0-1 range
    expr_norm = (expr - expr.min()) / (expr.max() - expr.min())
    return dict(zip(df[gene_col], expr_norm))


def aggregate_gene_expression(model, expression_data, method='max'):
    '''Map gene expression to reactions via GPR rules.

    method:
      - 'max'  : OR logic (use maximum gene expression)
      - 'min'  : AND logic (use minimum gene expression, e.g. for complexes)
      - 'mean' : average across genes
    For a GPR like (A and B) or C, combine min(A, B) for the complex then
    max(complex, C) for the alternatives.
    '''
    rxn_expression = {}
    for rxn in model.reactions:
        if not rxn.genes:
            rxn_expression[rxn.id] = 0.5  # default for non-enzymatic
            continue
        gene_expr = [expression_data.get(g.id, 0.5) for g in rxn.genes]
        if method == 'max':
            rxn_expression[rxn.id] = max(gene_expr)
        elif method == 'min':
            rxn_expression[rxn.id] = min(gene_expr)
        else:
            rxn_expression[rxn.id] = np.mean(gene_expr)
    return rxn_expression
```

## GIMME Context Model

_modules: GIMME, biomass-constraint, reaction-pruning_

```python
import cobra
import numpy as np

def gimme(model, expression_data, threshold=0.25, required_growth=0.1):
    '''Gene Inactivity Moderated by Metabolism and Expression (GIMME).

    Args:
        expression_data: dict mapping gene_id -> expression value
        threshold: expression percentile below which genes are inactive
                  (0.25 = bottom 25% considered inactive)
        required_growth: minimum biomass/growth rate to maintain

    Returns:
        Context-specific model with inactive reactions constrained.
    '''
    # Calculate expression threshold
    values = list(expression_data.values())
    cutoff = np.percentile(values, threshold * 100)

    # Identify lowly-expressed genes
    low_expressed = {g for g, v in expression_data.items() if v < cutoff}

    # Create context model and enforce minimum growth
    context_model = model.copy()
    context_model.reactions.get_by_id('Biomass_Ecoli_core').lower_bound = required_growth

    # Minimize flux through reactions whose genes are all low-expressed
    for rxn in context_model.reactions:
        genes = {g.id for g in rxn.genes}
        if genes and genes.issubset(low_expressed):
            rxn.upper_bound = min(rxn.upper_bound, 1.0)
            rxn.lower_bound = max(rxn.lower_bound, -1.0)

    return context_model
```

## iMAT Context Model

_modules: iMAT, milp, expression-thresholding_

```python
import numpy as np

def imat(model, expression_data, high_threshold=0.75, low_threshold=0.25):
    '''Integrative Metabolic Analysis Tool (iMAT).

    Maximizes agreement between flux activity and expression:
      - highly expressed reactions should carry flux
      - lowly expressed reactions should have zero flux
    More sophisticated than GIMME; full iMAT uses MILP with binary variables.
    '''
    from cobra import Reaction

    high_expr_rxns = []
    low_expr_rxns = []

    for rxn in model.reactions:
        if rxn.genes:
            # Aggregate gene expression (max for OR, min for AND)
            gene_expr = [expression_data.get(g.id, 0.5) for g in rxn.genes]
            rxn_expr = max(gene_expr)  # simplified OR logic

            if rxn_expr > np.percentile(list(expression_data.values()), high_threshold * 100):
                high_expr_rxns.append(rxn.id)
            elif rxn_expr < np.percentile(list(expression_data.values()), low_threshold * 100):
                low_expr_rxns.append(rxn.id)

    # Create MILP to maximize consistent reactions (simplified version)
    context_model = model.copy()

    # Force flux through highly expressed reactions
    for rxn_id in high_expr_rxns:
        rxn = context_model.reactions.get_by_id(rxn_id)
        rxn.lower_bound = max(rxn.lower_bound, 0.01)

    # Constrain lowly expressed reactions
    for rxn_id in low_expr_rxns:
        rxn = context_model.reactions.get_by_id(rxn_id)
        rxn.upper_bound = min(rxn.upper_bound, 0.1)
        rxn.lower_bound = max(rxn.lower_bound, -0.1)

    return context_model, high_expr_rxns, low_expr_rxns
```

## Tissue-Specific Model Construction

_modules: tissue-specific, gtex, human-model_

```python
import pandas as pd

def create_tissue_model(generic_model, gtex_expression, tissue='liver'):
    '''Create a tissue-specific model from GTex expression data.

    GTEx provides median TPM for 54 human tissues.
    Download from: https://gtexportal.org/home/datasets
    '''
    # Load GTEx median expression
    gtex = pd.read_csv(gtex_expression, sep='\t')

    # Extract the tissue column (case-insensitive match)
    tissue_col = [c for c in gtex.columns if tissue.lower() in c.lower()][0]
    expression = dict(zip(gtex['gene_id'], gtex[tissue_col]))

    # Apply GIMME to build the tissue-specific model
    tissue_model = gimme(generic_model, expression, threshold=0.25)
    return tissue_model
```

## Model Validation

_modules: validation, fba, growth-comparison_

```python
def validate_context_model(original, context, expression_data):
    '''Compare original and context-specific models.

    Checks:
      1. Growth capability maintained
      2. Inactive reactions reduced
      3. Active reactions maintained
    '''
    # Growth comparison via FBA
    orig_growth = original.optimize().objective_value
    context_growth = context.optimize().objective_value

    # Count constrained reactions
    constrained = 0
    for rxn in context.reactions:
        orig_rxn = original.reactions.get_by_id(rxn.id)
        if rxn.upper_bound < orig_rxn.upper_bound:
            constrained += 1

    return {
        'original_growth': orig_growth,
        'context_growth': context_growth,
        'growth_ratio': context_growth / orig_growth,
        'constrained_reactions': constrained,
        'total_reactions': len(context.reactions),
    }
```
