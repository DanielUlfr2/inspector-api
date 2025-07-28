"""add nombre apellido to usuarios

Revision ID: add_nombre_apellido_to_usuarios
Revises: d9ca4c7bbd7a
Create Date: 2025-07-28 11:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_nombre_apellido_to_usuarios'
down_revision = 'd9ca4c7bbd7a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columnas nombre y apellido a la tabla usuarios
    op.add_column('usuarios', sa.Column('nombre', sa.String(), nullable=True))
    op.add_column('usuarios', sa.Column('apellido', sa.String(), nullable=True))
    
    # Actualizar registros existentes con valores por defecto
    op.execute("UPDATE usuarios SET nombre = username WHERE nombre IS NULL")
    op.execute("UPDATE usuarios SET apellido = '' WHERE apellido IS NULL")


def downgrade() -> None:
    # Eliminar las columnas agregadas
    op.drop_column('usuarios', 'apellido')
    op.drop_column('usuarios', 'nombre') 