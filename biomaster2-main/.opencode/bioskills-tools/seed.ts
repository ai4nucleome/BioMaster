#!/usr/bin/env bun
/**
 * Seed the BioSkills management library from awesome-bio-agent-skills.
 *
 * - Imports skills whose CSV category == "single-cell".
 * - Normalises each into <repo>/.opencode/bioskills/<name>/ with:
 *     SKILL.md  (frontmatter: dual-layer tags + metadata)
 *     macro.md  (macro layer: overview/description, for the plan agent)
 *     micro.md  (micro layer: commands, params, thresholds, for execute/debug)
 * - Two bioclaw single-cell skills get hand-curated dual-layer tags.
 *
 * Usage:
 *   bun run .opencode/bioskills-tools/seed.ts [path-to-awesome-bio-agent-skills]
 */
import fs from "node:fs"
import path from "node:path"

const DEFAULT_AWESOME = "/home/yucheng/projectRaid/Biomaster_opencode/awesome-bio-agent-skills"
const AWESOME = path.resolve(process.argv[2] ?? DEFAULT_AWESOME)
const OUT = path.resolve(import.meta.dir, "..", "bioskills")
const CSV = path.join(AWESOME, "bioskill_index_v3.csv")

// --- keyword dictionaries for automatic dual-layer tagging -----------------

const MACRO_THEMES: Array<[string, RegExp]> = [
  ["single-cell", /single[-\s]?cell|scrna|scatac|sc-?seq/i],
  ["scrna-seq", /scrna|single[-\s]?cell rna/i],
  ["scatac", /scatac|atac/i],
  ["spatial", /spatial/i],
  ["quality-control", /quality control|\bqc\b|filtering|doublet/i],
  ["preprocessing", /preprocess|normali[sz]|hvg|scaling/i],
  ["clustering", /cluster|leiden|louvain|community/i],
  ["dimensionality-reduction", /umap|t-?sne|\bpca\b|embedding|dimensionality/i],
  ["annotation", /annotat|cell type|celltype|label transfer|marker/i],
  ["integration", /integrat|batch correct|harmony|bbknn|scanorama/i],
  ["trajectory", /trajector|pseudotime|lineage|velocity/i],
  ["differential-expression", /differential expression|\bde\b|deg|marker gene/i],
  ["cell-communication", /communication|ligand|receptor|cellchat|liana|interaction/i],
  ["deconvolution", /deconvolut/i],
  ["multiome", /multiome|multi-?omic|multimodal/i],
]

const METHODS: string[] = [
  "scanpy",
  "seurat",
  "anndata",
  "muon",
  "squidpy",
  "leiden",
  "louvain",
  "celltypist",
  "singler",
  "harmony",
  "bbknn",
  "scanorama",
  "scvi",
  "scvi-tools",
  "scanvi",
  "umap",
  "tsne",
  "pca",
  "scrublet",
  "scdblfinder",
  "doubletfinder",
  "cellchat",
  "liana",
  "monocle",
  "palantir",
  "scvelo",
  "velocyto",
  "sctransform",
  "mnn",
  "popv",
  "arboreto",
  "scenic",
  "cellrank",
]

const PARAMS: string[] = [
  "resolution",
  "n_neighbors",
  "n_pcs",
  "n_top_genes",
  "min_genes",
  "max_genes",
  "min_cells",
  "pct_counts_mt",
  "target_sum",
  "conf_score",
  "majority_voting",
]

// hand-curated overrides for the two bioclaw single-cell samples
const OVERRIDES: Record<string, { macroTags: string[]; microTags: string[] }> = {
  "bioclaw-scrna-preprocessing-clustering": {
    macroTags: [
      "single-cell",
      "scrna-seq",
      "preprocessing",
      "quality-control",
      "clustering",
      "dimensionality-reduction",
      "workflow",
    ],
    microTags: [
      "scanpy",
      "anndata",
      "leiden",
      "umap",
      "pca",
      "highly_variable_genes",
      "normalize_total",
      "n_neighbors",
      "n_pcs",
      "n_top_genes",
      "min_genes",
      "max_genes",
      "pct_counts_mt",
      "resolution",
    ],
  },
  "bioclaw-cell-annotation": {
    macroTags: ["single-cell", "scrna-seq", "annotation", "cell-type", "marker", "reference-transfer"],
    microTags: [
      "scanpy",
      "celltypist",
      "majority_voting",
      "conf_score",
      "marker-genes",
      "dotplot",
      "umap",
    ],
  },
}

// --- CSV parsing (RFC-4180 aware; descriptions contain commas) --------------

function parseCsv(text: string): Record<string, string>[] {
  const rows: string[][] = []
  let field = ""
  let record: string[] = []
  let inQuotes = false
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]
    if (inQuotes) {
      if (ch === '"') {
        if (text[i + 1] === '"') {
          field += '"'
          i++
        } else {
          inQuotes = false
        }
      } else {
        field += ch
      }
    } else if (ch === '"') {
      inQuotes = true
    } else if (ch === ",") {
      record.push(field)
      field = ""
    } else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++
      if (field !== "" || record.length > 0) {
        record.push(field)
        rows.push(record)
        record = []
        field = ""
      }
    } else {
      field += ch
    }
  }
  if (field !== "" || record.length > 0) {
    record.push(field)
    rows.push(record)
  }
  const header = rows.shift()
  if (!header) return []
  return rows.map((r) => {
    const obj: Record<string, string> = {}
    header.forEach((h, idx) => (obj[h] = r[idx] ?? ""))
    return obj
  })
}

// --- frontmatter + file helpers --------------------------------------------

function readSafe(file: string): string {
  try {
    return fs.readFileSync(file, "utf-8")
  } catch {
    return ""
  }
}

function splitFrontmatter(md: string): { data: Record<string, string>; body: string } {
  const match = /^---\n([\s\S]*?)\n---\n?/.exec(md)
  const data: Record<string, string> = {}
  if (!match) return { data, body: md.trim() }
  for (const line of match[1].split("\n")) {
    const m = /^([A-Za-z0-9_]+):\s*(.*)$/.exec(line)
    if (m) data[m[1]] = m[2].replace(/^["']|["']$/g, "").trim()
  }
  return { data, body: md.slice(match[0].length).trim() }
}

function dedupe(values: string[]): string[] {
  return [...new Set(values.map((v) => v.trim()).filter(Boolean))]
}

function deriveMacroTags(name: string, description: string): string[] {
  const hay = `${name} ${description}`
  const tags = ["single-cell"]
  for (const [tag, re] of MACRO_THEMES) if (re.test(hay)) tags.push(tag)
  return dedupe(tags)
}

function deriveMicroTags(primaryTool: string, description: string, micro: string): string[] {
  const hay = `${primaryTool} ${description} ${micro}`.toLowerCase()
  const tags: string[] = []
  if (primaryTool) tags.push(primaryTool.toLowerCase())
  for (const method of METHODS) if (hay.includes(method)) tags.push(method)
  for (const param of PARAMS) if (hay.includes(param)) tags.push(param)
  return dedupe(tags)
}

function yamlList(values: string[]): string {
  if (values.length === 0) return " []"
  return "\n" + values.map((v) => `  - ${JSON.stringify(v)}`).join("\n")
}

function writeSkill(opts: {
  name: string
  description: string
  domain: string
  primaryTool: string
  methods: string[]
  macroTags: string[]
  microTags: string[]
  source: string
  macro: string
  micro: string
}): void {
  const base = path.join(OUT, opts.name)
  fs.mkdirSync(base, { recursive: true })
  const title = opts.name
    .split("-")
    .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
    .join(" ")
  const frontmatter = [
    "---",
    `name: ${opts.name}`,
    `description: ${JSON.stringify(opts.description)}`,
    `domain: ${JSON.stringify(opts.domain)}`,
    `primary_tool: ${JSON.stringify(opts.primaryTool)}`,
    `methods:${yamlList(opts.methods)}`,
    `macro_tags:${yamlList(opts.macroTags)}`,
    `micro_tags:${yamlList(opts.microTags)}`,
    `source: ${JSON.stringify(opts.source)}`,
    `status: active`,
    "---",
    "",
    `# ${title}`,
    "",
  ].join("\n")
  fs.writeFileSync(path.join(base, "SKILL.md"), frontmatter)
  fs.writeFileSync(path.join(base, "macro.md"), opts.macro.trimEnd() + "\n")
  fs.writeFileSync(path.join(base, "micro.md"), opts.micro.trimEnd() + "\n")
}

// --- main -------------------------------------------------------------------

function collectMicro(srcDir: string): string {
  const parts: string[] = []
  for (const file of ["commands_and_thresholds.md", "technical_reference.md"]) {
    const content = readSafe(path.join(srcDir, file))
    if (content.trim()) parts.push(content.trim())
  }
  const refDir = path.join(srcDir, "references")
  if (fs.existsSync(refDir) && fs.statSync(refDir).isDirectory()) {
    for (const f of fs.readdirSync(refDir).sort()) {
      if (!f.endsWith(".md")) continue
      const content = readSafe(path.join(refDir, f))
      if (content.trim()) parts.push(`## ${f}\n\n${content.trim()}`)
    }
  }
  return parts.join("\n\n---\n\n")
}

function main(): void {
  if (!fs.existsSync(CSV)) {
    console.error(`CSV index not found: ${CSV}`)
    process.exit(1)
  }
  const records = parseCsv(readSafe(CSV)).filter((r) => r.category === "single-cell")
  fs.mkdirSync(OUT, { recursive: true })

  let imported = 0
  let skipped = 0
  for (const rec of records) {
    const archive = rec.archive_path?.trim()
    if (!archive) {
      skipped++
      continue
    }
    const srcDir = path.join(AWESOME, "skills", archive)
    const skillMd = path.join(srcDir, "SKILL.md")
    if (!fs.existsSync(skillMd)) {
      skipped++
      continue
    }
    const { data, body } = splitFrontmatter(readSafe(skillMd))
    const name = archive.replace(/\//g, "-").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "")
    const description = data.description || rec.description || ""
    const primaryTool = data.primary_tool || ""
    const macro = body
    const micro = collectMicro(srcDir)

    const override = OVERRIDES[name]
    const macroTags = override ? override.macroTags : deriveMacroTags(name, description)
    const microTags = override ? override.microTags : deriveMicroTags(primaryTool, description, micro)
    const methods = dedupe(microTags.filter((t) => METHODS.includes(t)))

    writeSkill({
      name,
      description,
      domain: "single-cell",
      primaryTool,
      methods,
      macroTags,
      microTags,
      source: archive,
      macro,
      micro,
    })
    imported++
  }

  console.log(`Imported ${imported} single-cell skills into ${OUT} (skipped ${skipped}).`)
}

main()
