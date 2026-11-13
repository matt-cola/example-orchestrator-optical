"""Validate customer workflow (consumer-owned).

Checks the two invariants of a customer subscription: it is its own customer,
and no other live customer shares its fullname or shortcode.
"""

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from pydantic_forms.types import State

from products.product_types.customer import Customer
from workflows.customer.shared import check_customer_uniqueness


@step("Load initial state")
def load_initial_state_customer(subscription: Customer) -> State:
    return {"subscription": subscription}


@step("Validate customer")
def validate_customer_subscription(subscription: Customer) -> State:
    subscription_id = str(subscription.subscription_id)
    if subscription.customer_id != subscription_id:
        msg = f"customer subscription {subscription_id} must be its own customer, found {subscription.customer_id!r}"
        raise ValueError(msg)
    check_customer_uniqueness(
        subscription.customer_info.fullname, subscription.customer_info.shortcode, exclude_customer_id=subscription_id
    )
    return {}


@validate_workflow()
def validate_customer() -> StepList:
    return begin >> load_initial_state_customer >> validate_customer_subscription
