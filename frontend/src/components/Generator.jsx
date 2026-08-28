import { useState } from "react";
import { api } from "../api";
import { usePersistedState } from "../usePersistedState";
import { RecipeCard } from "./RecipeCard";

export function Generator({ inStockCount, ingredients = [] }) {
  const [count, setCount] = usePersistedState("smoothiemixer.count", 7);
  const [calorieTarget, setCalorieTarget] = usePersistedState(
    "smoothiemixer.calorieTarget",
    400
  );
  const [mode, setMode] = usePersistedState("smoothiemixer.mode", "rule");
  const [requiredIds, setRequiredIds] = usePersistedState(
    "smoothiemixer.requiredIds",
    []
  );
  const [highProtein, setHighProtein] = usePersistedState(
    "smoothiemixer.highProtein",
    false
  );
  const [recipes, setRecipes] = usePersistedState("smoothiemixer.lastRecipes", []);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const inStockIngredients = ingredients.filter((i) => i.in_stock);

  function toggleRequired(id) {
    setRequiredIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function handleGenerate(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setRecipes([]);
    try {
      const result = await api.generate({
        count: parseInt(count),
        calorie_target: parseFloat(calorieTarget),
        mode,
        required_ingredient_ids: requiredIds,
        high_protein: highProtein,
      });
      setRecipes(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="generator">
      <h2>Generate Smoothies</h2>

      {inStockCount === 0 && (
        <div className="warning-banner">
          No in-stock ingredients. Mark some ingredients as in stock in the Pantry first.
        </div>
      )}

      <form className="generate-form" onSubmit={handleGenerate}>
        <label>
          Number of recipes
          <input
            type="number"
            min={5}
            max={10}
            value={count}
            onChange={(e) => setCount(e.target.value)}
            style={{ width: 60 }}
          />
        </label>

        <label>
          Calorie target (kcal)
          <input
            type="number"
            min={50}
            max={2000}
            step={10}
            value={calorieTarget}
            onChange={(e) => setCalorieTarget(e.target.value)}
            style={{ width: 80 }}
          />
        </label>

        <div className="mode-toggle">
          <label>
            <input
              type="radio"
              name="mode"
              value="rule"
              checked={mode === "rule"}
              onChange={() => setMode("rule")}
            />
            Rule-based
          </label>
          <label>
            <input
              type="radio"
              name="mode"
              value="ai"
              checked={mode === "ai"}
              onChange={() => setMode("ai")}
            />
            AI (Claude)
          </label>
        </div>

        <label className="mode-toggle-item">
          <input
            type="checkbox"
            checked={highProtein}
            onChange={(e) => setHighProtein(e.target.checked)}
          />
          High protein
        </label>

        {inStockIngredients.length > 0 && (
          <div className="required-section">
            <span className="required-label">Must include</span>
            <div className="required-chips">
              {inStockIngredients.map((ing) => {
                const active = requiredIds.includes(ing.id);
                return (
                  <button
                    key={ing.id}
                    type="button"
                    className={`chip${active ? " chip--active" : ""}`}
                    onClick={() => toggleRequired(ing.id)}
                  >
                    {ing.name}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <button
          type="submit"
          className="btn-primary btn-generate"
          disabled={loading || inStockCount === 0}
        >
          {loading ? "Generating…" : "Generate"}
        </button>
      </form>

      {error && <div className="error-banner">{error}</div>}

      {recipes.length > 0 && (
        <div className="recipes-grid">
          {recipes.map((r, i) => (
            <RecipeCard key={i} recipe={r} onFavorite={api.favorites.create} />
          ))}
        </div>
      )}
    </div>
  );
}
