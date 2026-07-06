import { sentryVitePlugin } from "@sentry/vite-plugin"
import { defineConfig } from "vite"
import desktopPlugin from "./vite"

const backendProxyTarget =
  process.env.VITE_OPENCODE_BACKEND_PROXY_TARGET ??
  `http://127.0.0.1:${process.env.VITE_OPENCODE_SERVER_PORT ?? process.env.BACKEND_PORT ?? "4096"}`

const apiProxy = {
  target: backendProxyTarget,
  changeOrigin: true,
  ws: true,
}

const proxyPrefixes = [
  "/agent",
  "/bioskills",
  "/command",
  "/config",
  "/event",
  "/file",
  "/formatter",
  "/global",
  "/instance",
  "/lsp",
  "/mcp",
  "/path",
  "/permission",
  "/project",
  "/provider",
  "/pty",
  "/question",
  "/session",
  "/skill",
  "/sync",
  "/tui",
  "/vcs",
  "/experimental",
] as const

const sentry =
  process.env.SENTRY_AUTH_TOKEN && process.env.SENTRY_ORG && process.env.SENTRY_PROJECT
    ? sentryVitePlugin({
        authToken: process.env.SENTRY_AUTH_TOKEN,
        org: process.env.SENTRY_ORG,
        project: process.env.SENTRY_PROJECT,
        telemetry: false,
        release: {
          name: process.env.SENTRY_RELEASE ?? process.env.VITE_SENTRY_RELEASE,
        },
        sourcemaps: {
          assets: "./dist/**",
          filesToDeleteAfterUpload: "./dist/**/*.map",
        },
      })
    : false

export default defineConfig({
  plugins: [desktopPlugin, sentry] as any,
  server: {
    host: "0.0.0.0",
    allowedHosts: true,
    port: 3000,
    proxy: Object.fromEntries(proxyPrefixes.map((prefix) => [prefix, apiProxy])),
  },
  build: {
    target: "esnext",
    sourcemap: true,
  },
})
