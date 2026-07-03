from __future__ import annotations

from pathlib import Path
import argparse
from datetime import datetime, timezone

from biomaster.knowledge import (
    DEFAULT_DB_PATH,
    connect,
    ensure_schema,
    json_dumps,
    json_loads,
    row_to_dict,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


DEFAULT_ROUTES = [
    {
        "route_id": "bioinformatics_rnaseq_de",
        "domain": "bioinformatics",
        "discipline": "rnaseq",
        "pipeline": "differential_expression",
        "title": "RNA-seq differential expression analysis",
        "description": "Plan and execute RNA-seq differential expression from count matrix or FASTQ inputs.",
        "preview_steps": [
            "Validate count matrix and sample metadata",
            "Run DESeq2 or equivalent differential expression",
            "Generate DEG table and QC plots",
            "Verify count matrix and DEG outputs",
        ],
        "required_skill_ids": ["registry"],
        "optional_skill_ids": ["discipline-scrnaseq"],
        "demo_dataset": "examples/data/rnaseq_counts.csv",
        "trigger_keywords": "rna-seq,rnaseq,differential expression,DEG,DESeq2,count matrix",
    },
    {
        "route_id": "bioinformatics_fastq_qc",
        "domain": "bioinformatics",
        "discipline": "general",
        "pipeline": "fastq_qc",
        "title": "FASTQ quality control",
        "description": "Inspect FASTQ inputs and produce a lightweight QC summary report.",
        "preview_steps": [
            "Validate FASTQ format and read structure",
            "Summarize read length and quality metrics",
            "Write QC report artifacts",
            "Verify report completeness",
        ],
        "required_skill_ids": ["registry"],
        "optional_skill_ids": ["discipline-scrnaseq"],
        "demo_dataset": "examples/data/tiny_reads.fastq",
        "trigger_keywords": "fastq,qc,quality control,read quality",
    },
    {
        "route_id": "tumor_scrnaseq_heterogeneity",
        "domain": "tumor",
        "discipline": "scrnaseq",
        "pipeline": "tumor_heterogeneity",
        "title": "Tumor heterogeneity and state trajectory analysis",
        "description": "Plan scRNA-seq tumor heterogeneity, malignant cell identification, trajectory, and co-expression module analysis.",
        "preview_steps": [
            "Data loading and QC",
            "Doublet removal and batch correction",
            "Cell subtype annotation",
            "inferCNVpy malignant cell identification",
            "Palantir state trajectory analysis",
            "cNMF co-expression module analysis",
            "Report generation",
        ],
        "required_skill_ids": [
            "registry",
            "domain-guide-tumor",
            "discipline-scrnaseq",
            "biomaster",
            "pipeline-scrnaseq-tumor",
            "plan-scrnaseq-tumor-heterogeneity",
        ],
        "optional_skill_ids": [
            "report-tumor-scrnaseq",
            "exec-scanpy",
            "exec-infercnvpy",
            "exec-palantir",
            "exec-cnmf",
            "verify-scrna-qc",
            "verify-infercnv",
            "verify-trajectory",
            "verify-cnmf",
            "env-python-scrnaseq",
            "debug-conda",
            "debug-tool-not-found",
            "debug-missing-files",
        ],
        "demo_dataset": "maynard2020_3k",
        "trigger_keywords": "tumor,heterogeneity,trajectory,infercnv,palantir,cnmf,scRNA-seq,single-cell",
    },
]


def upsert_route(connection, route: dict[str, object]) -> None:
    connection.execute(
        """
        INSERT INTO pipeline_routes (
          route_id, domain, discipline, pipeline, title, description,
          preview_steps, required_skill_ids, optional_skill_ids,
          demo_dataset, trigger_keywords, enabled, updated_at
        ) VALUES (
          :route_id, :domain, :discipline, :pipeline, :title, :description,
          :preview_steps, :required_skill_ids, :optional_skill_ids,
          :demo_dataset, :trigger_keywords, 1, :updated_at
        )
        ON CONFLICT(route_id) DO UPDATE SET
          domain = excluded.domain,
          discipline = excluded.discipline,
          pipeline = excluded.pipeline,
          title = excluded.title,
          description = excluded.description,
          preview_steps = excluded.preview_steps,
          required_skill_ids = excluded.required_skill_ids,
          optional_skill_ids = excluded.optional_skill_ids,
          demo_dataset = excluded.demo_dataset,
          trigger_keywords = excluded.trigger_keywords,
          enabled = excluded.enabled,
          updated_at = excluded.updated_at
        """,
        {
            **route,
            "preview_steps": json_dumps(route["preview_steps"]),
            "required_skill_ids": json_dumps(route["required_skill_ids"]),
            "optional_skill_ids": json_dumps(route["optional_skill_ids"]),
            "updated_at": utc_now(),
        },
    )


def seed_routes(db_path: Path = DEFAULT_DB_PATH) -> int:
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        for route in DEFAULT_ROUTES:
            upsert_route(connection, route)
        connection.commit()
        return connection.execute("SELECT COUNT(*) FROM pipeline_routes WHERE enabled = 1").fetchone()[0]
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed default pipeline routes into SQLite.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    count = seed_routes(args.db)
    print(f"Seeded {count} enabled pipeline routes into {args.db}")


if __name__ == "__main__":
    main()
