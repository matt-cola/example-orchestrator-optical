"""Validate Point of Presence workflow (consumer-owned).

Copied from the GARR Workflow Orchestrator
(``garr/workflows/pop/validate_pop.py``), modulo the import paths
(``orchestrator.core`` in orchestrator-core 5.x) and the dropped deprecated
``description`` decorator argument. Extended with the contract gate of the
anti-corruption example: besides loading the subscription, validation requires
the composed optical location block to be present (i.e. the subscription went
through composition — create/modify after adoption, or the backfill task) and
runs the shipped block-level validation on it.
"""

from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.utils import validate_workflow
from orchestrator.optical.workflows.optical_location.validate_optical_location import (
    validate_optical_module_location_block,
)
from pydantic_forms.types import State
from structlog import get_logger

from products.product_types.pop import PoP

logger = get_logger(__name__)


@step("Load initial state")
def load_initial_state_pop(subscription: PoP) -> State:
    return {
        "subscription": subscription,
    }


@step("Validate composed optical location block")
def validate_composed_optical_location_block(subscription: PoP) -> State:
    """Validate the composed optical location block of the subscription.

    This is the contract gate: every ACTIVE PoP is expected to carry a fully
    populated optical location block by now (populated at create/modify time or
    by the backfill task). A missing block means the subscription predates the
    composition and was never backfilled — modify it (or run the backfill task)
    instead of weakening this check.
    """
    optical_module_block = subscription.pop.optical_location
    if optical_module_block is None:
        msg = (
            f"PoP subscription {subscription.subscription_id} has no composed optical location block: "
            "run the backfill task or modify the subscription to populate it"
        )
        raise ValueError(msg)
    validate_optical_module_location_block(optical_module_block)
    return {}


@validate_workflow()
def validate_pop() -> StepList:
    return begin >> load_initial_state_pop >> validate_composed_optical_location_block
