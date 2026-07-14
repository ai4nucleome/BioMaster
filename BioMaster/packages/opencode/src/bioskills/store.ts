import { Database } from "bun:sqlite"
import matter from "gray-matter"
import crypto from "node:crypto"
import fs from "node:fs"
import path from "node:path"

export type SkillLayer = "macro" | "micro" | "all"

// A structured step of a workflow skill. Steps are first-class units: each one
// carries functional-module tags and is allocatable by the skiller agent.
// Muting is supported only at whole-skill level. The step's prose lives as a `##`
// section (matched by order/title) inside macro.md (description) and micro.md
// (execution/code).
export interface SkillStep {
  id: string
  title: string
  tags: string[]
}

export interface BioSkill {
  name: string
  description: string
  domain: string
  primaryTool: string
  methods: string[]
  macroTags: string[]
  microTags: string[]
  source: string
  status: string
  // When false the skill is "muted": it stays on disk but is hidden from the
  // biomaster sub-agents (skiller / plan / execute / debug). Defaults to true.
  enabled: boolean
  // True for skills the user added themselves via the UI (as opposed to the
  // curated library). Surfaced as a "customized" filter in the frontend.
  custom: boolean
  steps: SkillStep[]
  macro: string
  micro: string
}

export interface BioSkillInput {
  name: string
  description?: string
  domain?: string
  primaryTool?: string
  methods?: string[]
  macroTags?: string[]
  microTags?: string[]
  source?: string
  status?: string
  enabled?: boolean
  custom?: boolean
  steps?: SkillStep[]
  macro?: string
  micro?: string
}

export class BioSkillError extends Error {
  constructor(
    message: string,
    readonly status: number = 400,
  ) {
    super(message)
    this.name = "BioSkillError"
  }
}

const INDEX_FILE = ".index.db"
const KNOWLEDGE_DB = path.join(".opencode", "knowledge", "biomaster_skills.db")

export function bioskillsDir(directory: string): string {
  return path.join(directory, ".opencode", "bioskills")
}

function indexPath(dir: string): string {
  return path.join(dir, INDEX_FILE)
}

export function slugify(name: string): string {
  const slug = name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
  if (!slug) throw new BioSkillError(`Invalid skill name: ${JSON.stringify(name)}`)
  return slug
}

function toArray(value: unknown): string[] {
  if (Array.isArray(value)) return value.map((v) => String(v).trim()).filter(Boolean)
  if (typeof value === "string")
    return value
      .split(",")
      .map((v) => v.trim())
      .filter(Boolean)
  return []
}

function parseSteps(value: unknown): SkillStep[] {
  if (!Array.isArray(value)) return []
  return value
    .map((raw, index): SkillStep | null => {
      if (typeof raw === "string") {
        const title = raw.trim()
        if (!title) return null
        return { id: slugifySafe(title, `step-${index + 1}`), title, tags: [] }
      }
      if (raw && typeof raw === "object") {
        const obj = raw as Record<string, unknown>
        const title = String(obj.title ?? obj.name ?? "").trim()
        const id = String(obj.id ?? "").trim() || slugifySafe(title, `step-${index + 1}`)
        if (!title && !id) return null
        return {
          id,
          title: title || id,
          tags: toArray(obj.tags),
        }
      }
      return null
    })
    .filter((s): s is SkillStep => s !== null)
}

function slugifySafe(name: string, fallback: string): string {
  const slug = name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
  return slug || fallback
}

function skillDir(dir: string, name: string): string {
  return path.join(dir, name)
}

function readFileSafe(file: string): string {
  try {
    return fs.readFileSync(file, "utf-8")
  } catch {
    return ""
  }
}

const STEPS_FILE = "steps.json"

function readSteps(base: string): SkillStep[] {
  const file = path.join(base, STEPS_FILE)
  if (!fs.existsSync(file)) return []
  try {
    return parseSteps(JSON.parse(readFileSafe(file)))
  } catch {
    return []
  }
}

export function readSkill(dir: string, name: string): BioSkill | null {
  const base = skillDir(dir, name)
  const skillFile = path.join(base, "SKILL.md")
  if (!fs.existsSync(skillFile)) return null
  const parsed = matter(readFileSafe(skillFile))
  const data = parsed.data as Record<string, unknown>
  const macroFile = path.join(base, "macro.md")
  const microFile = path.join(base, "micro.md")
  const macro = fs.existsSync(macroFile) ? readFileSafe(macroFile) : parsed.content.trim()
  const micro = fs.existsSync(microFile) ? readFileSafe(microFile) : ""
  return {
    name: String(data.name ?? name),
    description: String(data.description ?? ""),
    domain: String(data.domain ?? ""),
    primaryTool: String(data.primary_tool ?? data.primaryTool ?? ""),
    methods: toArray(data.methods),
    macroTags: toArray(data.macro_tags ?? data.macroTags),
    microTags: toArray(data.micro_tags ?? data.microTags),
    source: String(data.source ?? ""),
    status: String(data.status ?? "active"),
    enabled: data.enabled === false ? false : true,
    custom: data.custom === true || String(data.custom).toLowerCase() === "true",
    steps: readSteps(base),
    macro,
    micro,
  }
}

export function writeSkill(dir: string, skill: BioSkill): void {
  const name = slugify(skill.name)
  const base = skillDir(dir, name)
  fs.mkdirSync(base, { recursive: true })
  const frontmatter = {
    name,
    description: skill.description ?? "",
    domain: skill.domain ?? "",
    primary_tool: skill.primaryTool ?? "",
    methods: skill.methods ?? [],
    macro_tags: skill.macroTags ?? [],
    micro_tags: skill.microTags ?? [],
    source: skill.source ?? "",
    status: skill.status ?? "active",
    enabled: skill.enabled === false ? false : true,
    custom: skill.custom === true,
  }
  const title = name
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ")
  fs.writeFileSync(path.join(base, "SKILL.md"), matter.stringify(`# ${title}\n`, frontmatter))
  fs.writeFileSync(path.join(base, "macro.md"), (skill.macro ?? "").trimEnd() + "\n")
  fs.writeFileSync(path.join(base, "micro.md"), (skill.micro ?? "").trimEnd() + "\n")
  // Structured steps live in a JSON sidecar (robust for the file-reading skiller
  // tool to parse without a YAML dependency).
  const stepsFile = path.join(base, STEPS_FILE)
  const steps = (skill.steps ?? []).map((s) => ({
    id: s.id,
    title: s.title,
    tags: s.tags ?? [],
  }))
  if (steps.length) fs.writeFileSync(stepsFile, JSON.stringify(steps, null, 2) + "\n")
  else if (fs.existsSync(stepsFile)) fs.rmSync(stepsFile)
}

export function listNames(dir: string): string[] {
  if (!fs.existsSync(dir)) return []
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."))
    .filter((entry) => fs.existsSync(path.join(dir, entry.name, "SKILL.md")))
    .map((entry) => entry.name)
    .sort()
}

function readAllSkills(dir: string): BioSkill[] {
  return listNames(dir)
    .map((name) => readSkill(dir, name))
    .filter((skill): skill is BioSkill => skill !== null)
}

function signature(dir: string): string {
  const parts: string[] = []
  for (const name of listNames(dir)) {
    const base = skillDir(dir, name)
    for (const file of ["SKILL.md", "macro.md", "micro.md", STEPS_FILE]) {
      const full = path.join(base, file)
      try {
        parts.push(`${name}/${file}:${fs.statSync(full).mtimeMs}`)
      } catch {
        // missing file, skip
      }
    }
  }
  return crypto.createHash("sha1").update(parts.join("|")).digest("hex")
}

function openIndex(dir: string): Database {
  fs.mkdirSync(dir, { recursive: true })
  const db = new Database(indexPath(dir))
  db.run("PRAGMA journal_mode = WAL")
  db.run(`CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)`)
  db.run(`CREATE TABLE IF NOT EXISTS skills (
    name TEXT PRIMARY KEY,
    description TEXT,
    domain TEXT,
    primary_tool TEXT,
    methods TEXT,
    macro_tags TEXT,
    micro_tags TEXT,
    source TEXT,
    status TEXT,
    enabled INTEGER DEFAULT 1,
    custom INTEGER DEFAULT 0,
    steps TEXT DEFAULT '[]',
    macro TEXT,
    micro TEXT
  )`)
  // Migrate pre-existing caches that predate newer columns.
  try {
    db.run("ALTER TABLE skills ADD COLUMN enabled INTEGER DEFAULT 1")
  } catch {
    // column already exists
  }
  try {
    db.run("ALTER TABLE skills ADD COLUMN steps TEXT DEFAULT '[]'")
  } catch {
    // column already exists
  }
  try {
    db.run("ALTER TABLE skills ADD COLUMN custom INTEGER DEFAULT 0")
  } catch {
    // column already exists
  }
  db.run(`CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
    name, description, tags, macro, micro
  )`)
  return db
}

function upsertRow(db: Database, skill: BioSkill): void {
  const stepTags = skill.steps.flatMap((s) => [s.title, ...s.tags])
  const tags = [...skill.macroTags, ...skill.microTags, ...stepTags, skill.domain, skill.primaryTool]
    .filter(Boolean)
    .join(" ")
  db.run("DELETE FROM skills WHERE name = ?", [skill.name])
  db.run("DELETE FROM skills_fts WHERE name = ?", [skill.name])
  db.run(
    `INSERT INTO skills (name, description, domain, primary_tool, methods, macro_tags, micro_tags, source, status, enabled, custom, steps, macro, micro)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      skill.name,
      skill.description,
      skill.domain,
      skill.primaryTool,
      JSON.stringify(skill.methods),
      JSON.stringify(skill.macroTags),
      JSON.stringify(skill.microTags),
      skill.source,
      skill.status,
      skill.enabled === false ? 0 : 1,
      skill.custom === true ? 1 : 0,
      JSON.stringify(skill.steps ?? []),
      skill.macro,
      skill.micro,
    ],
  )
  db.run("INSERT INTO skills_fts (name, description, tags, macro, micro) VALUES (?, ?, ?, ?, ?)", [
    skill.name,
    skill.description,
    tags,
    skill.macro,
    skill.micro,
  ])
}

function rebuild(db: Database, dir: string): number {
  const skills = readAllSkills(dir)
  db.run("DELETE FROM skills")
  db.run("DELETE FROM skills_fts")
  const insert = db.transaction((rows: BioSkill[]) => {
    for (const skill of rows) upsertRow(db, skill)
  })
  insert(skills)
  db.run("INSERT OR REPLACE INTO meta (key, value) VALUES ('signature', ?)", [signature(dir)])
  return skills.length
}

function ensureFresh(db: Database, dir: string): void {
  const current = signature(dir)
  const row = db.query("SELECT value FROM meta WHERE key = 'signature'").get() as { value?: string } | null
  if (!row || row.value !== current) rebuild(db, dir)
}

export function reindex(directory: string): number {
  const dir = bioskillsDir(directory)
  const db = openIndex(dir)
  try {
    return rebuild(db, dir)
  } finally {
    db.close()
  }
}

function ftsMatch(q: string, layer: SkillLayer): string | null {
  const terms = q.toLowerCase().match(/[a-z0-9_]+/g)
  if (!terms || terms.length === 0) return null
  const cols =
    layer === "macro"
      ? "{name description tags macro}"
      : layer === "micro"
        ? "{name description tags micro}"
        : "{name description tags macro micro}"
  const expr = terms.map((t) => `${t}*`).join(" ")
  return `${cols} : (${expr})`
}

function rowToSkill(row: Record<string, unknown>): BioSkill {
  return {
    name: String(row.name),
    description: String(row.description ?? ""),
    domain: String(row.domain ?? ""),
    primaryTool: String(row.primary_tool ?? ""),
    methods: JSON.parse(String(row.methods || "[]")),
    macroTags: JSON.parse(String(row.macro_tags || "[]")),
    microTags: JSON.parse(String(row.micro_tags || "[]")),
    source: String(row.source ?? ""),
    status: String(row.status ?? "active"),
    enabled: row.enabled === 0 || row.enabled === "0" ? false : true,
    custom: row.custom === 1 || row.custom === "1",
    steps: parseSteps(safeJsonParse(row.steps)),
    macro: String(row.macro ?? ""),
    micro: String(row.micro ?? ""),
  }
}

function safeJsonParse(value: unknown): unknown {
  if (typeof value !== "string" || !value) return []
  try {
    return JSON.parse(value)
  } catch {
    return []
  }
}

export function projectLayer(skill: BioSkill, layer: SkillLayer): Partial<BioSkill> & { name: string } {
  if (layer === "macro") {
    const { micro, microTags, ...rest } = skill
    return rest
  }
  if (layer === "micro") {
    const { macro, macroTags, ...rest } = skill
    return rest
  }
  return skill
}

export interface ListOptions {
  q?: string
  tag?: string
  layer?: SkillLayer
  // When true, only return skills that are turned on (enabled !== false).
  // Used by agent-facing access so muted skills are hidden.
  enabledOnly?: boolean
}

export function list(directory: string, opts: ListOptions = {}): Array<Partial<BioSkill> & { name: string }> {
  const layer = opts.layer ?? "all"
  const dir = bioskillsDir(directory)
  const db = openIndex(dir)
  try {
    ensureFresh(db, dir)
    let rows: Array<Record<string, unknown>>
    const match = opts.q ? ftsMatch(opts.q, layer) : null
    if (opts.q && !match) {
      rows = []
    } else if (match) {
      const names = (
        db.query("SELECT name FROM skills_fts WHERE skills_fts MATCH ? ORDER BY rank").all(match) as Array<{
          name: string
        }>
      ).map((r) => r.name)
      rows = names
        .map((name) => db.query("SELECT * FROM skills WHERE name = ?").get(name) as Record<string, unknown> | null)
        .filter((r): r is Record<string, unknown> => r !== null)
    } else {
      rows = db.query("SELECT * FROM skills ORDER BY name").all() as Array<Record<string, unknown>>
    }
    let skills = rows.map(rowToSkill)
    if (opts.enabledOnly) skills = skills.filter((s) => s.enabled !== false)
    if (opts.tag) {
      const tag = opts.tag.toLowerCase()
      skills = skills.filter(
        (s) =>
          s.macroTags.some((t) => t.toLowerCase() === tag) ||
          s.microTags.some((t) => t.toLowerCase() === tag) ||
          s.domain.toLowerCase() === tag,
      )
    }
    return skills.map((s) => projectLayer(s, layer))
  } finally {
    db.close()
  }
}

export function get(
  directory: string,
  name: string,
  layer: SkillLayer = "all",
): (Partial<BioSkill> & { name: string }) | null {
  const dir = bioskillsDir(directory)
  const skill = readSkill(dir, slugify(name))
  if (!skill) return null
  return projectLayer(skill, layer)
}

function applyInput(base: BioSkill | null, input: BioSkillInput): BioSkill {
  return {
    name: input.name ?? base?.name ?? "",
    description: input.description ?? base?.description ?? "",
    domain: input.domain ?? base?.domain ?? "",
    primaryTool: input.primaryTool ?? base?.primaryTool ?? "",
    methods: input.methods ?? base?.methods ?? [],
    macroTags: input.macroTags ?? base?.macroTags ?? [],
    microTags: input.microTags ?? base?.microTags ?? [],
    source: input.source ?? base?.source ?? "",
    status: input.status ?? base?.status ?? "active",
    enabled: input.enabled ?? base?.enabled ?? true,
    custom: input.custom ?? base?.custom ?? false,
    steps: input.steps !== undefined ? parseSteps(input.steps) : (base?.steps ?? []),
    macro: input.macro ?? base?.macro ?? "",
    micro: input.micro ?? base?.micro ?? "",
  }
}

export function create(directory: string, input: BioSkillInput): BioSkill {
  if (!input.name) throw new BioSkillError("Skill name is required")
  const name = slugify(input.name)
  const dir = bioskillsDir(directory)
  if (readSkill(dir, name)) throw new BioSkillError(`Skill already exists: ${name}`, 409)
  const skill = applyInput(null, { ...input, name })
  writeSkill(dir, skill)
  const db = openIndex(dir)
  try {
    ensureFresh(db, dir)
    upsertRow(db, { ...skill, name })
    db.run("INSERT OR REPLACE INTO meta (key, value) VALUES ('signature', ?)", [signature(dir)])
  } finally {
    db.close()
  }
  return { ...skill, name }
}

export function update(directory: string, name: string, input: BioSkillInput): BioSkill {
  const slug = slugify(name)
  const dir = bioskillsDir(directory)
  const existing = readSkill(dir, slug)
  if (!existing) throw new BioSkillError(`Skill not found: ${slug}`, 404)
  const skill = applyInput(existing, { ...input, name: slug })
  writeSkill(dir, skill)
  const db = openIndex(dir)
  try {
    ensureFresh(db, dir)
    upsertRow(db, { ...skill, name: slug })
    db.run("INSERT OR REPLACE INTO meta (key, value) VALUES ('signature', ?)", [signature(dir)])
  } finally {
    db.close()
  }
  if (input.enabled !== undefined) syncKnowledgeEnabled(directory, slug, skill.enabled)
  return { ...skill, name: slug }
}

export function syncKnowledgeEnabled(directory: string, skillID: string, enabled: boolean): boolean {
  const dbPath = path.join(directory, KNOWLEDGE_DB)
  if (!fs.existsSync(dbPath)) return false
  const db = new Database(dbPath)
  try {
    const table = db
      .query("SELECT 1 AS ok FROM sqlite_master WHERE type = 'table' AND name = 'skills'")
      .get() as { ok?: number } | null
    if (!table?.ok) return false
    const result = db.run("UPDATE skills SET enabled = ?, updated_at = CURRENT_TIMESTAMP WHERE skill_id = ?", [
      enabled ? 1 : 0,
      skillID,
    ])
    return result.changes > 0
  } finally {
    db.close()
  }
}

export function remove(directory: string, name: string): void {
  const slug = slugify(name)
  const dir = bioskillsDir(directory)
  const base = skillDir(dir, slug)
  if (!fs.existsSync(base)) throw new BioSkillError(`Skill not found: ${slug}`, 404)
  fs.rmSync(base, { recursive: true, force: true })
  const db = openIndex(dir)
  try {
    db.run("DELETE FROM skills WHERE name = ?", [slug])
    db.run("DELETE FROM skills_fts WHERE name = ?", [slug])
    db.run("INSERT OR REPLACE INTO meta (key, value) VALUES ('signature', ?)", [signature(dir)])
  } finally {
    db.close()
  }
}
