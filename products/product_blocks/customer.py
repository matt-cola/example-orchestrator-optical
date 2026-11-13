"""Customer product blocks (consumer-owned).

This deployment has no external CRM, so the orchestrator itself is the system of
record for customers: every customer is a subscription of the ``customer``
product, and the ``subscription_id`` of that subscription is the ``customer_id``
set on the subscriptions the customer owns (see ``workflows/customer/``).

The resource type names mirror orchestrator-core's GraphQL ``CustomerType``
(``fullname``/``shortcode``), which is what the UI displays.
"""

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from pydantic import computed_field


class CustomerBlockInactive(ProductBlockModel, product_block_name="Customer"):
    fullname: str | None = None
    shortcode: str | None = None


class CustomerBlockProvisioning(CustomerBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    fullname: str
    shortcode: str


class CustomerBlock(CustomerBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    fullname: str
    shortcode: str

    @computed_field
    @property
    def title(self) -> str:
        return f"{self.fullname}"
