"""changed datatype of traffic_intersection column

Revision ID: f5be92522762
Revises: a1011c82534a
Create Date: 2025-02-04 19:21:49.572144

"""
from typing import Sequence, Union
from geoalchemy2 import Geometry

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f5be92522762'
down_revision: Union[str, None] = 'a1011c82534a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert the column type with explicit casting
    op.execute(
        "ALTER TABLE \"order\" ALTER COLUMN traffic_light_intersection "
        "TYPE geometry(MULTILINESTRING,4326) USING "
        "ST_GeomFromEWKT(traffic_light_intersection::text)"
    )
    op.create_index(
        'idx_order_traffic_light_intersection',
        'order',
        ['traffic_light_intersection'],
        unique=False,
        postgresql_using='gist'
    )



def downgrade() -> None:
    op.drop_index(
        'idx_order_traffic_light_intersection',
        table_name='order',
        postgresql_using='gist'
    )
    op.execute(
        "ALTER TABLE \"order\" ALTER COLUMN traffic_light_intersection "
        "TYPE VARCHAR(20)[] USING array[traffic_light_intersection::text]"
    )


    # ### end Alembic commands ###
