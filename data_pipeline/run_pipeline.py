from __future__ import annotations

import argparse
import csv
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))
    from database_manager import (  # type: ignore
        DB_PATH,
        create_pipeline_run,
        finish_pipeline_run,
        init_db,
        insert_sentence,
        log_pipeline_error,
        sentence_exists,
        update_pipeline_run,
    )
    from preprocess import clean_text  # type: ignore
else:
    from .database_manager import (
        DB_PATH,
        create_pipeline_run,
        finish_pipeline_run,
        init_db,
        insert_sentence,
        log_pipeline_error,
        sentence_exists,
        update_pipeline_run,
    )
    from .preprocess import clean_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = Path(__file__).resolve().parent / "raw_data" / "corpus.txt"
DEFAULT_OUTPUT = PROJECT_ROOT / "processed_corpus.txt"


@dataclass
class PipelineStats:
    processed_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    augmented_count: int = 0
    elapsed_seconds: float = 0.0


class HeuristicScorer:
    """Fast offline scorer for smoke tests when BERT/LTP models are unavailable."""

    def calculate_score(self, sentence: str) -> float:
        punctuation_bonus = sum(sentence.count(mark) for mark in "，。？！、") * 0.04
        length_score = min(len(sentence) / 40.0, 1.0) * 0.45
        diversity_score = len(set(sentence)) / max(len(sentence), 1) * 0.35
        score = 0.15 + punctuation_bonus + length_score + diversity_score
        return max(0.0, min(score, 1.0))

    def detect_anomaly(self, sentence: str, threshold: float = 35.0) -> bool:
        del threshold
        if not sentence:
            return True
        repeated_ratio = 1.0 - (len(set(sentence)) / max(len(sentence), 1))
        return len(sentence) < 4 or repeated_ratio > 0.85


def build_scorer(kind: str):
    if kind == "heuristic":
        return HeuristicScorer()

    if __package__ in (None, ""):
        from context_scoring import ContextScorer  # type: ignore
    else:
        from .context_scoring import ContextScorer

    return ContextScorer()


def generate_variants(seed_sentence: str, num_variants: int) -> list[str]:
    if __package__ in (None, ""):
        from llm_augment import generate_similar_sentences  # type: ignore
    else:
        from .llm_augment import generate_similar_sentences

    return generate_similar_sentences(seed_sentence, num_variants=num_variants)


def iter_clean_sentences(input_path: Path, limit: int | None) -> Iterator[tuple[int, str, str]]:
    emitted = 0
    with input_path.open("r", encoding="utf-8") as source:
        for line_number, raw_line in enumerate(source, start=1):
            cleaned = clean_text(raw_line)
            if not cleaned:
                continue
            yield line_number, raw_line.strip(), cleaned
            emitted += 1
            if limit is not None and emitted >= limit:
                break


def batched(items: Iterable[tuple[int, str, str]], batch_size: int) -> Iterator[list[tuple[int, str, str]]]:
    batch: list[tuple[int, str, str]] = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def classify(score: float, threshold: float) -> str:
    return "HIGH" if score >= threshold else "LOW"


def write_output(output_path: Path, rows: Sequence[tuple[str, str, float, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t")
        writer.writerow(["text", "context_type", "score", "source"])
        for text, context_type, score, source in rows:
            writer.writerow([text, context_type, f"{score:.6f}", source])


def run_pipeline(args: argparse.Namespace) -> PipelineStats:
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    db_path = Path(args.db_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input corpus not found: {input_path}")

    init_db(db_path)
    run_id = create_pipeline_run(
        str(input_path),
        str(output_path),
        args.limit,
        args.batch_size,
        args.resume,
        args.scorer,
        not args.no_augment,
        db_path,
    )

    stats = PipelineStats()
    output_rows: list[tuple[str, str, float, str]] = []
    started = time.perf_counter()

    try:
        scorer = build_scorer(args.scorer)
        clean_items = iter_clean_sentences(input_path, args.limit)

        for batch in batched(clean_items, args.batch_size):
            for line_number, raw_text, text in batch:
                if args.resume and sentence_exists(text, db_path):
                    stats.skipped_count += 1
                    continue

                stats.processed_count += 1
                try:
                    score = float(scorer.calculate_score(text))
                    if not math.isfinite(score):
                        raise ValueError(f"non-finite score: {score}")

                    context_type = classify(score, args.high_threshold)
                    if insert_sentence(text, context_type, score, "raw", db_path):
                        stats.success_count += 1
                    else:
                        stats.skipped_count += 1
                    output_rows.append((text, context_type, score, "raw"))

                    if context_type == "LOW" and not args.no_augment:
                        variants = generate_variants(text, args.augment_count)
                        for variant in variants:
                            variant = clean_text(variant)
                            if not variant or variant == text:
                                continue
                            if scorer.detect_anomaly(variant, threshold=args.anomaly_threshold):
                                continue
                            if insert_sentence(variant, "LOW", score, "llm_augment", db_path):
                                stats.augmented_count += 1
                                output_rows.append((variant, "LOW", score, "llm_augment"))

                except Exception as exc:
                    stats.failed_count += 1
                    message = f"line {line_number}: {exc}"
                    log_pipeline_error(run_id, raw_text, message, db_path)

            update_pipeline_run(
                run_id,
                processed_count=stats.processed_count,
                success_count=stats.success_count,
                failed_count=stats.failed_count,
                skipped_count=stats.skipped_count,
                augmented_count=stats.augmented_count,
                db_path=db_path,
            )

        stats.elapsed_seconds = time.perf_counter() - started
        write_output(output_path, output_rows)
        finish_pipeline_run(run_id, "done", db_path=db_path)
        return stats
    except Exception as exc:
        stats.elapsed_seconds = time.perf_counter() - started
        finish_pipeline_run(run_id, "failed", error_message=str(exc), db_path=db_path)
        raise


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CAPD offline corpus pipeline.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Raw corpus path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="TSV output path.")
    parser.add_argument("--db-path", default=str(DB_PATH), help="SQLite database path.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum cleaned source sentences to process.")
    parser.add_argument("--batch-size", type=int, default=8, help="Number of source sentences per checkpoint.")
    parser.add_argument("--resume", action="store_true", help="Skip sentences already present in the database.")
    parser.add_argument(
        "--scorer",
        choices=("bert", "heuristic"),
        default="bert",
        help="Use bert for production scoring or heuristic for offline smoke tests.",
    )
    parser.add_argument("--high-threshold", type=float, default=0.4, help="Score threshold for HIGH context.")
    parser.add_argument("--no-augment", action="store_true", help="Disable GPT augmentation for LOW sentences.")
    parser.add_argument("--augment-count", type=int, default=3, help="Number of GPT variants per LOW sentence.")
    parser.add_argument("--anomaly-threshold", type=float, default=35.0, help="Pseudo-PPL anomaly threshold.")
    args = parser.parse_args(argv)

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if args.augment_count < 0:
        parser.error("--augment-count cannot be negative")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    stats = run_pipeline(args)
    print("Pipeline completed")
    print(f"  database: {args.db_path}")
    print(f"  output: {Path(args.output).resolve()}")
    print(f"  processed: {stats.processed_count}")
    print(f"  inserted_raw: {stats.success_count}")
    print(f"  augmented: {stats.augmented_count}")
    print(f"  skipped: {stats.skipped_count}")
    print(f"  failed: {stats.failed_count}")
    print(f"  elapsed_seconds: {stats.elapsed_seconds:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
