#!/usr/bin/env bun
/**
 * Minimal static file server for the built app (dist/).
 *
 * This avoids running `vite dev`/`vite preview`, which set up recursive file
 * watchers that exhaust the system inotify limit on shared hosts. It serves the
 * production build with SPA fallback (any unknown path -> index.html), so the
 * BioSkills panel at /:dir/skills and all other client routes work.
 *
 * Usage: bun run static-serve.ts [port] [host]
 * Rebuild first with: bun --bun run build
 */
import { existsSync, statSync } from "node:fs"
import path from "node:path"

const DIST = path.resolve(import.meta.dir, "dist")
const PORT = Number(process.argv[2] ?? 4444)
const HOST = process.argv[3] ?? "127.0.0.1"

if (!existsSync(path.join(DIST, "index.html"))) {
  console.error(`dist/index.html not found in ${DIST}. Run: bun --bun run build`)
  process.exit(1)
}

function resolveFile(pathname: string): string {
  const clean = decodeURIComponent(pathname.split("?")[0]).replace(/^\/+/, "")
  const candidate = path.join(DIST, clean)
  if (candidate.startsWith(DIST) && clean && existsSync(candidate) && statSync(candidate).isFile()) {
    return candidate
  }
  return path.join(DIST, "index.html")
}

Bun.serve({
  port: PORT,
  hostname: HOST,
  async fetch(req) {
    const url = new URL(req.url)
    const file = Bun.file(resolveFile(url.pathname))
    return new Response(file, {
      headers: { "cache-control": url.pathname.startsWith("/assets/") ? "max-age=31536000" : "no-cache" },
    })
  },
})

console.log(`BioSkills frontend (static build) serving on http://${HOST}:${PORT}`)
