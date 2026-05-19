# Fake Error Generator

A CRUD app that generates absurd, plausible-sounding error messages and lets you save, edit, and share your favorites.

> `ERROR 0x80FU: stack overflowed into the carpet`

## Stack

- **Backend:** FastAPI + SQLAlchemy + Alembic + SlowAPI rate limiting
- **DB:** SQLite (dev) / Postgres (prod)
- **Frontend:** React 18 + Vite + TypeScript + Tailwind + TanStack Query + Zod
- **Tests:** pytest + httpx (backend), Vitest + React Testing Library (frontend)
- **Container:** Docker + docker-compose

## Layout

```
backend/      FastAPI app, Alembic migrations, seed data, tests
frontend/     Vite + React app
docker-compose.yml
.env.example
```

## Quick start — Docker

```bash
docker-compose up --build
```

Boots Postgres + backend (`:8000`) + frontend (`:5173`). The backend container runs migrations and seeds the vocab/template tables on first boot.

- App: http://localhost:5173
- API: http://localhost:8000/api
- OpenAPI docs: http://localhost:8000/docs

## Local dev — without Docker

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python seed.py
uvicorn app.main:app --reload --port 8000
```

Or with `uv`:

```bash
cd backend
uv sync
alembic upgrade head
python seed.py
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
pnpm install     # or: npm install
pnpm dev         # http://localhost:5173
```

The Vite dev server proxies `/api` → `http://localhost:8000`.

## Tests

```bash
# backend
cd backend && pytest

# frontend
cd frontend && pnpm test
```

## API surface

All routes under `/api`.

### Generation (no persistence)
- `POST /generate` — body `{ severity?, subsystem?, seed? }`
- `GET /preview/:seed` — deterministic, shareable

### CRUD `/errors`
- `POST` create · `GET` list (filters: `severity`, `subsystem`, `favorite`, `q`, `tag`, `page`, `limit`)
- `GET/PUT/PATCH/DELETE /errors/:id`

### Admin
- `GET/POST/PUT/DELETE /templates`
- `GET/POST/DELETE /vocab`
- `GET /stats` · `GET /healthz`

## Data model

- **errors** — saved errors (`code`, `title`, `description`, `severity`, `subsystem`, `tags`, `is_favorite`, timestamps)
- **templates** — generation patterns with slots like `{verb_past} {noun} into the {place}`. Has a `kind` (`title` or `description`), optional `severity_hint` (used for `EXISTENTIAL`-only templates), and a `weight` for weighted sampling.
- **vocab** — slot/value pairs filling the templates.

## Generation behaviour

- **Seed:** every generation runs through a seeded RNG. `/preview/:seed` is deterministic. Seeds are 8-char base32 strings.
- **Code:** `0x` + 1–6 hex digits + optional 1–2 uppercase letters. Regex: `^0x[0-9A-F]{1,6}[A-Z]{0,2}$`. Not unique — cosmetic only.
- **Severity weights** (when not specified): ERROR 40%, WARNING 25%, CRITICAL 15%, INFO 15%, EXISTENTIAL 5%. `EXISTENTIAL` pulls from a more philosophical template pool.

## Validation

- title ≤ 120 chars · description ≤ 500 · subsystem ≤ 60
- code matches the regex above
- Severity must be in the enum
- 422 on validation failure

## Rate limiting

- 60 generations/min per IP (`POST /generate`)
- 120/min on CRUD routes

Storage falls back to in-memory; set `RATE_LIMIT_REDIS_URL` for distributed.

## Env vars

See `.env.example`.

- `DATABASE_URL` — default `sqlite:///./errors.db`
- `CORS_ORIGINS` — comma-separated
- `RATE_LIMIT_REDIS_URL` — optional

## UI

- **Home** (`/`) — a faux-OS dialog rendering of the generated error, with **Generate Another**, **Save**, **Copy as text**, **Copy as image** (`html-to-image`), **Share** (copies `/preview/:seed`). Filter chips above for severity and subsystem.
- **Library** (`/library`) — saved errors in a grid; filters sidebar (severity, search, tag, favorites-only); edit/favorite/delete actions; pagination.
- **Edit modal** — editable fields with a per-field **regenerate** button that calls `/generate` and swaps in just that slot.
- **Skins** — tabbed toggle in header switches between **win98**, **aqua**, **terminal**, **ios**. Pure CSS.

## Production notes

- Use Postgres, not SQLite (concurrent writes will bite you).
- Build the frontend (`pnpm build`) and serve the `dist/` via any static host, or mount via FastAPI `StaticFiles`.
- Single-container deploy works on Fly / Railway / Render.
