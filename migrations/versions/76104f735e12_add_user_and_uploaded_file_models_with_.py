"""Add user and uploaded file models with relationship

Revision ID: 76104f735e12
Revises: 9f9f6168ec27
Create Date: 2024-12-29 10:03:50.259261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76104f735e12'
down_revision = '9f9f6168ec27'
branch_labels = None
depends_on = None


def upgrade():
    # Create the 'user' table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(length=100), unique=True, nullable=False),
        sa.Column('email', sa.String(length=120), unique=True, nullable=False),
        sa.Column('password', sa.String(length=100), nullable=False),
    )

    # Create the 'uploaded_file' table with a named foreign key constraint
    op.create_table(
        'uploaded_file',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('filename', sa.String(length=120), nullable=False),
        sa.Column('extracted_text', sa.Text, nullable=False),
        sa.Column('summarized_text', sa.Text, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id', name='fk_user_uploaded_file'), nullable=False),
    )

def downgrade():
    # Drop the 'uploaded_file' table and the 'user' table in the downgrade
    op.drop_table('uploaded_file')
    op.drop_table('user')
