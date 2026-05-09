# Demo Runbook

This runbook is for a local MVP demo on Windows PowerShell.

## 1. Install And Verify

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

## 2. Prepare Corpus Data

If `capd_database.db` has no training sentences, run the fast heuristic pipeline:

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt
```

Use `--scorer bert` only after the local smoke path is stable.

## 3. Start The API And Frontend

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

## 4. Run The Frontend Demo

Open `http://127.0.0.1:8000/`.

Recommended demo flow:

1. Create a session with a demo user id.
2. Click **Next task**.
3. If audio generation succeeds, play the returned audio.
4. Type an answer and submit it.
5. Check the progress panel and API debug area.

If `edge-tts` cannot reach the online TTS service, the task request may fail. The expected frontend behavior is:

- the session remains visible and active;
- the task/audio panel shows an error state;
- the API panel shows the failed request/response;
- the user can retry once TTS/network access is available.

Formal training clients should not reveal `target_text` before the user answers. The local demo shows it only for MVP debugging.

## 5. Run API Smoke

In a second PowerShell window:

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_user
```

Expected result when online TTS is available: health is `ok`, a session id and task id are printed, the answer is correct, and `total_answers` increases.

If online TTS is blocked, this smoke may fail at `/api/v1/tasks/next`; that is an environment limitation, not a frontend contract change.

## 6. Manual API Flow

Create a session:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/sessions -ContentType "application/json" -Body '{"user_id":"demo_user","training_mode":"LOW","noise_profile":"cafe"}'
```

Get the next task using the returned `session_id`:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/tasks/next?session_id=<SESSION_ID>"
```

Submit an answer:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/answers -ContentType "application/json" -Body '{"session_id":"<SESSION_ID>","task_id":"<TASK_ID>","user_input":"<TARGET_TEXT>"}'
```

Check progress:

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/api/v1/users/demo_user/progress
```

## 7. Check Audio Quality

Generated task audio is written under `assets/` and served as `/static/<filename>`.

For each profile, create a session with `noise_profile` set to one of:

- `none`
- `white`
- `cafe`
- `street`
- `speech_babble`

Then call `/api/v1/tasks/next` and listen to the returned `audio_url`. Automated tests verify deterministic output, non-silence, and peak limiting, but the naturalness of the noise still needs a human listening pass.

## 8. What Not To Commit

Do not commit `.env`, real secrets, real user data, `__pycache__`, `.pyc`, virtual environments, or temporary generated audio under `assets/`.
