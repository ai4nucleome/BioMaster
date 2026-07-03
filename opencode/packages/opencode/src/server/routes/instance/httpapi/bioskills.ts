import { Effect, Schema } from "effect"
import { HttpRouter, HttpServerRequest, HttpServerResponse } from "effect/unstable/http"
import { execFileSync } from "node:child_process"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import * as Store from "@/bioskills/store"

// BioSkills management routes. These are plain HttpRouter routes (like the /doc
// and UI fallback routes) instead of typed HttpApi endpoints, so the frontend
// can call them through a thin fetch wrapper without regenerating the SDK.

const InputSchema = Schema.Struct({
  name: Schema.optional(Schema.String),
  description: Schema.optional(Schema.String),
  domain: Schema.optional(Schema.String),
  primaryTool: Schema.optional(Schema.String),
  methods: Schema.optional(Schema.Array(Schema.String)),
  macroTags: Schema.optional(Schema.Array(Schema.String)),
  microTags: Schema.optional(Schema.Array(Schema.String)),
  source: Schema.optional(Schema.String),
  status: Schema.optional(Schema.String),
  enabled: Schema.optional(Schema.Boolean),
  custom: Schema.optional(Schema.Boolean),
  steps: Schema.optional(
    Schema.Array(
      Schema.Struct({
        id: Schema.optional(Schema.String),
        title: Schema.optional(Schema.String),
        tags: Schema.optional(Schema.Array(Schema.String)),
        enabled: Schema.optional(Schema.Boolean),
      }),
    ),
  ),
  macro: Schema.optional(Schema.String),
  micro: Schema.optional(Schema.String),
})

// Body for POST /bioskills/ingest: a base64-encoded uploaded file. Used by the
// "New Skill → From a paper/URL/repo" flow to turn an uploaded document (PDF or
// text) into plain text the skill-creator agent can consume.
const IngestSchema = Schema.Struct({
  filename: Schema.optional(Schema.String),
  contentBase64: Schema.String,
  maxChars: Schema.optional(Schema.Number),
})

// Extract plain text from an uploaded file buffer. PDFs are run through
// `pdftotext` (poppler); everything else is decoded as UTF-8 text.
function extractText(filename: string, buffer: Buffer): string {
  const ext = path.extname(filename).toLowerCase()
  if (ext === ".pdf") {
    const tmp = path.join(os.tmpdir(), `bioskill-ingest-${Date.now()}-${Math.random().toString(36).slice(2)}.pdf`)
    try {
      fs.writeFileSync(tmp, buffer)
      // `pdftotext <in> -` writes extracted text to stdout.
      const out = execFileSync("pdftotext", ["-q", "-enc", "UTF-8", tmp, "-"], {
        maxBuffer: 64 * 1024 * 1024,
      })
      return out.toString("utf-8")
    } catch (error) {
      throw new Store.BioSkillError(
        `Could not extract text from PDF (${filename}). Is pdftotext installed? ${
          error instanceof Error ? error.message : String(error)
        }`,
        422,
      )
    } finally {
      try {
        fs.rmSync(tmp)
      } catch {
        // already gone
      }
    }
  }
  return buffer.toString("utf-8")
}

function directoryOf(request: HttpServerRequest.HttpServerRequest): string {
  const url = new URL(request.url, "http://localhost")
  return url.searchParams.get("directory") || request.headers["x-opencode-directory"] || process.cwd()
}

function jsonError(error: unknown) {
  const status = error instanceof Store.BioSkillError ? error.status : 500
  const message = error instanceof Error ? error.message : String(error)
  return HttpServerResponse.jsonUnsafe({ error: message }, { status })
}

function respond<T>(fn: () => T) {
  return Effect.try({ try: fn, catch: (error) => error }).pipe(
    Effect.match({
      onFailure: jsonError,
      onSuccess: (value) => HttpServerResponse.jsonUnsafe(value),
    }),
  )
}

function toLayer(value: string | null | undefined): Store.SkillLayer {
  return value === "macro" || value === "micro" ? value : "all"
}

const listHandler = Effect.gen(function* () {
  const request = yield* HttpServerRequest.HttpServerRequest
  const directory = directoryOf(request)
  const url = new URL(request.url, "http://localhost")
  const q = url.searchParams.get("q") ?? undefined
  const tag = url.searchParams.get("tag") ?? undefined
  const layer = toLayer(url.searchParams.get("layer"))
  const enabledOnly = url.searchParams.get("enabledOnly") === "1"
  return yield* respond(() => ({ skills: Store.list(directory, { q, tag, layer, enabledOnly }) }))
})

const getHandler = Effect.gen(function* () {
  const request = yield* HttpServerRequest.HttpServerRequest
  const route = yield* HttpRouter.RouteContext
  const directory = directoryOf(request)
  const url = new URL(request.url, "http://localhost")
  const layer = toLayer(url.searchParams.get("layer"))
  const name = decodeURIComponent(route.params.name ?? "")
  return yield* respond(() => {
    const skill = Store.get(directory, name, layer)
    if (!skill) throw new Store.BioSkillError(`Skill not found: ${name}`, 404)
    return skill
  })
})

const createHandler = Effect.gen(function* () {
  const request = yield* HttpServerRequest.HttpServerRequest
  const directory = directoryOf(request)
  const body = yield* HttpServerRequest.schemaBodyJson(InputSchema).pipe(
    Effect.match({ onFailure: () => null, onSuccess: (value) => value }),
  )
  if (!body) return HttpServerResponse.jsonUnsafe({ error: "Invalid JSON body" }, { status: 400 })
  return yield* respond(() => Store.create(directory, body as Store.BioSkillInput))
})

const updateHandler = Effect.gen(function* () {
  const request = yield* HttpServerRequest.HttpServerRequest
  const route = yield* HttpRouter.RouteContext
  const directory = directoryOf(request)
  const name = decodeURIComponent(route.params.name ?? "")
  const body = yield* HttpServerRequest.schemaBodyJson(InputSchema).pipe(
    Effect.match({ onFailure: () => null, onSuccess: (value) => value }),
  )
  if (!body) return HttpServerResponse.jsonUnsafe({ error: "Invalid JSON body" }, { status: 400 })
  return yield* respond(() => Store.update(directory, name, body as Store.BioSkillInput))
})

const deleteHandler = Effect.gen(function* () {
  const request = yield* HttpServerRequest.HttpServerRequest
  const route = yield* HttpRouter.RouteContext
  const directory = directoryOf(request)
  const name = decodeURIComponent(route.params.name ?? "")
  return yield* respond(() => {
    Store.remove(directory, name)
    return { ok: true, name }
  })
})

const reindexHandler = Effect.gen(function* () {
  const request = yield* HttpServerRequest.HttpServerRequest
  const directory = directoryOf(request)
  return yield* respond(() => ({ ok: true, count: Store.reindex(directory) }))
})

const ingestHandler = Effect.gen(function* () {
  const body = yield* HttpServerRequest.schemaBodyJson(IngestSchema).pipe(
    Effect.match({ onFailure: () => null, onSuccess: (value) => value }),
  )
  if (!body) return HttpServerResponse.jsonUnsafe({ error: "Invalid JSON body" }, { status: 400 })
  return yield* respond(() => {
    const filename = body.filename || "upload"
    const buffer = Buffer.from(body.contentBase64, "base64")
    const full = extractText(filename, buffer)
    const max = body.maxChars ?? 40000
    const text = full.length > max ? full.slice(0, max) + "\n\n... [truncated]" : full
    return { filename, chars: full.length, truncated: full.length > max, text }
  })
})

export const bioskillsRoutes = HttpRouter.use((router) =>
  Effect.gen(function* () {
    yield* router.add("GET", "/bioskills", listHandler)
    yield* router.add("POST", "/bioskills", createHandler)
    yield* router.add("POST", "/bioskills/reindex", reindexHandler)
    yield* router.add("POST", "/bioskills/ingest", ingestHandler)
    yield* router.add("GET", "/bioskills/:name", getHandler)
    yield* router.add("PATCH", "/bioskills/:name", updateHandler)
    yield* router.add("DELETE", "/bioskills/:name", deleteHandler)
  }),
)
