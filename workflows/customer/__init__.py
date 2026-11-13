"""Customer selection for the example optical orchestrator.

The orchestrator-optical workflows collect the subscription customer through a
``Choice`` built by a function defined in the user code-space, wired via the
``OPTICAL_CUSTOMER_CHOICE`` environment variable (import path
``module.path:function_name``) or the
``orchestrator.optical.workflows.customer.register_customer_choice`` hook.

This deployment has no external CRM: customers are subscriptions of the
consumer-owned ``customer`` product (managed with the workflows in this
package), and the selector offers the ACTIVE ones. The option value is the
``subscription_id`` of the customer subscription, which becomes the
``customer_id`` of the subscription being created or modified.
"""

from orchestrator.core.types import SubscriptionLifecycle
from pydantic_forms.validators import Choice

from workflows.customer.shared import find_customers


def customer_choice() -> type[Choice]:
    """Return the customer selector used by the shipped workflows.

    The selector is empty until a first customer subscription is created with
    the ``create_customer`` workflow.
    """
    customers = {
        customer.customer_id: customer.fullname for customer in find_customers(statuses=[SubscriptionLifecycle.ACTIVE])
    }
    return Choice("CustomerEnum", zip(customers.keys(), customers.items(), strict=False))
