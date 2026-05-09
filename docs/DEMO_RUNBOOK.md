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

## 3. Start The API

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

## 4. Run API Smoke

In a second PowerShell window:

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_user
```

Expected result: health is `ok`, a session id and task id are printed, the answer is correct, and `total_answers` increases.

## 5. Manual API Flow

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

## 6. Check Audio Quality

Generated task audio is written under `assets/` and served as `/static/<filename>`.

For each profile, create a session with `noise_profile` set to one of:

- `none`
- `white`
- `cafe`
- `street`
- `speech_babble`

Then call `/api/v1/tasks/next` and listen to the returned `audio_url`. Automated tests verify deterministic output, non-silence, and peak limiting, but the naturalness of the noise still needs a human listening pass.

## 7. What Not To Commit

Do not commit `.env`, real secrets, real user data, `__pycache__`, `.pyc`, virtual environments, or temporary generated audio under `assets/`.
