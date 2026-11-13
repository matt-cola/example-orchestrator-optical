"""Add customer product.

Customers are subscriptions of this consumer-owned product: the deployment has
no external CRM, so the ``subscription_id`` of a customer subscription is the
``customer_id`` of the subscriptions it owns (see ``workflows/customer/``).

Revision ID: 78a0cb032e0e
Revises: 7c3d24b9d5b4
Create Date: 2026-11-13

"""

from alembic import op
from orchestrator.core.migrations.helpers import (
    create,
    create_workflow,
    delete,
    delete_workflow,
    ensure_default_workflows,
)
from orchestrator.core.targets import Target

# revision identifiers, used by Alembic.
revision = "78a0cb032e0e"
down_revision = "7c3d24b9d5b4"
branch_labels = None
depends_on = None

new_products = {
    "products": {
        "customer": {
            "product_id": "7e2c593b-90fb-458c-832b-68ca2aea3076",
            "product_type": "Customer",
            "description": "Product of a customer",
            "tag": "CUSTOMER",
            "status": "active",
            "root_product_block": "Customer",
            "fixed_inputs": {},
        },
    },
    "product_blocks": {
        "Customer": {
            "product_block_id": "a0f1ac38-ea0c-4614-87e0-68ceb24c729b",
            "description": "Product Block of a customer",
            "tag": "CUSTOMER",
            "status": "active",
            "resources": {
                "fullname": "Full name of the customer",
                "shortcode": "Unique short code of the customer",
            },
            "depends_on_block_relations": [],
        },
    },
    "workflows": {},
}

new_workflows = [
    {
        "name": "create_customer",
        "target": Target.CREATE,
        "description": "create customer",
        "product_type": "Customer",
    },
    {
        "name": "modify_customer",
        "target": Target.MODIFY,
        "description": "modify customer",
        "product_type": "Customer",
    },
    {
        "name": "terminate_customer",
        "target": Target.TERMINATE,
        "description": "terminate customer",
        "product_type": "Customer",
    },
    {
        "name": "validate_customer",
        "target": Target.VALIDATE,
        "description": "validate customer",
        "product_type": "Customer",
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    create(conn, new_products)
    for workflow in new_workflows:
        create_workflow(conn, workflow)
    ensure_default_workflows(conn)


def downgrade() -> None:
    conn = op.get_bind()
    for workflow in new_workflows:
        delete_workflow(conn, workflow["name"])

    delete(conn, new_products)
