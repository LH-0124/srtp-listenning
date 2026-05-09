import sqlite3

from data_pipeline.run_pipeline import parse_args, run_pipeline


def test_pipeline_help_can_be_rendered():
    try:
        parse_args(["--help"])
    except SystemExit as exc:
        assert exc.code == 0


def test_heuristic_pipeline_smoke_uses_temp_database(tmp_path):
    input_path = tmp_path / "corpus.txt"
    output_path = tmp_path / "processed.tsv"
    db_path = tmp_path / "pipeline.db"
    input_path.write_text("第一句测试材料。\n第二句测试材料。\n", encoding="utf-8")

    args = parse_args(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--db-path",
            str(db_path),
            "--limit",
            "2",
            "--batch-size",
            "1",
            "--scorer",
            "heuristic",
            "--no-augment",
        ]
    )
    stats = run_pipeline(args)

    assert stats.processed_count == 2
    assert stats.failed_count == 0
    assert output_path.exists()
    assert "text\tcontext_type\tscore\tsource" in output_path.read_text(encoding="utf-8")

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM sentences").fetchone()[0] == 2
        run = conn.execute(
            "SELECT status, scorer, processed_count, failed_count FROM pipeline_runs"
        ).fetchone()
    assert run == ("done", "heuristic", 2, 0)
