import { useState, useRef } from "react";
import { api } from "../api";
import { usePersistedState } from "../usePersistedState";
import { IngredientRow } from "./IngredientRow";

const CATEGORIES = ["fruit", "liquid", "protein", "veggie", "fat", "sweetener", "extra"];

const EMPTY_FORM = {
  name: "",
  category: "fruit",
  unit_name: "",
  grams_per_unit: "",
  calories_per_100g: "",
  in_stock: true,
};

export function Ingredients({ ingredients, setIngredients }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState(null);
  const [filterCat, setFilterCat] = usePersistedState(
    "smoothiemixer.ingredientsFilterCat",
    "all"
  );

  // Online lookup state
  const [lookupQuery, setLookupQuery] = useState("");
  const [lookupResults, setLookupResults] = useState([]);
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupError, setLookupError] = useState(null);
  const debounceRef = useRef(null);

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  // Debounced online search
  function handleLookupChange(e) {
    const q = e.target.value;
    setLookupQuery(q);
    setLookupResults([]);
    setLookupError(null);
    clearTimeout(debounceRef.current);
    if (q.trim().length < 2) return;
    debounceRef.current = setTimeout(async () => {
      setLookupLoading(true);
      try {
        const results = await api.ingredients.lookup(q.trim());
        setLookupResults(results);
      } catch (err) {
        setLookupError("Could not reach Open Food Facts.");
      } finally {
        setLookupLoading(false);
      }
    }, 500);
  }

  function applyLookup(result) {
    setForm((f) => ({
      ...f,
      name: result.name,
      calories_per_100g: result.calories_per_100g,
      grams_per_unit: result.suggested_grams_per_unit ?? f.grams_per_unit,
    }));
    setLookupQuery("");
    setLookupResults([]);
  }

  async function handleAdd(e) {
    e.preventDefault();
    setError(null);
    try {
      const created = await api.ingredients.create({
        ...form,
        grams_per_unit: parseFloat(form.grams_per_unit),
        calories_per_100g: parseFloat(form.calories_per_100g),
      });
      setIngredients((prev) => [...prev, created]);
      setForm(EMPTY_FORM);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleUpdate(id, data) {
    setError(null);
    try {
      const updated = await api.ingredients.update(id, data);
      setIngredients((prev) => prev.map((i) => (i.id === id ? updated : i)));
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    setError(null);
    try {
      await api.ingredients.delete(id);
      setIngredients((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      setError(err.message);
    }
  }

  const visible = ingredients.filter(
    (i) => filterCat === "all" || i.category === filterCat
  );

  return (
    <div className="ingredients-page">
      <h2>Ingredients</h2>

      {error && <div className="error-banner">{error}</div>}

      {/* Category filter */}
      <div className="filters">
        <label>
          Category&nbsp;
          <select value={filterCat} onChange={(e) => setFilterCat(e.target.value)}>
            <option value="all">All</option>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </label>
      </div>

      {/* Ingredient table */}
      <div className="table-wrap">
        <table className="ingredient-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Unit</th>
              <th>g / unit</th>
              <th>kcal / 100g</th>
              <th>In pantry</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {visible.map((ing) => (
              <IngredientRow
                key={ing.id}
                ingredient={ing}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            ))}
            {visible.length === 0 && (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", color: "var(--muted)" }}>
                  No ingredients yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add ingredient */}
      <h3>Add ingredient</h3>

      {/* Online lookup */}
      <div className="lookup-wrap">
        <div className="lookup-field">
          <input
            className="lookup-input"
            placeholder="Search online (e.g. banana, oat milk)…"
            value={lookupQuery}
            onChange={handleLookupChange}
          />
          {lookupLoading && <span className="lookup-spinner">Searching…</span>}
        </div>
        {lookupError && <p className="lookup-error">{lookupError}</p>}
        {lookupResults.length > 0 && (
          <ul className="lookup-results">
            {lookupResults.map((r, i) => (
              <li key={i} className="lookup-result" onClick={() => applyLookup(r)}>
                <span className="lookup-result-name">{r.name}</span>
                <span className="lookup-result-meta">
                  {r.calories_per_100g} kcal/100g
                  {r.serving_size_label ? ` · ${r.serving_size_label}` : ""}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <form className="add-form" onSubmit={handleAdd}>
        <input
          required
          placeholder="Name"
          value={form.name}
          onChange={(e) => set("name", e.target.value)}
        />
        <select value={form.category} onChange={(e) => set("category", e.target.value)}>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <input
          required
          placeholder="Unit (e.g. banana, ml, g, scoop)"
          value={form.unit_name}
          onChange={(e) => set("unit_name", e.target.value)}
          style={{ width: 170 }}
        />
        <input
          required
          type="number"
          min="0.1"
          step="0.1"
          placeholder="g per unit"
          value={form.grams_per_unit}
          onChange={(e) => set("grams_per_unit", e.target.value)}
          style={{ width: 100 }}
        />
        <input
          required
          type="number"
          min="0"
          step="0.1"
          placeholder="kcal / 100g"
          value={form.calories_per_100g}
          onChange={(e) => set("calories_per_100g", e.target.value)}
          style={{ width: 110 }}
        />
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={form.in_stock}
            onChange={(e) => set("in_stock", e.target.checked)}
          />
          In pantry
        </label>
        <button type="submit" className="btn-primary">Add</button>
      </form>
    </div>
  );
}
