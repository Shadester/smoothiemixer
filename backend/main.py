"""Smoothie Mixer — FastAPI backend."""
from __future__ import annotations

import urllib.parse
import urllib.request
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db import db, fix_implausible_calories, init_db
from generator import generate_rule_based, generate_with_claude
from models import (
    FavoriteRecipe,
    GenerateRequest,
    Ingredient,
    IngredientIn,
    IngredientLookup,
    Recipe,
)
from seed import backfill_macros, seed

app = FastAPI(title="SmoothieMixer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed()
    backfill_macros()
    fix_implausible_calories()


# ---------------------------------------------------------------------------
# Ingredients
# ---------------------------------------------------------------------------

@app.get("/api/ingredients", response_model=list[Ingredient])
def list_ingredients():
    with db() as conn:
        rows = conn.execute("SELECT * FROM ingredients ORDER BY category, name").fetchall()
    return [Ingredient(**dict(r)) for r in rows]


@app.post("/api/ingredients", response_model=Ingredient, status_code=201)
def create_ingredient(data: IngredientIn):
    with db() as conn:
        cur = conn.execute(
            """INSERT INTO ingredients
               (name, category, unit_name, grams_per_unit, calories_per_100g, in_stock)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (data.name, data.category, data.unit_name,
             data.grams_per_unit, data.calories_per_100g, int(data.in_stock)),
        )
        row = conn.execute(
            "SELECT * FROM ingredients WHERE id=?", (cur.lastrowid,)
        ).fetchone()
    return Ingredient(**dict(row))


@app.put("/api/ingredients/{ingredient_id}", response_model=Ingredient)
def update_ingredient(ingredient_id: int, data: IngredientIn):
    with db() as conn:
        cur = conn.execute(
            """UPDATE ingredients SET
               name=?, category=?, unit_name=?, grams_per_unit=?,
               calories_per_100g=?, in_stock=?
               WHERE id=?""",
            (data.name, data.category, data.unit_name,
             data.grams_per_unit, data.calories_per_100g, int(data.in_stock),
             ingredient_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        row = conn.execute(
            "SELECT * FROM ingredients WHERE id=?", (ingredient_id,)
        ).fetchone()
    return Ingredient(**dict(row))


@app.delete("/api/ingredients/{ingredient_id}", status_code=204)
def delete_ingredient(ingredient_id: int):
    with db() as conn:
        cur = conn.execute(
            "DELETE FROM ingredients WHERE id=?", (ingredient_id,)
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ingredient not found")


# ---------------------------------------------------------------------------
# Online ingredient lookup (Open Food Facts)
# ---------------------------------------------------------------------------

@app.get("/api/ingredients/lookup", response_model=list[IngredientLookup])
def lookup_ingredient(q: str = Query(..., min_length=1)):
    url = (
        "https://world.openfoodfacts.org/cgi/search.pl?"
        + urllib.parse.urlencode({
            "search_terms": q,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 10,
            "fields": "product_name,nutriments,serving_size,serving_quantity,product_quantity",
        })
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SmoothieMixer/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Open Food Facts unavailable: {exc}")

    results: list[IngredientLookup] = []
    seen: set[str] = set()

    for p in data.get("products", []):
        name = (p.get("product_name") or "").strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())

        nutriments = p.get("nutriments", {})
        # Prefer the dedicated kcal field; fall back to kJ fields (always kJ in OFF)
        kcal = nutriments.get("energy-kcal_100g")
        if kcal is None:
            kj = nutriments.get("energy-kj_100g") or nutriments.get("energy_100g")
            kcal = (kj / 4.184) if kj else 0

        # Derive a sensible grams_per_unit from serving info
        serving_g = p.get("serving_quantity") or p.get("product_quantity")
        try:
            serving_g = float(str(serving_g).replace("g", "").strip()) if serving_g else None
        except ValueError:
            serving_g = None

        def _num(field: str) -> float | None:
            value = nutriments.get(field)
            return round(float(value), 1) if value is not None else None

        results.append(IngredientLookup(
            name=name,
            calories_per_100g=round(float(kcal or 0), 1),
            protein_per_100g=_num("proteins_100g"),
            carbs_per_100g=_num("carbohydrates_100g"),
            fat_per_100g=_num("fat_100g"),
            sugar_per_100g=_num("sugars_100g"),
            fiber_per_100g=_num("fiber_100g"),
            suggested_grams_per_unit=round(serving_g, 1) if serving_g else None,
            serving_size_label=p.get("serving_size"),
        ))

    return results[:8]


# ---------------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------------

def _row_to_favorite(row) -> FavoriteRecipe:
    data = dict(row)
    items = json.loads(data.pop("items"))
    return FavoriteRecipe(items=items, **data)


@app.get("/api/favorites", response_model=list[FavoriteRecipe])
def list_favorites():
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM favorites ORDER BY created_at DESC"
        ).fetchall()
    return [_row_to_favorite(r) for r in rows]


@app.post("/api/favorites", response_model=FavoriteRecipe, status_code=201)
def create_favorite(recipe: Recipe):
    with db() as conn:
        cur = conn.execute(
            """INSERT INTO favorites
               (title, items, total_calories, total_protein, total_carbs,
                total_fat, total_sugar, total_fiber)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                recipe.title,
                json.dumps([item.model_dump() for item in recipe.items]),
                recipe.total_calories, recipe.total_protein, recipe.total_carbs,
                recipe.total_fat, recipe.total_sugar, recipe.total_fiber,
            ),
        )
        row = conn.execute(
            "SELECT * FROM favorites WHERE id=?", (cur.lastrowid,)
        ).fetchone()
    return _row_to_favorite(row)


@app.delete("/api/favorites/{favorite_id}", status_code=204)
def delete_favorite(favorite_id: int):
    with db() as conn:
        cur = conn.execute("DELETE FROM favorites WHERE id=?", (favorite_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Favorite not found")


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------

@app.post("/api/generate", response_model=list[Recipe])
def generate(req: GenerateRequest):
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM ingredients WHERE in_stock=1"
        ).fetchall()

    if not rows:
        raise HTTPException(status_code=400, detail="No in-stock ingredients.")

    in_stock = [Ingredient(**dict(r)) for r in rows]

    # Resolve required ingredients (only keep those that are actually in-stock)
    in_stock_ids = {ing.id for ing in in_stock}
    required = [
        ing for ing in in_stock
        if ing.id in req.required_ingredient_ids and ing.id in in_stock_ids
    ]

    if req.mode == "ai":
        recipes = generate_with_claude(in_stock, req.count, req.calorie_target, required, req.high_protein)
    else:
        recipes = generate_rule_based(in_stock, req.count, req.calorie_target, required, req.high_protein)

    if not recipes:
        raise HTTPException(
            status_code=422,
            detail="Could not generate recipes with the current ingredient set.",
        )
    return recipes


# ---------------------------------------------------------------------------
# Serve built frontend (production / Docker)
# ---------------------------------------------------------------------------

_STATIC = Path(__file__).parent / "static"
if _STATIC.exists():
    app.mount("/", StaticFiles(directory=str(_STATIC), html=True), name="static")
