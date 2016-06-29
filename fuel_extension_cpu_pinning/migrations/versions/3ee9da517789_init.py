"""init

Revision ID: 3ee9da517789
Revises:
Create Date: 2016-06-29 04:16:01.654122

"""

# revision identifiers, used by Alembic.
revision = '3ee9da517789'
down_revision = None
branch_labels = None
depends_on = None

from alembic import context
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql


def upgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.create_table(
        table_prefix + 'pins',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('nova_cores', psql.ARRAY(sa.String(255)),
                  server_default='{}', nullable=False),
        sa.Column('vrouter_cores', psql.ARRAY(sa.String(255)),
                  server_default='{}', nullable=False))


def downgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.drop_table(table_prefix + 'pins')
