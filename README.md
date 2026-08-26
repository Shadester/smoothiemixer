# SmoothieMixer

Web app to manage a home ingredient pantry and generate smoothie recipes that hit a calorie target — self-hosted, runs great on a Raspberry Pi.

## Features

- Track a pantry of ingredients with calories, macros, and stock status
- Generate smoothie recipes for a target calorie count, either rule-based or via Claude ("AI mode")
- FastAPI backend + React frontend, packaged as a single Docker image
- SQLite storage in a named volume — no external database needed

## Quick start (Docker — Raspberry Pi)

```bash
# On the Pi (arm64) or any machine with Docker:
docker compose up --build
```

Open http://pi-hostname:8000

The SQLite database is stored in a named Docker volume and survives restarts.

### 32-bit Raspberry Pi (armv7)

Change the `platform:` line in `docker-compose.yml`:

```yaml
platform: linux/arm/v7
```

### AI mode (Claude)

Set `ANTHROPIC_API_KEY` in `docker-compose.yml` (uncomment the env line) then rebuild.
Without the key, AI mode automatically falls back to rule-based generation.

---

## Local development

### Backend

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -e .
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # proxies /api to localhost:8000
```

---

## Cross-building from macOS for the Pi

```bash
docker buildx build --platform linux/arm64 -t smoothiemixer:latest --load .
```

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/ingredients` | List pantry ingredients |
| `POST` | `/api/ingredients` | Add an ingredient |
| `PUT` | `/api/ingredients/{id}` | Update an ingredient |
| `DELETE` | `/api/ingredients/{id}` | Remove an ingredient |
| `GET` | `/api/ingredients/lookup` | Search ingredient nutrition data |
| `POST` | `/api/generate` | Generate recipes for a calorie target |

## Tech stack

Python / FastAPI · React (Vite) · SQLite · Docker (multi-stage, multi-arch) · Anthropic API (optional)
