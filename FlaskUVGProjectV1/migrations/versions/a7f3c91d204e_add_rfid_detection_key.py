
"""add rfid detection key

Revision ID: a7f3c91d204e
Revises: d9c824ee2a80

"""

from alembic import op
import sqlalchemy as sa


revision = "a7f3c91d204e"
down_revision = "d9c824ee2a80"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        "rfid_detection_events",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "detection_key",
                sa.String(length=36),
                nullable=True
            )
        )

        batch_op.create_unique_constraint(
            "uq_rfid_detection_events_detection_key",
            ["detection_key"]
        )


def downgrade():

    with op.batch_alter_table(
        "rfid_detection_events",
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            "uq_rfid_detection_events_detection_key",
            type_="unique"
        )

        batch_op.drop_column(
            "detection_key"
        )
