# Lateralus AI Platform

Lateralus AI Platform is a full-stack weather-agent demo. The backend exposes a FastAPI endpoint that streams LangGraph/LangChain agent events over Server-Sent Events, and the frontend renders those events as a chat interface with visible tool-call states.

## Stack

- **Backend:** FastAPI, LangGraph, LangChain, OpenAI, Pydantic, uv
- **Frontend:** Next.js App Router, React, TypeScript, Tailwind CSS
- **Streaming:** Server-Sent Events from backend to frontend

## Project Structure

```text
lateralus-ai-platform/
├── lateralus-backend/
│   ├── app/
│   │   ├── ai/                 # Agent, graph, model, SSE formatting, tools
│   │   ├── api/                # FastAPI routers and schemas
│   │   └── tests/              # Pytest tests
│   └── pyproject.toml
├── lateralus-frontend/
│   ├── app/                    # Next.js app routes and proxy route
│   └── features/chat/          # Chat UI, stream parser, reducer, renderers
└── .env.example
```

## Prerequisites

- Python `>=3.14`
- `uv`
- Node.js/npm
- OpenAI API key
- Docker Compose (for Redis and PostgreSQL)

## Environment

Create a `.env` file at the repository root:

```bash
cp .env.example .env
```

Then set your OpenAI key and adjust the local service URLs if needed:

```env
OPENAI_API_KEY='your_openai_api_key_here'
```

The root `.env` is ignored by Git. The example sets `REDIS_TTL_MINUTES=10` and
`CONTEXT_WINDOW_SIZE=10`. The latter is a deliberately low token trigger for
demonstrating summarization; increase it for normal use. The token count is an
approximation of unsummarized messages, not a hard model input limit.

The frontend proxies requests to the backend through `app/api/agent/execute`. By default it expects the backend at:

```text
http://localhost:8000
```

To override it, create `lateralus-frontend/.env.local`:

```env
BACKEND_API_BASE_URL=http://localhost:8000
```

## Run Locally

Start Redis and PostgreSQL from the repository root:

```bash
docker compose up -d
```

Apply the summary schema once, in order:

```bash
docker compose exec -T postgres-database psql -U root -d lateralus_db -f /dev/stdin < lateralus-backend/scripts/sql/001_memory_summaries.sql
docker compose exec -T postgres-database psql -U root -d lateralus_db -f /dev/stdin < lateralus-backend/scripts/sql/002_memory_summaries_coverage_unique.sql
```

In PowerShell, run the same scripts with:

```powershell
Get-Content -Raw lateralus-backend/scripts/sql/001_memory_summaries.sql | docker compose exec -T postgres-database psql -U root -d lateralus_db
Get-Content -Raw lateralus-backend/scripts/sql/002_memory_summaries_coverage_unique.sql | docker compose exec -T postgres-database psql -U root -d lateralus_db
```

Start the backend:

```bash
cd lateralus-backend
uv sync --dev
uv run uvicorn app.main:app --reload --port 8000
```

In another terminal, start the frontend:

```bash
cd lateralus-frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## How It Works

1. The user sends a weather question in the frontend.
2. The frontend posts to its local Next.js proxy route.
3. The proxy forwards the request to `POST /agent/execute` on the FastAPI backend.
4. The backend runs the LangGraph agent and streams chat/tool events as SSE frames.
5. The frontend parses the stream and renders:
   - user message
   - thinking/loading state
   - weather tool call
   - tool progress/completion
   - weather card
   - filtered JSON output
   - streamed assistant response

### Conversation memory

The frontend lists conversations in a sidebar and keeps each conversation's
messages and `thread_id` in browser memory while the page is open. Selecting a
conversation resumes that thread. This first version does not persist the list
across page reloads; the conversation records are kept together in the chat
state so a future API can load and save them.

The frontend sends the same `thread_id` for each turn of a chat. LangGraph
checkpoints recent messages in Redis with a configurable TTL (10 minutes by
default). After a completed turn exceeds `CONTEXT_WINDOW_SIZE`, the graph
summarizes completed messages and saves a revision in PostgreSQL. Only after
that save succeeds does it remove the covered messages from the checkpoint.
The next turn loads the active summary into the model's system prompt and keeps
any newer messages verbatim. A single long first turn is summarized in full;
with multiple turns, the newest turn remains available verbatim. If a save
commits before checkpoint pruning, the next turn finishes the removal before
calling the model.

To verify the flow, keep `CONTEXT_WINDOW_SIZE=10`, send a long message, then
send a follow-up in the same chat. The `memory_summary` model call should
appear after the first answer; the following model call should include the
saved summary in its system prompt. To inspect these prompts in LangSmith,
set `LANGSMITH_TRACING=true` and a real `LANGSMITH_API_KEY` in the root `.env`,
then open the project named by `LANGSMITH_PROJECT` (default:
`lateralus-memory`).

## Useful Commands

Backend tests:

```bash
cd lateralus-backend
uv run pytest app/tests
```

The memory integration test uses separate Redis and PostgreSQL containers, not
the application's databases. Start them with:

```bash
docker compose --profile test up -d --wait redis-test-database postgres-test-database
```

Then opt in to the integration test:

```bash
cd lateralus-backend
RUN_MEMORY_INTEGRATION=1 uv run pytest app/tests
```

In PowerShell, set `$env:RUN_MEMORY_INTEGRATION='1'` before running
`uv run pytest app/tests`. The test applies the summary SQL migrations to
`lateralus_test_db` automatically. It uses `localhost:55432` for PostgreSQL
and `localhost:56379` for Redis; `TEST_POSTGRES_URL` and `TEST_REDIS_URL` can
override those endpoints, but the test rejects the application's database
URLs. On Windows, psycopg needs a selector event loop; the integration test
selects one explicitly. The `uvicorn --reload` command above also uses a
selector loop on Windows.

Backend smoke stream:

```bash
cd lateralus-backend
uv run python scripts/smoke_agent.py
```

Frontend build:

```bash
cd lateralus-frontend
npm run build
```

Frontend lint:

```bash
cd lateralus-frontend
npm run lint
```

## API

### Health

```http
GET /health
```

Returns:

```json
{
  "status": "UP"
}
```

### Execute Agent

```http
POST /agent/execute
Content-Type: application/json
Accept: text/event-stream
```

Body:

```json
{
  "message": "Como está o tempo em São Paulo?"
}
```

Returns an SSE stream containing LangGraph chat model and tool events.

