from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import dlt


WORKSPACE_ROOT = Path(__file__).resolve().parent
DEFAULT_LOG_DIR = WORKSPACE_ROOT / "data" / "claude_logs"


def resolve_log_dir() -> Path:
    env_dir = os.getenv("CLAUDE_LOGS_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    if (Path.home() / ".claude").exists():
        return (Path.home() / ".claude").resolve()

    return DEFAULT_LOG_DIR


def iter_json_files(log_dir: Path) -> Iterator[Path]:
    if not log_dir.exists():
        return

    for path in sorted(log_dir.rglob("*.json")):
        if path.is_file():
            yield path


def load_raw_json_records() -> Iterator[dict[str, object]]:
    log_dir = resolve_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)

    files = list(iter_json_files(log_dir))

    for path in files:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        yield {
            "source_file": str(path),
            "raw_json": json.dumps(payload, ensure_ascii=False),
            "loaded_at": datetime.now(timezone.utc).isoformat(),
        }


@dlt.resource(name="claude_logs_raw", write_disposition="append")
def claude_logs_raw() -> Iterator[dict[str, object]]:
    yield from load_raw_json_records()


def run_pipeline() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="claude_logs_pipeline",
        destination="duckdb",
        dataset_name="claude_logs",
    )

    load_info = pipeline.run(
        claude_logs_raw(),
        table_name="claude_logs_raw",
        write_disposition="replace",
    )
    print(load_info)
    print(f"DuckDB database: {pipeline.pipeline_name}.duckdb")


if __name__ == "__main__":
    run_pipeline()
