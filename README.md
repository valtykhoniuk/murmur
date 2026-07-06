# Murmur — Backend

FastAPI backend for **Murmur**, a Character.AI-style chat app: create characters, start chats, customize behavior, and talk to personas powered by OpenAI + LangGraph.

Companion frontend: [murmur-web](../murmur-web) (separate repo).

## Features

- JWT auth (owner, friend, demo/public roles)
- CRUD for **characters** (create, read, update, delete)
- **Chats** with per-chat settings (temperature, reply length, speech style, etc.)
- **LangGraph** pipeline: build context → generate reply → rolling memory summary
- **Demo rate limit**: public users capped at 20 user messages total (`DEMO_MESSAGE_LIMIT`)
- Delete character (cascades chats/messages/summaries) or individual chats

## Stack

- Python 3.11+
- FastAPI, SQLModel, PostgreSQL
- LangChain + LangGraph + OpenAI

## Quick start (local)

### 1. PostgreSQL

Create a database:

```bash
createdb murmur
```

Tables are created automatically on first run via SQLModel metadata.

### 2. Environment

```bash
cp .env.example .env
# Edit .env — at minimum DATABASE_URL, SECRET_KEY, OPENAI_API_KEY
```

### 3. Install & run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health`

API docs: `http://localhost:8000/docs`

### 4. Seed users

On startup, the app seeds users from `.env` if they don't exist:

| Role   | Env vars              | Notes                          |
|--------|-----------------------|--------------------------------|
| owner  | `OWNER_EMAIL/PASSWORD`| Full access                    |
| friend | `DARIIA_EMAIL/PASSWORD` | Full access                  |
| public | `DEMO_EMAIL/PASSWORD` | Demo account, 20-msg limit   |

## API overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Email + password → JWT |
| POST | `/auth/demo` | Demo account token |
| GET | `/auth/me` | Current user |
| GET/POST | `/characters` | List / create |
| GET/PUT/DELETE | `/characters/{id}` | Read / update / delete |
| GET/POST | `/chats` | List / create |
| GET/PATCH/DELETE | `/chats/{id}` | Read / update settings / delete |
| GET | `/chats/{id}/messages` | Message history |
| POST | `/chats/{id}/message` | Send message → AI reply |

All routes except `/auth/login`, `/auth/demo`, and `/health` require `Authorization: Bearer <token>`.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | yes | PostgreSQL connection string |
| `SECRET_KEY` | yes | JWT signing key |
| `OPENAI_API_KEY` | yes | OpenAI API key |
| `OPENAI_MODEL` | no | Default `gpt-4.1-mini` |
| `DEMO_MESSAGE_LIMIT` | no | Default `20` — max user messages for `public` role |
| `OWNER_EMAIL/PASSWORD` | no | Seed owner account |
| `DARIIA_EMAIL/PASSWORD` | no | Seed friend account |
| `DEMO_EMAIL/PASSWORD` | no | Seed demo account |

## Deploy notes

Typical production setup:

1. **Backend** — Railway, Render, Fly.io, or any VPS running uvicorn behind HTTPS.
2. **Database** — managed PostgreSQL (Neon, Supabase, RDS, etc.).
3. Set all env vars in the host dashboard.
4. Run with a process manager, e.g.:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Point the frontend `VITE_API_URL` to your deployed API origin (see murmur-web README).

CORS: if frontend and backend are on different origins, add a CORS middleware in `app/main.py` for your frontend URL.

## Project structure

```
app/
  auth/          JWT login, demo, /me
  characters/    Character CRUD
  chats/         Chats, messages, demo limit, cleanup
  llm/           LangGraph, prompts, memory
  models/        SQLModel tables
  seed.py        User seeding on startup
```

## License

Personal portfolio project.
