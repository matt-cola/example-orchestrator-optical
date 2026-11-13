"""GraphQL customer resolution backed by the customer subscriptions.

orchestrator-core has no customer store: its ``customer`` fields and its
``customers`` query always return the single default customer from the
settings. This module resolves them from the consumer-owned ``customer``
product instead, and is passed to ``app.register_graphql()`` in ``wsgi.py``.

It lives under ``workflows/`` only because that directory is mounted into the
orchestrator container (and watched by ``uvicorn --reload``).
"""

import strawberry
from oauth2_lib.strawberry import authenticated_field
from orchestrator.core.graphql.pagination import Connection
from orchestrator.core.graphql.schema import Mutation, OrchestratorQuery, SearchQuery
from orchestrator.core.graphql.schemas.customer import CustomerType
from orchestrator.core.graphql.schemas.subscription import SubscriptionInterface
from orchestrator.core.graphql.types import GraphqlFilter, GraphqlSort, OrchestratorInfo
from orchestrator.core.graphql.utils.to_graphql_result_page import to_graphql_result_page
from orchestrator.core.settings import app_settings
from orchestrator.core.types import SubscriptionLifecycle
from strawberry.tools import merge_types

from workflows.customer.shared import find_customers

__all__ = ["CustomerSubscriptionInterface", "Mutation", "Query"]


def customer_type(customer_id: str) -> CustomerType:
    """Resolve a stored ``customer_id`` to the customer the UI displays.

    Ids that are not a customer subscription (core's default customer, or ids
    written before the customer product existed) keep their id and are labelled
    as unknown rather than silently shown as someone else.
    """
    if customers := find_customers(customer_id=customer_id):
        customer = customers[0]
        return CustomerType(customer_id=customer.customer_id, fullname=customer.fullname, shortcode=customer.shortcode)
    if customer_id == app_settings.DEFAULT_CUSTOMER_IDENTIFIER:
        return CustomerType(
            customer_id=customer_id,
            fullname=app_settings.DEFAULT_CUSTOMER_FULLNAME,
            shortcode=app_settings.DEFAULT_CUSTOMER_SHORTCODE,
        )
    return CustomerType(customer_id=customer_id, fullname=f"Unknown customer {customer_id}", shortcode="unknown")


@strawberry.federation.interface(description="Virtual base interface for subscriptions", keys=["subscriptionId"])
class CustomerSubscriptionInterface(SubscriptionInterface):
    @strawberry.field(description="Returns customer of a subscription")  # type: ignore
    def customer(self) -> CustomerType:
        return customer_type(self.customer_id)


async def resolve_customers(
    info: OrchestratorInfo,
    filter_by: list[GraphqlFilter] | None = None,
    sort_by: list[GraphqlSort] | None = None,
    first: int = 10,
    after: int = 0,
) -> Connection[CustomerType]:
    customers = [
        CustomerType(customer_id=customer.customer_id, fullname=customer.fullname, shortcode=customer.shortcode)
        for customer in find_customers(statuses=[SubscriptionLifecycle.ACTIVE])
    ]
    return to_graphql_result_page(customers[after : after + first], first, after, len(customers))


@strawberry.federation.type(description="Orchestrator customer Query")
class CustomerQuery:
    customers: Connection[CustomerType] = authenticated_field(
        resolver=resolve_customers, description="Returns the active customers"
    )


Query: type = merge_types("Query", (OrchestratorQuery, CustomerQuery, SearchQuery))
