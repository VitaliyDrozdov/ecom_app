"""Alter User table. is_activae -> default=True

Revision ID: 88c62de34604
Revises: c5b968f306f9
Create Date: 2025-02-05 18:16:04.571075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88c62de34604'
down_revision: Union[str, None] = 'c5b968f306f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
