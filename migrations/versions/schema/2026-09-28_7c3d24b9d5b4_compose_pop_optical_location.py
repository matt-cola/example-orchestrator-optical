"""Compose the shipped optical location block into the consumer PoP block.

This is the "expand" step of the anti-corruption adoption: it wires the
consumer-owned ``PoP`` product block to the shipped
``OpticalModuleLocationBlock`` (created by the optical module's own baseline,
which the data-head anchor orders before this migration) and registers the
backfill task. No product, block or resource type is created here — only the
relation between the two existing blocks plus the task row. Every other shipped
catalog row stays untouched: the shipped location workflows remain registered
alongside the PoP ones, so both consumption paths coexist.

The block ids are resolved by name at migration time on purpose: the optical
baseline generates its ids per import, so they cannot be frozen here.

Revision ID: 7c3d24b9d5b4
Revises: 2da4299d3560
Create Date: 2026-09-28
"""

import sqlalchemy as sa
from alembic import op
from orchestrator.core.migrations.helpers import (
    add_product_block_relation_between_products_by_id,
    create_task,
    delete_workflow,
    get_product_block_id_by_name,
    remove_product_block_relation_between_products_by_id,
)

# revision identifiers, used by Alembic.
revision = "7c3d24b9d5b4"
down_revision = "2da4299d3560"
branch_labels = None
depends_on = None

backfill_task = {
    "name": "backfill_pop_optical_blocks",
    "description": "backfill composed optical location blocks of pre-existing PoP subscriptions",
}


def _relation_exists(conn, in_use_by_id, depends_on_id) -> bool:
    result = conn.execute(
        sa.text(
            """
            SELECT 1 FROM product_block_relations
            WHERE in_use_by_id = :in_use_by_id AND depends_on_id = :depends_on_id
            """
        ),
        {"in_use_by_id": in_use_by_id, "depends_on_id": depends_on_id},
    )
    return result.first() is not None


def upgrade() -> None:
    conn = op.get_bind()
    pop_block_id = str(get_product_block_id_by_name(conn, "PoP"))
    location_block_id = str(get_product_block_id_by_name(conn, "OpticalModuleLocationBlock"))
    if not _relation_exists(conn, pop_block_id, location_block_id):
        add_product_block_relation_between_products_by_id(conn, pop_block_id, location_block_id)
    create_task(conn, backfill_task)


def downgrade() -> None:
    conn = op.get_bind()
    delete_workflow(conn, backfill_task["name"])
    pop_block_id = str(get_product_block_id_by_name(conn, "PoP"))
    location_block_id = str(get_product_block_id_by_name(conn, "OpticalModuleLocationBlock"))
    if _relation_exists(conn, pop_block_id, location_block_id):
        remove_product_block_relation_between_products_by_id(conn, pop_block_id, location_block_id)
