"""Anti-corruption wiring between the consumer-owned PoP fields and the shipped optical location block.

This module is the whole "anti-corruption layer" of the example: the only place
that knows both shapes. Everything else is single-shape — the PoP workflows speak
PoP-native (``code``, ``full_name``, coordinates, ``netbox_id``)
and the module speaks the shipped ``OpticalModuleLocationBlock``. The mapping:

* ``code`` (consumer convention: 4 uppercase alphanumerics, e.g. ``AZ99``) is
  **normalized** to the module's ``LocationCode`` (lowercase alphanumeric +
  hyphens, e.g. ``az99``) by :func:`normalize_location_code`. The direction is
  **forward-only**: the normalized value is never copied back, which would
  corrupt the consumer casing.
* ``full_name`` <-> ``location_name`` and the coordinates flow **both ways**;
  ``netbox_id`` is consumer-only and never crosses the boundary.

The layer has three callers sharing one transformation: the create workflow, the
modify workflow (ongoing sync) and the backfill task (one-shot sync of
pre-existing subscriptions).
"""

import re

from orchestrator.core.domain.lifecycle import lookup_specialized_type
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import step
from orchestrator.optical.products.product_blocks.optical_location import (
    LocationCode,
    OpticalModuleLocationBlockInactive,
)
from orchestrator.optical.workflows.optical_location.create_optical_location import (
    populate_optical_module_location_block,
)
from pydantic import TypeAdapter
from pydantic_forms.types import State

from products.product_blocks.pop import PoPBlockInactive
from products.product_types.pop import PoP, PopProvisioning

_LOCATION_CODE_ADAPTER = TypeAdapter(LocationCode)


def normalize_location_code(code: str) -> LocationCode:
    """Normalize a consumer PoP code to the module's ``LocationCode``.

    Lowercase the code and collapse every run of non-alphanumeric characters to
    a single hyphen (e.g. ``AZ99`` -> ``az99``). The result is validated against
    the shipped ``LocationCode`` type, so a code with no usable characters fails
    here with a clear error instead of deep inside the module.

    Args:
        code: The consumer PoP code, e.g. ``AZ99``.

    Returns:
        The normalized location code, e.g. ``az99``.

    Raises:
        ValueError: If nothing usable remains after normalization.
    """
    normalized = re.sub(r"[^a-z0-9]+", "-", code.lower()).strip("-")
    return _LOCATION_CODE_ADAPTER.validate_python(normalized)


def _require_pop_mirror_fields(pop: PoPBlockInactive) -> tuple[str, str, str, str]:
    """Return the PoP mirror fields, raising a clear error when any is missing.

    The composed optical block requires all four from PROVISIONING on, so every
    caller (create, modify, backfill) funnels through here instead of failing
    later on a half-populated block.

    Raises:
        ValueError: If ``code``, ``full_name`` or either coordinate is unset,
            naming the subscription that needs fixing.
    """
    if pop.code is None or pop.full_name is None or pop.latitude is None or pop.longitude is None:
        msg = (
            "Cannot sync PoP to the optical location block: "
            f"code={pop.code!r}, full_name={pop.full_name!r}, "
            f"latitude={pop.latitude!r}, longitude={pop.longitude!r}. "
            "Fill the missing PoP fields first (modify the subscription)."
        )
        raise ValueError(msg)
    return pop.code, pop.full_name, pop.latitude, pop.longitude


def forward_sync_pop_to_optical_block(
    pop: PoPBlockInactive,
    *,
    owner_subscription_id: str,
    status: SubscriptionLifecycle,
) -> OpticalModuleLocationBlockInactive:
    """Populate the composed optical location block from the PoP mirror fields.

    Reuses the existing composed block when there is one (modify of an already
    composed subscription, backfill re-run) and builds a fresh block otherwise,
    in the lifecycle variant matching the owner's current ``status`` (blocks
    always carry instance ids, so they are built with ``new()``, never with a
    bare constructor). Population itself goes through the shipped
    :func:`populate_optical_module_location_block` — the module's documented
    anti-corruption point — which re-checks the ``location_code`` uniqueness at
    execution time.

    Args:
        pop: The consumer PoP block (any lifecycle variant).
        owner_subscription_id: Id of the owning subscription, needed to anchor
            a freshly built block.
        status: Current lifecycle status of the owner subscription; selects the
            variant of a freshly built block.

    Returns:
        The populated optical location block, also assigned back onto
        ``pop.optical_location``.
    """
    code, full_name, latitude, longitude = _require_pop_mirror_fields(pop)
    optical_module_block = pop.optical_location
    if optical_module_block is None:
        # Blocks always carry instance ids, so they are built with ``new()``
        # (never with a bare constructor) — and ``new()`` only works on the
        # all-optional INACTIVE variant.
        optical_module_block = OpticalModuleLocationBlockInactive.new(owner_subscription_id)
    populate_optical_module_location_block(
        optical_module_block=optical_module_block,
        longitude=longitude,  # type: ignore[arg-type]
        latitude=latitude,  # type: ignore[arg-type]
        location_code=normalize_location_code(code),
        location_name=full_name,
    )
    block_class = lookup_specialized_type(OpticalModuleLocationBlockInactive, status)
    if not isinstance(optical_module_block, block_class):
        # Convert to the status-matching variant. A plain ``model_validate``
        # round-trip would drop the instance's db model and the later tree save
        # would fail, so it is carried over explicitly.
        converted = block_class(**optical_module_block.model_dump())
        converted._db_model = optical_module_block._db_model
        optical_module_block = converted
    pop.optical_location = optical_module_block
    return optical_module_block


def backward_sync_optical_block_to_pop(pop: PoPBlockInactive) -> None:
    """Copy the persisted optical block values back onto the PoP mirror fields.

    Selective by design: ``location_name`` and the coordinates flow back, but
    ``location_code`` is never copied into ``code`` — that would overwrite the
    consumer's uppercase convention (``AZ99``) with the normalized form
    (``az99``).

    Args:
        pop: The consumer PoP block (any lifecycle variant); no-op when it has
            no composed block yet.
    """
    optical_module_block = pop.optical_location
    if optical_module_block is None:
        return
    if optical_module_block.location_name:
        pop.full_name = optical_module_block.location_name
    if optical_module_block.latitude is not None:
        pop.latitude = optical_module_block.latitude  # type: ignore[assignment]
    if optical_module_block.longitude is not None:
        pop.longitude = optical_module_block.longitude  # type: ignore[assignment]


@step("Forward sync PoP fields to optical location block")
def forward_sync_pop_to_optical_block_step(subscription: PoP | PopProvisioning) -> State:
    """Populate the composed optical block of the subscription in the state.

    Runs after the construct/update step (PoP-native fields are set) and before
    the subscription tree is saved, so the composed block is persisted together
    with it.

    Args:
        subscription: The PoP subscription being created, modified or backfilled.

    Returns:
        The state with the updated subscription.
    """
    forward_sync_pop_to_optical_block(
        subscription.pop,
        owner_subscription_id=str(subscription.subscription_id),
        status=subscription.status,
    )
    return {"subscription": subscription}


@step("Backward sync optical location block to PoP fields")
def backward_sync_optical_block_to_pop_step(subscription: PoP | PopProvisioning) -> State:
    """Copy the composed optical block values back onto the PoP mirror fields.

    Runs after the subscription (and its composed tree) is saved, keeping the
    mirrored fields in sync with what is actually persisted.

    Args:
        subscription: The PoP subscription being created, modified or backfilled.

    Returns:
        The state with the updated subscription.
    """
    backward_sync_optical_block_to_pop(subscription.pop)
    return {"subscription": subscription}
