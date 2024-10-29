"""Update User

Revision ID: 15c3bee626d8
Revises: 4d6976b959ae
Create Date: 2024-10-28 13:27:39.842480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15c3bee626d8'
down_revision: Union[str, None] = '4d6976b959ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('telegram_id', sa.String(length=320), nullable=True))
    op.create_unique_constraint(None, 'user', ['telegram_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'telegram_id')
    # ### end Alembic commands ###