import type { ServerConnection } from "@/context/server"
import { authTokenFromCredentials } from "@/utils/server"

export interface SkillStep {
  id: string
  title: string
  tags: string[]
  enabled: boolean
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
  enabled: boolean
  custom: boolean
  steps: SkillStep[]
  macro?: string
  micro?: string
}

export interface BioSkillInput {
  name?: string
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

export type SkillLayer = "macro" | "micro" | "all"

export interface ListOptions {
  q?: string
  tag?: string
  layer?: SkillLayer
}

// Thin fetch client for the opencode backend /bioskills routes. These routes are
// plain HttpRouter endpoints (not part of the generated SDK), so we call them
// directly, reusing the server's base URL and optional Basic auth.
export function createBioskillsClient(
  server: ServerConnection.HttpBase,
  directory: string,
  platformFetch?: typeof fetch,
) {
  const doFetch = platformFetch ?? fetch
  const base = server.url.replace(/\/+$/, "")
  const headers: Record<string, string> = { "content-type": "application/json" }
  if (server.password) {
    headers.Authorization = `Basic ${authTokenFromCredentials({ username: server.username, password: server.password })}`
  }

  function query(extra: Record<string, string | undefined> = {}): string {
    const params = new URLSearchParams()
    params.set("directory", directory)
    for (const [key, value] of Object.entries(extra)) {
      if (value !== undefined && value !== "") params.set(key, value)
    }
    return params.toString()
  }

  async function request<T>(
    method: string,
    path: string,
    opts: { params?: Record<string, string | undefined>; body?: unknown } = {},
  ): Promise<T> {
    const res = await doFetch(`${base}${path}?${query(opts.params)}`, {
      method,
      headers,
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    })
    const text = await res.text()
    const json = text ? JSON.parse(text) : {}
    if (!res.ok) throw new Error(json?.error || `${res.status} ${res.statusText}`)
    return json as T
  }

  return {
    async list(opts: ListOptions = {}): Promise<BioSkill[]> {
      const result = await request<{ skills: BioSkill[] }>("GET", "/bioskills", {
        params: { q: opts.q, tag: opts.tag, layer: opts.layer },
      })
      return result.skills ?? []
    },
    get(name: string, layer?: SkillLayer): Promise<BioSkill> {
      return request<BioSkill>("GET", `/bioskills/${encodeURIComponent(name)}`, {
        params: { layer },
      })
    },
    create(input: BioSkillInput): Promise<BioSkill> {
      return request<BioSkill>("POST", "/bioskills", { body: input })
    },
    update(name: string, input: BioSkillInput): Promise<BioSkill> {
      return request<BioSkill>("PATCH", `/bioskills/${encodeURIComponent(name)}`, { body: input })
    },
    setEnabled(name: string, enabled: boolean): Promise<BioSkill> {
      return request<BioSkill>("PATCH", `/bioskills/${encodeURIComponent(name)}`, { body: { enabled } })
    },
    setSteps(name: string, steps: SkillStep[]): Promise<BioSkill> {
      return request<BioSkill>("PATCH", `/bioskills/${encodeURIComponent(name)}`, { body: { steps } })
    },
    remove(name: string): Promise<{ ok: boolean }> {
      return request<{ ok: boolean }>("DELETE", `/bioskills/${encodeURIComponent(name)}`)
    },
    reindex(): Promise<{ ok: boolean; count: number }> {
      return request<{ ok: boolean; count: number }>("POST", "/bioskills/reindex")
    },
    // Extract plain text from an uploaded file (PDF via pdftotext, else UTF-8).
    ingest(
      filename: string,
      contentBase64: string,
    ): Promise<{ filename: string; chars: number; truncated: boolean; text: string }> {
      return request("POST", "/bioskills/ingest", { body: { filename, contentBase64 } })
    },
  }
}

export type BioskillsClient = ReturnType<typeof createBioskillsClient>
