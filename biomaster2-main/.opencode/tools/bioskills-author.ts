import { tool } from "@opencode-ai/plugin"
import fs from "node:fs"
import path from "node:path"

/**
 * BioSkills author tool.
 *
 * Used by the `biomaster-skill-author` agent to (re)write a workflow skill into
 * the curated two-layer + structured-steps format:
 *   - macro.md : workflow overview + per-step DESCRIPTIONS (no code)
 *   - micro.md : per-step EXECUTION instructions / code
 *   - steps.json : structured, individually toggleable/allocatable steps
 *                  ([{ id, title, tags, enabled }]) that the skiller reads
 *   - SKILL.md : frontmatter metadata
 *
 * Steps in macro.md and micro.md are emitted as `## <Title>` sections in the
 * same order as steps.json so the store / skiller / frontend can align them.
 *
 * Writes files directly under `.opencode/bioskills/<slug>/`. The opencode
 * server's BioSkills index self-heals (re-reads) on the next read because the
 * file signature changes, so no HTTP call is required.
 */

function bioskillsDir(directory: string): string {
  return path.join(directory, ".opencode", "bioskills")
}

function slugify(name: string, fallback = "skill"): string {
  const slug = name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
  return slug || fallback
}

// Emit frontmatter using JSON-encoded scalars/arrays, which are valid YAML flow
// values and round-trip cleanly through the server's gray-matter parser.
function frontmatter(fields: Record<string, unknown>): string {
  const lines = ["---"]
  for (const [key, value] of Object.entries(fields)) {
    if (value === undefined || value === null) continue
    if (Array.isArray(value)) {
      lines.push(`${key}: ${JSON.stringify(value)}`)
    } else if (typeof value === "boolean") {
      lines.push(`${key}: ${value}`)
    } else {
      lines.push(`${key}: ${JSON.stringify(String(value))}`)
    }
  }
  lines.push("---")
  return lines.join("\n")
}

function titleCase(slug: string): string {
  return slug
    .split("-")
    .filter(Boolean)
    .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
    .join(" ")
}

function dedupe(values: string[]): string[] {
  return Array.from(new Set(values.map((v) => v.trim()).filter(Boolean)))
}

type StepInput = {
  title: string
  description: string
  code?: string
  tags?: string[]
}

export default tool({
  description:
    "Write (or re-divide) a curated bioinformatics workflow skill into the two-layer + structured-steps format used by the " +
    "BioSkills library. Provide a workflow-level `overview` (macro, NO code) and an ordered list of `steps`, each with a " +
    "`description` (macro, prose only), optional `code` (micro, execution/commands), and `tags` (small functional modules for " +
    "skiller allocation, e.g. ['qc','normalization']). The tool builds macro.md (overview + per-step descriptions), micro.md " +
    "(per-step code) and steps.json, then writes them under .opencode/bioskills/<name>. Use exact `name` of an existing skill to " +
    "re-divide it in place.",
  args: {
    name: tool.schema.string().describe("Skill name / slug (kebab-case). Existing name = re-divide in place."),
    description: tool.schema.string().describe("One-line summary of what the whole workflow does and when to use it."),
    domain: tool.schema.string().optional().describe("Domain, e.g. 'single-cell', 'atac', 'spatial'."),
    primary_tool: tool.schema.string().optional().describe("Primary tool/library, e.g. 'scanpy'."),
    methods: tool.schema.array(tool.schema.string()).optional().describe("Methods/libraries used, e.g. ['scanpy','leiden']."),
    macro_tags: tool.schema
      .array(tool.schema.string())
      .optional()
      .describe("Workflow-level concept tags for the description layer, e.g. ['workflow','clustering']."),
    micro_tags: tool.schema
      .array(tool.schema.string())
      .optional()
      .describe("Execution-level tags (methods/params). Defaults to the union of step tags + methods if omitted."),
    source: tool.schema.string().optional().describe("Provenance, e.g. original skill path or URL."),
    custom: tool.schema
      .boolean()
      .optional()
      .describe("Set true for user-authored skills (created from the UI). Surfaces under the 'customized' filter."),
    overview: tool.schema
      .string()
      .describe("Workflow-level macro description (prose, NO code): what the pipeline does, inputs/outputs, when to use."),
    steps: tool.schema
      .array(
        tool.schema.object({
          title: tool.schema.string().describe("Step title, e.g. 'Preprocessing', 'Clustering', 'Annotation'."),
          description: tool.schema.string().describe("Macro-level description of this step (prose only, NO code)."),
          code: tool.schema
            .string()
            .optional()
            .describe("Micro-level execution for this step: commands/code (fenced ```python blocks) and parameters."),
          tags: tool.schema
            .array(tool.schema.string())
            .optional()
            .describe("Functional-module tags for this step (for skiller allocation), e.g. ['qc','doublet-detection']."),
        }),
      )
      .describe("Ordered workflow steps. Each becomes an aligned `## Title` section in macro.md and micro.md + a steps.json entry."),
  },
  async execute(args, context) {
    const slug = slugify(args.name)
    const dir = bioskillsDir(context.directory)
    const base = path.join(dir, slug)
    fs.mkdirSync(base, { recursive: true })

    const steps = (args.steps ?? []).map((s: StepInput, i: number) => ({
      id: slugify(s.title, `step-${i + 1}`),
      title: s.title.trim() || `Step ${i + 1}`,
      description: (s.description ?? "").trim(),
      code: (s.code ?? "").trim(),
      tags: dedupe(s.tags ?? []),
    }))

    if (steps.length === 0) {
      return {
        title: "bioskills-author: rejected",
        output:
          "No steps provided. A high-quality skill must be broken into at least one workflow step. " +
          "If the source material is too thin to yield distinct steps with descriptions (and ideally code), reject it instead of writing.",
        metadata: { written: false, name: slug },
      }
    }

    // macro.md: overview + per-step descriptions (no code).
    const macro = [
      `# ${titleCase(slug)}`,
      "",
      "## Overview",
      "",
      args.overview.trim(),
      "",
      ...steps.flatMap((s) => [`## ${s.title}`, "", s.description || "_No description provided._", ""]),
    ]
      .join("\n")
      .trimEnd()

    // micro.md: per-step execution / code.
    const micro = steps
      .flatMap((s) => {
        const body = s.code || "_No execution detail provided for this step._"
        const tagLine = s.tags.length ? [`_modules: ${s.tags.join(", ")}_`, ""] : []
        return [`## ${s.title}`, "", ...tagLine, body, ""]
      })
      .join("\n")
      .trimEnd()

    const stepsJson = steps.map((s) => ({ id: s.id, title: s.title, tags: s.tags, enabled: true }))

    const microTags =
      args.micro_tags && args.micro_tags.length
        ? dedupe(args.micro_tags)
        : dedupe([...(args.methods ?? []), ...steps.flatMap((s) => s.tags)])

    const fm = frontmatter({
      name: slug,
      description: args.description,
      domain: args.domain ?? "",
      primary_tool: args.primary_tool ?? "",
      methods: args.methods ?? [],
      macro_tags: dedupe(args.macro_tags ?? []),
      micro_tags: microTags,
      source: args.source ?? "",
      status: "active",
      enabled: true,
      custom: args.custom === true,
    })

    fs.writeFileSync(path.join(base, "SKILL.md"), `${fm}\n\n# ${titleCase(slug)}\n`)
    fs.writeFileSync(path.join(base, "macro.md"), macro + "\n")
    fs.writeFileSync(path.join(base, "micro.md"), micro + "\n")
    fs.writeFileSync(path.join(base, "steps.json"), JSON.stringify(stepsJson, null, 2) + "\n")

    return {
      title: `bioskills-author: wrote ${slug} (${steps.length} steps)`,
      output:
        `Wrote skill '${slug}' with ${steps.length} step(s): ${steps.map((s) => s.title).join(", ")}.\n` +
        `Files: SKILL.md, macro.md (overview + per-step descriptions), micro.md (per-step execution), steps.json.\n` +
        `Location: ${base}`,
      metadata: { written: true, name: slug, steps: stepsJson.map((s) => s.id) },
    }
  },
})
