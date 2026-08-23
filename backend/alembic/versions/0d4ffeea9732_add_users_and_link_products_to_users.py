"""add users and link products to users

Revision ID: 0d4ffeea9732
Revises: 48ec60792024
Create Date: 2026-08-23 18:53:56.977478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d4ffeea9732'
down_revision: Union[str, Sequence[str], None] = '48ec60792024'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Create users table
    op.create_table(
        'users',

        sa.Column(
            'id',
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            'name',
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            'email',
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            'password_hash',
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            'google_id',
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            'auth_provider',
            sa.String(length=20),
            nullable=False
        ),

        sa.Column(
            'profile_picture_url',
            sa.String(length=500),
            nullable=True
        ),

        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        ),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('google_id')
    )

    # Create unique email index
    op.create_index(
        op.f('ix_users_email'),
        'users',
        ['email'],
        unique=True
    )

    # Add user_id to products
    op.add_column(
        'product_details',
        sa.Column(
            'user_id',
            sa.Integer(),
            nullable=False
        )
    )

    # Add foreign key
    op.create_foreign_key(
        'fk_product_details_user_id',
        'product_details',
        'users',
        ['user_id'],
        ['id']
    )

def downgrade() -> None:

    op.drop_constraint(
        'fk_product_details_user_id',
        'product_details',
        type_='foreignkey'
    )

    op.drop_column(
        'product_details',
        'user_id'
    )

    op.drop_index(
        op.f('ix_users_email'),
        table_name='users'
    )

    op.drop_table('users')