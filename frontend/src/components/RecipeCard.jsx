function formatUnits(units, unitName) {
  // Display like "1 banana", "½ scoop", "250 ml", "2 tbsp"
  if (units === 0.5) return `½ ${unitName}`;
  if (units === 1.5) return `1½ ${unitName}`;
  if (units === 2.5) return `2½ ${unitName}`;
  return `${units} ${unitName}`;
}

export function RecipeCard({ recipe }) {
  return (
    <div className="recipe-card">
      <div className="recipe-header">
        <h3 className="recipe-title">{recipe.title}</h3>
        <span className="recipe-total">{Math.round(recipe.total_calories)} kcal</span>
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
    </div>
  );
}
