"""Smoothie recipe generation — rule-based and Claude AI mode."""
from __future__ import annotations

import json
import os
import random
from typing import Any

from models import Ingredient, Recipe, RecipeItem

# Steps by unit type — ml/g need much larger ranges than natural units
ML_STEPS   = [50, 100, 150, 200, 250, 300]
G_STEPS    = [25, 50, 75, 100, 125, 150]
UNIT_STEPS = [0.5, 1, 1.5, 2, 2.5, 3]   # banana, scoop, tbsp, handful …


SINGLE_UNITS = {"avocado", "half"}  # ingredients you wouldn't use more than 1 of


def _steps(ing: Ingredient) -> list[float]:
    if ing.unit_name == "ml":
        return ML_STEPS
    if ing.unit_name == "g":
        return G_STEPS
    if ing.unit_name in SINGLE_UNITS:
        return [0.5, 1]
    return UNIT_STEPS


def _nearest_step(value: float, steps: list[float]) -> float:
    clamped = max(steps[0], min(steps[-1], value))
    return min(steps, key=lambda s: abs(s - clamped))


def _default_units(ing: Ingredient) -> float:
    steps = _steps(ing)
    return steps[len(steps) // 2]  # start in the middle of the range


NUTRIENTS = ["calories", "protein", "carbs", "fat", "sugar", "fiber"]


def _nutrient(ing: Ingredient, units: float, nutrient: str) -> float:
    per_100g = getattr(ing, f"{nutrient}_per_100g")
    return units * ing.grams_per_unit * per_100g / 100


def _calories(ing: Ingredient, units: float) -> float:
    return _nutrient(ing, units, "calories")


def _scale_to_target(
    items: list[tuple[Ingredient, float]],
    target: float,
    tolerance: float = 0.12,
) -> list[tuple[Ingredient, float]] | None:
    """
    Scale unit counts toward the calorie target.
    Zero-calorie ingredients (water, ice) are held at their default and
    excluded from the ratio so they don't dilute the scaling.
    """
    # Separate caloric vs zero-cal items
    caloric = [(ing, u) for ing, u in items if ing.calories_per_100g > 0]
    zero    = [(ing, u) for ing, u in items if ing.calories_per_100g == 0]

    if not caloric:
        return None

    for _ in range(40):
        total = sum(_calories(ing, u) for ing, u in caloric)
        if total == 0:
            # scale up from defaults
            caloric = [(ing, _default_units(ing) * 2) for ing, _ in caloric]
            continue
        if abs(total - target) / target <= tolerance:
            return caloric + zero
        ratio = target / total
        caloric = [
            (ing, _nearest_step(u * ratio, _steps(ing)))
            for ing, u in caloric
        ]

    total = sum(_calories(ing, u) for ing, u in caloric)
    if abs(total - target) / target <= 0.20:
        return caloric + zero
    return None


def _build_recipe_items(items: list[tuple[Ingredient, float]]) -> list[RecipeItem]:
    return [
        RecipeItem(
            ingredient_id=ing.id,
            name=ing.name,
            units=units,
            unit_name=ing.unit_name,
            grams=round(units * ing.grams_per_unit, 1),
            **{n: round(_nutrient(ing, units, n), 1) for n in NUTRIENTS},
        )
        for ing, units in items
    ]


def _recipe_totals(items: list[tuple[Ingredient, float]]) -> dict[str, float]:
    return {
        f"total_{n}": round(sum(_nutrient(ing, units, n) for ing, units in items), 1)
        for n in NUTRIENTS
    }


# ---------------------------------------------------------------------------
# Rule-based generation
# ---------------------------------------------------------------------------

TEMPLATES: list[dict[str, Any]] = [
    {"slots": [("liquid", True), ("fruit", True), ("fruit", False), ("protein", False), ("extra", False)]},
    {"slots": [("liquid", True), ("fruit", True), ("veggie", True), ("fat", False), ("extra", False)]},
    {"slots": [("liquid", True), ("fruit", True), ("fat", True), ("sweetener", False)]},
    {"slots": [("liquid", True), ("fruit", True), ("protein", True), ("sweetener", False), ("extra", False)]},
    {"slots": [("liquid", True), ("veggie", True), ("fruit", True), ("fat", False), ("extra", False)]},
]

TITLES = [
    "Morning Boost", "Green Power", "Berry Bliss", "Tropical Sunrise",
    "Protein Punch", "Golden Hour", "Creamy Dream", "Jungle Fuel",
    "Zen Garden", "Fiery Start",
]


def generate_rule_based(
    in_stock: list[Ingredient],
    count: int,
    calorie_target: float,
    required: list[Ingredient] | None = None,
) -> list[Recipe]:
    by_cat: dict[str, list[Ingredient]] = {}
    for ing in in_stock:
        by_cat.setdefault(ing.category, []).append(ing)

    required = required or []
    recipes: list[Recipe] = []
    used_titles: set[str] = set()
    attempts = 0

    while len(recipes) < count and attempts < count * 10:
        attempts += 1
        template = random.choice(TEMPLATES)

        # Pre-seed with required ingredients so every recipe contains them
        items: list[tuple[Ingredient, float]] = [
            (ing, _default_units(ing)) for ing in required
        ]

        ok = True
        for cat, req_slot in template["slots"]:
            pool = by_cat.get(cat, [])
            already = {ing.id for ing, _ in items}
            pool = [i for i in pool if i.id not in already]
            if not pool:
                if req_slot:
                    ok = False
                    break
                continue
            chosen = random.choice(pool)
            items.append((chosen, _default_units(chosen)))

        if not ok or not items:
            continue

        scaled = _scale_to_target(items, calorie_target)
        if scaled is None:
            continue

        title_pool = [t for t in TITLES if t not in used_titles] or TITLES
        title = random.choice(title_pool)
        used_titles.add(title)

        recipes.append(Recipe(
            title=title,
            items=_build_recipe_items(scaled),
            **_recipe_totals(scaled),
        ))

    return recipes


# ---------------------------------------------------------------------------
# Claude AI generation
# ---------------------------------------------------------------------------

def generate_with_claude(
    in_stock: list[Ingredient],
    count: int,
    calorie_target: float,
    required: list[Ingredient] | None = None,
) -> list[Recipe]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return generate_rule_based(in_stock, count, calorie_target, required)

    try:
        return _call_claude(in_stock, count, calorie_target, api_key, required or [])
    except Exception as exc:
        print(f"Claude generation failed ({exc}), falling back to rule-based.")
        return generate_rule_based(in_stock, count, calorie_target, required)


def _call_claude(
    in_stock: list[Ingredient],
    count: int,
    calorie_target: float,
    api_key: str,
    required: list[Ingredient] | None = None,
) -> list[Recipe]:
    import anthropic
    required = required or []

    ingredient_list = "\n".join(
        f"- id={ing.id} name={ing.name!r} category={ing.category} "
        f"unit={ing.unit_name} grams_per_unit={ing.grams_per_unit} "
        f"cal_per_100g={ing.calories_per_100g}"
        for ing in in_stock
    )

    prompt = f"""You are a nutritionist creating smoothie recipes.

Available ingredients:
{ingredient_list}

Create {count} smoothie recipes, each targeting approximately {calorie_target:.0f} kcal.
Rules:
- Each smoothie uses a SUBSET of the available ingredients (not all of them).
- Use AT MOST 7 ingredients per recipe (fewer is fine — simple smoothies are good).
- Use realistic portion sizes: 150-250 ml for liquids, 50-150 g for gram-based fruits,
  1-2 for whole items like bananas, 1-2 tbsp for powders/seeds.
- Each recipe must have a catchy title.
- Do NOT use cups — use the ingredient's own unit.
{f"- REQUIRED: Every recipe MUST include ALL of these ingredients (they may be used in any amount): {', '.join(f'{ing.name} (id={ing.id})' for ing in required)}." if required else ""}

Respond ONLY with valid JSON in this exact format:
{{
  "recipes": [
    {{
      "title": "...",
      "items": [
        {{"ingredient_id": <int>, "units": <float>}},
        ...
      ]
    }}
  ]
}}"""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    data = json.loads(raw)
    by_id = {ing.id: ing for ing in in_stock}

    recipes: list[Recipe] = []
    for raw_recipe in data["recipes"]:
        items: list[tuple[Ingredient, float]] = []
        for raw_item in raw_recipe["items"]:
            ing = by_id.get(raw_item["ingredient_id"])
            if ing is None:
                continue
            items.append((ing, float(raw_item["units"])))
        if not items:
            continue
        if len(items) > 7:
            required_ids = {ing.id for ing in required}
            items.sort(key=lambda pair: pair[0].id in required_ids or _calories(*pair), reverse=True)
            items = items[:7]
        recipes.append(Recipe(
            title=raw_recipe["title"],
            items=_build_recipe_items(items),
            **_recipe_totals(items),
        ))

    return recipes
