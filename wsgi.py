"""ASGI entrypoint of the example optical orchestrator."""

from orchestrator.core import OrchestratorCore
from orchestrator.core.settings import AppSettings

import db  # noqa: F401  Side-effects
import products  # noqa: F401  Side-effects: registers the shipped product types
import workflows  # noqa: F401  Side-effects: registers the shipped workflows
from workflows.customer.graphql import CustomerSubscriptionInterface, Query

app = OrchestratorCore(base_settings=AppSettings())
# Resolve the GraphQL customer of a subscription (and the customers query) from the
# consumer-owned customer product instead of core's single default customer.
app.register_graphql(query=Query, subscription_interface=CustomerSubscriptionInterface)
