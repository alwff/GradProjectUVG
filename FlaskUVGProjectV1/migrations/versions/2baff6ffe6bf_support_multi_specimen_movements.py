"""support multi specimen movements

Revision ID: 2baff6ffe6bf
Revises: c457aa257366
Create Date: 2026-09-26 04:31:20.222316

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2baff6ffe6bf'
down_revision = 'c457aa257366'
branch_labels = None
depends_on = None

def upgrade():

    # 1. Agregar relación opcional con solicitudes.
    with op.batch_alter_table(
        "movements",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "request_id",
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.create_foreign_key(
            "fk_movements_request_id",
            "requests",
            ["request_id"],
            ["id"]
        )


    # 2. Crear tabla para los especímenes
    # contenidos en cada movimiento.
    op.create_table(
        "movement_items",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "movement_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "specimen_id",
            sa.Integer(),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["movement_id"],
            ["movements.id"]
        ),

        sa.ForeignKeyConstraint(
            ["specimen_id"],
            ["specimens.id"]
        ),

        sa.PrimaryKeyConstraint(
            "id"
        )
    )


    # 3. Preservar todos los movimientos antiguos.
    op.execute(
        """
        INSERT INTO movement_items
            (movement_id, specimen_id)
        SELECT
            id,
            specimen_id
        FROM movements
        WHERE specimen_id IS NOT NULL
        """
    )


    # 4. Ahora sí podemos eliminar specimen_id
    # de movements sin perder el historial.
    with op.batch_alter_table(
        "movements",
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            "movements_specimen_id_fkey",
            type_="foreignkey"
        )

        batch_op.drop_column(
            "specimen_id"
        )


def downgrade():

    # 1. Restaurar specimen_id temporalmente nullable.
    with op.batch_alter_table(
        "movements",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "specimen_id",
                sa.Integer(),
                nullable=True
            )
        )


    # 2. Recuperar un espécimen para cada movimiento.
    #
    # IMPORTANTE:
    # Si un movimiento moderno contiene varios
    # especímenes, un downgrade al modelo antiguo
    # solo puede representar uno.
    op.execute(
        """
        UPDATE movements
        SET specimen_id = (
            SELECT movement_items.specimen_id
            FROM movement_items
            WHERE movement_items.movement_id
                = movements.id
            ORDER BY movement_items.id
            LIMIT 1
        )
        """
    )


    # 3. Restaurar la FK antigua.
    with op.batch_alter_table(
        "movements",
        schema=None
    ) as batch_op:

        batch_op.create_foreign_key(
            "movements_specimen_id_fkey",
            "specimens",
            ["specimen_id"],
            ["id"]
        )


    # 4. Eliminar la tabla nueva.
    op.drop_table(
        "movement_items"
    )


    # 5. Eliminar relación con solicitudes.
    with op.batch_alter_table(
        "movements",
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_movements_request_id",
            type_="foreignkey"
        )

        batch_op.drop_column(
            "request_id"
        )
