"""Backfill composed optical location blocks of pre-existing PoP subscriptions.

One-shot adoption task of the anti-corruption example: every PoP created before
the composition (``workflows/pop/`` + the ``7c3d24b9d5b4`` migration) has no
``optical_location`` block yet. This task populates it from the PoP-native
fields via the shared :mod:`workflows.pop.sync` transformation — the same
forward/backward sync the create/modify workflows run ongoing.

Idempotent: re-running re-syncs already-composed subscriptions. PoPs missing
``code``/``full_name``/coordinates are skipped and reported for manual fixing
via modify instead of failing the whole task.
"""

from orchestrator.core.db import db
from orchestrator.core.db.models import ProductTable, SubscriptionTable
from orchestrator.core.workflow import StepList, begin, done, step
from orchestrator.core.workflows.utils import task
from pydantic_forms.types import State
from sqlalchemy import select
from structlog import get_logger

from products.product_types.pop import PoP
from workflows.pop.sync import backward_sync_optical_block_to_pop, forward_sync_pop_to_optical_block

logger = get_logger(__name__)


@step("Backfill PoP optical location blocks")
def backfill_blocks() -> State:
    """Populate the composed optical block of every ACTIVE/PROVISIONING PoP."""
    ids = list(
        db.session.scalars(
            select(SubscriptionTable.subscription_id)
            .join(ProductTable, SubscriptionTable.product_id == ProductTable.product_id)
            .where(
                ProductTable.name == "pop",
                SubscriptionTable.status.in_(["active", "provisioning"]),
            )
        )
    )
    backfilled: list[str] = []
    skipped: list[dict[str, str]] = []
    for subscription_id in ids:
        sid = str(subscription_id)
        try:
            subscription = PoP.from_subscription(sid)
            forward_sync_pop_to_optical_block(
                subscription.pop,
                owner_subscription_id=sid,
                status=subscription.status,
            )
            backward_sync_optical_block_to_pop(subscription.pop)
            subscription.save()
            backfilled.append(sid)
        except ValueError as exc:
            logger.warning("Skipping PoP without mirror fields", subscription_id=sid, reason=str(exc))
            skipped.append({"subscription_id": sid, "reason": str(exc)})
    return {"backfilled": backfilled, "skipped": skipped}


@task()
def backfill_pop_optical_blocks() -> StepList:
    return begin >> backfill_blocks >> done
