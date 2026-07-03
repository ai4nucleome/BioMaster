.PHONY: build validate index access examples test knowledge-db knowledge-sync knowledge-seed knowledge-test clean bootstrap pytest compliance skill-add

PYTHONPATH := .opencode/runtime
PYTHON := PYTHONPATH=$(PYTHONPATH) python3

bootstrap:
	$(PYTHON) .opencode/runtime/biomaster/scripts/bootstrap_mvp.py

clean:
	rm -rf examples/results/*
	touch examples/results/.gitkeep
	rm -f CHECK_REPORT.yaml
	rm -rf runs/[0-9][0-9][0-9]
	rm -f .opencode/knowledge/biomaster_skills.db

pytest:
	$(PYTHON) -m pytest tests/ -q

build: bootstrap index

validate:
	$(PYTHON) .opencode/runtime/biomaster/skills/validate_skills.py --mvp

index:
	$(PYTHON) .opencode/runtime/biomaster/skills/build_skill_index.py

access:
	$(PYTHON) -m biomaster.skills.manager --show-access

skill-add:
	$(PYTHON) -m biomaster.skills.add_skill $(ARGS)

compliance:
	$(PYTHON) -c "from biomaster.compliance.plan_audit import audit_plan_compliance; errs=audit_plan_compliance(); print('OK' if not errs else '\n'.join(errs)); raise SystemExit(1 if errs else 0)"

examples:
	$(PYTHON) examples/run_smoke_tests.py

knowledge-db:
	$(PYTHON) .opencode/runtime/biomaster/knowledge/init_db.py

knowledge-sync: knowledge-db
	$(PYTHON) .opencode/runtime/biomaster/knowledge/sync_all.py

knowledge-seed: knowledge-sync
	$(PYTHON) .opencode/runtime/biomaster/knowledge/seed_routes.py

knowledge-test:
	$(PYTHON) examples/run_knowledge_tests.py

test: bootstrap validate index knowledge-seed examples knowledge-test pytest
	$(PYTHON) -m biomaster.skills.manager --summary
