"""implement user with superuser role

Revision ID: e2a4903b9b84
Revises: d3a84f8c2b45
Create Date: 2024-08-20 13:31:08.035379

"""
import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from dotenv import load_dotenv

from app.dependencies import pwd_context

# revision identifiers, used by Alembic.
revision: str = 'e2a4903b9b84'
down_revision: Union[str, None] = 'd3a84f8c2b45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

load_dotenv()


def upgrade() -> None:
    superuser_email = os.getenv('SUPERUSER_EMAIL')
    superuser_password = os.getenv('SUPERUSER_PASSWORD')

    superuser_password = pwd_context.hash(superuser_password)

    if not superuser_email or not superuser_password:
        raise Exception(
            "SUPERUSER_EMAIL or SUPERUSER_PASSWORD environment variables are not set."
        )

    metadata_obj = sa.MetaData()
    metadata_obj.reflect(
        bind=op.get_bind(), only=('users', 'role_user', 'roles')
    )
    users_table = sa.Table('users', metadata_obj)
    role_user_table = sa.Table('role_user', metadata_obj)
    roles_table = sa.Table('roles', metadata_obj)

    connection = op.get_bind()

    connection.execute(
        users_table.insert().values(
            email=superuser_email,
            password=superuser_password,
            nick_name='superuser',
            reputation=0,
            updated_at=sa.text('now()')
        )
    )

    query = sa.select(users_table.c.id).where(
        users_table.c.email == superuser_email
    )
    result = connection.execute(query)
    superuser_id = result.scalar()

    query = sa.select(roles_table.c.id).where(
        roles_table.c.name == 'superuser'
    )
    result = connection.execute(query)
    superuser_role_id = result.scalar()

    op.bulk_insert(
        role_user_table,
        [{
            'role_id': superuser_role_id,
            'user_id': superuser_id
        }]
    )


def downgrade() -> None:
    superuser_email = os.getenv('SUPERUSER_EMAIL')

    if not superuser_email:
        raise Exception(
            "SUPERUSER_EMAIL environment variable is not set."
        )

    metadata_obj = sa.MetaData()
    metadata_obj.reflect(
        bind=op.get_bind(), only=('users', 'role_user')
    )
    users_table = sa.Table('users', metadata_obj)
    role_user_table = sa.Table('role_user', metadata_obj)

    # Fetch the user ID of the superuser
    connection = op.get_bind()
    query = sa.select(users_table.c.id).where(
        users_table.c.email == superuser_email
    )
    result = connection.execute(query)
    superuser_id = result.scalar()

    if superuser_id:
        # Delete from role_user table
        connection.execute(
            role_user_table.delete().where(
                role_user_table.c.user_id == superuser_id
            )
        )

        # Delete the superuser from users table
        connection.execute(
            users_table.delete().where(
                users_table.c.id == superuser_id
            )
        )
