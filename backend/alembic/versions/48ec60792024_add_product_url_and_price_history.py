"""add product url and price history

Revision ID: 48ec60792024
Revises: eb43c386ce42
Create Date: 2026-08-23 12:27:44.701113
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '48ec60792024'
down_revision: Union[str, Sequence[str], None] = 'eb43c386ce42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Create price_history table
    op.create_table(
        'price_history',
        sa.Column(
            'id',
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            'product_id',
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            'price',
            sa.Numeric(precision=12, scale=2),
            nullable=False
        ),
        sa.Column(
            'recorded_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(
            ['product_id'],
            ['product_details.id']
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Add product_url
    op.add_column(
        'product_details',
        sa.Column(
            'product_url',
            sa.Text(),
            nullable=False
        )
    )

    # 3. Add created_at
    op.add_column(
        'product_details',
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        )
    )

    # 4. Make product_url unique
    op.create_unique_constraint(
        'uq_product_details_product_url',
        'product_details',
        ['product_url']
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'uq_product_details_product_url',
        'product_details',
        type_='unique'
    )

    op.drop_column(
        'product_details',
        'created_at'
    )

    op.drop_column(
        'product_details',
        'product_url'
    )

    op.drop_table('price_history')