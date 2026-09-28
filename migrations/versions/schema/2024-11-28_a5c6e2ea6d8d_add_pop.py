"""Add pop product.

Copied from the GARR Workflow Orchestrator
(``garr/migrations/versions/schema/2024-11-28_a5c6e2ea6d8d_add_pop.py``) as the
pre-existing consumer catalog of the anti-corruption example: this is the
migration a consumer already ran in production *before* adopting the optical
module. It is the first node of this repo's ``data`` branch — the empty
data-head anchor chains onto it, and the anchor's ``depends_on`` still orders
everything after the optical baseline.

Revision ID: a5c6e2ea6d8d
Revises:
Create Date: 2024-11-28 18:57:53.321893

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
revision = "a5c6e2ea6d8d"
down_revision = None
branch_labels = ("data",)
depends_on = "ca79fd834ba0"

new_products = {
    "products": {
        "pop": {
            "product_id": "0cefb9de-7fb1-41c4-8f3a-7934b3a83f11",
            "product_type": "PoP",
            "description": "Product of a Point of Presence",
            "tag": "POP",
            "status": "active",
            "root_product_block": "PoP",
            "fixed_inputs": {},
        },
    },
    "product_blocks": {
        "PoP": {
            "product_block_id": "6847d1a5-6c16-44f4-a0c4-43ca8f4b17ee",
            "description": "Product Block of a Point of Presence",
            "tag": "POP",
            "status": "active",
            "resources": {
                "netbox_id": "ID of the Point of Presence in NetBox",
                "code": "Unique code of the Point of Presence, e.g. AZ99",
                "full_name": "Full name of the Point of Presence",
                "latitude": "Latitude of the Point of Presence",
                "longitude": "Longitude of the Point of Presence",
            },
            "depends_on_block_relations": [],
        },
    },
    "workflows": {},
}

new_workflows = [
    {
        "name": "create_pop",
        "target": Target.CREATE,
        "description": "create Point of Presence",
        "product_type": "PoP",
    },
    {
        "name": "modify_pop",
        "target": Target.MODIFY,
        "description": "modify Point of Presence",
        "product_type": "PoP",
    },
    {
        "name": "terminate_pop",
        "target": Target.TERMINATE,
        "description": "terminate Point of Presence",
        "product_type": "PoP",
    },
    {
        "name": "validate_pop",
        "target": Target.VALIDATE,
        "description": "validate Point of Presence",
        "product_type": "PoP",
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
