"""add unique constraint on listing_contact name phone email

Revision ID: c48a6436086c
Revises: fdc9a82eee1a
Create Date: 2026-07-16 23:30:52.611705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c48a6436086c'
down_revision: Union[str, Sequence[str], None] = 'fdc9a82eee1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Note: rentcast_stats is intentionally excluded — it's managed outside
    # SQLModel metadata (raw SQL via db/constants.py), not part of this migration.
    op.create_unique_constraint('uq_listing_contact_identity', 'listing_contact', ['name', 'phone', 'email'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_listing_contact_identity', 'listing_contact', type_='unique')
