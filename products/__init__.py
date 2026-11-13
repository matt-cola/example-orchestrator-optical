"""Product registration for the example optical orchestrator.

Importing the orchestrator-optical module's products adds the shipped product
types to the orchestrator-core ``SUBSCRIPTION_MODEL_REGISTRY`` (keyed by
product name, exactly like the module does). The consumer-owned PoP product is
registered the same way below: the ``pop`` product name maps to the ``PoP``
subscription model, and the ``customer`` product name to the ``Customer`` one.
"""

import orchestrator.optical.products  # noqa: F401  Side-effects: registers the shipped product types
from orchestrator.core.domain import SUBSCRIPTION_MODEL_REGISTRY

from products.product_types.customer import Customer
from products.product_types.pop import PoP

SUBSCRIPTION_MODEL_REGISTRY.update({"pop": PoP, "customer": Customer})
