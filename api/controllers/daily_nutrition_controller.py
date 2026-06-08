"""
Daily nutrition controller - business logic.
"""
import os
import time
from datetime import date as DateType, datetime
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.models.daily_nutrition import DailyNutrition, MealCategory
from api.models.user import User
from api.schemas.daily_nutrition_schema import FoodItemResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

NUTRITION_KEYS = ["calories", "fat_g", "carb_g", "protein_g"]


# ── Helpers ────────────────────────────────────────────────────────────────────

async def save_food_image(file: UploadFile, username: str, date: DateType) -> str:
    """Save uploaded image to public/daily_nutrition/{username}/{date}/"""
    ext = os.path.splitext(file.filename)[-1].lower() if file.filename else ".png"
    folder = os.path.join(PUBLIC_DIR, "daily_nutrition", username, str(date))
    os.makedirs(folder, exist_ok=True)
    filename = f"{int(time.time())}{ext}"
    contents = await file.read()
    with open(os.path.join(folder, filename), "wb") as f:
        f.write(contents)
    return f"public/daily_nutrition/{username}/{date}/{filename}"


def _zero_nutrition() -> dict:
    return {k: 0.0 for k in NUTRITION_KEYS}


def _sum_nutrition(items: list) -> dict:
    total = _zero_nutrition()
    for item in items:
        n = item.get("nutrition") or {}
        for k in NUTRITION_KEYS:
            total[k] = round(total[k] + float(n.get(k, 0)), 2)
    return total


def _rows_to_food_items(rows) -> list:
    return [FoodItemResponse.model_validate(r).model_dump(mode="json") for r in rows]


def _build_category_block(rows_by_cat: dict, selected_category: Optional[str] = None) -> tuple:
    """
    Build category block and grand total.
    Returns (category_dict, grand_total_dict)
    """
    category_block = {}
    grand_total = _zero_nutrition()

    cats = [selected_category] if selected_category else [c.value for c in MealCategory]

    for cat in cats:
        items = rows_by_cat.get(cat, [])
        cat_total = _sum_nutrition(items)
        category_block[cat] = {
            "food": items,
            "nutrition_total": cat_total,
        }
        for k in NUTRITION_KEYS:
            grand_total[k] = round(grand_total[k] + cat_total[k], 2)

    return category_block, grand_total


# ── Create ─────────────────────────────────────────────────────────────────────

async def create_daily_nutrition(
    db: Session,
    current_user: User,
    data: dict,
    food_image: Optional[UploadFile] = None,
) -> DailyNutrition:
    """Insert a new daily nutrition entry."""
    category = data.get("category")
    if category not in [c.value for c in MealCategory]:
        raise HTTPException(status_code=400, detail="Invalid category. Must be: breakfast, lunch, dinner")

    image_path = None
    if food_image and food_image.filename:
        image_path = await save_food_image(food_image, current_user.username, data["date"])

    entry = DailyNutrition(
        user_id=current_user.id,
        date=data["date"],
        category=category,
        food_name=data["food_name"],
        nutrition=data["nutrition"],
        food_image=image_path,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ── Get single date ────────────────────────────────────────────────────────────

def get_daily_nutrition(
    db: Session,
    user_id: int,
    target_date: DateType,
    category: Optional[str] = None,
) -> dict:
    """Get daily nutrition for a specific date."""
    if category and category not in [c.value for c in MealCategory]:
        raise HTTPException(status_code=400, detail="Invalid category. Must be: breakfast, lunch, dinner")

    base_query = db.query(DailyNutrition).filter(
        DailyNutrition.user_id == user_id,
        DailyNutrition.date == target_date,
        DailyNutrition.deleted_at.is_(None),
    )

    rows_by_cat = {}
    cats = [category] if category else [c.value for c in MealCategory]
    for cat in cats:
        rows = base_query.filter(DailyNutrition.category == cat).all()
        rows_by_cat[cat] = _rows_to_food_items(rows)

    category_block, grand_total = _build_category_block(rows_by_cat, category)

    result = {
        "user_id": user_id,
        "date": str(target_date),
        "category": category_block,
        "nutrition_total": grand_total,
    }

    return result


# ── Get date range ─────────────────────────────────────────────────────────────

def get_daily_nutrition_range(
    db: Session,
    user_id: int,
    start_date: DateType,
    end_date: DateType,
    category: Optional[str] = None,
) -> list:
    """Get daily nutrition for a date range, grouped by date."""
    if category and category not in [c.value for c in MealCategory]:
        raise HTTPException(status_code=400, detail="Invalid category. Must be: breakfast, lunch, dinner")

    query = db.query(DailyNutrition).filter(
        DailyNutrition.user_id == user_id,
        DailyNutrition.date >= start_date,
        DailyNutrition.date <= end_date,
        DailyNutrition.deleted_at.is_(None),
    )
    if category:
        query = query.filter(DailyNutrition.category == category)

    rows = query.order_by(DailyNutrition.date).all()

    # Group rows by date then category
    date_cat_map: dict = {}
    for row in rows:
        d = str(row.date)
        cat = row.category.value if hasattr(row.category, "value") else row.category
        if d not in date_cat_map:
            date_cat_map[d] = {c.value: [] for c in MealCategory}
        date_cat_map[d][cat].append(FoodItemResponse.model_validate(row).model_dump(mode="json"))

    result = []
    for d, rows_by_cat in date_cat_map.items():
        filtered = {k: v for k, v in rows_by_cat.items() if (not category or k == category)}
        category_block, grand_total = _build_category_block(filtered, category)
        result.append({
            "user_id": user_id,
            "date": d,
            "category": category_block,
            "nutrition_total": grand_total,
        })

    return result


# ── Delete ─────────────────────────────────────────────────────────────────────

def delete_daily_nutrition(db: Session, entry_id: int, user_id: int) -> None:
    """Soft delete a daily nutrition entry."""
    entry = db.query(DailyNutrition).filter(
        DailyNutrition.id == entry_id,
        DailyNutrition.user_id == user_id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    entry.deleted_at = datetime.utcnow()
    db.commit()
