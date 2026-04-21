# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A cross-platform Electron desktop app for Japanese learning. Global hotkey (Cmd+Shift+X on Mac, Ctrl+Alt+D on Windows/Linux) triggers screen region capture, which is sent to a local FastAPI backend that calls OpenAI Vision API to extract Japanese text, translate it to Chinese, and provide grammar analysis.

## Setup

```bash
# Python backend
uv venv && source .venv/bin/activate
uv pip install -e .
cp .env.example .env  # then add OPENAI_API_KEY

# Node frontend
cd frontend && npm install
```

## Running

```bash
./start.sh          # full app (starts Electron, which spawns the Python backend)
python -m backend.main  # backend only (for API testing)
```

## Testing

```bash
python test_backend.py  # tests backend endpoints directly
MOCK_MODE=true python -m backend.main  # run without an API key
```

## Linting

```bash
ruff check backend/   # lint
ruff format backend/  # format
```

## Architecture

**Dual-process model:** Electron (`frontend/main.js`) spawns the Python FastAPI server as a child process on startup, polls `GET /health` until ready, then registers the global hotkey.

**Capture flow:**
1. Hotkey → full-screen transparent `capture.html` window
2. User drags to select region → `capture.js` crops canvas to Base64 PNG
3. Electron opens `result.html` window and sends image via IPC
4. `result.js` POSTs to `POST /api/analyze` on the local FastAPI server
5. Backend (`ai_service.py`) calls OpenAI Vision API and returns structured JSON

**IPC security:** `nodeIntegration: false` + `contextIsolation: true`; renderer communicates through the context bridge defined in `preload.js`.

**Backend models** (`backend/models.py`): `AnalyzeRequest` (image_base64, context) → `AnalyzeResponse` (status, data, error). `AnalyzeData` contains original_text, translation, furigana, grammar_analysis, example_sentence.

## Key Configuration

`.env` variables:
- `OPENAI_API_KEY` — required (unless `MOCK_MODE=true`)
- `OPENAI_BASE_URL` — defaults to `https://api.openai.com/v1`
- `OPENAI_MODEL` — defaults to `gpt-4o`
- `HOST` / `PORT` — defaults to `127.0.0.1:8000`
- `MOCK_MODE=true` — returns simulated responses without calling the API
