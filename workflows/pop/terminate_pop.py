"""Terminate Point of Presence workflow (consumer-owned).

Copied from the GARR Workflow Orchestrator
(``garr/workflows/pop/terminate_pop.py``), modulo the import paths
(``orchestrator.core`` in orchestrator-core 5.x) and the dropped deprecated
``description``/``additional_steps`` decorator arguments (descriptions live in
the database now). The OSS/BSS stub stays a stub, like in the source. No
optical-specific teardown is needed: the location family has no device state,
so the composed block tree terminates with the subscription.
"""

from orchestrator.core.forms import FormPage
from orchestrator.core.forms.validators import DisplaySubscription
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import terminate_workflow
from pydantic_forms.types import InputForm, State, UUIDstr
from structlog import get_logger

from products.product_types.pop import Pop

logger = get_logger(__name__)


def terminate_initial_input_form_generator(subscription_id: UUIDstr, customer_id: UUIDstr) -> InputForm:
    temp_subscription_id = subscription_id

    class TerminatePopForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore

    return TerminatePopForm


@step("Delete subscription from OSS/BSS")
def delete_subscription_from_oss_bss(subscription: Pop) -> State:
    # TODO: add actual call to OSS/BSS to delete subscription

    return {}


@terminate_workflow(initial_input_form=terminate_initial_input_form_generator)
def terminate_pop() -> StepList:
    return (
        begin >> delete_subscription_from_oss_bss
        # TODO: fill in additional steps if needed
    )
