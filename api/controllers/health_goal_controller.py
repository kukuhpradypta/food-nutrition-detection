"""
Health goal controller - business logic.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.models.user import User
from api.models.user_health_goal import UserHealthGoal, GoalCategory
from api.schemas.health_goal_schema import HealthGoalResponse


def get_health_goal(db: Session, current_user: User):
    """
    Get the health goal for the current logged-in user, based on the user's
    own `health_goal` setting.

    - If the user's goal is 'custom': return their personal custom goal.
    - Otherwise: return the global goal matching the user's gender.
    """
    category = current_user.health_goal.value if hasattr(current_user.health_goal, "value") else current_user.health_goal

    query = db.query(UserHealthGoal).filter(
        UserHealthGoal.goal_category == category,
        UserHealthGoal.deleted_at.is_(None),
    )

    if category == GoalCategory.custom.value:
        query = query.filter(UserHealthGoal.user_id == current_user.id)
    else:
        # Global goal, filtered by the user's gender
        gender = current_user.gender.value if hasattr(current_user.gender, "value") else current_user.gender
        query = query.filter(
            UserHealthGoal.user_id.is_(None),
            UserHealthGoal.gender == gender,
        )

    goal = query.first()
    if not goal:
        raise HTTPException(status_code=404, detail="Health goal not found")

    return HealthGoalResponse.model_validate(goal).model_dump(mode="json")


def list_global_goals_by_gender(db: Session, gender: str):
    """
    List all global health goals (user_id IS NULL) for a given gender,
    excluding the 'custom' category.
    """
    valid_genders = ["male", "female"]
    if gender not in valid_genders:
        raise HTTPException(status_code=400, detail="Invalid gender. Must be: male, female")

    goals = (
        db.query(UserHealthGoal)
        .filter(
            UserHealthGoal.user_id.is_(None),
            UserHealthGoal.gender == gender,
            UserHealthGoal.goal_category != GoalCategory.custom.value,
            UserHealthGoal.deleted_at.is_(None),
        )
        .all()
    )

    return [HealthGoalResponse.model_validate(g).model_dump(mode="json") for g in goals]
