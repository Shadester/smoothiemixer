import { useState } from "react";

function formatUnits(units, unitName) {
  // Display like "1 banana", "½ scoop", "250 ml", "2 tbsp"
  if (units === 0.5) return `½ ${unitName}`;
  if (units === 1.5) return `1½ ${unitName}`;
  if (units === 2.5) return `2½ ${unitName}`;
  return `${units} ${unitName}`;
}

export function RecipeCard({ recipe, onFavorite, onRemove }) {
  const [favorited, setFavorited] = useState(false);

  async function handleFavorite() {
    await onFavorite(recipe);
    setFavorited(true);
  }

  return (
    <div className="recipe-card">
      <div className="recipe-header">
        <h3 className="recipe-title">{recipe.title}</h3>
        <div className="recipe-header-actions">
          <span className="recipe-total">{Math.round(recipe.total_calories)} kcal</span>
          {onFavorite && (
            <button
              type="button"
              className="btn-favorite"
              onClick={handleFavorite}
              disabled={favorited}
              title={favorited ? "Saved to favorites" : "Save to favorites"}
            >
              {favorited ? "★" : "☆"}
            </button>
          )}
          {onRemove && (
            <button
              type="button"
              className="btn-delete"
              onClick={() => onRemove(recipe)}
            >
              Remove
            </button>
          )}
        </div>
      </div>
      <ul className="recipe-items">
        {recipe.items.map((item, i) => (
          <li key={i}>
            <span className="item-amount">
              {formatUnits(item.units, item.unit_name)}
            </span>
            <span className="item-name">{item.name}</span>
            <span className="item-meta">
              ({item.grams}g — {Math.round(item.calories)} kcal)
            </span>
          </li>
        ))}
      </ul>
      <div className="recipe-totals">
        <span>Protein {Math.round(recipe.total_protein)}g</span>
        <span>Carbs {Math.round(recipe.total_carbs)}g</span>
        <span>Fat {Math.round(recipe.total_fat)}g</span>
        <span>Sugar {Math.round(recipe.total_sugar)}g</span>
        <span>Fiber {Math.round(recipe.total_fiber)}g</span>
      </div>
    </div>
  );
}
