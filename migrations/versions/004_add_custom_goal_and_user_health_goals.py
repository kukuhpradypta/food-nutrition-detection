"""Add custom health goal and user_health_goals table

Revision ID: 004
Revises: 003
Create Date: 2025-01-01 00:00:03.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Alter users.health_goal enum to include "custom"
    op.alter_column(
        "users",
        "health_goal",
        type_=sa.Enum("lose_weight", "gain_muscle", "maintain_health", "custom", name="healthgoal"),
        existing_nullable=False,
    )

    # 2. Create user_health_goals table
    op.create_table(
        "user_health_goals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "goal_category",
            sa.Enum("lose_weight", "gain_muscle", "maintain_health", "custom", name="goalcategory"),
            nullable=False,
        ),
        sa.Column("nutrition", sa.JSON(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_user_health_goals_id", "user_health_goals", ["id"])
    op.create_index("ix_user_health_goals_user_id", "user_health_goals", ["user_id"])
    op.create_index("ix_user_health_goals_goal_category", "user_health_goals", ["goal_category"])

    # 3. Seed the 3 global goals (user_id = NULL)
    user_health_goals = sa.table(
        "user_health_goals",
        sa.column("goal_category", sa.String),
        sa.column("nutrition", sa.JSON),
        sa.column("user_id", sa.Integer),
    )
    op.bulk_insert(
        user_health_goals,
        [
            {
                "goal_category": "lose_weight",
                "nutrition": {"calories": 1500, "fat_g": 40, "carb_g": 150, "protein_g": 120},
                "user_id": None,
            },
            {
                "goal_category": "gain_muscle",
                "nutrition": {"calories": 2800, "fat_g": 80, "carb_g": 320, "protein_g": 180},
                "user_id": None,
            },
            {
                "goal_category": "maintain_health",
                "nutrition": {"calories": 2200, "fat_g": 70, "carb_g": 250, "protein_g": 140},
                "user_id": None,
            },
        ],
    )


def downgrade():
    op.drop_index("ix_user_health_goals_goal_category", table_name="user_health_goals")
    op.drop_index("ix_user_health_goals_user_id", table_name="user_health_goals")
    op.drop_index("ix_user_health_goals_id", table_name="user_health_goals")
    op.drop_table("user_health_goals")

    op.alter_column(
        "users",
        "health_goal",
        type_=sa.Enum("lose_weight", "gain_muscle", "maintain_health", name="healthgoal"),
        existing_nullable=False,
    )
