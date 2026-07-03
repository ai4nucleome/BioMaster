import { tool } from "@opencode-ai/plugin"
import fs from "node:fs"
import path from "node:path"

/**
 * BioSkills retrieval tool.
 *
 * Exposes the file-backed BioSkills library (`.opencode/bioskills/`) to biomaster
 * sub-agents with role-based layering:
 *   - plan   -> macro layer (description / overview)  -> for planning
 *   - execute/debug -> micro layer (commands, params, thresholds) -> for coding
 *   - check  -> usually none
 * The `biomaster-skiller` agent uses this tool to decide and fetch the right
 * layer for each sub-agent. Role -> layer defaults live in
 * `.opencode/bioskills-access.yaml`; an explicit `layer` arg overrides them.
 *
 * Self-contained: reads skill files directly (no HTTP dependency on the server).
 */

type Layer = "macro" | "micro" | "all" | "none"

type Step = { id: string; title: string; tags: string[]; enabled: boolean }

type Skill = {
  name: string
  description: string
  domain: string
  primaryTool: string
  macroTags: string[]
  microTags: string[]
  source: string
  enabled: boolean
  steps: Step[]
  macro: string
  micro: string
}

function bioskillsDir(directory: string): string {
  return path.join(directory, ".opencode", "bioskills")
}

function readFileSafe(file: string): string {
  try {
    return fs.readFileSync(file, "utf-8")
  } catch {
    return ""
  }
}

// Minimal frontmatter parser (scalars + inline/block string arrays).
function parseFrontmatter(md: string): Record<string, unknown> {
  const match = /^---\n([\s\S]*?)\n---/.exec(md)
  const data: Record<string, unknown> = {}
  if (!match) return data
  const lines = match[1].split("\n")
  let currentKey: string | null = null
  for (const line of lines) {
    const listItem = /^\s*-\s+(.*)$/.exec(line)
    if (listItem && currentKey) {
      const arr = (data[currentKey] as string[]) ?? []
      arr.push(listItem[1].replace(/^["']|["']$/g, "").trim())
      data[currentKey] = arr
      continue
    }
    const kv = /^([A-Za-z0-9_]+):\s*(.*)$/.exec(line)
    if (!kv) continue
    const key = kv[1]
    const raw = kv[2].trim()
    if (raw === "" ) {
      data[key] = []
      currentKey = key
    } else if (raw.startsWith("[") && raw.endsWith("]")) {
      data[key] = raw
        .slice(1, -1)
        .split(",")
        .map((v) => v.replace(/^["']|["']$/g, "").trim())
        .filter(Boolean)
      currentKey = null
    } else {
      data[key] = raw.replace(/^["']|["']$/g, "")
      currentKey = null
    }
  }
  return data
}

function toArray(value: unknown): string[] {
  if (Array.isArray(value)) return value.map((v) => String(v))
  if (typeof value === "string" && value) return value.split(",").map((v) => v.trim()).filter(Boolean)
  return []
}

function readSteps(base: string): Step[] {
  const file = path.join(base, "steps.json")
  if (!fs.existsSync(file)) return []
  try {
    const raw = JSON.parse(readFileSafe(file))
    if (!Array.isArray(raw)) return []
    return raw
      .map((s: any, i: number) => ({
        id: String(s?.id ?? `step-${i + 1}`),
        title: String(s?.title ?? s?.id ?? `Step ${i + 1}`),
        tags: toArray(s?.tags),
        enabled: s?.enabled === false ? false : true,
      }))
      .filter((s) => s.title)
  } catch {
    return []
  }
}

function readSkill(dir: string, name: string): Skill | null {
  const base = path.join(dir, name)
  const skillFile = path.join(base, "SKILL.md")
  if (!fs.existsSync(skillFile)) return null
  const data = parseFrontmatter(readFileSafe(skillFile))
  return {
    name: String(data.name ?? name),
    description: String(data.description ?? ""),
    domain: String(data.domain ?? ""),
    primaryTool: String(data.primary_tool ?? ""),
    macroTags: toArray(data.macro_tags),
    microTags: toArray(data.micro_tags),
    source: String(data.source ?? ""),
    enabled: data.enabled === false || String(data.enabled).toLowerCase() === "false" ? false : true,
    steps: readSteps(base),
    macro: readFileSafe(path.join(base, "macro.md")),
    micro: readFileSafe(path.join(base, "micro.md")),
  }
}

// Split markdown into sections by its top-level headings, aligned to steps by
// order. Used to drop muted-step content before handing skills to sub-agents.
function sectionsByHeading(md: string): { preamble: string; sections: { title: string; body: string }[] } {
  const lines = (md ?? "").split("\n")
  // Scan headings, ignoring lines inside fenced code blocks (```/~~~) so that
  // `# comment` lines inside code are not mistaken for section headings.
  const headings: { index: number; level: number; title: string }[] = []
  let inFence = false
  let fenceChar = ""
  for (let i = 0; i < lines.length; i++) {
    const fence = /^\s*(```+|~~~+)/.exec(lines[i])
    if (fence) {
      const ch = fence[1][0]
      if (!inFence) {
        inFence = true
        fenceChar = ch
      } else if (ch === fenceChar) {
        inFence = false
        fenceChar = ""
      }
      continue
    }
    if (inFence) continue
    const m = /^(#{1,6})\s+(.*\S)\s*$/.exec(lines[i])
    if (m) headings.push({ index: i, level: m[1].length, title: m[2].trim() })
  }
  if (headings.length === 0) return { preamble: md ?? "", sections: [] }
  const minLevel = Math.min(...headings.map((h) => h.level))
  const tops = headings.filter((h) => h.level === minLevel)
  const preamble = lines.slice(0, tops[0].index).join("\n").trim()
  const sections = tops.map((h, idx) => {
    const end = idx + 1 < tops.length ? tops[idx + 1].index : lines.length
    return { title: h.title, body: lines.slice(h.index, end).join("\n").trim() }
  })
  return { preamble, sections }
}

// Rebuild a layer's markdown keeping only the sections of enabled steps.
function filterByEnabledSteps(md: string, steps: Step[]): string {
  if (!steps.length) return md
  if (steps.every((s) => s.enabled !== false)) return md
  const { preamble, sections } = sectionsByHeading(md)
  if (sections.length === 0) return md
  const kept = sections.filter((_, i) => steps[i]?.enabled !== false)
  return [preamble, ...kept.map((s) => s.body)].filter(Boolean).join("\n\n")
}

function listSkills(dir: string): Skill[] {
  if (!fs.existsSync(dir)) return []
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory() && !e.name.startsWith("."))
    .map((e) => readSkill(dir, e.name))
    .filter((s): s is Skill => s !== null)
    // Muted (turned-off) skills are never exposed to sub-agents.
    .filter((s) => s.enabled !== false)
}

function isLayer(v: string): v is Layer {
  return v === "macro" || v === "micro" || v === "all" || v === "none"
}

// Resolve which skill layer a requesting agent should receive, returning both
// the layer and a human-readable note on HOW it resolved. Resolution order:
//   1. explicit `layer` override (skiller decision)
//   2. exact role in bioskills-access.yaml
//   3. alias -> canonical role (renamed / merged agents)
//   4. default layer (safe fallback for any unregistered/new agent)
// This keeps the agent<->skill wiring in one config file so the BioMaster agent
// graph can be refactored (merge/add/rename agents) without touching this tool.
function resolveLayer(directory: string, agent?: string, explicit?: string): { layer: Layer; via: string } {
  if (explicit && isLayer(explicit)) return { layer: explicit, via: "explicit layer override" }

  const yamlText = readFileSafe(path.join(directory, ".opencode", "bioskills-access.yaml"))
  let defaultLayer: Layer = "macro"
  const roles: Record<string, Layer> = {}
  const aliases: Record<string, string> = {}
  const lines = yamlText.split("\n")
  let section: "default" | "roles" | "aliases" | null = null
  let currentRole: string | null = null
  for (const raw of lines) {
    if (/^\s*#/.test(raw)) continue
    const line = raw.replace(/\s+#.*$/, "").replace(/\s+$/, "") // drop inline comments/trailing ws
    if (/^default:/.test(line)) {
      section = "default"
      currentRole = null
      continue
    }
    if (/^roles:/.test(line)) {
      section = "roles"
      currentRole = null
      continue
    }
    const aliasHeader = /^aliases:\s*(\{\s*\})?\s*$/.exec(line)
    if (aliasHeader) {
      section = "aliases"
      currentRole = null
      continue
    }
    if (section === "default") {
      const defLayer = /^\s+layer:\s*(\w+)/.exec(line)
      if (defLayer && isLayer(defLayer[1])) defaultLayer = defLayer[1]
    } else if (section === "roles") {
      const role = /^\s{2}([A-Za-z0-9_-]+):\s*$/.exec(line)
      if (role) {
        currentRole = role[1]
        continue
      }
      const rl = /^\s{4}layer:\s*(\w+)/.exec(line)
      if (rl && currentRole && isLayer(rl[1])) roles[currentRole] = rl[1]
    } else if (section === "aliases") {
      const a = /^\s{2}([A-Za-z0-9_-]+):\s*([A-Za-z0-9_-]+)\s*$/.exec(line)
      if (a) aliases[a[1]] = a[2]
    }
  }

  if (agent && roles[agent]) return { layer: roles[agent], via: `role '${agent}'` }
  if (agent && aliases[agent] && roles[aliases[agent]]) {
    return { layer: roles[aliases[agent]], via: `alias '${agent}' -> role '${aliases[agent]}'` }
  }
  return { layer: defaultLayer, via: agent ? `default (unregistered agent '${agent}')` : "default" }
}

function enabledSteps(skill: Skill): Step[] {
  return skill.steps.filter((s) => s.enabled !== false)
}

function matches(skill: Skill, q: string): boolean {
  if (!q) return true
  const stepTerms = enabledSteps(skill).flatMap((s) => [s.title, ...s.tags])
  const hay = [
    skill.name,
    skill.description,
    skill.domain,
    skill.primaryTool,
    ...skill.macroTags,
    ...skill.microTags,
    ...stepTerms,
  ]
    .join(" ")
    .toLowerCase()
  return q
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .every((term) => hay.includes(term))
}

function truncate(text: string, max = 1600): string {
  const t = text.trim()
  return t.length > max ? t.slice(0, max) + "\n... [truncated]" : t
}

function narrowToStep(skill: Skill, stepQuery: string): Skill {
  const q = stepQuery.trim().toLowerCase()
  const match = skill.steps.find(
    (s) => s.id.toLowerCase() === q || s.title.toLowerCase() === q || s.title.toLowerCase().includes(q),
  )
  if (!match || match.enabled === false) return { ...skill, steps: [], macro: "", micro: "" }
  const pick = (md: string) => {
    const { sections } = sectionsByHeading(md)
    const idx = skill.steps.indexOf(match)
    return sections[idx]?.body ?? ""
  }
  return { ...skill, steps: [match], macro: pick(skill.macro), micro: pick(skill.micro) }
}

function render(skill: Skill, layer: Layer): string {
  const active = enabledSteps(skill)
  const lines = [`## ${skill.name}`, skill.description, ""]
  if (active.length) {
    lines.push(
      `**steps:** ${active.map((s) => (s.tags.length ? `${s.title} [${s.tags.join(", ")}]` : s.title)).join(" | ")}`,
      "",
    )
  }
  if (layer === "macro" || layer === "all") {
    lines.push(`**macro_tags:** ${skill.macroTags.join(", ") || "-"}`)
    lines.push("", "### macro (description layer)", truncate(filterByEnabledSteps(skill.macro, skill.steps)), "")
  }
  if (layer === "micro" || layer === "all") {
    lines.push(`**primary_tool:** ${skill.primaryTool || "-"}`)
    lines.push(`**micro_tags:** ${skill.microTags.join(", ") || "-"}`)
    lines.push("", "### micro (execution layer)", truncate(filterByEnabledSteps(skill.micro, skill.steps)), "")
  }
  return lines.join("\n")
}

export default tool({
  description:
    "Retrieve bioinformatics skills from the file-backed BioSkills library with role-based layering. " +
    "Pass `agent` (e.g. biomaster-plan, biomaster-execute, biomaster-debug, biomaster-check) to get the layer that role " +
    "should see (plan->macro/overview, execute&debug->micro/commands+params, check->none), or set `layer` explicitly " +
    "(macro|micro|all|none). Use `q` to keyword-filter (e.g. 'single-cell clustering'), `name` for one skill, `step` to " +
    "narrow to a single workflow step, `limit` to cap results. Muted skills and muted steps are never returned.",
  args: {
    agent: tool.schema
      .string()
      .optional()
      .describe("Requesting sub-agent role; maps to a skill layer via .opencode/bioskills-access.yaml"),
    layer: tool.schema
      .enum(["macro", "micro", "all", "none"])
      .optional()
      .describe("Explicit layer override (macro=overview for plan, micro=commands/params for execute/debug)"),
    q: tool.schema
      .string()
      .optional()
      .describe("Keyword filter over name/description/tags/step-tags, e.g. 'single-cell clustering'"),
    name: tool.schema.string().optional().describe("Fetch a single skill by its exact name"),
    step: tool.schema
      .string()
      .optional()
      .describe("With `name`, narrow to one workflow step by its id/title (e.g. 'clustering') for fine-grained allocation"),
    limit: tool.schema.number().optional().describe("Max number of skills to return (default 8)"),
  },
  async execute(args, context) {
    const directory = context.directory
    const dir = bioskillsDir(directory)
    const { layer, via } = resolveLayer(directory, args.agent, args.layer)

    if (layer === "none") {
      return {
        title: "bioskills: no layer",
        output: `Role '${args.agent ?? "unknown"}' is configured to receive no skills (layer=none; via ${via}).`,
        metadata: { layer, via, agent: args.agent, count: 0 },
      }
    }

    let skills = listSkills(dir)
    if (args.name) {
      skills = skills.filter((s) => s.name === args.name)
      if (args.step) skills = skills.map((s) => narrowToStep(s, args.step!))
    } else {
      if (args.q) skills = skills.filter((s) => matches(s, args.q!))
      skills = skills.slice(0, args.limit ?? 8)
    }

    if (skills.length === 0) {
      return {
        title: "bioskills: no match",
        output: `No skills found${args.q ? ` for query '${args.q}'` : ""} in ${dir}.`,
        metadata: { layer, via, agent: args.agent, count: 0 },
      }
    }

    const header = `Returning ${skills.length} skill(s) at layer='${layer}'${args.agent ? ` for agent='${args.agent}'` : ""} (via ${via}).`
    const body = skills.map((s) => render(s, layer)).join("\n---\n\n")
    return {
      title: `bioskills: ${skills.length} @ ${layer}`,
      output: `${header}\n\n${body}`,
      metadata: { layer, via, agent: args.agent, count: skills.length, names: skills.map((s) => s.name) },
    }
  },
})
