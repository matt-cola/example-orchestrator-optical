"""Create customer workflow (consumer-owned).

Unlike every other create workflow there is no customer page: a customer
subscription is its own customer, so the construct step points its
``customer_id`` at its own ``subscription_id``.
"""

from orchestrator.core.forms import FormPage
from orchestrator.core.settings import app_settings
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.workflows.shared import create_summary_form
from pydantic import ConfigDict, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr

from products.product_types.customer import CustomerInactive, CustomerProvisioning
from workflows.customer.shared import NonEmptyStr, check_customer_uniqueness, subscription_description


def initial_input_form_generator(product_name: str) -> FormGenerator:
    class CreateCustomerForm(FormPage):
        model_config = ConfigDict(title=product_name)

        fullname: NonEmptyStr
        shortcode: NonEmptyStr

        @model_validator(mode="after")
        def validate_data(self) -> "CreateCustomerForm":
            check_customer_uniqueness(self.fullname, self.shortcode)
            return self

    user_input_dict = (yield CreateCustomerForm).model_dump()

    yield from create_summary_form(user_input_dict, product_name, ["fullname", "shortcode"])

    return user_input_dict


@step("Construct Subscription model")
def construct_customer_model(product: UUIDstr, fullname: str, shortcode: str) -> State:
    # The subscription id only exists once the model is built, so the model is
    # built with core's default customer and re-pointed at itself right after.
    customer = CustomerInactive.from_product_id(
        product_id=product,
        customer_id=app_settings.DEFAULT_CUSTOMER_IDENTIFIER,
        status=SubscriptionLifecycle.INITIAL,
    )
    customer.customer_id = str(customer.subscription_id)
    customer.customer_info.fullname = fullname
    customer.customer_info.shortcode = shortcode

    customer = CustomerProvisioning.from_other_lifecycle(customer, SubscriptionLifecycle.PROVISIONING)
    customer.description = subscription_description(customer)

    return {
        "subscription": customer,
        "subscription_id": customer.subscription_id,  # necessary to be able to use older generic step functions
        "subscription_description": customer.description,
    }


@create_workflow(initial_input_form=initial_input_form_generator)
def create_customer() -> StepList:
    return begin >> construct_customer_model >> store_process_subscription()
