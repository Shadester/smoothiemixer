from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal


class IngredientBase(BaseModel):
    name: str
    category: Literal["fruit", "liquid", "protein", "veggie", "fat", "sweetener", "extra"]
    unit_name: str                  # e.g. "banana", "tbsp", "ml", "g", "scoop"
    grams_per_unit: float           # grams per 1 unit_name
    calories_per_100g: float
    in_stock: bool = True


class IngredientIn(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: int

    model_config = {"from_attributes": True}


class IngredientLookup(BaseModel):
    name: str
    calories_per_100g: float
    suggested_grams_per_unit: float | None = None
    serving_size_label: str | None = None


class GenerateRequest(BaseModel):
    count: int = Field(default=7, ge=5, le=10)
    calorie_target: float = Field(gt=0)
    mode: Literal["rule", "ai"] = "rule"
    required_ingredient_ids: list[int] = Field(default_factory=list)


class RecipeItem(BaseModel):
    ingredient_id: int
    name: str
    units: float              # 0.5, 1, 1.5, 2 …
    unit_name: str
    grams: float
    calories: float


class Recipe(BaseModel):
    title: str
    items: list[RecipeItem]
    total_calories: float
