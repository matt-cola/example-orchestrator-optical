"""Modify customer workflow (consumer-owned).

Only the display attributes change; the ``customer_id`` (the subscription id)
is immutable, so the subscriptions owned by the customer need no update.
"""

from orchestrator.core.forms import FormPage
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import modify_workflow
from pydantic import model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from products.product_types.customer import Customer
from workflows.customer.shared import NonEmptyStr, check_customer_uniqueness, subscription_description


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    subscription = Customer.from_subscription(subscription_id)
    customer = subscription.customer_info

    class ModifyCustomerForm(FormPage):
        fullname: NonEmptyStr = customer.fullname
        shortcode: NonEmptyStr = customer.shortcode

        @model_validator(mode="after")
        def validate_data(self) -> "ModifyCustomerForm":
            check_customer_uniqueness(self.fullname, self.shortcode, exclude_customer_id=str(subscription_id))
            return self

    user_input = yield ModifyCustomerForm

    return user_input.model_dump() | {"subscription": subscription}


@step("Update subscription")
def update_subscription(subscription: Customer, fullname: str, shortcode: str) -> State:
    subscription.customer_info.fullname = fullname
    subscription.customer_info.shortcode = shortcode
    subscription.description = subscription_description(subscription)
    return {"subscription": subscription}


@modify_workflow(initial_input_form=initial_input_form_generator)
def modify_customer() -> StepList:
    return begin >> update_subscription
