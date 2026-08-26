"""Seed the database with common smoothie ingredients on first run."""
from db import db

STARTER_INGREDIENTS = [
    # (name, category, unit_name, grams_per_unit, calories_per_100g,
    #  protein_per_100g, carbs_per_100g, fat_per_100g, sugar_per_100g, fiber_per_100g)
    ("Banana",          "fruit",     "banana",   120,  89,  1.1, 22.8,  0.3, 12.2,  2.6),
    ("Strawberry",      "fruit",     "g",          1,  32,  0.7,  7.7,  0.3,  4.9,  2.0),
    ("Blueberry",       "fruit",     "g",          1,  57,  0.7, 14.5,  0.3, 10.0,  2.4),
    ("Raspberry",       "fruit",     "g",          1,  52,  1.2, 11.9,  0.7,  4.4,  6.5),
    ("Mango",           "fruit",     "g",          1,  60,  0.8, 15.0,  0.4, 13.7,  1.6),
    ("Pineapple",       "fruit",     "g",          1,  50,  0.5, 13.1,  0.1,  9.9,  1.4),
    ("Spinach",         "veggie",    "handful",   30,  23,  2.9,  3.6,  0.4,  0.4,  2.2),
    ("Kale",            "veggie",    "handful",   30,  49,  4.3,  8.8,  0.9,  2.3,  3.6),
    ("Avocado",         "fat",       "avocado",  150, 160,  2.0,  8.5, 14.7,  0.7,  6.7),
    ("Peanut Butter",   "fat",       "tbsp",      16, 588, 25.1, 20.0, 50.4,  9.2,  6.0),
    ("Oats",            "extra",     "tbsp",      10, 389, 16.9, 66.3,  6.9,  0.0, 10.6),
    ("Chia Seeds",      "extra",     "tbsp",      12, 486, 16.5, 42.1, 30.7,  0.0, 34.4),
    ("Flaxseed",        "extra",     "tbsp",      10, 534, 18.3, 28.9, 42.2,  1.6, 27.3),
    ("Honey",           "sweetener", "tbsp",      21, 304,  0.3, 82.4,  0.0, 82.1,  0.2),
    ("Medjool Date",    "sweetener", "date",      24, 277,  1.8, 75.0,  0.2, 66.5,  6.7),
    ("Protein Powder",  "protein",   "scoop",     30, 370, 80.0,  8.0,  3.0,  2.0,  1.0),
    ("Greek Yogurt",    "protein",   "g",          1,  59, 10.2,  3.6,  0.4,  3.2,  0.0),
    ("Milk",            "liquid",    "ml",          1,  42,  3.4,  5.0,  1.0,  5.0,  0.0),
    ("Oat Milk",        "liquid",    "ml",          1,  45,  1.0,  6.7,  1.5,  4.1,  0.8),
    ("Apple Juice",     "liquid",    "ml",          1,  46,  0.1, 11.3,  0.1, 10.1,  0.2),
    ("Coconut Water",   "liquid",    "ml",          1,  19,  0.7,  3.7,  0.2,  2.6,  1.1),
    ("Water",           "liquid",    "ml",          1,   0,  0.0,  0.0,  0.0,  0.0,  0.0),
    ("Orange Juice",    "liquid",    "ml",          1,  45,  0.7, 10.4,  0.2,  8.4,  0.2),
    ("Ginger",          "extra",     "tbsp",       6,  80,  1.8, 17.8,  0.8,  1.7,  2.0),
    ("Cinnamon",        "extra",     "tsp",         2, 247,  4.0, 80.6,  1.2,  2.2, 53.1),
    ("Cocoa Powder",    "extra",     "tbsp",        7, 228, 19.6, 57.9, 13.7,  1.8, 37.0),
    ("Ice",             "extra",     "g",           1,   0,  0.0,  0.0,  0.0,  0.0,  0.0),
]


def seed() -> None:
    with db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
        if count > 0:
            return  # already seeded
        conn.executemany(
            """INSERT INTO ingredients
               (name, category, unit_name, grams_per_unit, calories_per_100g,
                protein_per_100g, carbs_per_100g, fat_per_100g, sugar_per_100g, fiber_per_100g,
                in_stock)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            STARTER_INGREDIENTS,
        )
        print(f"Seeded {len(STARTER_INGREDIENTS)} ingredients.")


def backfill_macros() -> None:
    """Fill in macro values for pre-existing rows that predate those columns.

    Matches by name against STARTER_INGREDIENTS and only touches rows where
    every macro is still at its post-migration default of 0, so it never
    overwrites values a user has already edited.
    """
    macros_by_name = {row[0]: row[5:10] for row in STARTER_INGREDIENTS}
    with db() as conn:
        rows = conn.execute(
            """SELECT id, name FROM ingredients
               WHERE protein_per_100g = 0 AND carbs_per_100g = 0
                 AND fat_per_100g = 0 AND sugar_per_100g = 0 AND fiber_per_100g = 0"""
        ).fetchall()
        updated = 0
        for row in rows:
            macros = macros_by_name.get(row["name"])
            if macros is None:
                continue
            conn.execute(
                """UPDATE ingredients SET
                   protein_per_100g=?, carbs_per_100g=?, fat_per_100g=?,
                   sugar_per_100g=?, fiber_per_100g=?
                   WHERE id=?""",
                (*macros, row["id"]),
            )
            updated += 1
        if updated:
            print(f"Backfilled macros for {updated} ingredient(s).")


if __name__ == "__main__":
    seed()
