# Example Optical Orchestrator

An example [Workflow Orchestrator](https://workfloworchestrator.org) deployment that exercises the
[`orchestrator-optical`](https://github.com/workfloworchestrator/orchestrator-optical) module end to end through the
real orchestrator-core process engine and the orchestrator UI.

This repository is **user code**: it consumes the module like a real WFO deployment would. It contributes no domain
logic of its own — every product, product block, HAL entry point and workflow comes from the module. Its only
"business" content is a static pair of test customers and a set of fake device stubs.

## Repository layout

```
├── docker-compose.yml        # postgres (pgvector), redis, orchestrator, orchestrator-ui
├── docker/
│   ├── orchestrator/         # entrypoint.sh, orchestrator.env, is_healthy.py
│   ├── orchestrator-ui/      # orchestrator-ui.env
│   └── postgresql/           # only a README (no init scripts; pgvector ships in the image)
├── migrations/               # Alembic env + versions/schema (only the data-head anchor)
├── products/                 # imports the module's products (registers the shipped product types)
├── workflows/                # LazyWorkflowInstance registration + static customer choice
├── translations/             # workflow display strings (refreshed from the module at startup)
├── main.py                   # CLI entrypoint (wires the module's migrations into core CLI)
├── wsgi.py                   # ASGI entrypoint
├── device_stubs.py           # HAL-level fakes (FAKE_DEVICES=True)
├── pyproject.toml            # pins orchestrator-core
└── uv.lock
```

## Prerequisites

- Docker (with `docker compose`).
- The two sibling repositories on disk, in the layout below. The module is mounted into the orchestrator container
  from disk so your edits hot-reload.

```
parent/
├── orchestrator-optical/          # the module under test (this repo's sibling)
└── example-orchestrator-optical/  # this repo
```

## Quickstart

```shell
docker compose up -d --build
```

This starts four services:

| Service            | Host port | Notes                                        |
|--------------------|-----------|----------------------------------------------|
| `orchestrator-ui`  | 3000      | the orchestrator web UI                      |
| `orchestrator`     | 8080      | core backend (GraphQL + REST on `/api`)      |
| `postgres`         | 5433      | pgvector/postgres 17, `nwa`/`nwa`/`orchestrator-core` |
| `redis`            | (internal)| not published                                |

On startup the orchestrator container runs the entrypoint: it syncs the pinned dependencies (`uv sync --frozen`),
installs the module editable, refreshes `translations/en-GB.json` from the module's shipped strings, provisions the
database (`db upgrade heads`), indexes subscriptions/products/processes/
workflows, and starts `uvicorn` with `--reload` (watching `orchestrator-optical/src` by default, or `$CORE_OVERRIDE`
when that directory contains a `pyproject.toml`).

Point your browser at `http://localhost:3000/`. The backend is reachable directly at `http://localhost:8080/`.

### Overriding the module directory

The module is mounted into the orchestrator container at `/home/orchestrator/orchestrator-optical`. The mount path is
parameterized through the `OPTICAL_MODULE_DIR` environment variable (default `../orchestrator-optical`, relative to
this repo), so you can point the stack at any checkout:

```shell
OPTICAL_MODULE_DIR=/path/to/orchestrator-optical docker compose up -d --build
```

> [!NOTE]
> All services bind to `127.0.0.1` by default (`BIND_ADDRESS_<SERVICE>` widens them; see
> `docker-compose.override.yml.example` for a LAN-bind example). This stack is for local
> development only — it ships well-known credentials (`nwa`/`nwa`, redis password `nwa`) and no real devices.
> Real-device credentials for a non-fake stack are documented in `docker/overrides/orchestrator.env.example`.

## Using the UI

The stack ships **fake devices**: no FlexILS/G30/G42/TNMS hardware exists here. Set `FAKE_DEVICES=True` (in
`docker/orchestrator/orchestrator.env`) to replace the HAL entry points with the same fakes the module's DB-backed
test suite uses, so every shipped workflow family can be exercised end to end. The fakes advertise one client port
(`port-1/2/1`), one line port (`port-1/3.1/1.1`), transceiver mode `DP16QAM`, software version `1.0.0`, and a static
pair of test customers.

> [!IMPORTANT]
> The fakes validate **workflow and UI integration only** — that forms render, selectors populate, steps run in
> order and subscriptions land correctly — never device behavior. They return canned values, never raise, and the
> `validate_*`/`reconcile_*` checks trivially accept, so a fully green fake run can still fail against real
> hardware. Device truth lives in the module's lab-backed test suite.

The module's shipped workflows are registered through `workflows/__init__.py` (one `LazyWorkflowInstance` line per
workflow). A typical walk-through:

1. In the UI, click **New subscription** and pick a product — e.g. **Nokia FlexILS Optical Node**.
2. Fill the form. The **customer** field is served by the static choice in `workflows/customer.py`
   (wired via `OPTICAL_CUSTOMER_CHOICE="workflows.customer:customer_choice"`); node/port forms may ask for values that
   must match what the fake device reports.
3. Confirm on the summary form and **Start workflow**; watch the process run. Create the other products bottom-up as
   the forms demand (locations → nodes → pipes → spectrum → digital service → coherent pluggable).
4. On the **Subscriptions** page you can modify, validate or terminate any subscription through the **Actions**
   pulldown; the reconcile workflows appear for the optical pipe families plus the spectrum and digital service.

## Iterating on the module

The module is mounted at `/home/orchestrator/orchestrator-optical` and installed **editable**, and uvicorn runs with
`--reload` watching `orchestrator-optical/src` plus this repo's `products`, `workflows` and `translations`. Edit code
in either repo and the backend reloads automatically; refresh the browser to see the change.

Steps that do **not** reload (config or database-level changes) need a restart:

```shell
docker compose restart orchestrator      # re-runs the entrypoint
docker compose up -d --build             # rebuild if dependencies changed
```

## Migrations

The module ships its catalog (products, product blocks, resource types, workflows) as **coded programmatic
migrations** — the same way orchestrator-core provisions its own domain. The module owns no tables; everything lives
in the core catalog tables.

### The long-term model (module >= 1.0)

From the first stable release the module ships **immutable, versioned Alembic revisions inside the package**: one
frozen baseline at the 1.0 release plus one immutable delta revision per later release, chained linearly onto the
pinned orchestrator-core schema head. Consumers append the module's `versions/schema` directory to their Alembic
`version_locations` via the shipped helper — exactly how orchestrator-core itself is consumed:

```python
from orchestrator.core.cli import database as core_cli_database
from orchestrator.optical.migrations import add_optical_module_migrations

_cfg = core_cli_database.alembic_cfg
core_cli_database.alembic_cfg = lambda: add_optical_module_migrations(_cfg())
```

Then merge the optical head with your `data` head **once** after installing and `db upgrade head` from then on.

> [!IMPORTANT]
> Do **not** copy the module's revisions into this repo. That severs the link to the module, forces you to manually
> re-copy every future delta, and disables the module's `verify_no_drift` CI gate. Copying is only a fallback for
> consumers who need full in-repo audit control.

### How this harness runs it today (pre-1.0)

The module pre-1.0 ships **no checked-in baseline** (models are still being finalized). This harness simulates the
post-1.0 "shipped baseline" path instead:

- **`main.py` monkeypatches `orchestrator.core.cli.database.alembic_cfg`** with `add_optical_module_migrations`, so the
  core CLI's `db upgrade heads` sees the module's migration chain. This is the documented README >= 1.0 consumer path.
- **`migrations/versions/schema` holds only one file: the empty data-head anchor.** This is intentional and minimal:

  ```python
  revision = "2da4299d3560"
  down_revision = None
  branch_labels = ("data",)
  depends_on = "3b3fe1c2a7a6"   # the optical baseline revision (module)
  ```

  `down_revision` is a lineage edge; `depends_on` is a *soft ordering* dependency that creates a second root/head
  which Alembic orders after the optical baseline. A consumer with **no** existing data head adds such an anchor, and
  future consumer-owned product/data migrations chain onto `data@head`. A consumer that **already** has a data head
  (the typical case, from `db migrate-domain-models`/`migrate-workflows`) must not add a second data branch — use the
  module's documented one-time `db merge <your data head> <optical head>` instead.
- **The baseline itself is a generated, non-committed stand-in** sitting in the module's
  `src/orchestrator/optical/migrations/versions/schema/` (it is regenerated from the shipped models; the real
  checked-in baseline only happens at 1.0). The entrypoint applies it through the monkeypatch.

### Two heads: always `db upgrade heads`

With the optical baseline and the data head both present the Alembic chain has **two heads**. Always upgrade with
`db upgrade heads` (plural — the WFO entrypoint convention, and what `docker/orchestrator/entrypoint.sh` runs), never
`db upgrade head` (singular), which fails on multiple heads.

> [!NOTE]
> The module's own `--verify` / `verify_no_drift` path runs a singular `upgrade head` and would raise
> `MultipleHeads` in this two-head setup. That is expected and only matters if you run the module's verify gate from
> inside a two-head consumer database.

### The `depends_on` caveat (pre-1.0)

Pre-1.0 the optical baseline id **churns**: it is a deterministic hash of the model plan (`3b3fe1c2a7a6` will change
when the module models change and the baseline is regenerated). When that happens, this repo's
`migrations/versions/schema/2026-09-04_2da4299d3560_create_data_head.py` must have its `depends_on` updated to the new
id, and the database reset (below). This is exactly why baselines are only frozen at 1.0.

### Keeping core in sync

The orchestrator image tag in `docker-compose.yml` (`ORCH_BACKEND_TAG`, default
`ghcr.io/workfloworchestrator/orchestrator-core:5.1.3`) must stay in sync with this repo's pinned
`orchestrator-core==5.1.3` (`pyproject.toml`/`uv.lock`): the image ships a preinstalled venv, and migrating the
database with a different core version than the one that created it breaks the Alembic revision chain.

## Troubleshooting

- **`uv sync --frozen` fails** — the entrypoint syncs with `--frozen`, which requires the `uv.lock` present and in
  sync with `pyproject.toml`. Make sure both files are committed/present before starting the stack.
- **`uv sync`/`uv pip install` succeeded but the module is missing** — the module must be installed *editable* after
  the sync (`uv pip install -e /home/orchestrator/orchestrator-optical`, as the entrypoint does). A bare sync wipes
  extra installs from the shared venv.
- **Baseline changed / alembic chain broke** — the module's pre-1.0 baseline id is regenerated when the models
  change, so the persistent volume no longer matches. Reset the database with `docker compose down -v` and bring the
  stack up again (this drops all subscriptions — fine for a dev stack).
- **Can't reach postgres** — it is published on host `127.0.0.1:5433` (not 5432). Connection string:
  `postgresql+psycopg://nwa:nwa@127.0.0.1:5433/orchestrator-core`.
- **`MultipleHeads` on upgrade** — you used `db upgrade head` (singular) inside the container, or added a second
  data branch. Use `db upgrade heads`.
- **Workflow missing from the UI** — it is not in `workflows/__init__.py`, or it is not persisted. Registration is the
  consumer's job: keep the `LazyWorkflowInstance` list in sync with the module's shipped workflows and re-provision
  the database.
- **Customer dropdown empty / form error about customer** — `OPTICAL_CUSTOMER_CHOICE` must point at a function
  returning a `type[Choice]` (here `workflows.customer:customer_choice`).
- **Changes to `products/` or the module models** — this repo imports the module's products wholesale; model changes
  land here only by upgrading the module, not by editing local files.
