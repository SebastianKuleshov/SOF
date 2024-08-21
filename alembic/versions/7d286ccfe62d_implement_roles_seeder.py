"""implement roles seeder

Revision ID: 7d286ccfe62d
Revises: 0a7314f90eb1
Create Date: 2024-08-16 13:17:14.732704

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7d286ccfe62d'
down_revision: Union[str, None] = '0a7314f90eb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    roles = [
        {'name': 'superuser'},
        {'name': 'admin'},
        {'name': 'user'},
        {'name': 'moderator'},
        {'name': 'banned'}
    ]
    op.bulk_insert(
        sa.table(
            'roles',
            sa.column('name', sa.String)
        ),
        roles
    )


def downgrade() -> None:
    roles_to_remove = [
        'admin', 'user', 'moderator', 'superuser', 'banned'
    ]

    roles_table = sa.table(
        'roles',
        sa.column('name', sa.String)
    )

    op.execute(
        roles_table.delete().where(
            roles_table.c.name.in_(roles_to_remove)
        )
    )
