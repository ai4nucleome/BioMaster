import { Button } from "@opencode-ai/ui/button"
import { IconButton } from "@opencode-ai/ui/icon-button"
import { Markdown } from "@opencode-ai/session-ui/markdown"
import { A } from "@solidjs/router"
import { createMemo, createResource, createSignal, For, Show, type Component, type JSX } from "solid-js"
import { base64Encode } from "@opencode-ai/core/util/encode"
import { usePlatform } from "@/context/platform"
import { useSDK } from "@/context/sdk"
import { useServerSDK } from "@/context/server-sdk"
import { showToast } from "@/utils/toast"
import { authTokenFromCredentials } from "@/utils/server"
import { createBioskillsClient, type BioSkill, type BioSkillInput, type SkillStep } from "@/utils/bioskills"

type FormState = {
  mode: "create" | "edit"
  original?: string
  name: string
  description: string
  domain: string
  primaryTool: string
  methods: string
  macroTags: string
  microTags: string
  source: string
  macro: string
  micro: string
}

// Draft for the "New Skill → From a paper / URL / repo" flow.
type CreatorDraft = {
  name: string // article / tool name (optional)
  repo: string // GitHub repo URL (optional)
  url: string // article URL (optional)
  focus: string // required: what the skill should teach/enable
  fileName?: string // uploaded document name
  fileText?: string // extracted text of the uploaded document
}

// Live state of an AI skill-generation run (author / creator agent).
type RunState = {
  sessionID: string
  kind: "author" | "creator"
  title: string // short label of what is being generated
  request: string // the user's request text (shown as the first bubble)
  prior: string[] // skill names before the run, to detect the new skill
  status: "running" | "done"
  assistantText: string
  newSkill?: string
}

// Concatenate the text parts of the latest assistant message in a session.
function extractAssistantText(msgs: unknown): string {
  if (!Array.isArray(msgs)) return ""
  for (let i = msgs.length - 1; i >= 0; i--) {
    const m = msgs[i] as any
    if (m?.info?.role !== "assistant") continue
    const text = (m.parts ?? [])
      .filter((p: any) => p?.type === "text" && typeof p.text === "string")
      .map((p: any) => p.text)
      .join("\n")
      .trim()
    if (text) return text
  }
  return ""
}

function emptyForm(): FormState {
  return {
    mode: "create",
    name: "",
    description: "",
    domain: "single-cell",
    primaryTool: "",
    methods: "",
    macroTags: "",
    microTags: "",
    source: "",
    macro: "",
    micro: "",
  }
}

function toForm(skill: BioSkill): FormState {
  return {
    mode: "edit",
    original: skill.name,
    name: skill.name,
    description: skill.description ?? "",
    domain: skill.domain ?? "",
    primaryTool: skill.primaryTool ?? "",
    methods: (skill.methods ?? []).join(", "),
    macroTags: (skill.macroTags ?? []).join(", "),
    microTags: (skill.microTags ?? []).join(", "),
    source: skill.source ?? "",
    macro: skill.macro ?? "",
    micro: skill.micro ?? "",
  }
}

function splitTags(value: string): string[] {
  return value
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean)
}

function formToInput(form: FormState): BioSkillInput {
  return {
    name: form.name,
    description: form.description,
    domain: form.domain,
    primaryTool: form.primaryTool,
    methods: splitTags(form.methods),
    macroTags: splitTags(form.macroTags),
    microTags: splitTags(form.microTags),
    source: form.source,
    macro: form.macro,
    micro: form.micro,
  }
}

// Scan markdown headings, IGNORING lines inside fenced code blocks (```/~~~).
// This is critical: code blocks routinely contain `# comment` / `## comment`
// lines (e.g. Python comments) that must NOT be treated as section headings.
function scanHeadings(lines: string[]): { index: number; level: number; title: string }[] {
  const out: { index: number; level: number; title: string }[] = []
  let inFence = false
  let fenceChar = ""
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const fence = /^\s*(```+|~~~+)/.exec(line)
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
    const m = /^(#{1,6})\s+(.*\S)\s*$/.exec(line)
    if (m) out.push({ index: i, level: m[1].length, title: m[2].trim() })
  }
  return out
}

// Parse markdown into steps by its top-level headings. Returns null when there
// are fewer than 2 top-level sections (render as a single block in that case).
type Step = { title: string; body: string }
function splitSteps(md: string): { preamble: string; steps: Step[] } | null {
  const lines = (md ?? "").split("\n")
  const headings = scanHeadings(lines)
  if (headings.length < 2) return null
  const minLevel = Math.min(...headings.map((h) => h.level))
  const tops = headings.filter((h) => h.level === minLevel)
  if (tops.length < 2) return null
  const preamble = lines.slice(0, tops[0].index).join("\n").trim()
  const steps: Step[] = tops.map((h, idx) => {
    const start = h.index
    const end = idx + 1 < tops.length ? tops[idx + 1].index : lines.length
    return {
      title: h.title,
      body: lines.slice(start + 1, end).join("\n").trim(),
    }
  })
  return { preamble, steps }
}

// Return the body of the first heading whose title matches `title` (case
// insensitive), sliced up to the next heading of any level. Fence-aware.
function bodyForTitle(md: string, title: string): string {
  const lines = (md ?? "").split("\n")
  const hs = scanHeadings(lines)
  const norm = title.trim().toLowerCase()
  const hi = hs.findIndex((h) => h.title.trim().toLowerCase() === norm)
  if (hi < 0) return ""
  const end = hi + 1 < hs.length ? hs[hi + 1].index : lines.length
  return lines.slice(hs[hi].index + 1, end).join("\n").trim()
}

// Extract the workflow-level Overview (the `## Overview` section, else the
// preamble before the first step heading, else the whole doc).
function overviewOf(md: string, stepTitles: string[]): string {
  const explicit = bodyForTitle(md, "Overview")
  if (explicit) return explicit
  const lines = (md ?? "").split("\n")
  const hs = scanHeadings(lines)
  const norms = new Set(stepTitles.map((t) => t.trim().toLowerCase()))
  const firstStep = hs.find((h) => norms.has(h.title.trim().toLowerCase()))
  if (firstStep) {
    // strip a leading `# Title` line if present
    const body = lines.slice(0, firstStep.index).join("\n").trim()
    return body.replace(/^#\s+.*(\n+|$)/, "").trim()
  }
  return (md ?? "").replace(/^#\s+.*(\n+|$)/, "").trim()
}

// Align steps.json to the macro (description) + micro (execution) sections by
// title, producing one card per step. Returns null when the skill is not
// structured (no steps.json) so callers can fall back to blob rendering.
type LayeredCard = { id: string; title: string; tags: string[]; macro: string; micro: string }
function layeredCards(macro: string, micro: string, steps?: SkillStep[]): { overview: string; cards: LayeredCard[] } | null {
  if (!steps || steps.length === 0) return null
  const titles = steps.map((s) => s.title)
  const cards: LayeredCard[] = steps.map((s) => ({
    id: s.id,
    title: s.title,
    tags: s.tags ?? [],
    macro: bodyForTitle(macro, s.title),
    micro: bodyForTitle(micro, s.title),
  }))
  return { overview: overviewOf(macro, titles), cards }
}

// ── tones ──────────────────────────────────────────────────────────────
// macro (description layer, consumed by `plan`) -> blue / info
// micro (execution layer, consumed by `execute`/`debug`) -> amber / warning
const TONES = {
  macro: {
    bg: "var(--v2-state-bg-info)",
    fg: "var(--v2-state-fg-info)",
    border: "var(--v2-state-border-info)",
    dot: "var(--v2-blue-500)",
  },
  micro: {
    bg: "var(--v2-state-bg-warning)",
    fg: "var(--v2-state-fg-warning)",
    border: "var(--v2-state-border-warning)",
    dot: "var(--v2-yellow-500)",
  },
} as const

const inputClass =
  "w-full rounded-md border border-border-weak-base bg-background-base px-3 py-2 text-14-regular text-text-base outline-none transition-colors focus:border-border-focus focus:ring-2 focus:ring-[color-mix(in_srgb,var(--v2-blue-500)_25%,transparent)]"
const labelClass = "text-12-medium text-text-weak"

const Chip: Component<{ tone?: "macro" | "micro" | "neutral"; children: JSX.Element }> = (props) => {
  const tone = props.tone ?? "neutral"
  return (
    <span
      class="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-12-medium leading-none"
      classList={{ "border-border-weak-base bg-surface-base text-text-weak": tone === "neutral" }}
      style={
        tone === "neutral"
          ? undefined
          : { "background-color": TONES[tone].bg, color: TONES[tone].fg, "border-color": TONES[tone].border }
      }
    >
      {props.children}
    </span>
  )
}

const TagList: Component<{ tags: string[]; tone: "macro" | "micro"; max?: number }> = (props) => {
  const shown = createMemo(() => (props.max ? props.tags.slice(0, props.max) : props.tags))
  const rest = createMemo(() => Math.max(0, props.tags.length - shown().length))
  return (
    <Show when={props.tags.length} fallback={<span class="text-12-regular text-text-weak">—</span>}>
      <div class="flex flex-wrap gap-1.5">
        <For each={shown()}>{(tag) => <Chip tone={props.tone}>{tag}</Chip>}</For>
        <Show when={rest() > 0}>
          <Chip>+{rest()}</Chip>
        </Show>
      </div>
    </Show>
  )
}

const Toggle: Component<{ on: boolean; disabled?: boolean; label?: string; onToggle: () => void }> = (props) => (
  <button
    type="button"
    role="switch"
    aria-checked={props.on}
    aria-label={props.label}
    disabled={props.disabled}
    title={props.on ? "Turn off (mute)" : "Turn on"}
    onClick={(e) => {
      e.stopPropagation()
      props.onToggle()
    }}
    class="relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors disabled:opacity-50"
    style={{ "background-color": props.on ? "var(--v2-blue-500)" : "var(--v2-alpha-dark-20)" }}
  >
    <span
      class="inline-block size-4 rounded-full bg-white transition-transform"
      style={{ transform: props.on ? "translateX(18px)" : "translateX(2px)", "box-shadow": "0 1px 2px rgba(0,0,0,0.3)" }}
    />
  </button>
)

const SkillsPage: Component = () => {
  const platform = usePlatform()
  const sdk = useSDK()
  const serverSDK = useServerSDK()

  const client = createMemo(() => createBioskillsClient(serverSDK().server.http, sdk().directory, platform.fetch))

  const [search, setSearch] = createSignal("")
  const [selected, setSelected] = createSignal<string | undefined>()
  const [form, setForm] = createSignal<FormState | undefined>()
  const [busy, setBusy] = createSignal(false)
  // Omics/domain filter. "" = all, "__custom__" = user-added (customized) skills.
  const [omics, setOmics] = createSignal<string>("")
  const [menuOpen, setMenuOpen] = createSignal(false)
  const [ai, setAi] = createSignal<{ description: string } | undefined>()
  const [creator, setCreator] = createSignal<CreatorDraft | undefined>()
  const [run, setRun] = createSignal<RunState | undefined>()

  const [skills, { refetch, mutate }] = createResource(
    () => ({ q: search().trim(), dir: sdk().directory }),
    async (key) => client().list({ q: key.q || undefined, layer: "all" }),
  )

  // Distinct omics/domains present in the library (for the filter bar).
  const omicsList = createMemo(() => {
    const set = new Set<string>()
    for (const s of skills() ?? []) if (s.domain?.trim()) set.add(s.domain.trim())
    return Array.from(set).sort()
  })
  const customCount = createMemo(() => skills()?.filter((s) => s.custom === true).length ?? 0)

  const matchesOmics = (s: BioSkill): boolean => {
    const f = omics()
    if (!f) return true
    if (f === "__custom__") return s.custom === true
    return s.domain === f
  }
  const visible = createMemo(() => (skills() ?? []).filter(matchesOmics))

  const current = createMemo(() => skills()?.find((s) => s.name === selected()))
  const enabledCount = createMemo(() => visible().filter((s) => s.enabled !== false).length ?? 0)

  async function withBusy<T>(fn: () => Promise<T>, ok?: string): Promise<T | undefined> {
    setBusy(true)
    try {
      const result = await fn()
      if (ok) showToast({ variant: "success", title: ok })
      return result
    } catch (error) {
      showToast({
        variant: "error",
        title: "Operation failed",
        description: error instanceof Error ? error.message : String(error),
      })
      return undefined
    } finally {
      setBusy(false)
    }
  }

  async function toggleEnabled(skill: BioSkill) {
    const next = skill.enabled === false
    // optimistic update
    mutate((prev) => prev?.map((s) => (s.name === skill.name ? { ...s, enabled: next } : s)))
    const result = await withBusy(
      () => client().setEnabled(skill.name, next),
      next ? `Turned on “${skill.name}”` : `Muted “${skill.name}”`,
    )
    if (!result) await refetch()
  }

  async function save() {
    const f = form()
    if (!f) return
    if (!f.name.trim()) {
      showToast({ variant: "error", title: "Skill name is required" })
      return
    }
    // User-authored skills are flagged `custom` so they surface under the
    // "Customized" filter. On edit we omit the flag so the stored value is kept.
    const input: BioSkillInput = f.mode === "create" ? { ...formToInput(f), custom: true } : formToInput(f)
    const result = await withBusy(
      () => (f.mode === "create" ? client().create(input) : client().update(f.original!, input)),
      f.mode === "create" ? "Created" : "Saved",
    )
    if (result) {
      setForm(undefined)
      // Jump to the saved skill's detail page; clear filters so it is visible.
      if (f.mode === "create") {
        setSearch("")
        setOmics("")
      }
      await refetch()
      setSelected(result.name)
    }
  }

  async function remove(name: string) {
    if (!confirm(`Delete skill "${name}"? This cannot be undone.`)) return
    const ok = await withBusy(() => client().remove(name), "Deleted")
    if (ok) {
      if (selected() === name) setSelected(undefined)
      await refetch()
    }
  }

  async function reindex() {
    const result = await withBusy(() => client().reindex())
    if (result) {
      showToast({ variant: "success", title: `Reindexed (${result.count} skills)` })
      await refetch()
    }
  }

  // Server connection context (base URL + auth headers) for direct calls to the
  // session HTTP API (not part of the generated bioskills client).
  function serverCtx() {
    const server = serverSDK().server.http
    const base = server.url.replace(/\/+$/, "")
    const headers: Record<string, string> = {
      "content-type": "application/json",
      "x-opencode-directory": sdk().directory,
    }
    if (server.password) {
      headers.Authorization = `Basic ${authTokenFromCredentials({ username: server.username, password: server.password })}`
    }
    return { base, headers, doFetch: platform.fetch ?? fetch }
  }

  async function allSkillNames(): Promise<string[]> {
    try {
      return (await client().list({ layer: "all" })).map((s) => s.name)
    } catch {
      return skills()?.map((s) => s.name) ?? []
    }
  }

  // Create a background session for `agent`, send `prompt` (async), and return
  // the session id so the caller can follow the run live.
  async function startAgentSession(agent: string, title: string, prompt: string): Promise<string | undefined> {
    const { base, headers, doFetch } = serverCtx()
    return withBusy(async () => {
      const sres = await doFetch(`${base}/session`, { method: "POST", headers, body: JSON.stringify({ title, agent }) })
      const sjson = await sres.json()
      const sid = sjson?.id
      if (!sres.ok || !sid) throw new Error(sjson?.error || "Could not create an agent session")
      const pres = await doFetch(`${base}/session/${encodeURIComponent(sid)}/prompt_async`, {
        method: "POST",
        headers,
        body: JSON.stringify({ agent, parts: [{ type: "text", text: prompt }] }),
      })
      if (!pres.ok) throw new Error(`Failed to start generation (${pres.status})`)
      return sid as string
    })
  }

  // Poll a run's session until it goes idle, streaming the assistant text into
  // the run panel and, on completion, detecting the newly created skill.
  function pollRun(sid: string) {
    const { base, headers, doFetch } = serverCtx()
    const tick = async () => {
      const r = run()
      if (!r || r.sessionID !== sid) return // panel closed / superseded
      try {
        const stRes = await doFetch(`${base}/session/status`, { headers })
        const status = (await stRes.json())?.[sid]?.type ?? "idle"
        const mRes = await doFetch(`${base}/session/${encodeURIComponent(sid)}/message`, { headers })
        const assistantText = extractAssistantText(await mRes.json())
        if (status === "idle") {
          const after = await allSkillNames()
          const created = after.find((n) => !r.prior.includes(n))
          setRun({ ...r, status: "done", assistantText, newSkill: created })
          await refetch()
        } else {
          setRun({ ...r, assistantText })
          setTimeout(tick, 4000)
        }
      } catch {
        setTimeout(tick, 5000)
      }
    }
    setTimeout(tick, 3000)
  }

  // Jump from a finished run (or a create form) to a skill's detail page,
  // clearing filters so the skill is guaranteed visible.
  async function viewSkill(name: string) {
    setRun(undefined)
    setForm(undefined)
    setAi(undefined)
    setCreator(undefined)
    setSearch("")
    setOmics("")
    await refetch()
    setSelected(name)
  }

  // "From a description (AI)": draft a skill from a free-form description.
  async function startAiCreate() {
    const text = ai()?.description.trim() ?? ""
    if (!text) {
      showToast({ variant: "error", title: "Describe the skill first" })
      return
    }
    const prompt =
      "A user wants to add a NEW BioSkill from the free-form description below. " +
      "First judge whether it is detailed enough for a curated macro+micro skill; if too thin, reply that it was rejected. " +
      "Otherwise call the bioskills-author tool exactly ONCE to create the skill: choose a good kebab-case `name` and a `domain`, " +
      "set `custom` to true, write an `overview` (prose, no code) and 3-8 COHERENT steps, each with a `description` (prose, no code), " +
      "`code` (fenced execution), and `tags`. English only.\n\nDescription:\n\n" +
      text
    const prior = await allSkillNames()
    const sid = await startAgentSession("biomaster-skill-author", "ui-skill-author", prompt)
    if (!sid) return
    setAi(undefined)
    setRun({ sessionID: sid, kind: "author", title: "New skill from description", request: text, prior, status: "running", assistantText: "" })
    pollRun(sid)
  }

  // "From a paper / URL / repo": synthesize a skill from source material.
  async function startCreate() {
    const d = creator()
    if (!d) return
    const focus = d.focus.trim()
    if (!focus) {
      showToast({ variant: "error", title: "A skill focus description is required" })
      return
    }
    const lines: string[] = [
      "Create a NEW curated BioSkill (custom:true) from the source material below, scoped to the requested focus.",
      "",
      `SKILL FOCUS (required — what the skill must teach/enable): ${focus}`,
    ]
    if (d.name.trim()) lines.push(`ARTICLE / TOOL NAME: ${d.name.trim()}`)
    if (d.repo.trim()) lines.push(`GITHUB REPO URL (webfetch its README for install/usage/params): ${d.repo.trim()}`)
    if (d.url.trim()) lines.push(`ARTICLE URL (webfetch if you need method details): ${d.url.trim()}`)
    if (d.fileText?.trim()) {
      lines.push("", `UPLOADED DOCUMENT (${d.fileName ?? "file"}) — primary source text:`, "", d.fileText.trim())
    }
    lines.push(
      "",
      "Gather the material (use webfetch on the URLs), then call bioskills-author exactly ONCE: choose a kebab-case name, a domain, set custom:true and source to the repo/article, write an overview (no code) and 3-8 coherent steps each with description (no code) + code (real commands/params) + tags. English only.",
    )
    const summaryParts = [focus]
    if (d.repo.trim()) summaryParts.push(`repo: ${d.repo.trim()}`)
    if (d.url.trim()) summaryParts.push(`url: ${d.url.trim()}`)
    if (d.fileName) summaryParts.push(`file: ${d.fileName}`)
    const prior = await allSkillNames()
    const sid = await startAgentSession("biomaster-skill-creator", "ui-skill-creator", lines.join("\n"))
    if (!sid) return
    setCreator(undefined)
    setRun({
      sessionID: sid,
      kind: "creator",
      title: "New skill from paper / URL / repo",
      request: summaryParts.join("\n"),
      prior,
      status: "running",
      assistantText: "",
    })
    pollRun(sid)
  }

  // Read an uploaded document, extract its text via the backend, and stash it.
  async function onCreatorFile(file: File) {
    const buf = await file.arrayBuffer()
    let binary = ""
    const bytes = new Uint8Array(buf)
    for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i])
    const b64 = btoa(binary)
    const res = await withBusy(() => client().ingest(file.name, b64), `Loaded ${file.name}`)
    if (res) setCreator({ ...(creator() ?? { name: "", repo: "", url: "", focus: "" }), fileName: res.filename, fileText: res.text })
  }

  const sessionHref = createMemo(() => `/${base64Encode(sdk().directory)}/session`)

  return (
    <div class="flex flex-col h-full w-full min-h-0 bg-background-base text-text-base">
      {/* Header */}
      <div class="flex items-center gap-3 px-5 py-3 shrink-0 border-b border-border-weaker-base">
        <A href={sessionHref()}>
          <IconButton icon="arrow-left" variant="ghost" aria-label="Back to session" />
        </A>
        <div
          class="flex items-center justify-center size-9 rounded-[10px] shrink-0 text-text-inverse"
          style={{
            background: "linear-gradient(135deg, var(--v2-blue-500), var(--v2-blue-700))",
            "box-shadow": "var(--v2-elevation-raised)",
          }}
        >
          <span class="text-14-medium">Bio</span>
        </div>
        <div class="flex flex-col min-w-0">
          <span class="text-16-medium leading-tight">BioSkills Library</span>
          <span class="text-12-regular text-text-weak truncate max-w-[42ch]" title={sdk().directory}>
            {sdk().directory}
          </span>
        </div>

        <div class="flex-1" />

        <Button variant="ghost" icon="dot-grid" onClick={reindex} disabled={busy()}>
          Reindex
        </Button>
        <div class="relative">
          <Button icon="plus-small" onClick={() => setMenuOpen(!menuOpen())} disabled={busy()}>
            New Skill
          </Button>
          <Show when={menuOpen()}>
            <div class="fixed inset-0 z-20" onClick={() => setMenuOpen(false)} />
            <div class="absolute right-0 mt-1.5 z-30 w-80 rounded-xl border border-border-weak-base bg-background-base overflow-hidden shadow-[var(--v2-elevation-overlay)]">
              <button
                type="button"
                class="w-full text-left px-4 py-3 flex flex-col gap-0.5 hover:bg-surface-base transition-colors"
                onClick={() => {
                  setMenuOpen(false)
                  setAi(undefined)
                  setForm(emptyForm())
                }}
              >
                <span class="text-14-medium">Manual entry</span>
                <span class="text-12-regular text-text-weak">Fill in the fields and step content yourself.</span>
              </button>
              <button
                type="button"
                class="w-full text-left px-4 py-3 flex flex-col gap-0.5 hover:bg-surface-base transition-colors border-t border-border-weaker-base"
                onClick={() => {
                  setMenuOpen(false)
                  setForm(undefined)
                  setAi({ description: "" })
                }}
              >
                <span class="text-14-medium flex items-center gap-1.5">
                  From a description
                  <Chip tone="macro">AI</Chip>
                </span>
                <span class="text-12-regular text-text-weak">
                  Paste a rough description; skill-author drafts a curated skill.
                </span>
              </button>
              <button
                type="button"
                class="w-full text-left px-4 py-3 flex flex-col gap-0.5 hover:bg-surface-base transition-colors border-t border-border-weaker-base"
                onClick={() => {
                  setMenuOpen(false)
                  setForm(undefined)
                  setAi(undefined)
                  setCreator({ name: "", repo: "", url: "", focus: "" })
                }}
              >
                <span class="text-14-medium flex items-center gap-1.5">
                  From a paper / URL / repo
                  <Chip tone="macro">AI</Chip>
                </span>
                <span class="text-12-regular text-text-weak">
                  Auto-generate a skill from an article, link, or GitHub repository.
                </span>
              </button>
            </div>
          </Show>
        </div>
      </div>

      {/* Body */}
      <div class="flex-1 min-h-0 flex gap-4 px-5 py-4">
        {/* List */}
        <div class="w-80 xl:w-96 shrink-0 flex flex-col min-h-0 rounded-xl border border-border-weaker-base bg-background-stronger overflow-hidden">
          {/* Search */}
          <div class="px-2.5 pt-2.5 pb-2 shrink-0 border-b border-border-weaker-base">
            <div class="flex items-center gap-2 rounded-lg border border-border-weak-base bg-surface-base px-3 h-9 focus-within:border-border-focus transition-colors">
              <span class="text-text-weak text-14-regular shrink-0">⌕</span>
              <input
                class="flex-1 min-w-0 bg-transparent outline-none text-14-regular text-text-base placeholder:text-text-weak"
                placeholder="Search skills…"
                value={search()}
                onInput={(e) => setSearch(e.currentTarget.value)}
              />
              <Show when={search()}>
                <IconButton icon="circle-x" variant="ghost" size="small" onClick={() => setSearch("")} aria-label="Clear" />
              </Show>
            </div>
          </div>
          {/* Omics / customized filter dropdown + count */}
          <div class="flex items-center gap-2 px-2.5 py-2 shrink-0 border-b border-border-weaker-base">
            <select
              class="flex-1 min-w-0 h-9 rounded-md border border-border-weak-base px-3 text-14-regular text-text-base outline-none transition-colors focus:border-border-focus"
              style={{ "background-color": "#ffffff" }}
              value={omics()}
              onChange={(e) => setOmics(e.currentTarget.value)}
            >
              <option value="">All domains</option>
              <Show when={customCount() > 0}>
                <option value="__custom__">Customized ({customCount()})</option>
              </Show>
              <For each={omicsList()}>{(d) => <option value={d}>{d}</option>}</For>
            </select>
            <span class="text-12-medium text-text-weak shrink-0 whitespace-nowrap">
              {skills.loading ? "Loading…" : `${visible().length} · ${enabledCount()} on`}
            </span>
          </div>
          <div class="flex-1 min-h-0 overflow-y-auto p-2 flex flex-col gap-1.5">
            <For
              each={visible()}
              fallback={
                <div class="flex flex-col items-center justify-center gap-1 px-3 py-10 text-center">
                  <span class="text-14-medium text-text-weak">No matching skills</span>
                  <span class="text-12-regular text-text-weak">Try another keyword, or click “New Skill”.</span>
                </div>
              }
            >
              {(skill) => {
                const active = () => selected() === skill.name && !form()
                const muted = () => skill.enabled === false
                return (
                  <div
                    role="button"
                    tabindex={0}
                    class="group w-full text-left rounded-lg border px-3 py-2.5 flex flex-col gap-1.5 transition-colors cursor-pointer"
                    classList={{
                      "border-border-focus bg-surface-base": active(),
                      "border-transparent hover:border-border-weak-base hover:bg-surface-base": !active(),
                      "opacity-55": muted(),
                    }}
                    onClick={() => {
                      setSelected(skill.name)
                      setForm(undefined)
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault()
                        setSelected(skill.name)
                        setForm(undefined)
                      }
                    }}
                  >
                    <div class="flex items-center gap-2">
                      <span class="text-14-medium truncate flex-1">{skill.name}</span>
                      <Toggle
                        on={skill.enabled !== false}
                        disabled={busy()}
                        label={`Toggle ${skill.name}`}
                        onToggle={() => toggleEnabled(skill)}
                      />
                    </div>
                    <div class="flex items-center gap-1.5">
                      <Show when={skill.domain}>
                        <Chip>{skill.domain}</Chip>
                      </Show>
                      <Show when={skill.custom}>
                        <Chip tone="macro">customized</Chip>
                      </Show>
                      <Show when={muted()}>
                        <Chip>muted</Chip>
                      </Show>
                    </div>
                    <span class="text-12-regular text-text-weak line-clamp-2 leading-snug">{skill.description}</span>
                    <div class="flex items-center gap-2 pt-0.5">
                      <Show when={(skill.macroTags?.length ?? 0) > 0}>
                        <span class="inline-flex items-center gap-1 text-11-medium text-text-weak">
                          <span class="size-2 rounded-full" style={{ "background-color": TONES.macro.dot }} />
                          {skill.macroTags!.length} macro
                        </span>
                      </Show>
                      <Show when={(skill.microTags?.length ?? 0) > 0}>
                        <span class="inline-flex items-center gap-1 text-11-medium text-text-weak">
                          <span class="size-2 rounded-full" style={{ "background-color": TONES.micro.dot }} />
                          {skill.microTags!.length} micro
                        </span>
                      </Show>
                    </div>
                  </div>
                )
              }}
            </For>
          </div>
        </div>

        {/* Detail / Form */}
        <div class="flex-1 min-h-0 overflow-y-auto rounded-xl border border-border-weaker-base bg-background-stronger">
          <Show
            when={run()}
            fallback={
              <Show
                when={form()}
                fallback={
                  <Show
                    when={ai()}
                    fallback={
                      <Show
                        when={creator()}
                        fallback={
                          <SkillDetail
                            skill={current()}
                            onEdit={() => current() && setForm(toForm(current()!))}
                            onDelete={remove}
                            onToggle={toggleEnabled}
                            busy={busy()}
                          />
                        }
                      >
                        {(draft) => (
                          <CreatePanel
                            draft={draft()}
                            busy={busy()}
                            onChange={(patch) => setCreator({ ...draft(), ...patch })}
                            onFile={onCreatorFile}
                            onClearFile={() => setCreator({ ...draft(), fileName: undefined, fileText: undefined })}
                            onCancel={() => setCreator(undefined)}
                            onSubmit={startCreate}
                          />
                        )}
                      </Show>
                    }
                  >
                    {(draft) => (
                      <AiCreatePanel
                        description={draft().description}
                        busy={busy()}
                        onChange={(t) => setAi({ description: t })}
                        onCancel={() => setAi(undefined)}
                        onSubmit={startAiCreate}
                      />
                    )}
                  </Show>
                }
              >
                {(f) => (
                  <SkillForm
                    form={f}
                    busy={busy()}
                    domains={omicsList()}
                    onChange={(patch) => setForm({ ...f(), ...patch })}
                    onCancel={() => setForm(undefined)}
                    onSave={save}
                  />
                )}
              </Show>
            }
          >
            {(r) => <RunPanel run={r()} onClose={() => setRun(undefined)} onView={(name) => viewSkill(name)} />}
          </Show>
        </div>
      </div>
    </div>
  )
}

// ── detail ─────────────────────────────────────────────────────────────
const MetaItem: Component<{ label: string; value?: string }> = (props) => (
  <div class="flex flex-col gap-0.5 rounded-lg border border-border-weaker-base bg-background-base px-3 py-2 min-w-32">
    <span class="text-11-medium text-text-weak uppercase tracking-wide">{props.label}</span>
    <span class="text-13-regular text-text-base truncate" title={props.value || "—"}>
      {props.value || "—"}
    </span>
  </div>
)

const StepPanel: Component<{
  index: number
  step: Step
  defaultOpen?: boolean
  // Structured metadata (present when the skill has steps.json)
  tags?: string[]
}> = (props) => {
  const [open, setOpen] = createSignal(!!props.defaultOpen)
  return (
    <div class="rounded-lg border border-border-weak-base bg-background-base overflow-hidden">
      <div class="w-full flex items-center gap-2 px-3 py-2 hover:bg-surface-base transition-colors">
        <button
          type="button"
          class="flex items-center gap-2 flex-1 min-w-0 text-left"
          onClick={() => setOpen(!open())}
          aria-expanded={open()}
        >
          <span
            class="text-11-medium transition-transform shrink-0 text-text-weak"
            style={{ transform: open() ? "rotate(90deg)" : "rotate(0deg)" }}
          >
            ▶
          </span>
          <span
            class="flex items-center justify-center size-5 rounded-md text-11-medium shrink-0"
            style={{ "background-color": TONES.micro.bg, color: TONES.micro.fg }}
          >
            {props.index + 1}
          </span>
          <span class="text-13-medium min-w-0 truncate">{props.step.title}</span>
        </button>
        <Show when={(props.tags?.length ?? 0) > 0}>
          <div class="hidden sm:flex items-center gap-1 shrink-0 max-w-[45%] overflow-hidden">
            <For each={props.tags!.slice(0, 4)}>{(tag) => <Chip tone="micro">{tag}</Chip>}</For>
            <Show when={props.tags!.length > 4}>
              <Chip>+{props.tags!.length - 4}</Chip>
            </Show>
          </div>
        </Show>
      </div>
      <Show when={open()}>
        <div class="px-4 py-3 border-t border-border-weaker-base">
          <Show when={(props.tags?.length ?? 0) > 0}>
            <div class="flex flex-wrap gap-1.5 pb-2 sm:hidden">
              <For each={props.tags!}>{(tag) => <Chip tone="micro">{tag}</Chip>}</For>
            </div>
          </Show>
          <Show
            when={props.step.body?.trim()}
            fallback={<span class="text-12-regular text-text-weak">(no details)</span>}
          >
            <Markdown text={props.step.body} class="text-13-regular leading-relaxed" />
          </Show>
        </div>
      </Show>
    </div>
  )
}

const MicroBody: Component<{
  content: string
  steps?: SkillStep[]
}> = (props) => {
  const parsed = createMemo(() => splitSteps(props.content))
  // Structured steps (steps.json) align to the markdown sections by order.
  const structured = createMemo(() => props.steps && props.steps.length > 0)
  return (
    <Show
      when={parsed()}
      fallback={
        <Show when={props.content?.trim()} fallback={<span class="text-12-regular text-text-weak">(empty)</span>}>
          <Markdown text={props.content} class="text-13-regular leading-relaxed" />
        </Show>
      }
    >
      {(data) => (
        <div class="flex flex-col gap-2">
          <Show when={data().preamble}>
            <Markdown text={data().preamble} class="text-13-regular leading-relaxed" />
          </Show>
          <For each={data().steps}>
            {(step, i) => {
              const meta = () => (structured() ? props.steps![i()] : undefined)
              return (
                <StepPanel
                  index={i()}
                  step={step}
                  defaultOpen={i() === 0}
                  tags={meta()?.tags}
                />
              )
            }}
          </For>
        </div>
      )}
    </Show>
  )
}

// Unified per-step card: shows the step's MACRO description by default and the
// MICRO execution/code in a collapsible sub-panel.
const LayeredStepCard: Component<{
  index: number
  card: LayeredCard
}> = (props) => {
  const [showCode, setShowCode] = createSignal(false)
  return (
    <div
      class="rounded-xl border overflow-hidden"
      style={{ "border-color": TONES.macro.border }}
    >
      {/* header */}
      <div class="flex items-center gap-2 px-4 py-2.5 border-b bg-background-base" style={{ "border-color": "var(--v2-border-weaker-base)" }}>
        <span
          class="flex items-center justify-center size-6 rounded-md text-12-medium shrink-0"
          style={{ "background-color": TONES.macro.bg, color: TONES.macro.fg }}
        >
          {props.index + 1}
        </span>
        <span class="text-14-medium min-w-0 truncate flex-1">{props.card.title}</span>
        <Show when={props.card.tags.length}>
          <div class="hidden md:flex items-center gap-1 shrink-0 max-w-[40%] overflow-hidden">
            <For each={props.card.tags.slice(0, 4)}>{(tag) => <Chip tone="micro">{tag}</Chip>}</For>
            <Show when={props.card.tags.length > 4}>
              <Chip>+{props.card.tags.length - 4}</Chip>
            </Show>
          </div>
        </Show>
      </div>
      {/* body */}
      <div class="flex flex-col bg-background-base">
        {/* tags on small screens */}
        <Show when={props.card.tags.length}>
          <div class="flex md:hidden flex-wrap gap-1.5 px-4 pt-3">
            <For each={props.card.tags}>{(tag) => <Chip tone="micro">{tag}</Chip>}</For>
          </div>
        </Show>
        {/* macro description (always shown) */}
        <div class="px-4 py-3">
          <div class="flex items-center gap-1.5 pb-1.5">
            <span class="size-2 rounded-full" style={{ "background-color": TONES.macro.dot }} />
            <span class="text-11-medium" style={{ color: TONES.macro.fg }}>
              Description
            </span>
          </div>
          <Show
            when={props.card.macro?.trim()}
            fallback={<span class="text-12-regular text-text-weak">(no description)</span>}
          >
            <Markdown text={props.card.macro} class="text-13-regular leading-relaxed" />
          </Show>
        </div>
        {/* micro execution (collapsed by default) */}
        <div class="border-t" style={{ "border-color": "var(--v2-border-weaker-base)" }}>
          <button
            type="button"
            class="w-full flex items-center gap-2 px-4 py-2 hover:bg-surface-base transition-colors text-left"
            onClick={() => setShowCode(!showCode())}
            aria-expanded={showCode()}
          >
            <span
              class="text-11-medium transition-transform shrink-0 text-text-weak"
              style={{ transform: showCode() ? "rotate(90deg)" : "rotate(0deg)" }}
            >
              ▶
            </span>
            <span class="size-2 rounded-full" style={{ "background-color": TONES.micro.dot }} />
            <span class="text-11-medium" style={{ color: TONES.micro.fg }}>
              {showCode() ? "Hide execution / code" : "Show execution / code"}
            </span>
          </button>
          <Show when={showCode()}>
            <div class="px-4 py-3 border-t" style={{ "border-color": "var(--v2-border-weaker-base)" }}>
              <Show
                when={props.card.micro?.trim()}
                fallback={<span class="text-12-regular text-text-weak">(no execution detail)</span>}
              >
                <Markdown text={props.card.micro} class="text-13-regular leading-relaxed" />
              </Show>
            </div>
          </Show>
        </div>
      </div>
    </div>
  )
}

const SkillDetail: Component<{
  skill: BioSkill | undefined
  onEdit: () => void
  onDelete: (name: string) => void
  onToggle: (skill: BioSkill) => void
  busy: boolean
}> = (props) => (
  <Show
    when={props.skill}
    fallback={
      <div class="h-full flex flex-col items-center justify-center gap-2 text-center px-8">
        <div
          class="flex items-center justify-center size-12 rounded-xl text-text-inverse mb-1"
          style={{ background: "linear-gradient(135deg, var(--v2-blue-500), var(--v2-blue-700))" }}
        >
          <span class="text-16-medium">Bio</span>
        </div>
        <span class="text-16-medium">Select a skill to view details</span>
        <span class="text-13-regular text-text-weak max-w-sm">
          The list on the left supports keyword search. Each skill has a
          <b class="text-text-base"> macro (description) </b> layer for the <code>plan</code> agent and a
          <b class="text-text-base"> micro (execution) </b> layer for <code>execute</code> / <code>debug</code>.
        </span>
      </div>
    }
  >
    {(skill) => {
      const layered = createMemo(() => layeredCards(skill().macro ?? "", skill().micro ?? "", skill().steps))
      return (
        <div class="flex flex-col gap-5 p-5 max-w-4xl mx-auto">
          {/* hero */}
          <div class="flex items-start gap-3">
            <div class="flex flex-col gap-1.5 min-w-0 flex-1">
              <div class="flex items-center gap-2 flex-wrap">
                <h1 class="text-16-medium leading-tight break-words">{skill().name}</h1>
                <Show when={skill().custom}>
                  <Chip tone="macro">customized</Chip>
                </Show>
                <Show when={skill().enabled === false}>
                  <Chip>muted</Chip>
                </Show>
              </div>
              <p class="text-14-regular text-text-weak leading-relaxed">{skill().description || "(no description)"}</p>
            </div>
            <div class="flex items-center gap-3 shrink-0">
              <div class="flex items-center gap-2">
                <span class="text-12-medium text-text-weak">{skill().enabled === false ? "Off" : "On"}</span>
                <Toggle
                  on={skill().enabled !== false}
                  disabled={props.busy}
                  label={`Toggle ${skill().name}`}
                  onToggle={() => props.onToggle(skill())}
                />
              </div>
              <Button variant="ghost" icon="sliders" onClick={props.onEdit}>
                Edit
              </Button>
              <IconButton icon="trash" variant="ghost" aria-label="Delete" onClick={() => props.onDelete(skill().name)} />
            </div>
          </div>

          {/* meta */}
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <MetaItem label="Domain" value={skill().domain} />
            <MetaItem label="Primary tool" value={skill().primaryTool} />
            <MetaItem label="Source" value={skill().source} />
            <MetaItem label="Status" value={skill().status} />
          </div>

          {/* methods */}
          <Show when={(skill().methods?.length ?? 0) > 0}>
            <div class="flex flex-col gap-2">
              <span class={labelClass}>Methods / toolchain</span>
              <div class="flex flex-wrap gap-1.5">
                <For each={skill().methods}>{(m) => <Chip>{m}</Chip>}</For>
              </div>
            </div>
          </Show>

          {/* Structured skills: unified Overview + per-step (macro + collapsible micro) cards.
              Non-structured skills fall back to the classic macro/micro blob panels. */}
          <Show
            when={layered()}
            fallback={
              <>
                {/* macro */}
                <section class="rounded-xl border overflow-hidden" style={{ "border-color": TONES.macro.border }}>
                  <div
                    class="flex flex-wrap items-center gap-x-3 gap-y-2 px-4 py-3 border-b"
                    style={{ "background-color": TONES.macro.bg, "border-color": TONES.macro.border }}
                  >
                    <span class="size-2.5 rounded-full shrink-0" style={{ "background-color": TONES.macro.dot }} />
                    <div class="flex flex-col">
                      <span class="text-14-medium" style={{ color: TONES.macro.fg }}>
                        Macro · description layer (macro.md)
                      </span>
                      <span class="text-11-medium" style={{ color: TONES.macro.fg, opacity: 0.8 }}>
                        Read by biomaster-plan
                      </span>
                    </div>
                    <div class="flex-1" />
                    <TagList tags={skill().macroTags ?? []} tone="macro" />
                  </div>
                  <div class="px-4 py-3 bg-background-base">
                    <Show
                      when={skill().macro?.trim()}
                      fallback={<span class="text-12-regular text-text-weak">(empty)</span>}
                    >
                      <Markdown text={skill().macro ?? ""} class="text-13-regular leading-relaxed" />
                    </Show>
                  </div>
                </section>

                {/* micro */}
                <section class="rounded-xl border overflow-hidden" style={{ "border-color": TONES.micro.border }}>
                  <div
                    class="flex flex-wrap items-center gap-x-3 gap-y-2 px-4 py-3 border-b"
                    style={{ "background-color": TONES.micro.bg, "border-color": TONES.micro.border }}
                  >
                    <span class="size-2.5 rounded-full shrink-0" style={{ "background-color": TONES.micro.dot }} />
                    <div class="flex flex-col">
                      <span class="text-14-medium" style={{ color: TONES.micro.fg }}>
                        Micro · execution layer (micro.md)
                      </span>
                      <span class="text-11-medium" style={{ color: TONES.micro.fg, opacity: 0.8 }}>
                        Read by biomaster-execute / debug
                      </span>
                    </div>
                    <div class="flex-1" />
                    <TagList tags={skill().microTags ?? []} tone="micro" />
                  </div>
                  <div class="px-4 py-3 bg-background-base">
                    <MicroBody
                      content={skill().micro ?? ""}
                      steps={skill().steps}
                    />
                  </div>
                </section>
              </>
            }
          >
            {(data) => (
              <>
                {/* Overview (workflow-level macro description) */}
                <section class="rounded-xl border overflow-hidden" style={{ "border-color": TONES.macro.border }}>
                  <div
                    class="flex flex-wrap items-center gap-x-3 gap-y-2 px-4 py-3 border-b"
                    style={{ "background-color": TONES.macro.bg, "border-color": TONES.macro.border }}
                  >
                    <span class="size-2.5 rounded-full shrink-0" style={{ "background-color": TONES.macro.dot }} />
                    <div class="flex flex-col">
                      <span class="text-14-medium" style={{ color: TONES.macro.fg }}>
                        Overview
                      </span>
                      <span class="text-11-medium" style={{ color: TONES.macro.fg, opacity: 0.8 }}>
                        {data().cards.length} steps · description shown, execution collapsed
                      </span>
                    </div>
                    <div class="flex-1" />
                    <TagList tags={skill().macroTags ?? []} tone="macro" />
                  </div>
                  <div class="px-4 py-3 bg-background-base">
                    <Show
                      when={data().overview?.trim()}
                      fallback={<span class="text-12-regular text-text-weak">(no overview)</span>}
                    >
                      <Markdown text={data().overview} class="text-13-regular leading-relaxed" />
                    </Show>
                  </div>
                </section>

                {/* Per-step cards: each is macro description + collapsible micro. */}
                <div class="flex flex-col gap-3">
                  <For each={data().cards}>
                    {(card, i) => (
                      <LayeredStepCard
                        index={i()}
                        card={card}
                      />
                    )}
                  </For>
                </div>
              </>
            )}
          </Show>
        </div>
      )
    }}
  </Show>
)

// ── AI create ──────────────────────────────────────────────────────────
const AiCreatePanel: Component<{
  description: string
  busy: boolean
  onChange: (text: string) => void
  onCancel: () => void
  onSubmit: () => void
}> = (props) => (
  <div class="flex flex-col gap-5 p-5 max-w-4xl mx-auto">
    <div class="flex items-center gap-2 sticky top-0 -mx-5 -mt-5 px-5 py-3 bg-background-stronger border-b border-border-weaker-base z-10">
      <span class="text-16-medium flex items-center gap-2">
        New Skill from a description
        <Chip tone="macro">AI</Chip>
      </span>
      <div class="flex-1" />
      <Button variant="ghost" onClick={props.onCancel} disabled={props.busy}>
        Cancel
      </Button>
      <Button icon="plus-small" onClick={props.onSubmit} disabled={props.busy}>
        Generate
      </Button>
    </div>

    <div
      class="rounded-xl border px-4 py-3 text-13-regular leading-relaxed"
      style={{ "background-color": TONES.macro.bg, "border-color": TONES.macro.border, color: TONES.macro.fg }}
    >
      The <b>biomaster-skill-author</b> agent will read your description, judge whether it is detailed enough, and (if so)
      draft a curated skill with an overview plus per-step description + code. It runs in the background; when it finishes,
      click <b>Reindex</b> to pull the new skill into the library.
    </div>

    <Field
      label="Describe the workflow / method"
      hint="Include the goal, tools/libraries, key steps, and important parameters. The more detail, the better the result."
    >
      <textarea
        class={inputClass + " min-h-64 leading-relaxed resize-y"}
        placeholder="e.g. A bulk RNA-seq differential expression workflow using DESeq2: import salmon quant counts with tximport, build the DESeqDataSet, filter low counts, run DESeq, shrink log-fold-changes with apeglm, then export results and a volcano plot…"
        value={props.description}
        onInput={(e) => props.onChange(e.currentTarget.value)}
      />
    </Field>
  </div>
)

// ── create from paper / URL / repo ───────────────────────────────────────
const CreatePanel: Component<{
  draft: CreatorDraft
  busy: boolean
  onChange: (patch: Partial<CreatorDraft>) => void
  onFile: (file: File) => void
  onClearFile: () => void
  onCancel: () => void
  onSubmit: () => void
}> = (props) => {
  let fileInput: HTMLInputElement | undefined
  const canSubmit = () => props.draft.focus.trim().length > 0
  return (
    <div class="flex flex-col gap-5 p-5 max-w-4xl mx-auto">
      <div class="flex items-center gap-2 sticky top-0 -mx-5 -mt-5 px-5 py-3 bg-background-stronger border-b border-border-weaker-base z-10">
        <span class="text-16-medium flex items-center gap-2">
          New Skill from a paper / URL / repo
          <Chip tone="macro">AI</Chip>
        </span>
        <div class="flex-1" />
        <Button variant="ghost" onClick={props.onCancel} disabled={props.busy}>
          Cancel
        </Button>
        <Button icon="plus-small" onClick={props.onSubmit} disabled={props.busy || !canSubmit()}>
          Generate
        </Button>
      </div>

      <div
        class="rounded-xl border px-4 py-3 text-13-regular leading-relaxed"
        style={{ "background-color": TONES.macro.bg, "border-color": TONES.macro.border, color: TONES.macro.fg }}
      >
        Provide any of a tool/paper name, a GitHub repo, an article link, or an uploaded document — or none. The
        <b> biomaster-skill-creator</b> agent fetches the sources (README, article) and, guided by your skill focus,
        drafts an install → run → interpret skill. It runs in the background; click <b>Reindex</b> when it finishes.
      </div>

      <Field label="Skill focus (required)" hint="What the skill should teach or enable, e.g. 'Hi-C loop calling with RefHiC: install and run for TAD/loop annotation'.">
        <textarea
          class={inputClass + " min-h-24 leading-relaxed resize-y"}
          placeholder="e.g. Generate a workflow for Hi-C loop identification and TAD/structure annotation using RefHiC (installation + usage)."
          value={props.draft.focus}
          onInput={(e) => props.onChange({ focus: e.currentTarget.value })}
        />
      </Field>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Field label="Article / tool name" hint="Optional">
          <input
            class={inputClass}
            placeholder="Reference panel guided topological structure annotation of Hi-C data"
            value={props.draft.name}
            onInput={(e) => props.onChange({ name: e.currentTarget.value })}
          />
        </Field>
        <Field label="GitHub repo URL" hint="Optional — its README is fetched for install/usage">
          <input
            class={inputClass}
            placeholder="https://github.com/BlanchetteLab/RefHiC"
            value={props.draft.repo}
            onInput={(e) => props.onChange({ repo: e.currentTarget.value })}
          />
        </Field>
      </div>

      <Field label="Article URL" hint="Optional — fetched if method details are needed">
        <input
          class={inputClass}
          placeholder="https://www.nature.com/articles/s41467-022-35231-3"
          value={props.draft.url}
          onInput={(e) => props.onChange({ url: e.currentTarget.value })}
        />
      </Field>

      <Field label="Upload document" hint="Optional — PDF or text; the text is extracted and used as source material">
        <input
          ref={(el) => (fileInput = el)}
          type="file"
          accept=".pdf,.md,.markdown,.txt,.rst,.json,text/*,application/pdf"
          class="hidden"
          onChange={(e) => {
            const f = e.currentTarget.files?.[0]
            if (f) props.onFile(f)
            e.currentTarget.value = ""
          }}
        />
        <div class="flex items-center gap-2">
          <Button variant="ghost" icon="plus-small" onClick={() => fileInput?.click()} disabled={props.busy}>
            Choose file
          </Button>
          <Show
            when={props.draft.fileName}
            fallback={<span class="text-12-regular text-text-weak">No file selected</span>}
          >
            <span class="text-12-medium text-text-base truncate max-w-[24ch]" title={props.draft.fileName}>
              {props.draft.fileName}
            </span>
            <span class="text-11-regular text-text-weak">
              {(props.draft.fileText?.length ?? 0).toLocaleString()} chars
            </span>
            <IconButton icon="circle-x" variant="ghost" size="small" aria-label="Remove file" onClick={props.onClearFile} />
          </Show>
        </div>
      </Field>
    </div>
  )
}

// ── AI run (live conversation + jump-to-skill) ───────────────────────────
const RunPanel: Component<{
  run: RunState
  onClose: () => void
  onView: (name: string) => void
}> = (props) => {
  const running = () => props.run.status === "running"
  const done = () => props.run.status === "done"
  return (
    <div class="flex flex-col gap-4 p-5 max-w-4xl mx-auto">
      <div class="flex items-center gap-2 sticky top-0 -mx-5 -mt-5 px-5 py-3 bg-background-stronger border-b border-border-weaker-base z-10">
        <span class="text-16-medium flex items-center gap-2">
          {props.run.title}
          <Chip tone="macro">AI</Chip>
        </span>
        <div class="flex-1" />
        <Button variant="ghost" onClick={props.onClose}>
          {running() ? "Run in background" : "Close"}
        </Button>
      </div>

      {/* request bubble */}
      <div class="flex flex-col gap-1">
        <span class="text-11-medium text-text-weak">Your request</span>
        <div class="rounded-xl border border-border-weak-base bg-background-base px-4 py-3 text-13-regular leading-relaxed whitespace-pre-wrap">
          {props.run.request}
        </div>
      </div>

      {/* agent bubble */}
      <div class="flex flex-col gap-1">
        <span class="text-11-medium text-text-weak flex items-center gap-2">
          biomaster-skill-{props.run.kind}
          <Show when={running()}>
            <span
              class="inline-block size-3 rounded-full border-2 border-transparent animate-spin"
              style={{ "border-top-color": TONES.macro.dot, "border-right-color": TONES.macro.dot }}
            />
            <span style={{ color: TONES.macro.fg }}>working…</span>
          </Show>
        </span>
        <div
          class="rounded-xl border px-4 py-3 text-13-regular leading-relaxed"
          style={{ "border-color": TONES.macro.border, "background-color": TONES.macro.bg, color: TONES.macro.fg }}
        >
          <Show
            when={props.run.assistantText?.trim()}
            fallback={
              <span class="opacity-80">
                {running()
                  ? "Reading the material and drafting the skill… this usually takes 1–3 minutes."
                  : "(the agent produced no message)"}
              </span>
            }
          >
            <Markdown text={props.run.assistantText} class="text-13-regular leading-relaxed" />
          </Show>
        </div>
      </div>

      {/* result / jump */}
      <Show when={done()}>
        <Show
          when={props.run.newSkill}
          fallback={
            <div class="flex items-center gap-3 rounded-xl border border-border-weak-base bg-background-base px-4 py-3">
              <span class="text-13-regular text-text-weak flex-1">
                No new skill was created — the agent may have rejected the material as too thin. See its message above.
              </span>
              <Button variant="ghost" onClick={props.onClose}>
                Close
              </Button>
            </div>
          }
        >
          {(name) => (
            <div
              class="flex items-center gap-3 rounded-xl border px-4 py-3"
              style={{ "border-color": TONES.macro.border, "background-color": TONES.macro.bg }}
            >
              <span class="text-13-medium flex-1" style={{ color: TONES.macro.fg }}>
                Skill “{name()}” was created and added to the library.
              </span>
              <Button icon="arrow-right" onClick={() => props.onView(name())}>
                View skill
              </Button>
            </div>
          )}
        </Show>
      </Show>
    </div>
  )
}

// ── form ───────────────────────────────────────────────────────────────
const Field: Component<{ label: string; hint?: string; children: JSX.Element }> = (props) => (
  <label class="flex flex-col gap-1.5">
    <span class={labelClass}>{props.label}</span>
    {props.children}
    <Show when={props.hint}>
      <span class="text-11-regular text-text-weak">{props.hint}</span>
    </Show>
  </label>
)

const SkillForm: Component<{
  form: () => FormState
  busy: boolean
  domains: string[]
  onChange: (patch: Partial<FormState>) => void
  onCancel: () => void
  onSave: () => void
}> = (props) => {
  const f = props.form
  const stepCount = createMemo(() => splitSteps(f().micro)?.steps.length ?? 0)
  // Domain is a dropdown of existing workflow domains, with a "new domain"
  // escape hatch that reveals a free-text input.
  const [newDomain, setNewDomain] = createSignal(false)
  const domainKnown = () => props.domains.includes(f().domain)
  const domainCustom = () => newDomain() || (!!f().domain && !domainKnown())
  const domainSelectValue = () => (domainCustom() ? "__new__" : f().domain)
  return (
    <div class="flex flex-col gap-5 p-5 max-w-4xl mx-auto">
      <div class="flex items-center gap-2 sticky top-0 -mx-5 -mt-5 px-5 py-3 bg-background-stronger border-b border-border-weaker-base z-10">
        <span class="text-16-medium">{f().mode === "create" ? "New Skill" : `Edit: ${f().original}`}</span>
        <div class="flex-1" />
        <Button variant="ghost" onClick={props.onCancel} disabled={props.busy}>
          Cancel
        </Button>
        <Button icon="check" onClick={props.onSave} disabled={props.busy}>
          Save
        </Button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Field label="Name" hint="Lowercase slug, e.g. single-cell-clustering">
          <input
            class={inputClass}
            value={f().name}
            disabled={f().mode === "edit"}
            onInput={(e) => props.onChange({ name: e.currentTarget.value })}
          />
        </Field>
        <Field label="Domain" hint={domainCustom() ? "Type a new domain name" : "Pick an existing workflow domain, or add a new one"}>
          <div class="flex flex-col gap-2">
            <select
              class={inputClass}
              value={domainSelectValue()}
              onChange={(e) => {
                const v = e.currentTarget.value
                if (v === "__new__") {
                  setNewDomain(true)
                  props.onChange({ domain: "" })
                } else {
                  setNewDomain(false)
                  props.onChange({ domain: v })
                }
              }}
            >
              <option value="">Select a domain…</option>
              <For each={props.domains}>{(d) => <option value={d}>{d}</option>}</For>
              <option value="__new__">+ New domain…</option>
            </select>
            <Show when={domainCustom()}>
              <input
                class={inputClass}
                placeholder="e.g. spatial-transcriptomics"
                value={f().domain}
                onInput={(e) => props.onChange({ domain: e.currentTarget.value })}
              />
            </Show>
          </div>
        </Field>
      </div>

      <Field label="Description">
        <input
          class={inputClass}
          value={f().description}
          onInput={(e) => props.onChange({ description: e.currentTarget.value })}
        />
      </Field>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Field label="Primary tool">
          <input
            class={inputClass}
            value={f().primaryTool}
            onInput={(e) => props.onChange({ primaryTool: e.currentTarget.value })}
          />
        </Field>
        <Field label="Methods" hint="Comma-separated, e.g. scanpy, leiden, harmony">
          <input class={inputClass} value={f().methods} onInput={(e) => props.onChange({ methods: e.currentTarget.value })} />
        </Field>
      </div>

      {/* macro card */}
      <div class="rounded-xl border overflow-hidden" style={{ "border-color": TONES.macro.border }}>
        <div
          class="flex items-center gap-2 px-4 py-2.5 border-b"
          style={{ "background-color": TONES.macro.bg, "border-color": TONES.macro.border }}
        >
          <span class="size-2.5 rounded-full" style={{ "background-color": TONES.macro.dot }} />
          <span class="text-14-medium" style={{ color: TONES.macro.fg }}>
            Macro · description layer (for plan)
          </span>
        </div>
        <div class="flex flex-col gap-3 p-4 bg-background-base">
          <Field label="Macro tags" hint="Comma-separated; summarize purpose/scope for plan retrieval">
            <input
              class={inputClass}
              value={f().macroTags}
              onInput={(e) => props.onChange({ macroTags: e.currentTarget.value })}
            />
          </Field>
          <Field label="Macro content (macro.md)">
            <textarea
              class={inputClass + " min-h-40 font-mono text-13-regular leading-relaxed resize-y"}
              value={f().macro}
              onInput={(e) => props.onChange({ macro: e.currentTarget.value })}
            />
          </Field>
        </div>
      </div>

      {/* micro card */}
      <div class="rounded-xl border overflow-hidden" style={{ "border-color": TONES.micro.border }}>
        <div
          class="flex items-center gap-2 px-4 py-2.5 border-b"
          style={{ "background-color": TONES.micro.bg, "border-color": TONES.micro.border }}
        >
          <span class="size-2.5 rounded-full" style={{ "background-color": TONES.micro.dot }} />
          <span class="text-14-medium" style={{ color: TONES.micro.fg }}>
            Micro · execution layer (for execute / debug)
          </span>
          <div class="flex-1" />
          <Show when={stepCount() > 0}>
            <span class="text-11-medium" style={{ color: TONES.micro.fg }}>
              {stepCount()} steps detected
            </span>
          </Show>
        </div>
        <div class="flex flex-col gap-3 p-4 bg-background-base">
          <Field label="Micro tags" hint="Comma-separated; execution detail/tools/params for execute/debug retrieval">
            <input
              class={inputClass}
              value={f().microTags}
              onInput={(e) => props.onChange({ microTags: e.currentTarget.value })}
            />
          </Field>
          <Field label="Source">
            <input class={inputClass} value={f().source} onInput={(e) => props.onChange({ source: e.currentTarget.value })} />
          </Field>
          <Field
            label="Micro content (micro.md)"
            hint="Use markdown headings (## Step name) to split into collapsible steps, e.g. ## Preprocessing / ## Clustering / ## Annotation"
          >
            <textarea
              class={inputClass + " min-h-48 font-mono text-13-regular leading-relaxed resize-y"}
              value={f().micro}
              onInput={(e) => props.onChange({ micro: e.currentTarget.value })}
            />
          </Field>
        </div>
      </div>
    </div>
  )
}

export default SkillsPage
