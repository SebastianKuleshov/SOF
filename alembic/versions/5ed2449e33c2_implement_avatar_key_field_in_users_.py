"""implement avatar_key field in users table

Revision ID: 5ed2449e33c2
Revises: e2a4903b9b84
Create Date: 2024-08-22 11:41:50.765593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ed2449e33c2'
down_revision: Union[str, None] = 'e2a4903b9b84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_key', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_key')
    # ### end Alembic commands ###
