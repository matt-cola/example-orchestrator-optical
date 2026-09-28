"""Modify Point of Presence workflow (consumer-owned).

Copied from the GARR Workflow Orchestrator (``garr/workflows/pop/modify_pop.py``)
as the pre-existing consumer workflow of the anti-corruption example, extended
with the optical wiring: after the update step the forward-sync step refreshes
the composed optical location block from the PoP-native fields, and the
backward-sync step copies the block values back. The engine persist at the end
of the workflow saves the whole tree.
"""

from re import match
from typing import Annotated

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.forms import FormPage
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import set_status
from orchestrator.core.workflows.utils import modify_workflow
from orchestrator.optical.utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate
from orchestrator.optical.workflows.optical_location.shared import check_location_code_uniqueness
from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from products.product_types.pop import PoP
from workflows.pop.create_pop import pop_resource_in_use
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

Instruction = Annotated[
    str,
    Field(
        "Fields are pre-filled with the current subscription values. "
        "Keep them unchanged if they are correct. "
        "The subscription will be updated with the new values.",
        title="ℹ️ℹ️ℹ️ Instruction ℹ️ℹ️ℹ️",
        json_schema_extra={
            "disabled": True,
        },
    ),
]


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    subscription = PoP.from_subscription(subscription_id)
    pop = subscription.pop

    class ModifyPopForm(FormPage):
        instruction: Instruction

        netbox_id: int | None = pop.netbox_id
        code: str | None = pop.code
        full_name: str | None = pop.full_name
        latitude: LatitudeCoordinate | None = pop.latitude  # type: ignore[assignment]
        longitude: LongitudeCoordinate | None = pop.longitude  # type: ignore[assignment]

        @model_validator(mode="after")
        def validate_data(self) -> "ModifyPopForm":
            if self.code and not match(r"^[A-Z0-9]{4}$", self.code):
                msg = "code must be 4 uppercase alphanumeric characters, e.g. 'AZ99'"
                raise ValueError(msg)
            if self.code and self.full_name and not self.full_name.startswith(self.code):
                msg = "full_name must start with the code, e.g. 'AZ99-Alpha'"
                raise ValueError(msg)
            if self.latitude is None or self.longitude is None:
                msg = "latitude and longitude are required: the optical location block needs them"
                raise ValueError(msg)
            exclude = str(subscription.subscription_id)
            for resource, value in [
                ("netbox_id", self.netbox_id),
                ("code", self.code),
            ]:
                if value is not None and (
                    conflicting := pop_resource_in_use(resource, value, exclude_subscription_id=exclude)
                ):
                    raise ValueError(f"{resource} {value} already in use by subscription {conflicting}")
            if self.code is not None:
                check_location_code_uniqueness(normalize_location_code(self.code), exclude_subscription_id=exclude)
            return self

    user_input = yield ModifyPopForm
    user_input_dict = user_input.model_dump()

    return user_input_dict | {"subscription": subscription}


@step("Update subscription")
def update_subscription(
    subscription: PoP,
    netbox_id: int | None,
    code: str | None,
    full_name: str | None,
    latitude: LatitudeCoordinate | None,
    longitude: LongitudeCoordinate | None,
) -> State:
    # NOTE: annotated as the ACTIVE model on purpose (GARR used PopProvisioning).
    # Step arguments are reloaded from the database in the step's lifecycle
    # variant, and legacy rows without coordinates cannot load as Provisioning
    # (coordinates are required there) — which would block the modify that is
    # supposed to fix them. The form requires the coordinates and the forward
    # sync asserts them, so the saved tree always satisfies Provisioning.
    pop = subscription.pop

    if netbox_id is not None:
        pop.netbox_id = netbox_id
    if code is not None:
        pop.code = code
    if full_name is not None:
        pop.full_name = full_name
    if latitude is not None:
        pop.latitude = latitude
    if longitude is not None:
        pop.longitude = longitude

    return {"subscription": subscription}


@step("Update subscription description")
def update_subscription_description(subscription: PoP) -> State:
    subscription.description = subscription_description(subscription)
    return {"subscription": subscription}


@modify_workflow(initial_input_form=initial_input_form_generator)
def modify_pop() -> StepList:
    # NOTE: ``update_subscription`` runs before the first ``set_status`` (GARR
    # does it the other way around). The PROVISIONING transition converts and
    # validates the whole tree — including the required coordinates — so legacy
    # rows without coordinates must receive the form values first; otherwise
    # the transition itself fails and the remediation modify can never run.
    return (
        begin
        >> update_subscription
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> forward_sync_pop_to_optical_block_step
        >> backward_sync_optical_block_to_pop_step
        >> update_subscription_description
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
