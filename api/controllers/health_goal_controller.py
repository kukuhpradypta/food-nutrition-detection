"""
Health goal controller - business logic.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.models.user_health_goal import UserHealthGoal, GoalCategory
from api.schemas.health_goal_schema import HealthGoalResponse


def get_health_goal(db: Session, category: str, user_id: int):
    """
    Get health goal by category.

    - For global categories (lose_weight, gain_muscle, maintain_health):
      return the global goal (user_id IS NULL).
    - For custom: return the goal belonging to the current user.
    """
    if category not in [c.value for c in GoalCategory]:
        raise HTTPException(
            status_code=400,
            detail="Invalid category. Must be: lose_weight, gain_muscle, maintain_health, custom",
        )

    query = db.query(UserHealthGoal).filter(
        UserHealthGoal.goal_category == category,
        UserHealthGoal.deleted_at.is_(None),
    )

    if category == GoalCategory.custom.value:
        query = query.filter(UserHealthGoal.user_id == user_id)
    else:
        query = query.filter(UserHealthGoal.user_id.is_(None))

    goal = query.first()
    if not goal:
        raise HTTPException(status_code=404, detail="Health goal not found")

    return HealthGoalResponse.model_validate(goal).model_dump(mode="json")
