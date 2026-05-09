# T03 Data Pipeline Result

Completed at: 2026-05-09T16:17:47+08:00
Owner: codex-T03-pipeline

## Summary

Implemented a resumable offline corpus pipeline without modifying the API layer.

Changes:

- Replaced `data_pipeline/run_pipeline.py` with an argparse CLI supporting `--input`, `--output`, `--db-path`, `--limit`, `--batch-size`, `--resume`, `--scorer`, `--no-augment`, `--augment-count`, and `--anomaly-threshold`.
- Added `data_pipeline/__init__.py` so the pipeline can run as `python -m data_pipeline.run_pipeline`.
- Extended `data_pipeline/database_manager.py` to migrate `sentences` with `source` and `created_at`, and to create `pipeline_runs` and `pipeline_errors`.
- Kept the real BERT/LTP path available as `--scorer bert`, while adding `--scorer heuristic` for fast local smoke tests that do not download models.
- Delayed `OPENAI_API_KEY` validation in `llm_augment.py` until GPT augmentation is actually used, so `--no-augment` smoke tests work without secrets.
- Added `docs/PIPELINE_RUNBOOK.md` with smoke, production, resume, schema, and GPU decision guidance.

## Validation

Passed:

- `Get-ChildItem -Path data_pipeline,server -Filter *.py | ForEach-Object { python -m py_compile $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }`
- `python -m data_pipeline.run_pipeline --help`
- `python -c "import data_pipeline.llm_augment; print('llm import ok')"`
- `python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt`
- `python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --scorer heuristic --no-augment --output processed_corpus.txt`
- SQLite inspection of `pipeline_runs`, `pipeline_errors`, and migrated `sentences` columns.

Observed smoke results:

- Resume run skipped 20 existing corpus rows with 0 failures.
- Non-resume run processed 20 cleaned rows, skipped 20 duplicate inserts via the unique `sentences.text` constraint, and recorded a completed `pipeline_runs` row.

Failed environment checks:

- Temporary DB under `.codex\tmp` failed because Python could not create `.codex\tmp`.
- Temporary DB under `.codex\logs` failed because Python could not open a new DB file there.
- These failures appear to be local filesystem permission limits on Python writes under `.codex`; the main project DB and `processed_corpus.txt` path worked.

## GPU Estimate

Do not rent GPU yet. The pipeline now has the controls needed for the required CPU probes:

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer bert --no-augment
python -m data_pipeline.run_pipeline --limit 100 --batch-size 8 --resume --scorer bert --no-augment
python -m data_pipeline.run_pipeline --limit 500 --batch-size 8 --resume --scorer bert --no-augment
```

GPU should only be considered after those BERT/LTP CPU timing results show throughput is too low for the target corpus size. GPT augmentation is network-bound and will not benefit from GPU.

## Remaining Risks

- Full BERT/LTP scoring was not run in this turn to avoid model download/runtime surprises during the small smoke path.
- GPT augmentation was not called because no `OPENAI_API_KEY` should be stored in the repo; the code path now fails clearly when augmentation is requested without credentials.
- Existing corpus/database content appears encoded inconsistently in shell output, but pipeline behavior and schema updates are verified.
