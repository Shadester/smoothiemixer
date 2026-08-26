import { useEffect, useState } from "react";
import { api } from "./api";
import { Pantry } from "./components/Pantry";
import { Ingredients } from "./components/Ingredients";
import { Generator } from "./components/Generator";
import { Favorites } from "./components/Favorites";
import "./styles.css";

export default function App() {
  const [tab, setTab] = useState("generate");
  const [ingredients, setIngredients] = useState([]);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    api.ingredients
      .list()
      .then(setIngredients)
      .catch((e) => setLoadError(e.message));
  }, []);

  const inStockCount = ingredients.filter((i) => i.in_stock).length;

  return (
    <div className="app">
      <header className="app-header">
        <span className="app-logo">🥤</span>
        <h1>SmoothieMixer</h1>
        <nav>
          <button
            className={tab === "generate" ? "tab active" : "tab"}
            onClick={() => setTab("generate")}
          >
            Generate
          </button>
          <button
            className={tab === "pantry" ? "tab active" : "tab"}
            onClick={() => setTab("pantry")}
          >
            Pantry
            <span className="stock-badge">{inStockCount}</span>
          </button>
          <button
            className={tab === "ingredients" ? "tab active" : "tab"}
            onClick={() => setTab("ingredients")}
          >
            Ingredients
          </button>
          <button
            className={tab === "favorites" ? "tab active" : "tab"}
            onClick={() => setTab("favorites")}
          >
            Favorites
          </button>
        </nav>
      </header>

      <main className="app-main">
        {loadError && (
          <div className="error-banner">Could not load ingredients: {loadError}</div>
        )}
        {tab === "pantry" && (
          <Pantry ingredients={ingredients} setIngredients={setIngredients} />
        )}
        {tab === "ingredients" && (
          <Ingredients ingredients={ingredients} setIngredients={setIngredients} />
        )}
        {tab === "generate" && (
          <Generator inStockCount={inStockCount} ingredients={ingredients} />
        )}
        {tab === "favorites" && <Favorites />}
      </main>
    </div>
  );
}
