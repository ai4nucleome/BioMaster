"""BioMaster-OpenCode MVP constants per implementation plan."""

from __future__ import annotations

MVP_SKILL_IDS: frozenset[str] = frozenset(
    {
        "biomaster",
        "registry",
        "domain-guide-tumor",
        "discipline-scrnaseq",
        "pipeline-scrnaseq-tumor",
        "plan-scrnaseq-tumor-heterogeneity",
        "exec-scanpy",
        "exec-infercnvpy",
        "exec-palantir",
        "exec-cnmf",
        "verify-scrna-qc",
        "verify-infercnv",
        "verify-trajectory",
        "verify-cnmf",
        "debug-conda",
        "debug-tool-not-found",
        "debug-missing-files",
        "debug-python-package",
        "debug-reference-genome",
        "env-python-scrnaseq",
        "env-r-bioc",
        "report-tumor-scrnaseq",
    }
)

LEGACY_SKILL_IDS: frozenset[str] = frozenset(
    {
        "plan-workflow",
        "exec-task",
        "exec-conda",
        "exec-r-package",
        "verify-report",
        "debug-runtime",
    }
)

MVP_CORE_TABLES: tuple[str, ...] = (
    "skills",
    "pipeline_routes",
    "run_states",
)

MVP_OPTIONAL_TABLES: tuple[str, ...] = ("skill_selection_logs",)

MVP_REQUIRED_TABLES: tuple[str, ...] = MVP_CORE_TABLES + MVP_OPTIONAL_TABLES

TUMOR_PIPELINE_STEPS: tuple[dict[str, object], ...] = (
    {
        "step_id": "01_data_preflight",
        "objective": "Validate input scRNA-seq data format and load demo or user dataset.",
        "required_execute_skills": ["exec-scanpy"],
        "required_verify_skills": ["verify-scrna-qc"],
        "expected_outputs": ["input validation summary", "adata_raw.h5ad"],
        "acceptance_criteria": [
            "h5ad or 10x matrix is readable",
            "cell and gene counts are reported",
        ],
    },
    {
        "step_id": "02_qc_filter",
        "objective": "Filter low-quality cells and genes.",
        "required_execute_skills": ["exec-scanpy"],
        "required_verify_skills": ["verify-scrna-qc"],
        "expected_outputs": ["adata_qc.h5ad", "qc_metrics.csv"],
        "acceptance_criteria": ["mitochondrial fraction thresholds applied", "gene/cell counts logged"],
    },
    {
        "step_id": "03_doublet_removal",
        "objective": "Detect and remove doublets.",
        "required_execute_skills": ["exec-scanpy"],
        "required_verify_skills": ["verify-scrna-qc"],
        "expected_outputs": ["adata_no_doublets.h5ad"],
        "acceptance_criteria": ["doublet scores computed", "filtered cell count reported"],
    },
    {
        "step_id": "04_batch_correction",
        "objective": "Correct batch effects when batch metadata exists.",
        "required_execute_skills": ["exec-scanpy"],
        "required_verify_skills": ["verify-scrna-qc"],
        "expected_outputs": ["adata_batch_corrected.h5ad"],
        "acceptance_criteria": ["batch column validated or skipped with reason"],
    },
    {
        "step_id": "05_clustering_annotation",
        "objective": "Cluster cells and annotate major cell types.",
        "required_execute_skills": ["exec-scanpy"],
        "required_verify_skills": ["verify-scrna-qc"],
        "expected_outputs": ["adata_annotated.h5ad", "umap.png", "marker_genes.csv"],
        "acceptance_criteria": ["clusters and UMAP generated", "annotation table exported"],
    },
    {
        "step_id": "06_infercnv_malignancy",
        "objective": "Identify malignant cells with inferCNVpy.",
        "required_execute_skills": ["exec-infercnvpy"],
        "required_verify_skills": ["verify-infercnv"],
        "expected_outputs": ["infercnv/", "malignancy_scores.csv"],
        "acceptance_criteria": ["reference vs observation labels defined", "CNV heatmap exported"],
    },
    {
        "step_id": "07_palantir_trajectory",
        "objective": "Infer state trajectory with Palantir.",
        "required_execute_skills": ["exec-palantir"],
        "required_verify_skills": ["verify-trajectory"],
        "expected_outputs": ["palantir/pseudotime.csv", "palantir/branch_probs.csv"],
        "acceptance_criteria": ["pseudotime values generated", "branch probabilities exported"],
    },
    {
        "step_id": "08_cnmf_modules",
        "objective": "Discover co-expression modules with cNMF.",
        "required_execute_skills": ["exec-cnmf"],
        "required_verify_skills": ["verify-cnmf"],
        "expected_outputs": ["cnmf/modules.csv", "cnmf/gene_loadings.csv"],
        "acceptance_criteria": ["module count selected", "top genes per module exported"],
    },
    {
        "step_id": "09_report_generation",
        "objective": "Summarize all prior steps into a structured report.",
        "required_report_skills": ["report-tumor-scrnaseq"],
        "required_verify_skills": ["verify-scrna-qc"],
        "expected_outputs": ["REPORT.md"],
        "acceptance_criteria": [
            "report contains QC, annotation, malignancy, trajectory, and cNMF sections",
        ],
    },
)

REGISTRY_REQUIRED_OUTPUT_FIELDS: tuple[str, ...] = (
    "domain",
    "discipline",
    "candidate_pipeline",
    "confidence",
    "missing_information",
    "next_skill_candidates",
)
