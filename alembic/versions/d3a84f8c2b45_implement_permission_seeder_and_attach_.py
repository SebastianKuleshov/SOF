"""implement permission seeder and attach to roles

Revision ID: d3a84f8c2b45
Revises: bb1f0b636ff8
Create Date: 2024-08-20 12:06:00.346948

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd3a84f8c2b45'
down_revision: Union[str, None] = 'bb1f0b636ff8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    permissions = [
        {'name': 'read_any_question'},
        {'name': 'create_own_question'},
        {'name': 'update_own_question'},
        {'name': 'delete_own_question'},
        {'name': 'update_any_question'},
        {'name': 'delete_any_question'},
        {'name': 'create_permission'},
        {'name': 'give_permission'},
        {'name': 'create_role'},
        {'name': 'give_role'}
    ]

    op.bulk_insert(
        sa.table(
            'permissions',
            sa.column('name', sa.String)
        ),
        permissions
    )

    connection = op.get_bind()
    roles = connection.execute(
        sa.text("SELECT id, name FROM roles")
    ).fetchall()
    role_dict = {
        role[1]: role[0]
        for role in roles
    }

    # Fetch permission IDs
    permissions = connection.execute(
        sa.text("SELECT id, name FROM permissions")
    ).fetchall()
    permission_dict = {
        permission[1]: permission[0]
        for permission in permissions
    }

    role_permissions = []

    role_permissions_map = {
        'superuser': list(permission_dict.keys()),
        'user': [
            'read_any_question',
            'create_own_question',
            'update_own_question',
            'delete_own_question'
        ],
        'moderator': [
            'read_any_question',
            'create_own_question',
            'update_own_question',
            'delete_own_question',
            'update_any_question',
        ],
        'admin': [
            'read_any_question',
            'create_own_question',
            'update_own_question',
            'delete_own_question',
            'update_any_question',
            'delete_any_question'
        ]
    }

    # Populate role_permissions list
    for role, permissions in role_permissions_map.items():
        for permission_name in permissions:
            role_permissions.append(
                {
                    'role_id': role_dict[role],
                    'permission_id': permission_dict[permission_name]
                }
            )

    op.bulk_insert(
        sa.table(
            'permission_role',
            sa.column('role_id', sa.Integer),
            sa.column('permission_id', sa.Integer)
        ),
        role_permissions
    )


def downgrade() -> None:
    connection = op.get_bind()

    # Fetch permission IDs to be removed
    permissions = [
        'read_any_question',
        'create_own_question',
        'update_own_question',
        'delete_own_question',
        'update_any_question',
        'delete_any_question',
        'create_permission',
        'give_permission',
        'create_role',
        'give_role'
    ]

    permission_ids = connection.execute(
        sa.text(
            "SELECT id FROM permissions WHERE name = ANY(:permissions)"
            ).params(permissions=permissions)
    ).fetchall()

    permission_ids = [perm_id[0] for perm_id in permission_ids]

    # Delete from permission_role table
    op.execute(
        sa.text(
            "DELETE FROM permission_role WHERE permission_id = ANY(:permission_ids)"
        ).params(permission_ids=permission_ids)
    )

    # Delete permissions themselves
    op.execute(
        sa.text(
            "DELETE FROM permissions WHERE id = ANY(:permission_ids)"
            ).params(permission_ids=permission_ids)
    )
