"""merge heads

Revision ID: 759611e96df7
Revises: 4b61175457e7, add_nombre_apellido_to_usuarios
Create Date: 2025-11-04 20:39:27.130994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '759611e96df7'
down_revision: Union[str, Sequence[str], None] = ('4b61175457e7', 'add_nombre_apellido_to_usuarios')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
