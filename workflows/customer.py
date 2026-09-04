"""Customer selection for the example optical orchestrator.

The orchestrator-optical workflows collect the subscription customer through a
``Choice`` built by a function defined in the user code-space, wired via the
``OPTICAL_CUSTOMER_CHOICE`` environment variable (import path
``module.path:function_name``) or the
``orchestrator.optical.workflows.customer.register_customer_choice`` hook.

This example serves a static pair of test customers so every shipped create
and modify workflow can be exercised through the UI without an external
system of record.
"""

from pydantic_forms.validators import Choice


def customer_choice() -> type[Choice]:
    """Return the customer selector used by the shipped workflows."""
    customers = {
        "2f19b5c2-5c62-41d8-97cd-52b31993ee1e": "Example NREN",
        "db2b8c9d-0d5a-4f4b-8dc3-4e1e1d0e9f0a": "Example Research Institute",
    }
    return Choice("CustomerEnum", zip(customers.keys(), customers.items(), strict=False))
