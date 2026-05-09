# Project Log

## 2026-05-09

- Backend MVP reached the tested API/demo stage.
- `/api/v1` includes session creation, next task, answer submission, and user progress endpoints.
- SQLite persistence covers users, training sessions, training tasks, answers, and progress.
- Offline pipeline smoke path and runbook are available.
- Audio service supports multiple noise profiles, fade, RMS normalization, and peak limiting.
- Local static frontend demo is available at `http://127.0.0.1:8000/`.
- Frontend demo supports session/task/audio/answer/progress flow, API debug output, day/night theme, responsive layout, and clear error states.

## Current Notes

- Online TTS can fail in restricted network environments. This is expected during local sandbox validation; the frontend should display a task/audio error and keep the session active.
- Before final delivery, run T10 full demo acceptance and document any files that should not be submitted.
