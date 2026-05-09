# T04 Audio Noise Result

Completed at: 2026-05-09T17:40:00+08:00
Owner: codex-T04-audio

## Summary

Implemented configurable audio noise profiles while preserving the T02/T05 API contract and response field names.

Changes:

- Added `server/noise_profiles.py` with deterministic synthetic profile generation, SNR mixing, fade in/out, RMS normalization, and peak limiting.
- Reworked `server/audio_service.py` so task audio generation accepts `noise_profile` and optional explicit `seed`.
- Updated `server/main.py` minimally so `/api/v1/tasks/next` passes the persisted session `noise_profile` into the audio layer.
- Updated `docs/API_CONTRACT.md` and `docs/openapi-draft.yaml` with behavior notes only; no new `/api/v1` endpoints and no response field renames.

Supported profiles:

- `none`: normalized clean speech, no synthetic background noise.
- `white`: seeded white noise mixed to requested SNR.
- `cafe`: seeded smoothed crowd/chatter-like noise with sparse transient events.
- `street`: seeded low-frequency rumble/wind with sparse pass-by events.
- `speech_babble`: seeded multi-voice murmur-like synthetic babble.

## Audio Processing

- Noise seed is explicit when provided, otherwise derived from `text`, `speed`, `snr`, and `noise_profile`.
- Clean speech is RMS-normalized before mixing.
- Non-`none` profiles are normalized, faded in/out, and scaled to the requested SNR.
- Final output is RMS-normalized again, peak-limited to avoid clipping, and faded at the boundaries.
- Temporary TTS files are cleaned up in a `finally` block.

## Validation

Passed:

- `python -m compileall -q data_pipeline server`
- `python -c "import server.main; print('server import ok')"`
- `python -c "from server.noise_profiles import SUPPORTED_NOISE_PROFILES; print(SUPPORTED_NOISE_PROFILES)"`
- `python -c` smoke test using `mix_with_snr` to generate `assets/t04_smoke_cafe.wav`.
  - profile: `cafe`
  - output file: `assets\t04_smoke_cafe.wav`
  - exists: `True`
  - RMS: `0.119371`
  - peak: `0.323512`
  - silent: `False`
  - clipped: `False`
- `AudioService.generate_task_audio` smoke with local monkeypatched TTS/librosa input.
  - profile: `street`
  - output file: `D:\Program Files\Project\CAPD_Server_Backend\assets\task_1a162c5c-c06d-44eb-9101-6895efde9103.wav`
  - sample rate: `16000`
  - RMS: `0.119272`
  - peak: `0.260223`
  - silent: `False`
  - clipped: `False`

## Remaining Risks For T06

- Add automated pytest coverage for each noise profile, invalid profile handling, reproducibility with fixed seed, and no clipping/no silence thresholds.
- Add API smoke coverage confirming `noise_profile` from `POST /api/v1/sessions` appears in task difficulty and is passed into audio generation.
- Real online `edge_tts` output should be checked in an environment with network access; T04 smoke used local deterministic audio input to avoid depending on external TTS availability.
- Subjective listening quality is still unvalidated; T06/demo should include a quick human listening pass.
