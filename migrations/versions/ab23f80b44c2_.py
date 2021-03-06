"""empty message

Revision ID: ab23f80b44c2
Revises: ff20fe3f4c96
Create Date: 2020-11-25 02:24:04.664444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab23f80b44c2'
down_revision = 'ff20fe3f4c96'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('booking', sa.Column('dow', sa.String(), nullable=False))
    op.add_column('booking', sa.Column('time', sa.String(), nullable=False))
    op.drop_column('booking', 'client_time')
    op.drop_column('booking', 'client_dow')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('booking', sa.Column('client_dow', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('booking', sa.Column('client_time', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('booking', 'time')
    op.drop_column('booking', 'dow')
    # ### end Alembic commands ###
