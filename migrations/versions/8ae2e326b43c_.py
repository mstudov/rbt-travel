"""empty message

Revision ID: 8ae2e326b43c
Revises: 5770af42843a
Create Date: 2020-02-26 13:51:04.899602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ae2e326b43c'
down_revision = '5770af42843a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'travel_arrangement',
        sa.Column(
            'total_spots',
            sa.Integer(),
            nullable=True))
    with op.batch_alter_table('travel_arrangement_tourist_user') as batch_op:
        batch_op.drop_column('reserved_spots')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('travel_arrangement_tourist_user', sa.Column('reserved_spots', sa.INTEGER(), nullable=False))
    op.drop_column('travel_arrangement', 'total_spots')
    # ### end Alembic commands ###
