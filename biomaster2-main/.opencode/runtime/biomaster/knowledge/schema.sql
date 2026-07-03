CREATE TABLE IF NOT EXISTS skills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  skill_id TEXT UNIQUE NOT NULL,
  path TEXT NOT NULL,

  layer TEXT NOT NULL,
  domain TEXT,
  discipline TEXT,
  pipeline TEXT,
  tool TEXT,

  description TEXT NOT NULL,
  tags TEXT,

  allowed_agents TEXT,
  insertion_mode TEXT DEFAULT 'full',

  enabled INTEGER DEFAULT 1,
  priority INTEGER DEFAULT 0,

  io_contract TEXT,
  env_contract TEXT,
  extra_json TEXT,

  content_hash TEXT,
  body TEXT,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pipeline_routes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  route_id TEXT UNIQUE NOT NULL,

  domain TEXT NOT NULL,
  discipline TEXT NOT NULL,
  pipeline TEXT NOT NULL,

  title TEXT NOT NULL,
  description TEXT,

  preview_steps TEXT NOT NULL,
  required_skill_ids TEXT,
  optional_skill_ids TEXT,

  demo_dataset TEXT,
  trigger_keywords TEXT,

  enabled INTEGER DEFAULT 1,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS run_states (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT UNIQUE NOT NULL,

  phase TEXT NOT NULL,
  mode TEXT,

  domain TEXT,
  discipline TEXT,
  pipeline TEXT,
  selected_route_id TEXT,

  selected_skill_ids TEXT,
  disabled_skill_ids TEXT,

  state_json TEXT,

  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skill_selection_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT,
  agent_name TEXT,
  phase TEXT,
  user_request TEXT,

  candidate_skill_ids TEXT,
  selected_skill_ids TEXT,
  rejected_skill_ids TEXT,

  reason TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skills_layer ON skills(layer);
CREATE INDEX IF NOT EXISTS idx_skills_enabled ON skills(enabled);

CREATE TABLE IF NOT EXISTS knowledge_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  record_id TEXT UNIQUE NOT NULL,
  record_type TEXT NOT NULL,

  path TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT,

  keywords TEXT,
  analysis_type TEXT,
  tool TEXT,
  domain TEXT,
  discipline TEXT,

  canonical_skill_id TEXT,
  allowed_agents TEXT,

  origin_source TEXT,
  origin_page TEXT,
  source_entry_index INTEGER,
  source_subindex INTEGER,
  source_file TEXT,

  enabled INTEGER DEFAULT 1,
  content_hash TEXT,
  content TEXT,
  extra_json TEXT,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_records_type ON knowledge_records(record_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_records_analysis ON knowledge_records(analysis_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_records_tool ON knowledge_records(tool);
CREATE INDEX IF NOT EXISTS idx_knowledge_records_enabled ON knowledge_records(enabled);
CREATE INDEX IF NOT EXISTS idx_pipeline_routes_domain ON pipeline_routes(domain, discipline, pipeline);
CREATE INDEX IF NOT EXISTS idx_run_states_phase ON run_states(phase);
CREATE INDEX IF NOT EXISTS idx_skill_selection_logs_run ON skill_selection_logs(run_id);
