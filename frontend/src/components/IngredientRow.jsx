import { useState } from "react";

const CATEGORIES = ["fruit", "liquid", "protein", "veggie", "fat", "sweetener", "extra"];

export function IngredientRow({ ingredient, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ ...ingredient });

  function handleToggleStock() {
    onUpdate(ingredient.id, { ...ingredient, in_stock: !ingredient.in_stock });
  }

  function handleSave() {
    onUpdate(ingredient.id, {
      ...form,
      grams_per_unit: parseFloat(form.grams_per_unit),
      calories_per_100g: parseFloat(form.calories_per_100g),
    });
    setEditing(false);
  }

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  if (editing) {
    return (
      <tr className="editing-row">
        <td>
          <input value={form.name} onChange={(e) => set("name", e.target.value)} />
        </td>
        <td>
          <select value={form.category} onChange={(e) => set("category", e.target.value)}>
            {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
          </select>
        </td>
        <td>
          <input value={form.unit_name} onChange={(e) => set("unit_name", e.target.value)} style={{ width: 70 }} />
        </td>
        <td>
          <input type="number" min="0.1" step="0.1" value={form.grams_per_unit}
            onChange={(e) => set("grams_per_unit", e.target.value)} style={{ width: 70 }} />
        </td>
        <td>
          <input type="number" min="0" step="1" value={form.calories_per_100g}
            onChange={(e) => set("calories_per_100g", e.target.value)} style={{ width: 70 }} />
        </td>
        <td>
          <input type="checkbox" checked={form.in_stock}
            onChange={(e) => set("in_stock", e.target.checked)} />
        </td>
        <td className="actions">
          <button className="btn-save" onClick={handleSave}>Save</button>
          <button className="btn-cancel" onClick={() => { setForm({ ...ingredient }); setEditing(false); }}>
            Cancel
          </button>
        </td>
      </tr>
    );
  }

  return (
    <tr className={ingredient.in_stock ? "" : "out-of-stock"}>
      <td>{ingredient.name}</td>
      <td><span className={`category-badge cat-${ingredient.category}`}>{ingredient.category}</span></td>
      <td>{ingredient.unit_name}</td>
      <td>{ingredient.grams_per_unit} g</td>
      <td>{ingredient.calories_per_100g} kcal</td>
      <td>
        <input type="checkbox" checked={ingredient.in_stock} onChange={handleToggleStock} />
      </td>
      <td className="actions">
        <button className="btn-edit" onClick={() => setEditing(true)}>Edit</button>
        <button className="btn-delete" onClick={() => onDelete(ingredient.id)}>Delete</button>
      </td>
    </tr>
  );
}
