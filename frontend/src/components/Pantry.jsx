import { useState } from "react";
import { api } from "../api";

const CATEGORIES = ["fruit", "liquid", "protein", "veggie", "fat", "sweetener", "extra"];

export function Pantry({ ingredients, setIngredients }) {
  const [filter, setFilter] = useState("");
  const [error, setError] = useState(null);

  async function handleToggle(ingredient) {
    setError(null);
    try {
      const updated = await api.ingredients.update(ingredient.id, {
        ...ingredient,
        in_stock: !ingredient.in_stock,
      });
      setIngredients((prev) => prev.map((i) => (i.id === ingredient.id ? updated : i)));
    } catch (err) {
      setError(err.message);
    }
  }

  const q = filter.toLowerCase();
  const visible = ingredients.filter((i) => i.name.toLowerCase().includes(q));

  const grouped = CATEGORIES.reduce((acc, cat) => {
    const items = visible.filter((i) => i.category === cat);
    if (items.length) acc[cat] = items;
    return acc;
  }, {});

  const inStockCount = ingredients.filter((i) => i.in_stock).length;

  return (
    <div className="pantry">
      <div className="pantry-header">
        <h2>Pantry</h2>
        <span className="pantry-count">{inStockCount} of {ingredients.length} in stock</span>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {ingredients.length === 0 ? (
        <div className="empty-state">
          No ingredients yet. Add some in the <strong>Ingredients</strong> tab.
        </div>
      ) : (
        <>
          <input
            className="pantry-search"
            placeholder="Search…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />

          <div className="pantry-groups">
            {Object.entries(grouped).map(([cat, items]) => (
              <div key={cat} className="pantry-group">
                <h3 className={`pantry-cat cat-${cat}`}>{cat}</h3>
                <ul className="pantry-list">
                  {items.map((ing) => (
                    <li
                      key={ing.id}
                      className={`pantry-item ${ing.in_stock ? "in-stock" : "out-stock"}`}
                      onClick={() => handleToggle(ing)}
                    >
                      <span className={`pantry-check ${ing.in_stock ? "checked" : ""}`}>
                        {ing.in_stock ? "✓" : ""}
                      </span>
                      <span className="pantry-name">{ing.name}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
            {Object.keys(grouped).length === 0 && (
              <p style={{ color: "var(--muted)" }}>No ingredients match "{filter}".</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
