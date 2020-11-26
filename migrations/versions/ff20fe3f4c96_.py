"""empty message

Revision ID: ff20fe3f4c96
Revises: 9275a6296794
Create Date: 2020-11-24 23:34:16.276758

"""
import json
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff20fe3f4c96'
down_revision = '9275a6296794'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # set server_default to space. it unneccesary because can not create nullable Column without data
    op.add_column('goals', sa.Column('picture', sa.Integer(), nullable=False, server_default='32'))
    # ### end Alembic commands ###
    # fill DB
    with open('data.json', 'r') as jf:
        data = json.load(jf)
    count_id = 1

    for goal in data['goals']:
        for g_name, g_pic in data['goals_pic'].items():
            if g_name == goal:
                op.execute("UPDATE goals SET picture={} WHERE id={}".format(ord(g_pic), count_id))
                break
        count_id += 1


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('goals', 'picture')
    # ### end Alembic commands ###