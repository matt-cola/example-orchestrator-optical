"""Point of Presence product blocks (consumer-owned).

Copied from the GARR Workflow Orchestrator
(``garr/products/product_blocks/pop.py``) as the pre-existing consumer model of
the anti-corruption example: this is what a consumer already has in production
*before* adopting the optical module. Two deliberate deviations from the GARR
source, both documented where they are used:

1. The coordinate import points at the optical module's copy of the string
   coordinate types (``orchestrator.optical.utils.custom_types.coordinates``);
   this repo has no ``utils/`` package and the types are identical.
2. Every lifecycle variant composes the shipped
   ``OpticalModuleLocationBlock`` under ``optical_location`` (composition, never
   inheritance — the consumption path 2 of the module README). The field is
   ``Optional`` so pre-existing subscriptions without a location still load;
   presence is enforced by the backfill task and the validate workflow, not by
   the models.
3. ``PoPBlockProvisioning`` requires ``latitude``/``longitude`` (GARR leaves
   them optional): the composed optical block needs them from PROVISIONING on,
   so anything moving forward must supply them. ACTIVE keeps them optional so
   legacy rows still load and are fixed on their next modify.
"""

from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlock,
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.utils.custom_types.coordinates import LatitudeCoordinate, LongitudeCoordinate
from pydantic import computed_field


class PoPBlockInactive(ProductBlockModel, product_block_name="PoP"):
    netbox_id: int | None = None
    code: str | None = None
    full_name: str | None = None
    latitude: LatitudeCoordinate | None = None
    longitude: LongitudeCoordinate | None = None
    optical_location: OpticalModuleLocationBlockInactive | None = None


class PoPBlockProvisioning(PoPBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    netbox_id: int
    code: str | None = None
    full_name: str | None = None
    latitude: LatitudeCoordinate
    longitude: LongitudeCoordinate
    optical_location: OpticalModuleLocationBlockProvisioning | None = None


class PoPBlock(PoPBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    netbox_id: int
    code: str
    full_name: str
    latitude: LatitudeCoordinate | None = None
    longitude: LongitudeCoordinate | None = None
    optical_location: OpticalModuleLocationBlock | None = None

    @computed_field
    @property
    def title(self) -> str:
        return f"{self.full_name}"
