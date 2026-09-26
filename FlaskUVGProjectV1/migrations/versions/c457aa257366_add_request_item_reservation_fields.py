"""Add request item reservation fields

Revision ID: c457aa257366
Revises: 5d5e6659befd
Create Date: 2026-09-24 03:13:24.831120

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c457aa257366'
down_revision = '5d5e6659befd'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        "request_items",
        sa.Column(
            "specimen_id",
            sa.Integer(),
            nullable=False
        )
    )

    op.add_column(
        "request_items",
        sa.Column(
            "item_status",
            sa.String(length=50),
            nullable=False,
            server_default="pending"
        )
    )

    op.add_column(
        "request_items",
        sa.Column(
            "rejection_reason",
            sa.String(length=100),
            nullable=True
        )
    )

    op.add_column(
        "request_items",
        sa.Column(
            "rejection_comment",
            sa.Text(),
            nullable=True
        )
    )

    op.create_foreign_key(
        "fk_request_items_specimen_id",
        "request_items",
        "specimens",
        ["specimen_id"],
        ["id"]
    )

    op.alter_column(
        "request_items",
        "portal_code",
        existing_type=sa.String(length=100),
        nullable=False
    )

    op.alter_column(
        "requests",
        "start_time",
        existing_type=sa.Time(),
        nullable=False
    )

    op.alter_column(
        "requests",
        "end_time",
        existing_type=sa.Time(),
        nullable=False
    )


def downgrade():
    op.alter_column(
        "requests",
        "end_time",
        existing_type=sa.Time(),
        nullable=True
    )

    op.alter_column(
        "requests",
        "start_time",
        existing_type=sa.Time(),
        nullable=True
    )

    op.alter_column(
        "request_items",
        "portal_code",
        existing_type=sa.String(length=100),
        nullable=True
    )

    op.drop_constraint(
        "fk_request_items_specimen_id",
        "request_items",
        type_="foreignkey"
    )

    op.drop_column(
        "request_items",
        "rejection_comment"
    )

    op.drop_column(
        "request_items",
        "rejection_reason"
    )

    op.drop_column(
        "request_items",
        "item_status"
    )

    op.drop_column(
        "request_items",
        "specimen_id"
    )
