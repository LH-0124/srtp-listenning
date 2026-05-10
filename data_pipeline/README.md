# Data Pipeline README

This folder contains the offline corpus pipeline for preparing training sentences before the FastAPI backend serves them.

## 1. What The Pipeline Does

The pipeline reads a raw text corpus, cleans each line, scores the sentence context, optionally expands low-context sentences with GPT, and writes results into a SQLite database.

Main flow:

1. `run_pipeline.py` parses CLI arguments and coordinates the run.
2. `preprocess.py` cleans raw text lines and filters unusable short lines.
3. `context_scoring.py` scores each cleaned sentence with BERT plus LTP segmentation when `--scorer bert` is used.
4. `run_pipeline.py` classifies each sentence as `HIGH` or `LOW` by `--high-threshold`.
5. `llm_augment.py` optionally calls a GPT-compatible API to generate variants for `LOW` sentences.
6. `database_manager.py` creates/resumes SQLite tables and inserts accepted sentences.
7. A TSV output file is also written for inspection.

The default pipeline database is now:

```text
new_capd_datebase.db
```

This intentionally avoids overwriting the existing local demo database `capd_database.db`.

## 2. Important Files

- `run_pipeline.py`: command-line entry point.
- `preprocess.py`: text cleanup.
- `context_scoring.py`: BERT/LTP scorer and anomaly detection.
- `llm_augment.py`: GPT-based sentence expansion.
- `database_manager.py`: SQLite tables, run records, error logs, sentence inserts.
- `raw_data/`: local raw corpus files.
- `source_backups/`: backups of source files before the GPU/500MiB changes.

## 3. Database Tables

The pipeline creates these tables in the selected SQLite database:

- `sentences`: cleaned sentence text, context type, score, source, creation time.
- `pipeline_runs`: one row per pipeline run with parameters, counters, status, and timing.
- `pipeline_errors`: per-line failures with the raw text and error message.

Use `--resume` to skip cleaned sentences already present in `sentences`.

## 4. Parameters

Common parameters:

- `--input PATH`: raw corpus input file.
- `--output PATH`: TSV output path.
- `--db-path PATH`: SQLite output database path. Default: `new_capd_datebase.db`.
- `--limit N`: process at most N cleaned sentences.
- `--max-input-mb MB`: stop after reading approximately MB MiB from the raw input file.
- `--batch-size N`: update run counters every N source sentences.
- `--resume`: skip sentences already in the database.
- `--scorer heuristic|bert`: fast heuristic scorer or production BERT/LTP scorer.
- `--device auto|cpu|cuda`: BERT device. `auto` uses CUDA when available.
- `--high-threshold FLOAT`: score cutoff for `HIGH` context.
- `--no-augment`: disable GPT expansion.
- `--augment-count N`: GPT variants per `LOW` sentence.
- `--anomaly-threshold FLOAT`: pseudo-PPL cutoff for filtering GPT variants.

Recommended defaults for a first server run:

```bash
--scorer bert --device cuda --no-augment --resume --batch-size 32
```

Add GPT only after the BERT/LTP path is stable, because GPT calls are network/API-bound and can be slow or expensive.

## 5. Local Smoke Test

Run this before renting or using a GPU server:

```bash
python -m data_pipeline.run_pipeline \
  --input data_pipeline/raw_data/corpus.txt \
  --db-path new_capd_datebase.db \
  --output processed_corpus.tsv \
  --limit 20 \
  --batch-size 8 \
  --scorer heuristic \
  --no-augment \
  --resume
```

Then confirm:

```bash
python -m data_pipeline.run_pipeline --help
python -m compileall -q data_pipeline
```

## 6. GPU Server Setup

On a Linux GPU server:

```bash
git clone <your-repo-url>
cd CAPD_Server_Backend

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install a CUDA-enabled PyTorch build if the default `pip install -r requirements.txt` gives you CPU-only PyTorch. Check the official PyTorch install command for your CUDA version, then verify:

```bash
python - <<'PY'
import torch
print("cuda_available:", torch.cuda.is_available())
print("device_count:", torch.cuda.device_count())
print("device_name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
PY
```

If this prints `cuda_available: False`, `--device cuda` will fail and `--device auto` will fall back to CPU.

## 7. Run The First 500 MiB Of Baike Triples

Your large source file is:

```text
data_pipeline/raw_data/baike_triple/baike_triples.txt
```

To process approximately the first 500 MiB with BERT/LTP on GPU and no GPT:

```bash
python -m data_pipeline.run_pipeline \
  --input data_pipeline/raw_data/baike_triple/baike_triples.txt \
  --db-path new_capd_datebase.db \
  --output processed_baike_500m.tsv \
  --max-input-mb 500 \
  --batch-size 32 \
  --resume \
  --scorer bert \
  --device cuda \
  --no-augment
```

Use `--device auto` if you want the script to use GPU when available and CPU otherwise:

```bash
python -m data_pipeline.run_pipeline \
  --input data_pipeline/raw_data/baike_triple/baike_triples.txt \
  --db-path new_capd_datebase.db \
  --output processed_baike_500m.tsv \
  --max-input-mb 500 \
  --batch-size 32 \
  --resume \
  --scorer bert \
  --device auto \
  --no-augment
```

## 8. Run With GPT Augmentation

GPT augmentation needs environment variables:

```bash
export OPENAI_API_KEY="..."
export GPT_API_URL="https://api.openai.com/v1/chat/completions"
export GPT_MODEL="gpt-3.5-turbo"
```

Then run:

```bash
python -m data_pipeline.run_pipeline \
  --input data_pipeline/raw_data/baike_triple/baike_triples.txt \
  --db-path new_capd_datebase.db \
  --output processed_baike_500m_gpt.tsv \
  --max-input-mb 500 \
  --batch-size 32 \
  --resume \
  --scorer bert \
  --device cuda \
  --augment-count 3
```

Notes:

- GPT speed depends on the remote API, not GPU.
- GPT cost scales with the number of `LOW` sentences and `--augment-count`.
- For a first 500 MiB test, run `--no-augment` first, then enable GPT on a smaller `--limit` sample.

## 9. How To Inspect Results

Check row counts:

```bash
python - <<'PY'
import sqlite3
conn = sqlite3.connect("new_capd_datebase.db")
print("sentences:", conn.execute("select count(*) from sentences").fetchone()[0])
print("latest runs:")
for row in conn.execute("""
select id, status, scorer, processed_count, success_count, skipped_count, failed_count, augmented_count, started_at, completed_at
from pipeline_runs
order by id desc
limit 5
"""):
    print(row)
conn.close()
PY
```

Inspect context distribution:

```bash
python - <<'PY'
import sqlite3
conn = sqlite3.connect("new_capd_datebase.db")
for row in conn.execute("select context_type, source, count(*) from sentences group by context_type, source"):
    print(row)
conn.close()
PY
```

## 10. Practical Server Advice

- Start with `--max-input-mb 10` or `--limit 100` to confirm the environment.
- Then try `--max-input-mb 100`.
- Then run `--max-input-mb 500`.
- Keep `--resume` enabled so interrupted runs can continue.
- Keep `--no-augment` enabled until BERT/LTP throughput is acceptable.
- Increase `--batch-size` to 32 or 64 on a stable GPU server to reduce database update overhead.
- Do not commit `new_capd_datebase.db`, `.env`, raw corpus dumps, generated cache files, or API keys.

## 11. Did We Need Code Changes?

Yes. Two small changes were needed for your target workflow:

- `--max-input-mb` was added so the pipeline can process the first 500 MiB of a multi-GB corpus without manually splitting the file.
- `--device auto|cpu|cuda` was added so BERT can explicitly run on GPU.

The previous source files were backed up under:

```text
data_pipeline/source_backups/
```
