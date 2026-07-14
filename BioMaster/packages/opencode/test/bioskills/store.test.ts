import { Database } from "bun:sqlite"
import { expect, test } from "bun:test"
import fs from "node:fs"
import path from "node:path"
import * as Store from "../../src/bioskills/store"
import { tmpdir } from "../fixture/fixture"

test("whole-skill toggle remains visible to management and immediately updates knowledge sqlite", async () => {
  await using tmp = await tmpdir()
  const skill = Store.create(tmp.path, {
    name: "exec-toggle-test",
    description: "Toggle integration test",
    enabled: true,
    steps: [{ id: "run", title: "Run", tags: ["test"] }],
    macro: "## Run\nDescription",
    micro: "## Run\nCommand",
  })

  const knowledgeDir = path.join(tmp.path, ".opencode", "knowledge")
  fs.mkdirSync(knowledgeDir, { recursive: true })
  const knowledge = new Database(path.join(knowledgeDir, "biomaster_skills.db"))
  knowledge.run(
    "CREATE TABLE skills (skill_id TEXT PRIMARY KEY, enabled INTEGER NOT NULL, updated_at TEXT)",
  )
  knowledge.run("INSERT INTO skills (skill_id, enabled) VALUES (?, 1)", [skill.name])
  knowledge.close()

  Store.update(tmp.path, skill.name, { name: skill.name, enabled: false })
  expect(Store.list(tmp.path).find((item) => item.name === skill.name)?.enabled).toBe(false)
  expect(Store.list(tmp.path, { enabledOnly: true }).some((item) => item.name === skill.name)).toBe(false)

  const mutedDb = new Database(path.join(knowledgeDir, "biomaster_skills.db"), { readonly: true })
  expect((mutedDb.query("SELECT enabled FROM skills WHERE skill_id = ?").get(skill.name) as { enabled: number }).enabled).toBe(0)
  mutedDb.close()

  Store.update(tmp.path, skill.name, { name: skill.name, enabled: true })
  expect(Store.list(tmp.path, { enabledOnly: true }).some((item) => item.name === skill.name)).toBe(true)
  const activeDb = new Database(path.join(knowledgeDir, "biomaster_skills.db"), { readonly: true })
  expect((activeDb.query("SELECT enabled FROM skills WHERE skill_id = ?").get(skill.name) as { enabled: number }).enabled).toBe(1)
  activeDb.close()
})
