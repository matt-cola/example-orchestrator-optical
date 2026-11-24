"""GraphQL and REST listing of product block instances, derived from the registered product block models.

orchestrator-core only reaches product block instances through their owning subscription. This module adds, for
every product block model in ``ProductBlockModel.registry`` (so for every block the shipped and consumer products
define, with no per-block code), a listing of all its instances across subscriptions:

- GraphQL: a root field ``<blockName>Instances(first, after, statuses)`` returning a ``Connection`` of the block's
  existing auto-registered GraphQL type (e.g. ``olsLinePortBlockInstances`` -> ``OlsLinePortBlockInactive``).
- REST: ``GET /api/product_block_instances/<BlockName>?range=&statuses=`` returning the block's Pydantic model
  (e.g. ``/api/product_block_instances/OlsLinePortBlock``), paged with core's ``range``/``Content-Range`` convention.

Each instance is loaded with its owning subscription's lifecycle, the same way the subscription's own domain model
loads it. Both are wired in ``wsgi.py``.
"""

from collections.abc import Callable, Sequence
from http import HTTPStatus
from typing import Any

import strawberry
from fastapi import APIRouter, Query, Response
from oauth2_lib.strawberry import authenticated_field
from orchestrator.core.api.error_handling import raise_status
from orchestrator.core.db import ProductBlockTable, SubscriptionInstanceTable, SubscriptionTable, db
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.graphql.autoregistration import add_class_to_strawberry, graphql_name, register_domain_models
from orchestrator.core.graphql.pagination import Connection
from orchestrator.core.graphql.schemas import DEFAULT_GRAPHQL_MODELS
from orchestrator.core.graphql.types import StrawberryModelType
from orchestrator.core.graphql.utils.to_graphql_result_page import to_graphql_result_page
from orchestrator.core.types import SubscriptionLifecycle
from sqlalchemy import func, select

__all__ = ["block_instances_query", "block_instances_router", "graphql_models_with_blocks"]


def load_block_instances(
    block_name: str, statuses: Sequence[SubscriptionLifecycle] | None, offset: int, limit: int | None
) -> tuple[list[ProductBlockModel], int]:
    """One page of the instances of product block `block_name`, in a stable order, and the total count."""
    stmt = (
        select(SubscriptionInstanceTable)
        .join(SubscriptionInstanceTable.product_block)
        .join(SubscriptionInstanceTable.subscription)
        .where(ProductBlockTable.name == block_name)
        .order_by(SubscriptionInstanceTable.subscription_id, SubscriptionInstanceTable.subscription_instance_id)
    )
    if statuses:
        stmt = stmt.where(SubscriptionTable.status.in_([status.value for status in statuses]))
    total = db.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    instances = db.session.scalars(stmt.offset(offset).limit(limit)).all()
    return [ProductBlockModel.from_db(subscription_instance=instance) for instance in instances], total


def graphql_models_with_blocks(subscription_interface: type) -> StrawberryModelType:
    """Core's GraphQL models plus a type for every product block, also those no product type reaches.

    Pass the result to ``register_graphql(graphql_models=...)``, so the block fields and the subscriptions share the
    same block types.
    """
    models = register_domain_models(subscription_interface, existing_models=dict(DEFAULT_GRAPHQL_MODELS))
    for block in ProductBlockModel.registry.values():
        add_class_to_strawberry(graphql_name(block.__name__), block, models, {})
    return models


def _block_field(block_name: str, graphql_type: Any) -> Any:
    # Synchronous, like core's db.session users: field resolvers running in parallel threads would share the session.
    def resolve(first: int = 10, after: int = 0, statuses: list[str] | None = None) -> Connection[Any]:
        lifecycles = [SubscriptionLifecycle(status) for status in statuses or []]
        # One extra item tells to_graphql_result_page whether a next page follows.
        instances, total = load_block_instances(block_name, lifecycles, after, first + 1)
        return to_graphql_result_page([graphql_type.from_pydantic(i) for i in instances], first, after, total)

    resolve.__annotations__["return"] = Connection[graphql_type]
    field = authenticated_field(
        resolver=resolve, description=f"Returns the {block_name} product block instances of all subscriptions"
    )
    field.graphql_name = f"{block_name[0].lower()}{block_name[1:]}Instances"
    return field


def block_instances_query(graphql_models: StrawberryModelType) -> type:
    """GraphQL query type with one field per product block, to merge into the root Query."""
    fields = {
        f"{name}_instances": _block_field(name, graphql_models[graphql_name(block.__name__)])
        for name, block in ProductBlockModel.registry.items()
    }
    return strawberry.type(type("ProductBlockInstancesQuery", (), fields), description="Product block instances")


def _block_route(block_name: str) -> Callable[..., list[ProductBlockModel]]:
    def list_block_instances(
        response: Response,
        range: str | None = Query(None, description="start,end: the first index and the first index excluded"),
        statuses: list[SubscriptionLifecycle] | None = Query(None, description="Owning subscription statuses"),
    ) -> list[ProductBlockModel]:
        if not range:
            return load_block_instances(block_name, statuses, 0, None)[0]
        try:
            start, end = map(int, range.split(","))
        except ValueError:
            raise_status(HTTPStatus.BAD_REQUEST, "range must be 'start,end'")
        if start >= end:
            raise_status(HTTPStatus.BAD_REQUEST, "range start must be lower than end")
        instances, total = load_block_instances(block_name, statuses, start, end - start)
        response.headers["Content-Range"] = f"{block_name} {start}-{end}/{total}"
        return instances

    list_block_instances.__doc__ = f"List the {block_name} product block instances of all subscriptions."
    return list_block_instances


def block_instances_router() -> APIRouter:
    """REST router with one listing per product block; include it under ``/api/product_block_instances``."""
    router = APIRouter()
    for name, block in ProductBlockModel.registry.items():
        router.add_api_route(
            f"/{name}",
            _block_route(name),
            methods=["GET"],
            response_model=list[block],  # type: ignore[valid-type]
            operation_id=f"list_{name}_instances",
        )
    return router
