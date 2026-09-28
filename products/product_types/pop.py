"""Point of Presence subscription product types (consumer-owned).

Copied verbatim from the GARR Workflow Orchestrator
(``garr/products/product_types/pop.py``), modulo the import path of
``SubscriptionModel`` (``orchestrator.core`` in orchestrator-core 5.x).
"""

from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle

from products.product_blocks.pop import PoPBlock, PoPBlockInactive, PoPBlockProvisioning


class PopInactive(SubscriptionModel, is_base=True):
    pop: PoPBlockInactive


class PopProvisioning(PopInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    pop: PoPBlockProvisioning


class PoP(PopProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    pop: PoPBlock
