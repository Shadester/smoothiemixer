"""Seed the database with common smoothie ingredients on first run."""
from db import db

STARTER_INGREDIENTS = [
    # (name, category, unit_name, grams_per_unit, calories_per_100g)
    ("Banana",          "fruit",     "banana",   120,  89),
    ("Strawberry",      "fruit",     "g",          1,  32),
    ("Blueberry",       "fruit",     "g",          1,  57),
    ("Raspberry",       "fruit",     "g",          1,  52),
    ("Mango",           "fruit",     "g",          1,  60),
    ("Pineapple",       "fruit",     "g",          1,  50),
    ("Spinach",         "veggie",    "handful",   30,  23),
    ("Kale",            "veggie",    "handful",   30,  49),
    ("Avocado",         "fat",       "avocado",  150, 160),
    ("Peanut Butter",   "fat",       "tbsp",      16, 588),
    ("Oats",            "extra",     "tbsp",      10, 389),
    ("Chia Seeds",      "extra",     "tbsp",      12, 486),
    ("Flaxseed",        "extra",     "tbsp",      10, 534),
    ("Honey",           "sweetener", "tbsp",      21, 304),
    ("Medjool Date",    "sweetener", "date",      24, 277),
    ("Protein Powder",  "protein",   "scoop",     30, 370),
    ("Greek Yogurt",    "protein",   "g",          1,  59),
    ("Milk",            "liquid",    "ml",          1,  42),
    ("Oat Milk",        "liquid",    "ml",          1,  45),
    ("Apple Juice",     "liquid",    "ml",          1,  46),
    ("Coconut Water",   "liquid",    "ml",          1,  19),
    ("Water",           "liquid",    "ml",          1,   0),
    ("Orange Juice",    "liquid",    "ml",          1,  45),
    ("Ginger",          "extra",     "tbsp",       6,  80),
    ("Cinnamon",        "extra",     "tsp",         2, 247),
    ("Cocoa Powder",    "extra",     "tbsp",        7, 228),
    ("Ice",             "extra",     "g",           1,   0),
]


def seed() -> None:
    with db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
        if count > 0:
            return  # already seeded
        conn.executemany(
            """INSERT INTO ingredients
               (name, category, unit_name, grams_per_unit, calories_per_100g, in_stock)
               VALUES (?, ?, ?, ?, ?, 1)""",
            STARTER_INGREDIENTS,
        )
        print(f"Seeded {len(STARTER_INGREDIENTS)} ingredients.")


if __name__ == "__main__":
    seed()
