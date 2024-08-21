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
    entities = ['question', 'answer', 'comment']
    permissions = []

    for entity in entities:
        permissions.extend(
            [
                {'name': f'read_any_{entity}'},
                {'name': f'create_own_{entity}'},
                {'name': f'update_own_{entity}'},
                {'name': f'delete_own_{entity}'},
                {'name': f'update_any_{entity}'},
                {'name': f'delete_any_{entity}'}
            ]
        )

    # Add additional permissions
    permissions.extend(
        [
            {'name': 'upvote'},
            {'name': 'downvote'},
            {'name': 'create_permission'},
            {'name': 'attach_permission'},
            {'name': 'create_role'},
            {'name': 'attach_role'},
            {'name': 'ban_user'},
            {'name': 'unban_user'},
            {'name': 'create_tag'},
            {'name': 'delete_tag'}
        ]
    )

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

    user_permissions = [
        'read_any_question',
        'create_own_question',
        'update_own_question',
        'delete_own_question',
        'read_any_answer',
        'create_own_answer',
        'update_own_answer',
        'delete_own_answer',
        'read_any_comment',
        'create_own_comment',
        'update_own_comment',
        'delete_own_comment',
        'upvote',
        'downvote',
    ]

    advanced_user_permissions = user_permissions + [
        'create_tag'
    ]

    moderator_permissions = advanced_user_permissions + [
        'update_any_question',
        'update_any_answer',
        'update_any_comment',
        'delete_any_question',
        'delete_any_answer',
        'delete_any_comment',
        'delete_tag'
    ]

    admin_permissions = moderator_permissions + [
        'ban_user',
        'unban_user'
    ]

    role_permissions = []

    role_permissions_map = {
        'superuser': list(permission_dict.keys()),
        'user': user_permissions,
        'advanced_user': advanced_user_permissions,
        'moderator': moderator_permissions,
        'admin': admin_permissions
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
        'read_any_answer',
        'create_own_answer',
        'update_own_answer',
        'delete_own_answer',
        'update_any_answer',
        'delete_any_answer',
        'read_any_comment',
        'create_own_comment',
        'update_own_comment',
        'delete_own_comment',
        'update_any_comment',
        'delete_any_comment',
        'create_permission',
        'attach_permission',
        'create_role',
        'attach_role',
        'ban_user',
        'unban_user'
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
