# T10_full_demo_acceptance Result

## Status

Done, with environment-limited TTS/API-smoke result.

## Summary

- Re-read required project, frontend, API, runbook, shared-state, T07, T08, T09, and T10 context.
- Marked T10 as `in_progress` before validation.
- Ran the required automated acceptance commands.
- Started uvicorn and validated HTTP routes for `/`, `/docs`, and `/openapi.json`.
- Verified session creation succeeds through `/api/v1/sessions`.
- Verified `GET /api/v1/tasks/next` reaches the known online TTS failure path in this environment and returns 500.
- Confirmed frontend source preserves the session and exposes task/audio error messaging plus API debug visibility for the TTS failure path.
- Checked README, README-zh, DEMO_RUNBOOK, and FRONTEND_INTEGRATION. README.md, DEMO_RUNBOOK, and FRONTEND_INTEGRATION already describe the complete local demo and TTS limitation. README-zh remains historically mojibake but contains the same major route/run commands, so no large rewrite was made in T10 scope.
- Cleaned temporary validation artifacts.

## Verification Commands And Results

- `python -m compileall -q data_pipeline server tests` passed.
- `pytest -q` passed: 14 passed. PowerShell/xonsh history warnings appeared after test success and did not affect results.
- `python -c "import server.main; print('server import ok')"` passed and printed `server import ok`.
- `python -m data_pipeline.run_pipeline --help` passed and printed CLI help.

## Server And Static Route Validation

Using uvicorn on `http://127.0.0.1:8000`:

- `GET /health` returned 200.
- `GET /` returned 200.
- `GET /docs` returned 200.
- `GET /openapi.json` returned 200.
- `POST /api/v1/sessions` returned 200 and created a demo session.
- `GET /api/v1/tasks/next?session_id=...` returned 500 in this environment.

Notes:

- `Start-Process` still fails in this Windows shell because duplicated `Path`/`PATH` environment keys trigger a .NET dictionary error. A foreground Python subprocess was used for route/API validation and then terminated cleanly.
- The browser automation attempt timed out while the foreground server window was open. HTTP route validation and frontend source inspection were used as fallback evidence.

## Frontend Demo Acceptance

- Page load route: passed by HTTP 200 for `/`.
- Session creation: passed by direct API validation.
- Task/audio flow: blocked by online TTS/network failure at `/api/v1/tasks/next`.
- Error behavior: accepted for the environment-limited path. `web/app.js` keeps the session, clears the failed task, marks task/audio error state, shows the message: `Audio could not be generated. This often means edge-tts or network access failed; keep the session and retry when TTS is available.`, and records the failed `/api/v1/tasks/next` request/response in the API debug area.
- Answer/progress full flow: not run end-to-end with real audio because no task was returned. Existing pytest coverage still verifies the answer/progress path with mocked TTS and temporary SQLite data.

## API Smoke Result

Command attempted with a live uvicorn process:

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_user
```

Observed result:

- `GET /health` passed.
- `POST /api/v1/sessions` passed.
- `GET /api/v1/tasks/next` returned 500 and the smoke command timed out while reading the failed response.

Conclusion: API smoke did not complete because online `edge-tts` task generation failed in this environment. This matches the known restriction around access to `speech.platform.bing.com:443`; no API contract or schema changes were made.

## Submit / No-submit File List

Submit:

- `.codex/shared_state.json`
- `.codex/logs/T10_result.md`

Do not submit:

- `.env`
- `capd_database.db` local demo DB changes from validation
- `__pycache__/`
- `.pytest_cache/`
- generated audio under `assets/*.wav` or `assets/*.mp3`
- temporary T10 files such as `t10_server.pid` or `t10_uvicorn_*.tmp.log`
- real user data
- raw corpus data under `data_pipeline/raw_data/`

Existing non-T10 local modifications:

- `.gitignore` was already modified before T10 and was not edited for this task.
- `capd_database.db` was touched by live session/API validation; T10 demo rows were removed afterward, but the SQLite file remains modified at the file level and should not be submitted as a T10 deliverable.

## Cleanup

- Removed `.pytest_cache/`.
- Removed `data_pipeline/__pycache__/`, `server/__pycache__/`, and `tests/__pycache__/`.
- Removed temporary `t10_server.pid`, `t10_uvicorn_stdout.tmp.log`, and `t10_uvicorn_stderr.tmp.log`.
- No generated `.wav` or `.mp3` files were found under `assets/`.
- Removed T10 demo users/sessions created in `capd_database.db`.

## Remaining Risks

- Real demo task/audio generation still requires network access to online Edge TTS.
- Human listening review is still needed for generated audio quality when TTS is available.
- Browser plugin verification was unstable in this environment; route/API checks and source inspection covered the same acceptance path.
- README-zh appears mojibake from earlier encoding issues; T10 did not rewrite it to avoid broad documentation churn outside acceptance scope.
