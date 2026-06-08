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
        sa.Column("gender", sa.Enum("male", "female", name="gender"), nullable=True),
        sa.Column("nutrition", sa.JSON(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_user_health_goals_id", "user_health_goals", ["id"])
    op.create_index("ix_user_health_goals_user_id", "user_health_goals", ["user_id"])
    op.create_index("ix_user_health_goals_goal_category", "user_health_goals", ["goal_category"])

    # 3. Seed the global goals (user_id = NULL) per gender
    user_health_goals = sa.table(
        "user_health_goals",
        sa.column("goal_category", sa.String),
        sa.column("gender", sa.String),
        sa.column("nutrition", sa.JSON),
        sa.column("user_id", sa.Integer),
    )
    op.bulk_insert(
        user_health_goals,
        [
            # ── Male ──────────────────────────────────────────────
            {
                "goal_category": "lose_weight",
                "gender": "male",
                "nutrition": {"calories": 1800, "fat_g": 50, "carb_g": 180, "protein_g": 140},
                "user_id": None,
            },
            {
                "goal_category": "gain_muscle",
                "gender": "male",
                "nutrition": {"calories": 2800, "fat_g": 80, "carb_g": 320, "protein_g": 180},
                "user_id": None,
            },
            {
                "goal_category": "maintain_health",
                "gender": "male",
                "nutrition": {"calories": 2500, "fat_g": 75, "carb_g": 280, "protein_g": 150},
                "user_id": None,
            },
            # ── Female ────────────────────────────────────────────
            {
                "goal_category": "lose_weight",
                "gender": "female",
                "nutrition": {"calories": 1400, "fat_g": 40, "carb_g": 140, "protein_g": 110},
                "user_id": None,
            },
            {
                "goal_category": "gain_muscle",
                "gender": "female",
                "nutrition": {"calories": 2200, "fat_g": 65, "carb_g": 250, "protein_g": 150},
                "user_id": None,
            },
            {
                "goal_category": "maintain_health",
                "gender": "female",
                "nutrition": {"calories": 2000, "fat_g": 60, "carb_g": 230, "protein_g": 120},
                "user_id": None,
            },
        ],
    )


def downgrade():
    op.drop_table("user_health_goals")

    op.alter_column(
        "users",
        "health_goal",
        type_=sa.Enum("lose_weight", "gain_muscle", "maintain_health", name="healthgoal"),
        existing_nullable=False,
    )
