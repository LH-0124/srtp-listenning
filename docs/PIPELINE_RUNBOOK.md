# Pipeline Runbook

This document covers the offline corpus pipeline owned by `T03_data_pipeline`.
It does not require or modify the API layer.

## Commands

Fast local smoke test without model downloads or GPT calls:

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt
```

Production scoring path with BERT/LTP and no GPT augmentation:

```powershell
python -m data_pipeline.run_pipeline --input data_pipeline/raw_data/corpus.txt --limit 100 --batch-size 8 --resume --scorer bert --no-augment --output processed_corpus.txt
```

Production scoring plus GPT augmentation for LOW-context sentences:

```powershell
python -m data_pipeline.run_pipeline --input data_pipeline/raw_data/corpus.txt --limit 100 --batch-size 8 --resume --scorer bert --augment-count 3 --output processed_corpus.txt
```

GPT augmentation requires `OPENAI_API_KEY` in the environment or `.env`.

## Resume Behavior

`--resume` skips any cleaned sentence that already exists in the `sentences`
table. The database has a unique constraint on `sentences.text`, so repeated
runs are idempotent even without `--resume`; with `--resume`, expensive scoring
is skipped for existing rows.

## Database Tables

`sentences` now stores:

- `id`
- `text`
- `context_type`
- `score`
- `source`
- `created_at`

`pipeline_runs` stores one row per run with input path, output path, limit,
batch size, resume flag, scorer, augmentation flag, counters, timestamps, status,
and error message.

`pipeline_errors` stores per-sentence failures with `run_id`, raw text, error
message, and timestamp.

## GPU Decision

Do not rent GPU before these local CPU probes are run and logged:

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer bert --no-augment
python -m data_pipeline.run_pipeline --limit 100 --batch-size 8 --resume --scorer bert --no-augment
python -m data_pipeline.run_pipeline --limit 500 --batch-size 8 --resume --scorer bert --no-augment
```

GPU is worth considering only if BERT/LTP scoring throughput is too low for the
target corpus size after the 20/100/500 CPU timing curve is measured. GPT calls
are network-bound and will not benefit from GPU.
