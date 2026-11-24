"""Create Point of Presence workflow (consumer-owned).

Copied from the GARR Workflow Orchestrator (``garr/workflows/pop/create_pop.py``)
as the pre-existing consumer workflow of the anti-corruption example, extended
with the optical wiring: after the construct step the forward-sync step
populates the composed optical location block from the PoP-native fields (the
single tree persist at the end saves both), and the backward-sync step copies
the block values back. For the location family the shipped block steps are
persist-only (no device mutation), so forward + backward collapse around the
single ``store_process_subscription`` save — the steps mark the slots the README
pattern prescribes (forward before persist, backward after).
"""

from re import match

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from orchestrator.optical.db import subscription_instances_by_block_type_and_resource_value
from orchestrator.optical.utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate
from orchestrator.optical.workflows.customer import customer_choice_form_page
from orchestrator.optical.workflows.optical_location.shared import check_location_code_uniqueness
from orchestrator.optical.workflows.shared import create_summary_form
from pydantic import ConfigDict, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from products.product_types.pop import PopInactive, PopProvisioning
from workflows.pop.sync import (
    backward_sync_optical_block_to_pop_step,
    forward_sync_pop_to_optical_block_step,
    normalize_location_code,
)


def subscription_description(subscription: SubscriptionModel) -> str:
    """Generate subscription description.

    The suggested pattern is to implement a subscription service that generates a subscription specific
    description, in case that is not present the description will just be set to the product name.
    """
    return f"{subscription.pop.full_name} (Point of Presence)"


logger = get_logger(__name__)


def pop_resource_in_use(resource: str, value: str | int, exclude_subscription_id: str | None = None) -> str | None:
    """Return the id of the subscription already using a PoP resource value, if any.

    Block-based lookup on the consumer ``PoP`` block, covering INITIAL,
    PROVISIONING and ACTIVE owner subscriptions so two concurrent creates cannot
    claim the same value. The subscription being modified is excluded by
    ``exclude_subscription_id``, so a subscription never conflicts with itself.

    Args:
        resource: The resource type, e.g. ``code``.
        value: The value to check.
        exclude_subscription_id: Identifier of the subscription being modified,
            whose own block is not a conflict.

    Returns:
        The conflicting subscription id, or None when the value is free.
    """
    instances = subscription_instances_by_block_type_and_resource_value(
        "Pop",
        resource,
        str(value),
        [SubscriptionLifecycle.INITIAL, SubscriptionLifecycle.PROVISIONING, SubscriptionLifecycle.ACTIVE],
    )
    for instance in instances:
        if exclude_subscription_id is not None and str(instance.subscription_id) == str(exclude_subscription_id):
            continue
        return str(instance.subscription_id)
    return None


def initial_input_form_generator(product_name: str) -> FormGenerator:
    user_input_dict = yield from customer_choice_form_page(title=product_name)

    class CreatePopForm(FormPage):
        model_config = ConfigDict(title=product_name)

        code: str
        full_name: str
        netbox_id: int
        latitude: LatitudeCoordinate
        longitude: LongitudeCoordinate

        @model_validator(mode="after")
        def validate_data(self) -> "CreatePopForm":
            if self.code and not match(r"^[A-Z0-9]{4}$", self.code):
                msg = "code must be 4 uppercase alphanumeric characters, e.g. 'AZ99'"
                raise ValueError(msg)

            if not self.full_name.startswith(self.code):
                msg = "full_name must start with the code, e.g. 'AZ99-Alpha'"
                raise ValueError(msg)

            for resource, value in [
                ("netbox_id", self.netbox_id),
                ("code", self.code),
            ]:
                if conflicting := pop_resource_in_use(resource, value):
                    raise ValueError(f"{resource} {value} already in use by subscription {conflicting}")
            check_location_code_uniqueness(normalize_location_code(self.code))

            return self

    user_input_dict.update((yield CreatePopForm).model_dump())

    summary_fields = [
        "customer_id",
        "netbox_id",
        "code",
        "full_name",
        "latitude",
        "longitude",
    ]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Construct Subscription model")
def construct_pop_model(
    product: UUIDstr,
    customer_id: UUIDstr,
    netbox_id: int,
    code: str,
    full_name: str,
    latitude: LatitudeCoordinate,
    longitude: LongitudeCoordinate,
) -> State:
    pop = PopInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )
    pop.pop.code = code
    pop.pop.full_name = full_name
    pop.pop.netbox_id = netbox_id
    pop.pop.latitude = latitude
    pop.pop.longitude = longitude

    pop = PopProvisioning.from_other_lifecycle(pop, SubscriptionLifecycle.PROVISIONING)
    pop.description = subscription_description(pop)

    return {
        "subscription": pop,
        "subscription_id": pop.subscription_id,  # necessary to be able to use older generic step functions
        "subscription_description": pop.description,
    }


@create_workflow(initial_input_form=initial_input_form_generator)
def create_pop() -> StepList:
    return (
        begin
        >> construct_pop_model
        >> forward_sync_pop_to_optical_block_step
        >> backward_sync_optical_block_to_pop_step
        >> store_process_subscription()
    )
