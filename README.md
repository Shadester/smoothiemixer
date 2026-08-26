# SmoothieMixer

Web app to manage a home ingredient pantry and generate smoothie recipes with calorie targets.

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
