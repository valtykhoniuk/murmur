# Murmur — Backend

FastAPI backend for **Murmur**, a Character.AI-style chat app: create characters, start chats, customize behavior, and talk to personas powered by OpenAI + LangGraph.

Companion frontend: [murmur-web](https://github.com/valtykhoniuk/murmur-web) (separate repo).

**Live API:** http://murmur.us-east-1.elasticbeanstalk.com  
**Live app:** https://murmur-web-tawny.vercel.app  
**Health:** http://murmur.us-east-1.elasticbeanstalk.com/health

Production stack: **Neon** (Postgres) + **AWS Elastic Beanstalk** (API) + **Vercel** (frontend, proxies `/api` to EB).

## Features

- JWT auth (owner, friend, demo/public roles)
- CRUD for **characters** (create, read, update, delete)
- **Chats** with per-chat settings (temperature, reply length, speech style, etc.)
- **LangGraph** pipeline: build context → generate → LLM-as-judge verifier → retry or summarize memory
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

## LangGraph pipeline

Each `POST /chats/{id}/message` runs a compiled LangGraph (`app/llm/graph.py`). State is a shared dict (`ChatGraphState`) passed between nodes; each node reads from it and returns fields to merge in.

```
build_context → generate → verify_response ──pass──→ update_memory → END
                              │
                              └──fail (retry < 2)──→ generate
                              └──fail (retry ≥ 2)──→ update_memory → END
```

| Node | What it does |
|------|----------------|
| `build_context` | Builds system prompt from persona, chat settings, and rolling summary |
| `generate` | Calls the character LLM (temperature + max tokens from chat settings) |
| `verify_response` | **LLM-as-judge verifier** — separate LLM (`temperature=0`) scores the draft reply against persona, format, and settings; returns `{"pass": bool, "reason": "..."}` |
| `update_memory` | If history exceeds `max_messages`, summarizes older messages into `summaries` table |

**Conditional routing** (`route_after_verifier`) runs *after* `verify_response` finishes — not at graph build time. The router reads `verifier_pass` and `retry_count` from state:

- `pass=true` → save memory, return reply
- `pass=false` and `retry_count < 2` → regenerate
- `pass=false` and `retry_count ≥ 2` → accept last draft (avoid infinite loops)

Verifier prompt: `VERIFIER_PROMPT` in `app/llm/prompts.py`. Chain: `build_verifier_chain` in `app/llm/chain.py`.

If the verifier returns invalid JSON, the reply is allowed through (logged warning) so a failed verifier call does not break chat.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | yes | PostgreSQL connection string |
| `SECRET_KEY` | yes | JWT signing key |
| `OPENAI_API_KEY` | yes | OpenAI API key |
| `OPENAI_MODEL` | no | Default `gpt-4.1-mini` |
| `DEMO_MESSAGE_LIMIT` | no | Default `20` — max user messages for `public` role |
| `CORS_ORIGINS` | prod | Comma-separated frontend URLs |
| `SQL_ECHO` | no | Set `true` to log SQL queries |
| `OWNER_EMAIL/PASSWORD` | no | Seed owner account |
| `DARIIA_EMAIL/PASSWORD` | no | Seed friend account |
| `DEMO_EMAIL/PASSWORD` | no | Seed demo account |

## Deploy (Neon + AWS Elastic Beanstalk)

### 1. Database (Neon)

Create a project at [neon.tech](https://neon.tech), copy the `postgresql://...` connection string.

### 2. Elastic Beanstalk

1. [AWS Console](https://console.aws.amazon.com/elasticbeanstalk) → **Create application**
2. Platform: **Python 3.11** on **Amazon Linux 2023**
3. Preset: **Single instance** (t3.micro / t3.small)
4. Upload a zip of the repo root — files at the top level (`app/`, `requirements.txt`, `Procfile`), not nested in a subfolder. See `.ebignore` for exclusions.

```bash
cd murmur
zip -r ../murmur-deploy.zip . -x "*.git*" -x ".venv/*" -x ".env" -x "__pycache__/*" -x "*.zip"
```

5. After the environment is **Ok**, open **Configuration** → **Environment properties** and set:

| Variable | Example |
|----------|---------|
| `DATABASE_URL` | Neon connection string |
| `SECRET_KEY` | random secret |
| `OPENAI_API_KEY` | your key |
| `CORS_ORIGINS` | `http://localhost:5173,https://murmur-web-tawny.vercel.app` |
| seed accounts | `OWNER_EMAIL/PASSWORD`, etc. |

6. **Apply** — the environment redeploys with the new variables.

### 3. Updates

**Upload and deploy** a new zip (e.g. `version-1.3`). Environment variables are kept.

### 4. Frontend (Vercel)

The Vercel app proxies `/api/*` to this backend (EB is HTTP-only). Set `VITE_API_URL=/api` on the frontend — see [murmur-web README](https://github.com/valtykhoniuk/murmur-web).

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| 502 Bad Gateway | Missing env vars — add `DATABASE_URL`, `SECRET_KEY`, apply config |
| Zip extract failed | Zip must contain `Procfile` at root, not inside a `murmur/` folder |
| CORS 400 | Add Vercel URL to `CORS_ORIGINS` |
| Delete character 500 | Deploy latest code (summaries deleted before messages) |
| Login 422 | Email must be valid (`user@domain.tld`) |

## Project structure

```
app/
  auth/          JWT login, demo, /me
  characters/    Character CRUD
  chats/         Chats, messages, demo limit, cleanup
  llm/           LangGraph, LLM-as-judge verifier, prompts, memory
  models/        SQLModel tables
  seed.py        User seeding on startup
Procfile         EB process (gunicorn + uvicorn worker)
application.py   EB entrypoint
.ebextensions/  EB config (health check path)
```

## License

Personal portfolio project.
