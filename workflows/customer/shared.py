"""Customer lookups shared by the customer workflows, the selector and GraphQL.

Customers are subscriptions of the consumer-owned ``customer`` product; these
helpers read them straight from the catalog tables (one query, no domain model
load) because the GraphQL ``customer`` field resolves once per listed
subscription.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from orchestrator.core.db import (
    ProductTable,
    ResourceTypeTable,
    SubscriptionInstanceTable,
    SubscriptionInstanceValueTable,
    SubscriptionTable,
    db,
)
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle
from pydantic import StringConstraints
from sqlalchemy import func, select

CUSTOMER_PRODUCT_TYPE = "Customer"

# States in which a customer subscription claims its fullname and shortcode.
CLAIMING_STATES = [SubscriptionLifecycle.INITIAL, SubscriptionLifecycle.PROVISIONING, SubscriptionLifecycle.ACTIVE]

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


@dataclass(frozen=True)
class CustomerRecord:
    customer_id: str
    status: str
    fullname: str
    shortcode: str


def find_customers(
    statuses: Sequence[SubscriptionLifecycle] | None = None, customer_id: str | None = None
) -> list[CustomerRecord]:
    """Return the customer subscriptions, sorted by fullname.

    Args:
        statuses: Only return customers whose subscription is in one of these
            lifecycle states; all states when omitted.
        customer_id: Only return the customer with this id (the
            ``subscription_id`` of its customer subscription).
    """
    stmt = (
        select(
            SubscriptionTable.subscription_id,
            SubscriptionTable.status,
            ResourceTypeTable.resource_type,
            SubscriptionInstanceValueTable.value,
        )
        .join(ProductTable, ProductTable.product_id == SubscriptionTable.product_id)
        .join(SubscriptionInstanceTable, SubscriptionInstanceTable.subscription_id == SubscriptionTable.subscription_id)
        .join(
            SubscriptionInstanceValueTable,
            SubscriptionInstanceValueTable.subscription_instance_id
            == SubscriptionInstanceTable.subscription_instance_id,
        )
        .join(ResourceTypeTable, ResourceTypeTable.resource_type_id == SubscriptionInstanceValueTable.resource_type_id)
        .where(ProductTable.product_type == CUSTOMER_PRODUCT_TYPE)
    )
    if statuses is not None:
        stmt = stmt.where(SubscriptionTable.status.in_([str(status) for status in statuses]))
    if customer_id is not None:
        try:
            stmt = stmt.where(SubscriptionTable.subscription_id == UUID(str(customer_id)))
        except ValueError:
            return []  # not a subscription id, so not one of our customers

    rows: dict[str, dict[str, str]] = {}
    for subscription_id, status, resource_type, value in db.session.execute(stmt):
        rows.setdefault(str(subscription_id), {"status": status})[resource_type] = value

    customers = [
        CustomerRecord(
            customer_id=subscription_id,
            status=values["status"],
            fullname=values.get("fullname", ""),
            shortcode=values.get("shortcode", ""),
        )
        for subscription_id, values in rows.items()
    ]
    return sorted(customers, key=lambda customer: customer.fullname.casefold())


def check_customer_uniqueness(fullname: str, shortcode: str, exclude_customer_id: str | None = None) -> None:
    """Raise ``ValueError`` when another live customer already uses the fullname or shortcode."""
    for customer in find_customers(statuses=CLAIMING_STATES):
        if customer.customer_id == str(exclude_customer_id):
            continue
        if customer.fullname.casefold() == fullname.casefold():
            raise ValueError(f"fullname {fullname!r} already in use by customer {customer.customer_id}")
        if customer.shortcode.casefold() == shortcode.casefold():
            raise ValueError(f"shortcode {shortcode!r} already in use by customer {customer.customer_id}")


def count_subscriptions_of_customer(customer_id: str) -> int:
    """Count the non-terminated subscriptions owned by a customer, the customer subscription itself excluded."""
    stmt = (
        select(func.count())
        .select_from(SubscriptionTable)
        .where(
            SubscriptionTable.customer_id == str(customer_id),
            SubscriptionTable.subscription_id != UUID(str(customer_id)),
            SubscriptionTable.status != str(SubscriptionLifecycle.TERMINATED),
        )
    )
    return db.session.scalar(stmt) or 0


def subscription_description(subscription: SubscriptionModel) -> str:
    return f"{subscription.customer_info.fullname} (Customer)"
