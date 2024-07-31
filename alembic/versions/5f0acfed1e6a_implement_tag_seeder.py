"""implement tag seeder

Revision ID: 5f0acfed1e6a
Revises: 1832f591bc01
Create Date: 2024-07-31 08:34:13.403167

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5f0acfed1e6a'
down_revision: Union[str, None] = '1832f591bc01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    tags = [
        {'name': 'Python'},
        {'name': 'FastAPI'},
        {'name': 'SQLAlchemy'},
        {'name': 'Docker'},
        {'name': 'PostgreSQL'},
        {'name': 'APIs'},
        {'name': 'Web Development'},
        {'name': 'Programming'},
        {'name': 'Development'},
        {'name': 'Testing'}
    ]

    # Insert tags into the 'tags' table
    op.bulk_insert(
        sa.table(
            'tags',
            sa.column('name', sa.String)
        ),
        tags
    )


def downgrade() -> None:
    tags_to_remove = [
        'Python', 'FastAPI', 'SQLAlchemy', 'Docker', 'PostgreSQL',
        'APIs', 'Web Development', 'Programming', 'Development', 'Testing'
    ]

    # Define the tags table
    tags_table = sa.table(
        'tags',
        sa.column('name', sa.String)
    )

    # Delete tags from the 'tags' table
    op.execute(
        tags_table.delete().where(
            tags_table.c.name.in_(tags_to_remove)
        )
    )
