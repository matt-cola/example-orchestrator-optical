"""Rename the PoP product type and product block from ``PoP`` to ``Pop``.

Only names change: subscriptions, instances and relations reference products
and blocks by id, so existing PoP subscriptions are untouched.

Revision ID: 3f8e1c6a9b2d
Revises: 78a0cb032e0e
Create Date: 2026-11-24

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3f8e1c6a9b2d"
down_revision = "78a0cb032e0e"
branch_labels = None
depends_on = None


def _rename(old: str, new: str) -> None:
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE products SET product_type = :new WHERE product_type = :old"), {"old": old, "new": new})
    conn.execute(sa.text("UPDATE product_blocks SET name = :new WHERE name = :old"), {"old": old, "new": new})


def upgrade() -> None:
    _rename("PoP", "Pop")


def downgrade() -> None:
    _rename("Pop", "PoP")
