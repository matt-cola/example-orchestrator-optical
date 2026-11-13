"""Customer subscription product types (consumer-owned).

A customer subscription is its own customer: its ``customer_id`` equals its own
``subscription_id`` (set by the create workflow, checked by the validate one).

The root block field is ``customer_info`` rather than ``customer`` on purpose:
orchestrator-core's GraphQL subscription interface already has a ``customer``
field, and a product block field of the same name breaks the schema.
"""

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle

from products.product_blocks.customer import CustomerBlock, CustomerBlockInactive, CustomerBlockProvisioning


class CustomerInactive(SubscriptionModel, is_base=True):
    customer_info: CustomerBlockInactive


class CustomerProvisioning(CustomerInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    customer_info: CustomerBlockProvisioning


class Customer(CustomerProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    customer_info: CustomerBlock
