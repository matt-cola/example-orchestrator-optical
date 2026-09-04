"""CLI entrypoint for the example optical orchestrator.

Run with ``python main.py --help`` (inside the container), e.g.::

    python main.py db upgrade heads
"""

import typer
from orchestrator.core import app_settings
from orchestrator.core.cli.main import app as core_cli
from orchestrator.core.db import init_database
from orchestrator.core.log_config import LOGGER_OVERRIDES

import db  # noqa: F401  Side-effects
import device_stubs
import products  # noqa: F401  Side-effects: registers the shipped product types

# Wire the shipped orchestrator-optical migrations into every alembic config the
# orchestrator-core CLI builds (the README >= 1.0 consumer path): the core CLI
# builds its own Config from ./alembic.ini, so the shipped versions/schema
# directory is appended by wrapping the CLI's alembic_cfg() factory.
from orchestrator.core.cli import database as core_cli_database
from orchestrator.optical.migrations import add_optical_module_migrations
from nwastdlib.logging import initialise_logging

_alembic_cfg = core_cli_database.alembic_cfg


def _alembic_cfg_with_optical_migrations():
    """Return the core CLI Alembic config extended with the shipped optical migrations."""
    return add_optical_module_migrations(_alembic_cfg())


core_cli_database.alembic_cfg = _alembic_cfg_with_optical_migrations


def init_cli_app() -> typer.Typer:
    initialise_logging(LOGGER_OVERRIDES)
    init_database(app_settings)
    device_stubs.install_device_stubs_if_enabled()
    return core_cli()


if __name__ == "__main__":
    init_cli_app()
