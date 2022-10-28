"""First Commit

Revision ID: 5189e96958ce
Revises: 
Create Date: 2022-10-28 16:24:57.486055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5189e96958ce'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('address',
    sa.Column('idAddress', sa.Integer(), nullable=False),
    sa.Column('a_street', sa.String(length=45), nullable=False),
    sa.Column('a_house', sa.String(length=45), nullable=False),
    sa.Column('a_flat', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('idAddress')
    )
    op.create_table('menu',
    sa.Column('idMenu', sa.Integer(), nullable=False),
    sa.Column('m_name', sa.String(length=45), nullable=True),
    sa.Column('m_price', sa.Integer(), nullable=True),
    sa.Column('m_availability', sa.Boolean(), nullable=True),
    sa.Column('m_demand', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('idMenu')
    )
    op.create_table('product',
    sa.Column('idProduct', sa.Integer(), nullable=False),
    sa.Column('p_name', sa.String(length=45), nullable=True),
    sa.Column('p_price', sa.Integer(), nullable=True),
    sa.Column('p_weight', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('idProduct')
    )
    op.create_table('user',
    sa.Column('idUser', sa.Integer(), nullable=False),
    sa.Column('u_name', sa.String(length=45), nullable=False),
    sa.Column('u_surname', sa.String(length=45), nullable=False),
    sa.Column('u_phone', sa.Integer(), nullable=False),
    sa.Column('u_email', sa.String(length=45), nullable=True),
    sa.Column('u_password', sa.String(length=45), nullable=False),
    sa.Column('u_role', sa.Enum('CLIENT', 'MANAGER', name='userstatus'), nullable=True),
    sa.PrimaryKeyConstraint('idUser'),
    sa.UniqueConstraint('u_email')
    )
    op.create_table('custom',
    sa.Column('idCustom', sa.Integer(), nullable=False),
    sa.Column('c_price', sa.Integer(), nullable=True),
    sa.Column('Address_id', sa.Integer(), nullable=True),
    sa.Column('User_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['Address_id'], ['address.idAddress'], ),
    sa.ForeignKeyConstraint(['User_id'], ['user.idUser'], ),
    sa.PrimaryKeyConstraint('idCustom')
    )
    op.create_table('ingredient',
    sa.Column('idIngredient', sa.Integer(), nullable=False),
    sa.Column('i_weight', sa.Integer(), nullable=False),
    sa.Column('i_percent', sa.Integer(), nullable=False),
    sa.Column('Menu_id', sa.Integer(), nullable=True),
    sa.Column('Product_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['Menu_id'], ['menu.idMenu'], ),
    sa.ForeignKeyConstraint(['Product_id'], ['product.idProduct'], ),
    sa.PrimaryKeyConstraint('idIngredient')
    )
    op.create_table('details',
    sa.Column('idDetails', sa.Integer(), nullable=False),
    sa.Column('d_quantity', sa.Integer(), nullable=True),
    sa.Column('Custom_id', sa.Integer(), nullable=True),
    sa.Column('Menu_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['Custom_id'], ['custom.idCustom'], ),
    sa.ForeignKeyConstraint(['Menu_id'], ['menu.idMenu'], ),
    sa.PrimaryKeyConstraint('idDetails')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('details')
    op.drop_table('ingredient')
    op.drop_table('custom')
    op.drop_table('user')
    op.drop_table('product')
    op.drop_table('menu')
    op.drop_table('address')
    # ### end Alembic commands ###
