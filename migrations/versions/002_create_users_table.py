"""Create users table

Revision ID: 002
Revises: None
Create Date: 2025-01-01 00:00:01.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "002"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("gender", sa.Enum("male", "female", name="gender"), nullable=False),
        sa.Column("height_cm", sa.Float(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column(
            "health_goal",
            sa.Enum("lose_weight", "gain_muscle", "maintain_health", name="healthgoal"),
            nullable=False,
        ),
        sa.Column(
            "activity_level",
            sa.Enum("sedentary", "light", "moderate", "active", "athlete", name="activitylevel"),
            nullable=False,
        ),
        sa.Column("session_token", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)


def downgrade():
    op.drop_table("users")
    # Drop PostgreSQL ENUM types that were created with this table
    op.execute("DROP TYPE IF EXISTS gender")
    op.execute("DROP TYPE IF EXISTS healthgoal")
    op.execute("DROP TYPE IF EXISTS activitylevel")
