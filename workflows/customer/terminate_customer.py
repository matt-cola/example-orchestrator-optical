"""Terminate customer workflow (consumer-owned).

Nothing but the matching ``customer_id`` links a customer to its subscriptions
(there is no ``in_use_by`` relation core could guard), so this workflow refuses
to terminate a customer that still owns non-terminated subscriptions: in the
form, and again in a step in case one was created in between.
"""

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from pydantic import model_validator
from pydantic_forms.types import InputForm, State, UUIDstr

from products.product_types.customer import Customer
from workflows.customer.shared import count_subscriptions_of_customer


def _check_customer_not_in_use(customer_id: str) -> None:
    if in_use := count_subscriptions_of_customer(customer_id):
        msg = f"customer still owns {in_use} non-terminated subscription(s): terminate or reassign them first"
        raise ValueError(msg)


def terminate_initial_input_form_generator(subscription_id: UUIDstr) -> InputForm:
    temp_subscription_id = subscription_id

    class TerminateCustomerForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore

        @model_validator(mode="after")
        def validate_data(self) -> "TerminateCustomerForm":
            _check_customer_not_in_use(str(temp_subscription_id))
            return self

    return TerminateCustomerForm


@step("Check customer is not in use")
def check_customer_not_in_use(subscription: Customer) -> State:
    _check_customer_not_in_use(str(subscription.subscription_id))
    return {}


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_customer() -> StepList:
    return begin >> check_customer_not_in_use
