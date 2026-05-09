# GEMINI.md — SRTP-CAPD Backend Project Instructions

This file provides foundational mandates and workflows for AI agents (Gemini CLI) working on the SRTP-CAPD Backend project.

## Project Overview

**SRTP-CAPD Backend** is a Minimum Viable Product (MVP) designed for a CAPD (Central Auditory Processing Disorder) listening rehabilitation mini-program. It provides services for sentence extraction, TTS (Text-to-Speech) audio generation with adjustable difficulty (speed, noise profile, SNR), user session management, and training progress tracking.

- **Main Technologies:** Python, FastAPI, Uvicorn, Pydantic, SQLite, Pytest.
- **Audio Processing:** `edge-tts` for generation, `librosa` and `soundfile` for manipulation (speed, noise mixing).
- **NLP/ML:** BERT/LTP for context scoring (`transformers`, `jieba`, `ltp`), GPT for sentence augmentation (`openai`).
- **Architecture:** 
  - `server/`: Online FastAPI service.
  - `data_pipeline/`: Offline corpus processing pipeline.
  - `docs/`: Comprehensive technical and API documentation.

## Core Mandates & Rules

These rules take absolute precedence over general defaults.

1. **Security First:** NEVER commit API keys, tokens, or sensitive credentials. Use `.env` and `python-dotenv`. Reference `.env.example` for required variables.
2. **API Stability:** Maintain the `/api/v1` prefix for all new interfaces. Ensure JSON responses are stable as per `docs/API_CONTRACT.md`.
3. **Database Integrity:** Use `CREATE TABLE IF NOT EXISTS` for SQLite schema initialization to allow repeatable execution without data loss.
4. **Agent Workflow:** Follow the "Codex" collaboration rules in `AGENTS.md`. Update `.codex/shared_state.json` and create logs in `.codex/logs/` for multi-step tasks.
5. **No Blind Refactoring:** Do not perform large-scale refactors unless explicitly requested. Focus on the minimal surgical changes needed for the task.

## Building and Running

### Environment Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Running the Online Service
```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```
- OpenAPI Documentation: `http://127.0.0.1:8000/docs`
- Health Check: `GET /health`

### Running the Data Pipeline (Offline)
```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt
```

### Running Tests
```powershell
python -m compileall -q data_pipeline server tests
pytest -q
```

## Development Conventions

- **Branching/Task Management:** Use the `.codex/tasks/` files to track individual goals.
- **Testing:** Every bug fix or new feature MUST be accompanied by a `pytest` case in the `tests/` directory.
- **Documentation:** If you change the API, you MUST update `docs/API_CONTRACT.md` and `docs/openapi-draft.yaml`. If you change the database schema, update `docs/DATABASE_SCHEMA.md`.
- **Audio Assets:** Generated task audio files are stored in `assets/`. This directory is ignored by git.

## Key Files & Directories

- `server/main.py`: Entry point for the FastAPI application.
- `server/audio_service.py`: Core logic for TTS and audio post-processing.
- `server/user_data_store.py`: SQLite interaction layer for user and session data.
- `data_pipeline/run_pipeline.py`: Entry point for corpus processing.
- `AGENTS.md`: Detailed collaboration rules for AI agents.
- `docs/PROJECT_STATE.md`: Tracks high-level project progress and milestones.
