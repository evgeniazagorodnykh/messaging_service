"""Update Message

Revision ID: 745ce49bdb28
Revises: d441edacb87b
Create Date: 2024-10-25 11:34:39.537929

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '745ce49bdb28'
down_revision: Union[str, None] = 'd441edacb87b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('delivered', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'delivered')
    # ### end Alembic commands ###
