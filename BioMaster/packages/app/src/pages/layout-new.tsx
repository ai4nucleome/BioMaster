import { createEffect, Suspense, type ParentProps } from "solid-js"
import { useNavigate } from "@solidjs/router"
import { base64Encode } from "@opencode-ai/core/util/encode"
import { DebugBar } from "@/components/debug-bar"
import { HelpButton } from "@/components/help-button"
import { Titlebar, type TitlebarUpdate } from "@/components/titlebar"
import { usePlatform } from "@/context/platform"
import { setNavigate } from "@/utils/notification-click"
import { setV2Toast, ToastRegion } from "@/utils/toast"

export default function NewLayout(props: ParentProps) {
  const platform = usePlatform()
  const navigate = useNavigate()
  const biomasterRoot = () => import.meta.env.VITE_BIOMASTER_PROJECT_PATH
  setNavigate(navigate)

  createEffect(() => setV2Toast(true))

  const update: TitlebarUpdate = {
    version: () => {
      const state = platform.updater?.state()
      if (state?.status !== "ready") return
      return state.version
    },
    installing: () => platform.updater?.state().status === "installing",
    install: () => void platform.updater?.install(),
  }

  return (
    <div
      class="relative bg-v2-background-bg-deep flex-1 min-h-0 min-w-0 flex flex-col select-none [&_input]:select-text [&_textarea]:select-text [&_[contenteditable]]:select-text"
      style={{
        "padding-top": "env(safe-area-inset-top, 0px)",
        "padding-bottom": "env(safe-area-inset-bottom, 0px)",
      }}
    >
      <Titlebar update={update} />
      <main class="flex-1 min-h-0 min-w-0 overflow-x-hidden flex flex-col items-start contain-strict">
        <Suspense>{props.children}</Suspense>
      </main>
      {import.meta.env.DEV && <DebugBar inline />}
      <button
        type="button"
        title="BioSkills"
        aria-label="Open BioSkills"
        class="fixed bottom-4 left-4 z-50 flex h-8 items-center gap-2 rounded-full bg-background-base px-3 text-12-medium text-text-base shadow-[var(--shadow-lg-border-base)] hover:text-text-strong transition-colors"
        onClick={() => {
          const root = biomasterRoot()
          if (!root) return
          navigate(`/${base64Encode(root)}/skills`)
        }}
      >
        <span class="flex size-4 items-center justify-center rounded bg-v2-blue-500 text-[10px] font-semibold text-white">
          B
        </span>
        <span>BioSkills</span>
      </button>
      <HelpButton />
      <ToastRegion v2 />
    </div>
  )
}
