"""Product registration for the example optical orchestrator.

Importing the orchestrator-optical module's products adds the shipped product
types to the orchestrator-core ``SUBSCRIPTION_MODEL_REGISTRY``.
"""

import orchestrator.optical.products  # noqa: F401  Side-effects: registers the shipped product types
