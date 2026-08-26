from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal


class IngredientBase(BaseModel):
    name: str
    category: Literal["fruit", "liquid", "protein", "veggie", "fat", "sweetener", "extra"]
    unit_name: str                  # e.g. "banana", "tbsp", "ml", "g", "scoop"
    grams_per_unit: float           # grams per 1 unit_name
    calories_per_100g: float
    protein_per_100g: float = 0
    carbs_per_100g: float = 0
    fat_per_100g: float = 0
    sugar_per_100g: float = 0
    fiber_per_100g: float = 0
    in_stock: bool = True


class IngredientIn(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: int

    model_config = {"from_attributes": True}


class IngredientLookup(BaseModel):
    name: str
    calories_per_100g: float
    protein_per_100g: float | None = None
    carbs_per_100g: float | None = None
    fat_per_100g: float | None = None
    sugar_per_100g: float | None = None
    fiber_per_100g: float | None = None
    suggested_grams_per_unit: float | None = None
    serving_size_label: str | None = None


class GenerateRequest(BaseModel):
    count: int = Field(default=7, ge=5, le=10)
    calorie_target: float = Field(gt=0)
    mode: Literal["rule", "ai"] = "rule"
    required_ingredient_ids: list[int] = Field(default_factory=list)
    high_protein: bool = False


class RecipeItem(BaseModel):
    ingredient_id: int
    name: str
    units: float              # 0.5, 1, 1.5, 2 …
    unit_name: str
    grams: float
    calories: float
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    sugar: float = 0
    fiber: float = 0


class Recipe(BaseModel):
    title: str
    items: list[RecipeItem]
    total_calories: float
    total_protein: float = 0
    total_carbs: float = 0
    total_fat: float = 0
    total_sugar: float = 0
    total_fiber: float = 0


class FavoriteRecipe(Recipe):
    id: int
    created_at: str
