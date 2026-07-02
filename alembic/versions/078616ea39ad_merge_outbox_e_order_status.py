"""Merge outbox e order status

Revision ID: 078616ea39ad
Revises: a01fa662e983, c772e0abde2c
Create Date: 2026-07-01 20:50:56.148151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '078616ea39ad'
down_revision: Union[str, Sequence[str], None] = ('a01fa662e983', 'c772e0abde2c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
