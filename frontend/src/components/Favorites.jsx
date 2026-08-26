import { useEffect, useState } from "react";
import { api } from "../api";
import { RecipeCard } from "./RecipeCard";

export function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.favorites
      .list()
      .then(setFavorites)
      .catch((e) => setError(e.message));
  }, []);

  async function handleRemove(recipe) {
    await api.favorites.delete(recipe.id);
    setFavorites((prev) => prev.filter((r) => r.id !== recipe.id));
  }

  return (
    <div className="favorites">
      <h2>Favorites</h2>
      {error && <div className="error-banner">{error}</div>}
      {favorites.length === 0 && !error && (
        <div className="empty-state">
          No favorites yet. Star a recipe on the Generate page to save it here.
        </div>
      )}
      {favorites.length > 0 && (
        <div className="recipes-grid">
          {favorites.map((r) => (
            <RecipeCard key={r.id} recipe={r} onRemove={handleRemove} />
          ))}
        </div>
      )}
    </div>
  );
}
