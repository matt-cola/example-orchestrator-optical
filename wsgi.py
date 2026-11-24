"""ASGI entrypoint of the example optical orchestrator."""

from fastapi import Depends
from orchestrator.core import OrchestratorCore
from orchestrator.core.graphql.schema import Query
from orchestrator.core.security import authorize
from orchestrator.core.settings import AppSettings
from strawberry.tools import merge_types

import db  # noqa: F401  Side-effects
import products  # noqa: F401  Side-effects: registers the shipped product types
import workflows  # noqa: F401  Side-effects: registers the shipped workflows
from products.block_instances import block_instances_query, block_instances_router, graphql_models_with_blocks
from workflows.customer.graphql import CustomerSubscriptionInterface

app = OrchestratorCore(base_settings=AppSettings())
# Resolve the GraphQL customer of a subscription from the consumer-owned customer product
# instead of core's single default customer, and list the instances of every product block
# across subscriptions (products/block_instances.py), customers included (customerInstances).
graphql_models = graphql_models_with_blocks(CustomerSubscriptionInterface)
app.register_graphql(
    query=merge_types("Query", (Query, block_instances_query(graphql_models))),
    subscription_interface=CustomerSubscriptionInterface,
    graphql_models=graphql_models,
)
app.include_router(
    block_instances_router(),
    prefix="/api/product_block_instances",
    tags=["Product block instances"],
    dependencies=[Depends(authorize)],
)
