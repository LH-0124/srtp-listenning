# STATE_MACHINE.md - SRTP-CAPD Project State Machine

This document describes the working state model used by Codex tasks in this repository.

## 1. State Flow

```text
S0_DISCOVERED
  -> S1_REPO_STABILIZED
  -> S2_API_CONTRACT_READY
  -> S3_USER_DATA_READY
  -> S4_PIPELINE_SMOKE_READY
  -> S5_AUDIO_NOISE_READY
  -> S6_TESTS_READY
  -> S7_MINIPROGRAM_BACKEND_READY
  -> S8_DEMO_READY
```

Current practical state after T10: `S8_DEMO_READY`.

`.codex/shared_state.json` may still contain historical task metadata and older state labels, but the latest task log is `.codex/logs/T10_result.md`.

## 2. State Definitions

### S0_DISCOVERED

Initial repository audit is complete.

Expected evidence:

- repository structure reviewed;
- major risks listed;
- `docs/AUDIT_REPORT.md` created.

Related task: `T00_repo_audit`.

### S1_REPO_STABILIZED

Basic repository safety and importability are in place.

Expected evidence:

- Python files compile;
- hardcoded secrets removed;
- `.env.example` exists;
- generated assets are ignored.

Related task: `T01_repo_stabilize`.

### S2_API_CONTRACT_READY

Stable mini program API contract exists.

Expected evidence:

- `GET /health`;
- `POST /api/v1/sessions`;
- `GET /api/v1/tasks/next`;
- `POST /api/v1/answers`;
- `GET /api/v1/users/{user_id}/progress`;
- `GET /openapi.json`;
- `docs/API_CONTRACT.md` updated.

Related task: `T02_api_contract`.

### S3_USER_DATA_READY

Persistent user/session/task/answer/progress storage exists.

Expected evidence:

- SQLite tables for users, sessions, tasks, answers, and progress;
- idempotent schema initialization;
- answer submission updates progress.

Related task: `T05_user_data`.

### S4_PIPELINE_SMOKE_READY

Offline corpus processing has a resumable smoke path.

Expected evidence:

- heuristic pipeline smoke works;
- batch/resume options exist;
- pipeline status and error records are stored;
- large BERT/LTP/GPT runs remain gated by small-sample validation.

Related task: `T03_data_pipeline`.

### S5_AUDIO_NOISE_READY

Audio generation supports difficulty and noise profile controls.

Expected evidence:

- online TTS integration;
- supported noise profiles;
- speed/SNR controls;
- fade, normalization, and peak limiting;
- deterministic synthetic noise where applicable.

Related task: `T04_audio_noise`.

### S6_TESTS_READY

Automated validation and release documentation exist.

Expected evidence:

- `python -m compileall -q data_pipeline server tests` passes;
- `pytest -q` passes;
- pipeline help or smoke path works;
- API smoke scripts exist;
- demo runbook exists.

Related task: `T06_tests_docs_release`.

### S7_MINIPROGRAM_BACKEND_READY

Backend behavior is ready for mini program integration planning.

Expected evidence:

- stable `/api/v1` contract;
- OpenAPI export;
- CORS and static audio URL behavior documented;
- persistence behavior documented.

Related tasks: `T02`, `T05`, `T06`.

### S8_DEMO_READY

Local end-to-end demo surface is available.

Expected evidence:

- `GET /` serves the frontend demo;
- frontend can create sessions;
- frontend can request tasks and play audio when TTS/network is available;
- frontend can submit answers and refresh progress when a task is available;
- frontend preserves the session and shows clear task/audio errors when online TTS is blocked;
- `/docs` and `/openapi.json` are available;
- T10 acceptance log exists.

Related tasks: `T07`, `T08`, `T09`, `T10`.

## 3. Task To State Mapping

| Task | State contribution |
| --- | --- |
| `T00_repo_audit` | `S0_DISCOVERED` |
| `T01_repo_stabilize` | `S1_REPO_STABILIZED` |
| `T02_api_contract` | `S2_API_CONTRACT_READY`, part of `S7_MINIPROGRAM_BACKEND_READY` |
| `T05_user_data` | `S3_USER_DATA_READY`, part of `S7_MINIPROGRAM_BACKEND_READY` |
| `T03_data_pipeline` | `S4_PIPELINE_SMOKE_READY` |
| `T04_audio_noise` | `S5_AUDIO_NOISE_READY` |
| `T06_tests_docs_release` | `S6_TESTS_READY`, part of `S7_MINIPROGRAM_BACKEND_READY` |
| `T07_static_frontend_shell` | part of `S8_DEMO_READY` |
| `T08_frontend_api_flow_demo` | part of `S8_DEMO_READY` |
| `T09_frontend_polish_and_accessibility` | part of `S8_DEMO_READY` |
| `T10_full_demo_acceptance` | final local demo acceptance for `S8_DEMO_READY` |

## 4. State Update Format

When a task changes the project state, update `.codex/shared_state.json` with fields like:

```json
{
  "current_state": "S8_DEMO_READY",
  "last_updated_by": "codex-T10-full-demo-acceptance",
  "last_updated_at": "2026-05-10T16:50:24+08:00",
  "state_notes": "T10 completed: automated tests and static/demo routes passed; real task/audio/API smoke is limited by online edge-tts network failure in this environment."
}
```

Also write a task result file under `.codex/logs/`.
