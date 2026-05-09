# Functional Test Plan

## Automated Pytest Coverage

- `tests/test_api_contract.py`: health, OpenAPI core paths, session creation, next task, answer submission, progress update, persistence rows, and invalid `noise_profile` validation.
- `tests/test_database_schema.py`: combined pipeline and user-data SQLite schema.
- `tests/test_pipeline_smoke.py`: `--help` parsing and heuristic pipeline execution against temporary input, output, and database files.
- `tests/test_audio_noise_profiles.py`: supported profiles, fixed-seed reproducibility, non-silence, peak limiting, and invalid profile errors.

## Required Release Checks

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

## Manual Smoke Checks

Start the API:

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Run:

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId smoke_user
```

## Residual Manual Review

- Listen to generated audio for each noise profile and judge whether the noise is acceptable for demo use.
- Confirm mini program developers can consume `/openapi.json` and the examples in `docs/API_CONTRACT.md`.
