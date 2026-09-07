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

## Environment

Create a `.env` file at the repository root:

```bash
cp .env.example .env
```

Then set:

```env
OPENAI_API_KEY='your_openai_api_key_here'
```

The frontend proxies requests to the backend through `app/api/agent/execute`. By default it expects the backend at:

```text
http://localhost:8000
```

To override it, create `lateralus-frontend/.env.local`:

```env
BACKEND_API_BASE_URL=http://localhost:8000
```

## Run Locally

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

## Useful Commands

Backend tests:

```bash
cd lateralus-backend
uv run pytest app/tests
```

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

