# Murmur — Backend

FastAPI backend for **Murmur**, a Character.AI-style chat app: create characters, start chats, customize behavior, and talk to personas powered by OpenAI + LangGraph.

Companion frontend: [murmur-web](https://github.com/valtykhoniuk/murmur-web) (separate repo).

**Live API:** https://murmur-oa8r.onrender.com  
**Health:** https://murmur-oa8r.onrender.com/health

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

- Health: `GET http://localhost:8000/health`
- Docs: `http://localhost:8000/docs`

### 4. Seed users

On startup, the app seeds users from `.env` if they don't exist:

| Role   | Env vars                | Notes                        |
|--------|-------------------------|------------------------------|
| owner  | `OWNER_EMAIL/PASSWORD`  | Full access                  |
| friend | `DARIIA_EMAIL/PASSWORD` | Full access                |
| public | `DEMO_EMAIL/PASSWORD` | Demo account, 20-msg limit   |

Use a valid email format (e.g. `owner@murmur.dev`) — login rejects invalid addresses with HTTP 422.

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
| `CORS_ORIGINS` | prod | Comma-separated frontend URLs |
| `OWNER_EMAIL/PASSWORD` | no | Seed owner account |
| `DARIIA_EMAIL/PASSWORD` | no | Seed friend account |
| `DEMO_EMAIL/PASSWORD` | no | Seed demo account |

## Deploy (Neon + Render)

Production setup used for the live demo:

1. **Neon** — create a Postgres project, copy the `postgresql://...` connection string.
2. **Render** — New Web Service → connect this repo.

| Setting | Value |
|---------|--------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

3. Add all env vars from `.env.example` in Render **Environment**.
4. Set `DATABASE_URL` to the Neon connection string (not `localhost`).
5. After deploying the frontend, set `CORS_ORIGINS`:

```bash
http://localhost:5173,https://your-app.vercel.app
```

6. Redeploy if you change `CORS_ORIGINS`.

**Free tier note:** Render sleeps after ~15 min idle. The first request after sleep may take 30–60 seconds (cold start).

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| CORS / preflight 400 | Add your Vercel URL to `CORS_ORIGINS` and redeploy |
| Login 422 | Email must be valid (`user@domain.tld`) |
| 503 on chat | Check `OPENAI_API_KEY` on Render |
| Empty Neon tables | Backend must start once with correct `DATABASE_URL` |

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
