"""ASGI entrypoint of the example optical orchestrator."""

from orchestrator.core import OrchestratorCore
from orchestrator.core.settings import AppSettings

import db  # noqa: F401  Side-effects
import products  # noqa: F401  Side-effects: registers the shipped product types
import workflows  # noqa: F401  Side-effects: registers the shipped workflows

app = OrchestratorCore(base_settings=AppSettings())
app.register_graphql()
