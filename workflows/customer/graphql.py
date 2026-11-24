"""GraphQL customer of a subscription, backed by the customer subscriptions.

orchestrator-core has no customer store: its subscription ``customer`` field
always returns the single default customer from the settings. This module
resolves it from the consumer-owned ``customer`` product instead, and is passed
to ``app.register_graphql()`` in ``wsgi.py``. Customers themselves are listed by
the generated ``customerInstances`` field (``products/block_instances.py``).

It lives under ``workflows/`` only because that directory is mounted into the
orchestrator container (and watched by ``uvicorn --reload``).
"""

import strawberry
from orchestrator.core.graphql.schemas.customer import CustomerType
from orchestrator.core.graphql.schemas.subscription import SubscriptionInterface
from orchestrator.core.settings import app_settings

from workflows.customer.shared import find_customers

__all__ = ["CustomerSubscriptionInterface"]


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
