const BASE = import.meta.env.VITE_API_URL ?? "";

async function request(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  ingredients: {
    list: () => request("GET", "/api/ingredients"),
    create: (data) => request("POST", "/api/ingredients", data),
    update: (id, data) => request("PUT", `/api/ingredients/${id}`, data),
    delete: (id) => request("DELETE", `/api/ingredients/${id}`),
    lookup: (q) => request("GET", `/api/ingredients/lookup?q=${encodeURIComponent(q)}`),
  },
  generate: (params) => request("POST", "/api/generate", params),
  favorites: {
    list: () => request("GET", "/api/favorites"),
    create: (recipe) => request("POST", "/api/favorites", recipe),
    delete: (id) => request("DELETE", `/api/favorites/${id}`),
  },
};
