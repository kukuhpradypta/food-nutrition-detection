"""Create daily_nutritions table

Revision ID: 003
Revises: 002
Create Date: 2025-01-01 00:00:02.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "daily_nutritions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "category",
            sa.Enum("breakfast", "lunch", "dinner", name="mealcategory"),
            nullable=False,
        ),
        sa.Column("food_name", sa.String(255), nullable=False),
        sa.Column("nutrition", sa.JSON(), nullable=False),
        sa.Column("food_image", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_daily_nutritions_id", "daily_nutritions", ["id"])
    op.create_index("ix_daily_nutritions_user_id", "daily_nutritions", ["user_id"])
    op.create_index("ix_daily_nutritions_date", "daily_nutritions", ["date"])


def downgrade():
    op.drop_table("daily_nutritions")
    op.execute("DROP TYPE IF EXISTS mealcategory")
