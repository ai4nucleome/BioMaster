// @refresh reload

import * as Sentry from "@sentry/solid"
import { render } from "solid-js/web"
import { AppBaseProviders, AppInterface } from "@/app"
import { type Platform, PlatformProvider } from "@/context/platform"
import { dict as en } from "@/i18n/en"
import { dict as zh } from "@/i18n/zh"
import { handleNotificationClick } from "@/utils/notification-click"
import { authFromToken } from "@/utils/server"
import pkg from "../package.json"
import { ServerConnection } from "./context/server"

const DEFAULT_SERVER_URL_KEY = "opencode.settings.dat:defaultServerUrl"

const getLocale = () => {
  if (typeof navigator !== "object") return "en" as const
  const languages = navigator.languages?.length ? navigator.languages : [navigator.language]
  for (const language of languages) {
    if (!language) continue
    if (language.toLowerCase().startsWith("zh")) return "zh" as const
  }
  return "en" as const
}

const getRootNotFoundError = () => {
  const key = "error.dev.rootNotFound" as const
  const locale = getLocale()
  return locale === "zh" ? (zh[key] ?? en[key]) : en[key]
}

const getStorage = (key: string) => {
  if (typeof localStorage === "undefined") return null
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

const setStorage = (key: string, value: string | null) => {
  if (typeof localStorage === "undefined") return
  try {
    if (value !== null) {
      localStorage.setItem(key, value)
      return
    }
    localStorage.removeItem(key)
  } catch {
    return
  }
}

const removeStorage = (key: string) => {
  if (typeof localStorage === "undefined") return
  try {
    localStorage.removeItem(key)
  } catch {
    return
  }
}

const browserReachableServerUrl = (url: string | null) => {
  if (!url) return url
  try {
    const parsed = new URL(url)
    if (parsed.hostname !== "0.0.0.0") return url
    parsed.hostname = location.hostname || "localhost"
    return parsed.toString().replace(/\/+$/, "")
  } catch {
    return url.replace("://0.0.0.0:", `://${location.hostname || "localhost"}:`)
  }
}

const isSinglePortMode = () => import.meta.env.VITE_OPENCODE_SINGLE_PORT === "1"
const biomasterProjectPath = () => import.meta.env.VITE_BIOMASTER_PROJECT_PATH

const singlePortServerUrl = () => {
  const frontendPort = import.meta.env.VITE_OPENCODE_FRONTEND_PORT
  if (!frontendPort) return location.origin
  const protocol = location.protocol || "http:"
  const hostname = location.hostname || import.meta.env.VITE_OPENCODE_SERVER_HOST || "127.0.0.1"
  return `${protocol}//${hostname}:${frontendPort}`
}
const readDefaultServerUrl = () => {
  if (isSinglePortMode()) return singlePortServerUrl()
  return browserReachableServerUrl(getStorage(DEFAULT_SERVER_URL_KEY))
}
const writeDefaultServerUrl = (url: string | null) => {
  setStorage(DEFAULT_SERVER_URL_KEY, isSinglePortMode() ? singlePortServerUrl() : url)
}

const isStaleSinglePortServerUrl = (value: string) => {
  try {
    const parsed = new URL(value)
    const hostname = parsed.hostname
    const backendPort = import.meta.env.VITE_OPENCODE_SERVER_PORT || "4096"
    return (
      (hostname === "127.0.0.1" || hostname === "localhost" || hostname === location.hostname) &&
      parsed.port === backendPort
    )
  } catch {
    const backendPort = import.meta.env.VITE_OPENCODE_SERVER_PORT || "4096"
    return new RegExp(`https?://(127\\.0\\.0\\.1|localhost)(:${backendPort})(/|$)`).test(value)
  }
}

const clearStaleSinglePortServers = () => {
  const key = "opencode.global.dat:server"
  const raw = getStorage(key)
  if (!raw) return
  try {
    const parsed = JSON.parse(raw) as {
      list?: unknown[]
      projects?: Record<string, unknown>
      lastProject?: Record<string, unknown>
    }
    if (Array.isArray(parsed.list)) {
      parsed.list = parsed.list.filter((item) => {
        const url =
          typeof item === "string"
            ? item
            : item && typeof item === "object" && "http" in item && item.http && typeof item.http === "object" && "url" in item.http
              ? String(item.http.url)
              : item && typeof item === "object" && "url" in item
                ? String(item.url)
                : ""
        return !url || !isStaleSinglePortServerUrl(url)
      })
    }
    for (const section of [parsed.projects, parsed.lastProject]) {
      if (!section || typeof section !== "object") continue
      for (const storedKey of Object.keys(section)) {
        if (isStaleSinglePortServerUrl(storedKey)) delete section[storedKey]
      }
    }
    setStorage(key, JSON.stringify(parsed))
  } catch {
    removeStorage(key)
  }
}

const decodePathSegment = (value: string) => {
  try {
    const padded = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(value.length / 4) * 4, "=")
    return atob(padded)
  } catch {
    return ""
  }
}

const clearStaleBioMasterState = () => {
  if (!isSinglePortMode() || typeof localStorage === "undefined") return
  const current = biomasterProjectPath()
  const stale = ["biomaster-skill-v0.3", "biomaster2-main", "biomaster-skill-v0.5-deploy-test"]
  try {
    for (let index = localStorage.length - 1; index >= 0; index--) {
      const key = localStorage.key(index)
      if (!key) continue
      const value = localStorage.getItem(key) ?? ""
      const text = `${key}\n${value}`
      const staleBioMaster = stale.some((item) => text.includes(item))
      const currentProject = current ? text.includes(current) : false
      if (staleBioMaster && !currentProject) localStorage.removeItem(key)
    }
  } catch {
    return
  }

  writeDefaultServerUrl(singlePortServerUrl())
  clearStaleSinglePortServers()

  const first = location.pathname.split("/").filter(Boolean)[0]
  const decoded = first ? decodePathSegment(first) : ""
  if (decoded && stale.some((item) => decoded.includes(item)) && (!current || decoded !== current)) {
    history.replaceState(null, "", location.search ? `/${location.search}` : "/")
  }
}

const notify: Platform["notify"] = async (title, description, href) => {
  if (!("Notification" in window)) return

  const permission =
    Notification.permission === "default"
      ? await Notification.requestPermission().catch(() => "denied")
      : Notification.permission

  if (permission !== "granted") return

  const inView = document.visibilityState === "visible" && document.hasFocus()
  if (inView) return

  const notification = new Notification(title, {
    body: description ?? "",
    icon: "https://opencode.ai/favicon-96x96-v3.png",
  })

  notification.onclick = () => {
    handleNotificationClick(href)
    notification.close()
  }
}

const openLink: Platform["openLink"] = (url) => {
  window.open(url, "_blank")
}

const back: Platform["back"] = () => {
  window.history.back()
}

const forward: Platform["forward"] = () => {
  window.history.forward()
}

const restart: Platform["restart"] = async () => {
  window.location.reload()
}

const root = document.getElementById("root")
if (!(root instanceof HTMLElement) && import.meta.env.DEV) {
  throw new Error(getRootNotFoundError())
}
clearStaleBioMasterState()

const getCurrentUrl = () => {
  if (location.hostname.includes("opencode.ai")) return "http://localhost:4096"
  if (isSinglePortMode()) return location.origin
  const envHost = import.meta.env.VITE_OPENCODE_SERVER_HOST
  const envPort = import.meta.env.VITE_OPENCODE_SERVER_PORT
  const browserReachableHost = envHost === "0.0.0.0" ? location.hostname || "localhost" : envHost
  if (import.meta.env.DEV) return `http://${browserReachableHost ?? "localhost"}:${envPort ?? "4096"}`
  // Production static builds are served from a plain file server (e.g. our
  // static-serve.ts on 4444), which is NOT the opencode backend. When the API
  // host/port is provided at build time, point the SDK there instead of
  // `location.origin` (which would return index.html for every API call).
  if (envHost || envPort) return `http://${browserReachableHost ?? "localhost"}:${envPort ?? "4096"}`
  return location.origin
}

const getDefaultUrl = () => {
  if (isSinglePortMode()) return getCurrentUrl()
  const lsDefault = readDefaultServerUrl()
  if (lsDefault) return lsDefault
  return getCurrentUrl()
}

const clearAuthToken = () => {
  const params = new URLSearchParams(location.search)
  if (!params.has("auth_token")) return
  params.delete("auth_token")
  history.replaceState(null, "", location.pathname + (params.size ? `?${params}` : "") + location.hash)
}

const platform: Platform = {
  platform: "web",
  version: pkg.version,
  openLink,
  back,
  forward,
  restart,
  notify,
  getDefaultServer: async () => {
    const stored = readDefaultServerUrl()
    return stored ? ServerConnection.Key.make(stored) : null
  },
  setDefaultServer: writeDefaultServerUrl,
}

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_SENTRY_ENVIRONMENT ?? import.meta.env.MODE,
    release: import.meta.env.VITE_SENTRY_RELEASE ?? `web@${pkg.version}`,
    initialScope: {
      tags: {
        platform: "web",
      },
    },
    integrations: (integrations) => {
      return integrations.filter(
        (i) =>
          i.name !== "Breadcrumbs" && !(import.meta.env.OPENCODE_CHANNEL === "prod" && i.name === "GlobalHandlers"),
      )
    },
  })
}

if (root instanceof HTMLElement) {
  const auth = authFromToken(new URLSearchParams(location.search).get("auth_token"))
  clearAuthToken()
  const server: ServerConnection.Http = {
    type: "http",
    authToken: !!auth,
    http: {
      url: getCurrentUrl(),
      ...auth,
    },
  }
  render(
    () => (
      <PlatformProvider value={platform}>
        <AppBaseProviders>
          <AppInterface
            defaultServer={ServerConnection.Key.make(getDefaultUrl())}
            canonicalLocalServer={ServerConnection.key(server)}
            servers={[server]}
            disableHealthCheck
          />
        </AppBaseProviders>
      </PlatformProvider>
    ),
    root,
  )
}
