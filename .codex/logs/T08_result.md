# T08_frontend_api_flow_demo Result

## Status

Done.

## Summary

- Wired the existing static frontend shell to the `/api/v1` API flow.
- Added session creation through `POST /api/v1/sessions`.
- Added next-task loading through `GET /api/v1/tasks/next?session_id=...`.
- Added browser audio playback using the returned `audio_url`.
- Added answer submission through `POST /api/v1/answers`.
- Added progress refresh through `GET /api/v1/users/{user_id}/progress`.
- Added friendly task/audio error messaging for TTS or network failure.
- Added `docs/FRONTEND_INTEGRATION.md` for frontend and mini program integration.
- Kept the existing API contract and database schema unchanged.

## Files Changed

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `docs/FRONTEND_INTEGRATION.md`
- `tests/test_api_contract.py`
- `.codex/shared_state.json`
- `.codex/logs/T08_result.md`

## Verification

- `python -m compileall -q data_pipeline server tests` passed.
- `pytest -q` passed: 14 passed.
- `python -c "import server.main; print('server import ok')"` passed.

## Notes And Risks

- `/api/v1/tasks/next` still depends on `edge-tts`; if network/TTS fails, the frontend now keeps the session visible and shows a retry-friendly error.
- `target_text` is displayed for MVP demo convenience only. `docs/FRONTEND_INTEGRATION.md` states that formal training clients should not reveal it before the user answers.
- PowerShell profile and xonsh history warnings appeared in command output but did not block validation.
- T08 is complete and work is paused before T09.
