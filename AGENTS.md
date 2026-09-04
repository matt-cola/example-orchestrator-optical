# AGENTS.md — Example Optical Orchestrator (harness for the orchestrator-optical module)

## What this project is

An example [Workflow Orchestrator](https://workfloworchestrator.org) deployment that consumes the
[`orchestrator-optical`](https://github.com/workfloworchestrator/orchestrator-optical) module the way a real WFO
deployment would, and runs it end to end through the real orchestrator-core process engine and the orchestrator UI.

This is **user code**, not module code. It adds no domain logic: every product, product block, HAL entry point and
workflow is shipped by the module and consumed here. Its only local "business" content is a static pair of test
customers (`workflows/customer.py`) and HAL-level fake device stubs (`device_stubs.py`). Stack: Python 3.13, Docker
Compose (postgres/pgvector, redis, orchestrator-core backend, orchestrator-ui).

## Repo layout at a glance

```
├── docker-compose.yml        # 4 services; mounts the module + this repo into the orchestrator container
├── docker/
│   ├── orchestrator/         #   entrypoint.sh (provisioning sequence), orchestrator.env, is_healthy.py
│   ├── orchestrator-ui/      #   orchestrator-ui.env
│   └── postgresql/           #   no init scripts needed
├── migrations/               # Alembic env (from core), + versions/schema holding ONLY the data-head anchor
├── products/__init__.py      # imports the module's products -> registers the shipped product types
├── workflows/                # __init__.py (LazyWorkflowInstance list) + customer.py (static customer choice)
├── translations/             # workflow display strings; refreshed from the module at startup
├── main.py                   # CLI entrypoint; monkeypatches core CLI alembic_cfg for the module migrations
├── wsgi.py                   # ASGI entrypoint
├── device_stubs.py           # HAL fakes, active when FAKE_DEVICES=True
├── pyproject.toml / uv.lock   # pins orchestrator-core==5.1.3
└── alembic.ini, db.py        # alembic config; neutral db.py (no custom tables)
```

## Operational invariants

### Entrypoint sequence (docker/orchestrator/entrypoint.sh)

The orchestrator container boots and, in this exact order:

1. `uv sync --frozen` — aligns the image's preinstalled venv with `pyproject.toml`/`uv.lock` (`UV_PYTHON_DOWNLOADS=never`).
2. `uv pip install -e /home/orchestrator/orchestrator-optical` — the module under test, **editable**, so module edits hot-reload.
3. `cp` the module's `translations/en-GB.json` over `translations/en-GB.json` — core deep-merges `TRANSLATIONS_DIR` over its own defaults.
4. `python main.py db upgrade heads` — **plural** (two heads; see Migrations).
5. `python main.py index subscriptions|products|processes|workflows`.
6. `uvicorn --host 0.0.0.0 --port 8080 wsgi:app --reload --proxy-headers`, watching `orchestrator-optical/src`, `products`, `translations`, `workflows`.

### The `add_optical_module_migrations` monkeypatch (and why)

`main.py` wraps `orchestrator.core.cli.database.alembic_cfg` with
`orchestrator.optical.migrations.add_optical_module_migrations`, so every alembic config the core CLI builds appends
the module's shipped `versions/schema` to `version_locations`. Without it, core CLI `db upgrade heads` would never see
the optical chain and the database would only get core's own schema. This is the documented README >= 1.0 consumer
path; it is what lets this pre-1.0 harness apply the module's generated baseline. Keep the monkeypatch intact.

### Environment

- `docker/orchestrator/orchestrator.env` — core config (postgres/redis URIs, `TRANSLATIONS_DIR`, `CACHE_URI`, …
  `UVICORN_WORKERS=1` so `--reload` and in-process stubs are shared) plus module config:
  - `OPTICAL_CUSTOMER_CHOICE="workflows.customer:customer_choice"` — the user-code-space customer selector the
    shipped workflows require (the `Choice` function lives in user code, per the module's hard rules).
  - `FAKE_DEVICES=False` — when truthy (`1`/`true`/`yes`) `install_device_stubs_if_enabled()` swaps HAL entry points
    for the fakes in `device_stubs.py`. There are no real FlexILS/G30/G42/TNMS devices in this stack.
  - `CORE_OVERRIDE=/home/orchestrator/orchestrator-core` — entrypoint uses an editable core checkout if that
    directory contains a `pyproject.toml`; otherwise it uses core as pinned in `pyproject.toml`.
- `docker/orchestrator-ui/orchestrator-ui.env` — UI env; points at the backend on host `localhost:8080`, websocket on
  `/api/ws/events`.
- Overrides are read from `docker/overrides/*.env` (optional) if present.
- Compose variables: `BIND_ADDRESS_<SERVICE>` (loopback bind), `POSTGRES_PORT` (5433), `ORCH_BACKEND_TAG`
  (default `ghcr.io/workfloworchestrator/orchestrator-core:5.1.3`), `ORCH_UI_TAG`, `OPTICAL_MODULE_DIR`.

## Migrations

The module ships its catalog as **coded programmatic migrations** (no tables of its own). Two models coexist here;
do not conflate them.

### Long-term model (module >= 1.0)

The module ships immutable, versioned Alembic revisions in the package (frozen baseline at 1.0 + one delta per later
release). Consumers append the module's `versions/schema` via `add_optical_module_migrations`, `db merge` the optical
head with their `data` head once, then `db upgrade head`. **Never copy the module's revisions into this repo** — it
severs the link, forces manual re-copy of future deltas, and disables the module's `verify_no_drift` CI gate. Copying
is only a fallback for consumers needing full in-repo audit control.

### This harness's current setup (pre-1.0)

- The module pre-1.0 ships **no checked-in baseline**. This harness simulates the post-1.0 "shipped baseline" path
  using the module's **generated, non-committed baseline** (present as a stand-in in
  `orchestrator-optical/src/orchestrator/optical/migrations/versions/schema/2026-09-04_263aedd1b28d_optical_baseline.py`,
  regenerated from the models) plus the editable install and the monkeypatch above.
- `migrations/versions/schema` holds **only the empty data-head anchor**
  (`2026-09-04_2da4299d3560_create_data_head.py`): `revision="2da4299d3560"`, `down_revision=None`,
  `branch_labels=("data",)`, `depends_on="263aedd1b28d"`. This mirrors the WFO data-head convention (see
  `example-orchestrator/migrations/versions/schema/2023-10-24_a77227fe5455_create_data_head.py`). It is intentional
  and minimal: future consumer-owned product/data migrations chain onto `data@head`.

### Hard rules (migrations)

- **Always upgrade with `db upgrade heads` (plural).** With the optical head and the data head both present there are
  two heads; singular `db upgrade head` fails with `MultipleHeads`.
- **Do not regenerate/edit the module's baseline by hand here.** It is generated in the module repo from the models
  (the models are the single source of truth); treat it as a black box.
- **Keep `depends_on` in sync.** Pre-1.0 the baseline id is a deterministic hash of the model plan, so it **churns**
  when the module models change. When the module regenerates its baseline, update this repo's data-head `depends_on`
  to the new id and reset the database (`docker compose down -v`). Baselines are frozen only at 1.0.
- **Do not add a second data branch.** A consumer that already has a data head (typical, from
  `db migrate-domain-models`/`migrate-workflows`) uses the module's one-time `db merge <data head> <optical head>`,
  not a second anchor.
- **Keep the core image tag in sync** with the module's pinned `orchestrator-core==5.1.3` (see `pyproject.toml` of
  the module and `uv.lock`). The image ships a preinstalled venv; a version mismatch breaks the alembic revision
  chain mid-upgrade.
- The module's `--verify`/`verify_no_drift` gate uses singular `head` and would raise `MultipleHeads` in this
  two-head DB. That is expected; it only matters if you run the module's verify from inside a two-head consumer DB.

## Workflow registration

Registration is the **consumer's job** (per the module's rules): `workflows/__init__.py` is the single
`LazyWorkflowInstance` list, one line per shipped workflow, names and import paths mirroring the module's shipped
workflows (discoverable via `python -c "import orchestrator.optical.workflows"` or the module README). **Keep this
list in sync when the module ships new workflows** — a missing line means the workflow never appears in the UI, and a
stale line breaks registration. Workflows are persisted to the database by the entrypoint's `db upgrade heads` (the
baseline inserts them).

## Hard rules

- **No org-specific business logic.** This harness is a clean consumer; any GARR/NREN-specific logic belongs in user
  deployments, not here. Do not reintroduce anything beyond the static test customers and the device stubs.
- **Never edit `products/` models or the module.** This repo imports the module's products wholesale; model changes
  land here only by upgrading the module. Don't "fix" module issues from this repo.
- **`hal/` depends on blocks, never workflows, never consumer models** (module invariant). Respect it when adding
  anything that reaches into the module.
- **Do not check in secrets.** The stack's `nwa`/`nwa` credentials are intentional and well-known dev-only values.

## Known pre-existing noise (do NOT "fix" as a side quest)

- `device_stubs.py` mirrors the module's `test/conftest.py::install_device_stubs` (HAL functions are patched by name
  into each importing workflow module); keep them in sync, but don't refactor the stub table for its own sake.
- `migrations/env.py` and `migrations/helpers.py` are stock orchestrator-core scaffolding; `helpers.py` has an empty
  `# from orchestrator.core.migrations.helpers import *` placeholder left in place.
- The empty data-head anchor is deliberately minimal (empty `upgrade`/`downgrade`).

## Development commands

Development happens mostly in the **module** repo (`orchestrator-optical`), where the module's lint/type/import gates
live (`uv run ruff check`, `uv run ty check`, `uv run pyrefly check`). From this repo, the day-to-day loop is:

```shell
docker compose up -d --build     # start the stack
docker compose restart orchestrator   # re-run the entrypoint after config/DB changes
docker compose down -v           # reset the database (needed when the baseline changes)
docker compose logs -f orchestrator    # follow backend logs
```

Host ports: UI 3000, backend 8080, postgres 5433 (`postgresql+psycopg://nwa:nwa@127.0.0.1:5433/orchestrator-core`),
debugpy 5678.
